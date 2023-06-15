import os
import json
import logging
import requests
import boto3
import sentry_sdk
import pandas as pd
import numpy as np
from datetime import date
from ast import literal_eval
from botocore.exceptions import ClientError
from topic_generator import TopicGenerator
from nlp_modules_utils import (
    Database,
    StateHandler,
    prepare_sql_statement_success,
    prepare_sql_statement_failure,
    status_update_db,
    upload_to_s3,
    send_request_on_callback,
    update_db_table_callback_retry
)

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

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

        self.default_umap_components = os.environ.get("UMAP_COMPONENTS", 24)

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
                self.dispatch_results(status=StateHandler.FAILED.value)
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

    def dispatch_results(self, status, presigned_url=None):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": self.client_id,
            "presigned_s3_url": presigned_url,
            "status": status
        }

        if self.callback_url:
            callback_response = send_request_on_callback(
                self.callback_url,
                response_data=response_data,
                headers=self.headers
            )
            if not callback_response:
                db_client = Database(**self.db_config)
                db_conn, db_cursor = db_client.db_connection()
                update_db_table_callback_retry(
                    db_conn,
                    db_cursor,
                    self.topicmodel_id,
                    self.db_table_callback_tracker
                )
        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if presigned_url and self.db_table_name: # update for presigned url
            sql_statement = prepare_sql_statement_success(
                self.topicmodel_id,
                self.db_table_name,
                status,
                response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                self.topicmodel_id,
                self.db_table_name,
                status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")

    def __call__(self):
        if self.entries_df.empty:
            logging.error("The input data is not available.")
            self.dispatch_results(status=StateHandler.INPUT_URL_PROCESS_FAILED.value)
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
                if df_merged.empty:
                    logging.warning("The clusters could not be formed.")
                    topics_dict = {}
                else:
                    topics_dict = self.select_most_relevant_excerpts(df_merged)
                date_today = date.today().isoformat()
                presigned_url = upload_to_s3(
                    contents=json.dumps(topics_dict),
                    contents_type="application/json",
                    bucket_name=self.bucket_name,
                    key=f"topicmodel/{date_today}/{self.topicmodel_id}/topicmodel.json",
                    aws_region=self.aws_region,
                    signed_url_expiry_secs=self.signed_url_expiry_secs
                )
            except Exception as exc:
                logging.error("Some errors occurred during processing of topics. %s", str(exc))
                presigned_url = None

            if presigned_url:
                self.dispatch_results(status=StateHandler.SUCCESS.value, presigned_url=presigned_url)
            else:
                self.dispatch_results(status=StateHandler.FAILED.value)
        else:
            logging.error("Some errors occurred. Could not generate embeddings of the excerpts")
            self.dispatch_results(status=StateHandler.FAILED.value)

topicmodel_generator_handler = TopicModelGeneratorHandler()
topicmodel_generator_handler()
