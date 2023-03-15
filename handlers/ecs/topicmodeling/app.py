import os
import io
import json
import logging
import psycopg2
import requests
import boto3
import pandas as pd
import numpy as np
from datetime import datetime
from enum import Enum
from ast import literal_eval
from botocore.client import Config
from botocore.exceptions import ClientError
from topic_generator import TopicGenerator

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


class TopicModelGeneratorHandler:
    def __init__(self):
        self.entries_url = os.environ.get("ENTRIES_URL", None)
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.callback_url = os.environ.get("CALLBACK_URL", None)
        self.topicmodel_id = os.environ.get("TOPICMODEL_ID", None)
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)

        self.max_cluster_num = os.environ.get("MAX_CLUSTER_NUM", 5)
        self.cluster_size = os.environ.get("CLUSTER_SIZE")
        
        self.entries_df = self._download_prepare_entries()
        self.embeddings = self._get_embeddings(self.entries_df.excerpts)

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

        self.db_table_name = os.environ.get("DB_TBL_NAME", "test")

        if not self.callback_url:
            self.status_update_db(
                sql_statement=f""" INSERT INTO {self.db_table_name} (status, unique_id, s3_link) VALUES ({ReportStatus.INITIATED.value},{self.topicmodel_id},'') """
            )
    
    def _download_prepare_entries(self):
        """
        The json format (*.json) in the link file should be
        [
            {
                "entry_id": int,
                "excerpt": str
            }
        ]
        """
        if self.entries_url:
            logging.info(f"The request url is {self.entries_url}")
            try:
                response = requests.get(self.entries_url)
                entries_data = json.loads(response.text)
                return pd.DataFrame(entries_data)
            except Exception as e:
                logging.error(f"Error occurred: {str(e)}")
        return None

    def _get_embeddings(
        self,
        excerpts: list,
        model_name: str = "main-model-cpu",
        pooling_type: list = ["cls"],
        finetuned_task: list = ["first_level_tags"],
        return_type: str = "default_analyis",
        embeddings_return_type: str = "array",
        batch_size: int = 5
    ):  
        total = []
        
        client = boto3.client("sagemaker-runtime", region_name=self.aws_region)
        
        for i in range(0, len(excerpts), batch_size):
            batch = excerpts[i:i+batch_size]
            
            req = {
                "excerpt": batch,
                "output_backbone_embeddings": True,
                "return_prediction_labels": False,
                "interpretability": False,
                "pooling_type": str(pooling_type),
                "finetuned_task": str(finetuned_task),
                "return_type": return_type,
                "embeddings_return_type": embeddings_return_type
            }
            
            
            response = client.invoke_endpoint(
                EndpointName=model_name,
                Body=pd.DataFrame(req).to_json(orient="split"),
                ContentType="application/json; format=pandas-split",
            )
            
            output = literal_eval(response["Body"].read().decode("ascii"))
            total.append(output["output_backbone"])
        
        return np.vstack([x for b in total for x in  b])

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
        except ClientError as e:
            logging.error(f"Error while generating presigned url {e}")
            return None
        return url

    def topicmodel_summary(self, summary, bucket_name="test-ecs-parser11", key="summary.txt"):
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
        try:
            response = requests.post(
                self.callback_url,
                headers=self.headers,
                data=json.dumps({
                    "client_id": self.client_id,
                    "topicmodel_s3_url": presigned_url
                }),
                timeout=30
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Exception occurred while sending request - {e}")
        if response.status == 200:
            logging.info("Successfully sent the request on callback url")
        else:
            logging.error("Error while sending the request on callback url")

    
    def __call__(self):
        if not self.entries_df.empty and self.embeddings.any():
            topicmodel_summary = TopicGenerator(
                self.entries_df.excerpts,
                self.embeddings
            )
            topicmodel_summary.get_total_topics(n_topics=self.max_cluster_num)
            topicmodel_df = topicmodel_summary.topics_df
            topicmodel_merged_df = pd.merge(topicmodel_df, self.entries_df, how="left", on=["excerpts"])
            topicmodel_op_dict = topicmodel_merged_df.groupby("topics")["entry_id"].apply(list).to_dict()
            logging.info(topicmodel_op_dict)
            date_today = str(datetime.now().date())
            presigned_url = self.topicmodel_summary(
                summary=json.dumps(topicmodel_op_dict),
                bucket_name=self.bucket_name,
                key=f"topicmodel/{date_today}/{self.topicmodel_id}/topicmodel.json"
            )

            if self.callback_url:
                self.send_request_on_callback(presigned_url)
            elif presigned_url: # update for presigned url
                self.status_update_db(
                    sql_statement=f""" UPDATE {self.db_table_name} SET status='{ReportStatus.SUCCESS.value}', s3_link='{presigned_url}' WHERE unique_id='{self.topicmodel_id}' """
                )
            else:
                # Presigned url generation failed
                self.status_update_db(
                    sql_statement=f""" UPDATE {self.db_table_name} SET status='{ReportStatus.FAILED.value}' WHERE unique_id='{self.topicmodel_id}' """
                )
        else:
            logging.error("Some errors occurred.")


topicmodel_generator_handler = TopicModelGeneratorHandler()
topicmodel_generator_handler()
