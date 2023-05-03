import os
import io
import json
import logging
import psycopg2
import requests
import boto3
import sentry_sdk
import pandas as pd
import numpy as np
from datetime import date, datetime
from enum import Enum
from ast import literal_eval
from botocore.client import Config
from botocore.exceptions import ClientError
from topic_generator import TopicGenerator

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

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
        self.entries_url = os.environ.get("ENTRIES_URL", None)
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.callback_url = os.environ.get("CALLBACK_URL", None)
        self.topicmodel_id = os.environ.get("TOPICMODEL_ID", None)
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)

        self.max_cluster_num = int(os.environ.get("MAX_CLUSTERS_NUM", 10))
        self.cluster_size = int(os.environ.get("CLUSTER_SIZE", 200))

        self.headers = {
            "Content-Type": "application/json"
        }

        self.default_umap_components = os.environ.get("UMAP_COMPONENTS", 25)

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

        self.entries_df = self._download_prepare_entries()
        if self.entries_df.empty:
            self.embeddings = np.array([])
        else:
            self.embeddings = self._get_embeddings(self.entries_df.Document)

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
                    df = pd.DataFrame(response.json())
                    self.rename_columns(df)
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
        batch_size: int = 10
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

            try:
                response = client.invoke_endpoint(
                    EndpointName=model_name,
                    Body=pd.DataFrame(req).to_json(orient="split"),
                    ContentType="application/json; format=pandas-split",
                )
            except ClientError as cexc:
                self.dispatch_results(status=ReportStatus.FAILED.value)
                raise Exception(f"Error occurred while invoking sagemaker endpoint. {str(cexc)}")

            output = literal_eval(response["Body"].read().decode("ascii"))
            total.append(output["output_backbone"])

        return np.vstack([x for b in total for x in  b])

    def rename_columns(self, df):
        """
        Renames the column names
        """
        df.rename(columns={"excerpt":"Document"}, inplace=True)

    def generate_topics(self, entries, entries_embeddings, n_topics=15, umap_n_compontens=25):
        """
        Generates the topic predicted by the Bertopic library
        """
        topic_model = TopicGenerator(entries, entries_embeddings)
        topic_model.get_total_topics(n_topics=n_topics, umap_n_compontens=umap_n_compontens)
        return topic_model.general_topics_df

    def create_complete_df(self, main_df, topic_model_df):
        """
        Merge the input dataframe with the topic model dataframe
        and also includes embeddings as a column
        """
        return topic_model_df.merge(main_df, how="inner", on="Document")

    def exclude_topic_clusters(self, dataframe, topic_value=-1):
        """
        Excludes the topic from the dataframe.
        """
        return dataframe[dataframe["Topic"] != topic_value]

    def select_most_relevant_excerpts(self, df):
        """
        Select only the most relevant excerpts if it exceeds the cluster size
        """
        df.set_index("entry_id", inplace=True)
        df_per_topic_nlargest = df.groupby("Topic")["Probability"].nlargest(self.cluster_size).reset_index()
        return df_per_topic_nlargest.groupby("Topic")["entry_id"].apply(list).to_dict()

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
    
    def _update_db_table_callback_retry(self):
        """
        Updates the table whenever the callback fails
        """
        if self.db_table_callback_tracker and self.topicmodel_id:
            now_date = datetime.now().isoformat()
            self.status_update_db(
                sql_statement=f""" INSERT INTO {self.db_table_callback_tracker} 
                                (request_unique_id, created_at, modified_at, retries_count, status) 
                                VALUES ('{self.topicmodel_id}', '{now_date}', '{now_date}', 0, 3) """  # status = 3(Retrying)
            )
            logging.info("Updated the db table for callback retries.")

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
            logging.error("Exception occurred while sending request %s", str(rexc))
            self._update_db_table_callback_retry()
        if response.status_code == 200:
            logging.info("Successfully sent the request on callback url")
        else:
            logging.error("Error while sending the request on callback url")
            self._update_db_table_callback_retry()

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
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}' WHERE unique_id='{self.topicmodel_id}' """
            )
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")

    def __call__(self):
        if self.entries_df.empty:
            logging.error("The input data is not available.")
            self.dispatch_results(status=ReportStatus.INPUT_URL_PROCESS_FAILED.value)
            return

        if self.embeddings.any():
            entries = self.entries_df.Document.to_list()
            try:
                df_topics = self.generate_topics(
                    entries,
                    self.embeddings,
                    n_topics=self.max_cluster_num,
                    umap_n_compontens=self.default_umap_components
                )
                df_merged = self.create_complete_df(self.entries_df, df_topics)
                df_merged = self.exclude_topic_clusters(df_merged)
                topics_dict = self.select_most_relevant_excerpts(df_merged)
                date_today = date.today().isoformat()
                presigned_url = self.topicmodel_summary(
                    tm_summary=json.dumps(topics_dict),
                    bucket_name=self.bucket_name,
                    key=f"topicmodel/{date_today}/{self.topicmodel_id}/topicmodel.json"
                )
            except Exception as exc:
                logging.error("Some errors occurred during processing of topics. %s", str(exc))
                presigned_url = None

            if presigned_url:
                self.dispatch_results(status=ReportStatus.SUCCESS.value, presigned_url=presigned_url)
            else:
                self.dispatch_results(status=ReportStatus.FAILED.value)
        else:
            logging.error("Some errors occurred. Could not generate embeddings of the excerpts")
            self.dispatch_results(status=ReportStatus.FAILED.value)

topicmodel_generator_handler = TopicModelGeneratorHandler()
topicmodel_generator_handler()
