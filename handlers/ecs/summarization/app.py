import os
import io
import json
import logging
import psycopg2
import requests
import boto3
from datetime import datetime
from enum import Enum
from botocore.client import Config
from botocore.exceptions import ClientError
from huggingface_hub import snapshot_download
from reports_generator import ReportsGenerator

logging.getLogger().setLevel(logging.INFO)

class ReportStatus(Enum):
    INITIATED = 1
    SUCCESS = 2
    FAILED = 3

class Database:
    def __init__(
        self,
        endpoint: str,
        database: str,
        username: str,
        password: str,
        port: int=5432,
    ):
        self.endpoint = endpoint
        self.database = database
        self.username = username
        self.password = password
        self.port = port
    
    def __call__(self):
        try:
            conn = psycopg2.connect(
                host=self.endpoint,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            cur = conn.cursor()
            return conn, cur
        except Exception as e:
            logging.error(f"Database connection failed {e}")
            return None, None


class ReportsGeneratorHandler:
    def __init__(self):
        test_entry = '''
        “Since the start of the full-scale war we, along with our humanitarian partners in Ukraine, have made every effort to ramp up operations to provide life-saving support to those who need it most,” UN Spokesperson Stéphane Dujarric told journalists in New York. Last year, thousands of convoys delivered vital supplies to people in all regions of the country, he said, and humanitarians reached nearly 16 million with aid, including water, medicines, heating appliances, and other supplies, as well as support for home repairs. Some six million people received cash assistance totalling $1.2 billion – the largest such programme in history, he added. As the war enters a second year, the UN and partners are calling for nearly $4 billion to support more than 11 million people. The appeal is just over 14 per cent funded, Mr. Dujarric said.  **Young lives lost ** UN agencies have been taking stock of the death, destruction, devastation, and displacement that have occurred in Ukraine over the past 12 months. Nearly 500 children have been killed and almost 1,000 injured, UN humanitarians said on Friday in Geneva. In addition to that terrible human toll, the UN Children’s Fund (UNICEF) said that more than 800 health facilities had been damaged or destroyed by shelling. Education under fire The fighting has also disrupted access to education, and thousands of pre-schools and secondary schools have been damaged. In total, 7.8 million children have been impacted and more than five million have no access to schooling in Ukraine at all, UNICEF warned. Toxic legacy looms. The war will have a toxic legacy for generations to come, the UN Environment Programme (UNEP) said earlier in the week, reporting on a preliminary monitoring of the conflict conducted last year together with partners. While UNEP will verify the full range and severity, the agency noted that “thousands of possible incidents of air, water, and land pollution and the degradation of ecosystems, including risks to neighbouring countries, have already been identified.” UNEP is supporting the Ukrainian Government on remote environmental impact monitoring and is preparing to undertake field-level impact assessments – expected to be a colossal task, due to the scale and geographical spread of reported incidents. “The mapping and initial screening of environmental hazards only serves to confirm that war is quite literally toxic,” said UNEP Executive Director Inger Andersen. “Ukraine will then need huge international support to assess, mitigate, and remediate the damage across the country, and alleviate risks to the wider region,” she added.  Air and waters polluted. The data showed that the conflict has resulted in damage across many regions of the country, with incidents at nuclear power plants and facilities; energy infrastructure, including oil storage tankers, oil refineries, and drilling platforms; and other locations as well as distribution pipelines, mines, industrial sites, and agro-processing facilities.  The result has been multiple incidents of air pollution and potentially serious contamination of ground and surface waters, UNEP said.  Significant damage has also occurred to such water infrastructure as pumping stations, purification plants, and sewage facilities. Clean-up challenges  UNEP added that hazardous substances have also been released from explosions in agro-industrial storage facilities, including fertilizer and nitric acid plants. Damage also extends to urban areas, where the clean-up of destroyed housing could lead to debris being mixed with hazardous chemicals, particularly asbestos. Furthermore, satellite imagery has also revealed a significant increase of fires in various nature reserves, protected areas, and forests. Additionally, pollution from weapons use, and the large volumes of military waste, also creates a major clean-up challenge, the UN agency said. Averting nuclear disaster. The conflict has also marked the first time in history that a war is being fought amid the facilities of a major nuclear power programme. The International Atomic Energy Agency (IAEA) issued a report this week highlighting its activities to reduce the likelihood of a nuclear accident during the fighting. IAEA has been working to implement a nuclear safety and security protection zone at the Zaporizhzhya Nuclear Power Plant, the largest in Europe, which has been occupied by Russian forces since the early weeks of the war. The plant has repeatedly come under fire, sparking fears of a nuclear disaster.
        '''
        self.entries = test_entry #os.environ.get("ENTRIES", [])
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.callback_url = os.environ.get("CALLBACK_URL", None)
        self.summarization_id = os.environ.get("SUMMARIZATION_ID", 123)
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", "test")

        # db
        self.db_config = {
            "endpoint": os.environ.get("DB_HOST"),
            "database": os.environ.get("DB_NAME"),
            "username": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PWD"),
            "port": os.environ.get("DB_PORT")
        }

        self.db_table_name = os.environ.get("DB_TBL_NAME", "test")

        if not self.callback_url:
            self.status_update_db(
                sql_statement=f""" INSERT INTO {self.db_table_name} (status, unique_id, s3_link) VALUES ({ReportStatus.INITIATED.value},{self.summarization_id},'') """
            )
    
    def download_models(
            self,
            summ_model: str="csebuetnlp/mT5_multilingual_XLSum",
            sent_embedding_model: str="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        model_info = {}
        if not any(os.listdir("/models")):
            summarization_model_local_path = snapshot_download(
                repo_id=summ_model,
                cache_dir="/models"
            )
            summarization_embedding_model_local_path = snapshot_download(
                repo_id=sent_embedding_model,
                cache_dir="/models"
            )
            model_info = {
                "summarization_model_path": summarization_model_local_path,
                "summarization_embedding_model_path": summarization_embedding_model_local_path
            }
            with open("/models/model_info.json", "w", encoding="utf-8") as f:
                json.dump(model_info, f)
        else:
            model_info_path = "/models/model_info.json"
            if os.path.exists(model_info_path):
                with open(model_info_path, "r") as f:
                    model_info = json.load(f)
            else:
                return {}
        return model_info

    def generate_presigned_url(self, bucket_name, key):
        # Note that the bucket and service(e.g. summarization) should run on the same aws region
        try:
            s3_client = boto3.client(
                "s3",
                region_name=self.aws_region,
                config=Config(
                    signature_version="s3v4",
                    s3={"addressing_style": "path"}
                )
            )
            url = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": key
                },
                ExpiresIn=self.signed_url_expiry_secs
            )
            print(f"The url is {url}")
        except ClientError as e:
            logging.error(f"Error while generating presigned url {e}")
            return None
        return url

    def summary_store_s3(self, summary, bucket_name="test-ecs-parser11", key="summary.txt"):
        try:
            session = boto3.Session()
            s3_resource = session.resource("s3")
            bucket = s3_resource.Bucket(bucket_name)
            summary_bytes = bytes(summary, "utf-8")
            summary_bytes_obj = io.BytesIO(summary_bytes)
            bucket.upload_fileobj(summary_bytes_obj, key)
            return self.generate_presigned_url(bucket_name, key)
        except ClientError as e:
            logging.error(str(e))
            return None


    def status_update_db(self, sql_statement):
        db = Database(**self.db_config)
        db_conn, db_cursor = db()
        if db_cursor:
            try:
                db_cursor.execute(sql_statement)
                logging.info(f"Db updated. Number of rows affected: {db_cursor.rowcount}")
                db_conn.commit()
                db_cursor.close()
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error(error)
            finally:
                if db_conn is not None:
                    db_conn.close()
    
    def send_request_on_callback(self, presigned_url):
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(
                self.callback_url,
                headers=headers,
                data=json.dumps({
                    "client_id": self.client_id,
                    "summary_s3_url": presigned_url
                }),
                timeout=30
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception occurred while sending request - {e}")
        if response.status == 200:
            logging.info("Successfully sent the request on callback url")
        else:
            logging.error("Error while sending the request on callback url")

    
    def __call__(self, model_info):
        if ("summarization_model_path" and 
            "summarization_embedding_model_path" in model_info):
            self.repgen = ReportsGenerator(
                summarization_model_name=model_info["summarization_model_path"],
                sentence_embedding_model_name=model_info["summarization_embedding_model_path"],
                device="cpu"
            )
            summary = self.repgen(self.entries)
            date_today = str(datetime.now().date())
            presigned_url = self.summary_store_s3(
                summary=summary,
                bucket_name=self.bucket_name,
                key=f"{self.summarization_id}/{date_today}/summary.txt"
            )

            if self.callback_url:
                self.send_request_on_callback(presigned_url)
            elif presigned_url: # update for presigned url
                self.status_update_db(
                    sql_statement=f""" UPDATE {self.db_table_name} SET status='{ReportStatus.SUCCESS.value}', s3_link='{presigned_url}' WHERE unique_id='{self.summarization_id}' """
                )
            else:
                # Presigned url generation failed
                self.status_update_db(
                    sql_statement=f""" UPDATE {self.db_table_name} SET status='{ReportStatus.FAILED.value}' WHERE unique_id='{self.summarization_id}' """
                )
            return summary
        else:
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{ReportStatus.FAILED.value}' WHERE unique_id='{self.summarization_id}' """
            )
            return "Summarization models could not be loaded."


reports_generator_handler = ReportsGeneratorHandler()
model_info = reports_generator_handler.download_models()
result = reports_generator_handler(model_info=model_info)
logging.info(f"Result generated: {result}")
