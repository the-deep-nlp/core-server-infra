import os
import io
import json
import logging
import psycopg2
import requests
import boto3
import sentry_sdk
from pathlib import Path
from datetime import date, datetime
from enum import Enum
from botocore.client import Config
from botocore.exceptions import ClientError
from huggingface_hub import snapshot_download
from reports_generator import ReportsGenerator

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Union

logging.getLogger().setLevel(logging.INFO)

logging.info("Loaded module as ecs task.")

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

# Note: boto3 initialization outside class to make it thread safe.
# s3_client for generating presigned Url.
s3_client = boto3.client(
    "s3",
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)

class InputStructure(BaseModel):
    """Input Str"""
    entries_url: Union[str, None] = None
    client_id: Union[str, None] = None
    callback_url: Union[str, None] = None
    summarization_id: Union[str, None] = None

ecs_app = FastAPI()

@ecs_app.get("/")
def home():
    """ Test endpoint """
    return "Welcome to the ECS Task of Summarization Module v2."

@ecs_app.post("/generate_report")
async def gen_report(item: InputStructure, background_tasks: BackgroundTasks):
    """Generate reports"""
    entries_url = item.entries_url
    client_id = item.client_id
    callback_url = item.callback_url
    summarization_id = item.summarization_id

    entries = reports_generator_handler.download_prepare_entries(entries_url=entries_url)

    background_tasks.add_task(
        reports_generator_handler,
        client_id,
        entries,
        summarization_id,
        callback_url
    )

    return {
        "message": "Task received and running in background."
    }


class ReportStatus(Enum):
    """
    List of categories to indicate the status of task
    """
    INITIATED = 1
    SUCCESS = 2
    FAILED = 3
    INPUT_URL_PROCESS_FAILED = 4

class Database:
    """
    Class to handle database connections
    """
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
        except Exception as exc:
            logging.error("Database connection failed %s", exc)
            return None, None


class ReportsGeneratorHandler:
    """
    Summarization class to generate summary of the excerpts
    """
    def __init__(self):
        self.repgenerator = None

        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)

        self.headers = {
            "Content-Type": "application/json"
        }

        # db
        self.db_config = {
            "endpoint": os.environ.get("DB_HOST"),
            "database": os.environ.get("DB_NAME"),
            "username": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PWD"),
            "port": os.environ.get("DB_PORT")
        }

        self.db_table_name = os.environ.get("DB_TABLE_NAME", None)
        self.db_table_callback_tracker = os.environ.get("DB_TABLE_CALLBACK_TRACKER", None)

        if not self.db_table_name:
            logging.error("Database table name is not found.")

    def download_prepare_entries(self, entries_url):
        """
        The json format (*.json) in the link file should be
        [
            {
                "entry_id": int,
                "excerpt": str
            }
        ]
        """
        if entries_url:
            logging.info("The request url is %s", entries_url)
            try:
                response = requests.get(entries_url, timeout=30)
                if response.status_code == 200:
                    return [x["excerpt"] for x in response.json()]
            except Exception as exc:
                logging.error("Error occurred: %s", str(exc))
        return None


    def download_models(
            self,
            summ_model: str="csebuetnlp/mT5_multilingual_XLSum",
            sent_embedding_model: str="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Downloads the models and store them in the EFS
        """
        model_info = {}
        models_path = Path("/models/summarization")
        models_info_path = models_path / "model_info.json"

        if not os.path.exists(models_path):
            os.makedirs(models_path)

        if not any(os.listdir(models_path)):
            logging.info("Downloading the summarization resources.")
            summarization_model_local_path = snapshot_download(
                repo_id=summ_model,
                cache_dir=models_path
            )
            summarization_embedding_model_local_path = snapshot_download(
                repo_id=sent_embedding_model,
                cache_dir=models_path
            )
            model_info = {
                "summarization_model_path": summarization_model_local_path,
                "summarization_embedding_model_path": summarization_embedding_model_local_path
            }
            with open(models_info_path, "w", encoding="utf-8") as models_info_f:
                json.dump(model_info, models_info_f)
        else:
            if os.path.exists(models_info_path):
                logging.info("Resources already exist in the EFS.")
                with open(models_info_path, "r", encoding="utf-8") as models_info_f:
                    model_info = json.load(models_info_f)
                    logging.info(model_info)
            else:
                return {}
        return model_info

    def generate_presigned_url(self, bucket_name, key):
        """
        Generates a presigned url of the file stored in s3
        """
        # Note that the bucket and service(e.g. summarization) should run on the same aws region
        try:
            url = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": key
                },
                ExpiresIn=self.signed_url_expiry_secs
            )
        except ClientError as cexc:
            logging.error("Error while generating presigned url %s", cexc)
            return None
        return url

    def summary_store_s3(self, summary, bucket_name="test-ecs-parser11", key="summary.txt"):
        """
        Stores the summary in s3
        """
        try:
            session = boto3.Session()
            s3_resource = session.resource("s3")
            bucket = s3_resource.Bucket(bucket_name)
            summary_bytes = bytes(summary, "utf-8")
            summary_bytes_obj = io.BytesIO(summary_bytes)
            bucket.upload_fileobj(
                summary_bytes_obj,
                key,
                ExtraArgs={"ContentType": "text/plain; charset=utf-8"}
            )
            return self.generate_presigned_url(bucket_name, key)
        except ClientError as cexp:
            logging.error(str(cexp))
            return None


    def status_update_db(self, sql_statement):
        """
        Updates the status in the database
        """
        db = Database(**self.db_config)
        db_conn, db_cursor = db()
        if db_cursor:
            try:
                db_cursor.execute(sql_statement)
                logging.info("Db updated. Number of rows affected: %s", db_cursor.rowcount)
                db_conn.commit()
                db_cursor.close()
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error(error)
            finally:
                if db_conn is not None:
                    db_conn.close()
    
    def _update_db_table_callback_retry(self, summarization_id):
        """
        Updates the table whenever the callback fails
        """
        if self.db_table_callback_tracker and summarization_id:
            now_date = datetime.now().isoformat()
            self.status_update_db(
                sql_statement=f""" INSERT INTO {self.db_table_callback_tracker} 
                                (request_unique_id, created_at, modified_at, retries_count, status) 
                                VALUES ('{summarization_id}', '{now_date}', '{now_date}', 0, 3) """  # status = 3(Retrying)
            )
            logging.info("Updated the db table for callback retries.")

    def send_request_on_callback(self, client_id, callback_url, summarization_id, presigned_url, status):
        """
        Sends the results in a callback url
        """
        try:
            response = requests.post(
                callback_url,
                headers=self.headers,
                data=json.dumps({
                    "client_id": client_id,
                    "presigned_s3_url": presigned_url,
                    "status": status
                }),
                timeout=30
            )
        except requests.exceptions.RequestException as rexc:
            logging.error("Exception occurred while sending request %s", str(rexc))
            self._update_db_table_callback_retry(summarization_id)
        if response.status_code == 200:
            logging.info("Successfully sent the request on callback url")
        else:
            logging.error("Error while sending the request on callback url")
            self._update_db_table_callback_retry(summarization_id)

    def dispatch_results(self, client_id, summarization_id, callback_url, status, presigned_url=None):
        """
        Dispatch results to callback url or write to database
        """
        if callback_url:
            self.send_request_on_callback(client_id, callback_url, summarization_id, presigned_url=presigned_url, status=status)
        if presigned_url and self.db_table_name: # update for presigned url
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}', result_s3_link='{presigned_url}' WHERE unique_id='{summarization_id}' """
            )
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}' WHERE unique_id='{summarization_id}' """
            )
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")
    
    def load_model(self, model_info):
        """
        Loads the summarization model
        """
        if ("summarization_model_path" and 
            "summarization_embedding_model_path" in model_info):
            self.repgenerator = ReportsGenerator(
                summarization_model_name=model_info["summarization_model_path"],
                sentence_embedding_model_name=model_info["summarization_embedding_model_path"],
                device="cpu"
            )


    def __call__(self, client_id, entries, summarization_id, callback_url):
        if not entries:
            self.dispatch_results(client_id, summarization_id, callback_url, status=ReportStatus.INPUT_URL_PROCESS_FAILED.value)
            return

        if self.repgenerator:
            summary = self.repgenerator(entries)
            date_today = date.today().isoformat()
            presigned_url = self.summary_store_s3(
                summary=summary,
                bucket_name=self.bucket_name,
                key=f"summarization/{date_today}/{summarization_id}/summary.txt"
            )

            if presigned_url:
                self.dispatch_results(client_id, summarization_id, callback_url, status=ReportStatus.SUCCESS.value, presigned_url=presigned_url)
            else:
                self.dispatch_results(client_id, summarization_id, callback_url, status=ReportStatus.FAILED.value)
        else:
            self.dispatch_results(client_id, summarization_id, callback_url, status=ReportStatus.FAILED.value)
            logging.warning("Summarization models could not be loaded.")


reports_generator_handler = ReportsGeneratorHandler()
model_info_dict = reports_generator_handler.download_models()
reports_generator_handler.load_model(model_info_dict)
