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


class TopicModelGeneratorHandler:
    """
    TopicModel class to generate clusters from the excerpts
    """
    def __init__(self):
        action_type = "topicmodel"
        self.entries_url = os.environ.get("ENTRIES_URL", None)
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.callback_url = os.environ.get("CALLBACK_URL", None)
        self.topicmodel_id = os.environ.get("TOPICMODEL_ID", None)
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)

        self.max_cluster_num = os.environ.get("MAX_CLUSTER_NUM", 5)
        self.cluster_size = os.environ.get("CLUSTER_SIZE")

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

        if self.db_table_name:
            self.status_update_db(
                sql_statement=f""" INSERT INTO {self.db_table_name} (status, unique_id, result_s3_link, type) VALUES ({ReportStatus.INITIATED.value},{self.topicmodel_id},'', {action_type}) """
            )
        else:
            logging.error("Database table name is not found.")

        self.entries_df = self._download_prepare_entries()
        if self.entries_df.empty:
            self.embeddings = np.array([])
        else:
            self.embeddings = self._get_embeddings(self.entries_df.excerpts)

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
            logging.info("The request url is %s", self.entries_url)
            try:
                response = requests.get(self.entries_url, timeout=30)
                if response.status_code == 200:
                    entries_data = json.loads(response.text)
                    df = pd.DataFrame(entries_data)
                    df.rename({"excerpt":"excerpts"}, axis=1, inplace=True)
                    return df
            except Exception as exc:
                logging.error("Error occurred: %s", str(exc))
        return pd.DataFrame([], columns=["excerpts", "entry_id"])

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
        """
        Calculates the embeddings of the entries
        """
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
        """
        Generates a presigned url of the file stored in s3
        """
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
        except ClientError as cexc:
            logging.error("Error while generating presigned url %s", cexc)
            return None
        return url

    def topicmodel_summary(self, tm_summary, bucket_name="test-ecs-parser11", key="topicmodel.json"):
        """
        Stores the topic model clusters in s3
        """
        try:
            session = boto3.Session()
            s3_resource = session.resource("s3")
            bucket = s3_resource.Bucket(bucket_name)
            tm_summary_bytes = bytes(tm_summary, "utf-8")
            tm_summary_bytes_obj = io.BytesIO(tm_summary_bytes)
            bucket.upload_fileobj(
                tm_summary_bytes_obj,
                key,
                ExtraArgs={"ContentType": "application/json"}
            )
            return self.generate_presigned_url(bucket_name, key)
        except ClientError as cexc:
            logging.error(str(cexc))
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

    def send_request_on_callback(self, presigned_url, status):
        """
        Sends the results in a callback url
        """
        try:
            response = requests.post(
                self.callback_url,
                headers=self.headers,
                data=json.dumps({
                    "client_id": self.client_id,
                    "presigned_s3_url": presigned_url,
                    "status": status
                }),
                timeout=30
            )
        except requests.exceptions.RequestException as rexc:
            raise Exception(f"Exception occurred while sending request - {rexc}")
        if response.status_code == 200:
            logging.info("Successfully sent the request on callback url")
        else:
            logging.error("Error while sending the request on callback url")

    def dispatch_results(self, status, presigned_url=None):
        """
        Dispatch results to callback url or write to database
        """
        if self.callback_url:
            self.send_request_on_callback(presigned_url=presigned_url, status=status)
        if presigned_url and self.db_table_name: # update for presigned url
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}', result_s3_link='{presigned_url}' WHERE unique_id='{self.topicmodel_id}' """
            )
        elif self.db_table_name:
            # Presigned url generation failed
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}' WHERE unique_id='{self.topicmodel_id}' """
            )
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")

    def __call__(self):
        if self.entries_df.empty:
            self.dispatch_results(status=ReportStatus.INPUT_URL_PROCESS_FAILED.value)
            return

        if self.embeddings.any():
            topicmodel_summary = TopicGenerator(
                self.entries_df.excerpts,
                self.embeddings
            )
            topicmodel_summary.get_total_topics(n_topics=self.max_cluster_num)
            topicmodel_df = topicmodel_summary.topics_df
            topicmodel_merged_df = pd.merge(topicmodel_df, self.entries_df, how="left", on=["excerpts"])
            topicmodel_op_dict = topicmodel_merged_df.groupby("topics")["entry_id"].apply(list).to_dict()

            date_today = str(datetime.now().date())
            presigned_url = self.topicmodel_summary(
                tm_summary=json.dumps(topicmodel_op_dict),
                bucket_name=self.bucket_name,
                key=f"topicmodel/{date_today}/{self.topicmodel_id}/topicmodel.json"
            )

            if presigned_url:
                self.dispatch_results(status=ReportStatus.SUCCESS.value, presigned_url=presigned_url)
            else:
                self.dispatch_results(status=ReportStatus.FAILED.value)
        else:
            logging.error("Some errors occurred. Could not generate embeddings of the excerpts")
            self.dispatch_results(status=ReportStatus.FAILED.value)

topicmodel_generator_handler = TopicModelGeneratorHandler()
topicmodel_generator_handler()
