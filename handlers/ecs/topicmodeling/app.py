import json
import logging
import os
from ast import literal_eval
from datetime import date
from typing import Optional

import boto3
import numpy as np
import pandas as pd
import requests
import sentry_sdk
from botocore.exceptions import ClientError
from fastapi import BackgroundTasks, FastAPI
from group_tags import GroupTags
from nlp_modules_utils import (Database, StateHandler,
                               prepare_sql_statement_failure,
                               prepare_sql_statement_success,
                               send_request_on_callback, status_update_db,
                               update_db_table_callback_retry, upload_to_s3)
from pydantic import BaseModel
from topic_generator import TopicGenerator
from topic_generator_llm import TopicGenerationLLM
from utils import preprocess_text

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(
    SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0
)


class RequestSchema(BaseModel):
    """Request Schema"""

    client_id: str
    entries_url: str
    topicmodel_id: str
    callback_url: str
    max_cluster_num: Optional[int] = 10
    cluster_size: Optional[int] = 200
    umap_components: Optional[int] = 3


ecs_app = FastAPI()


@ecs_app.get("/")
def home():
    """Home page message for Topic Modeling"""
    return "This is Topic Modeling ECS Task page."


@ecs_app.get("/healthcheck")
async def healthcheckup():
    """Health check up endpoint"""
    return "The task is ok and running."


@ecs_app.post("/get_excerpt_clusters")
async def excerpts_cluster(item: RequestSchema, background_tasks: BackgroundTasks):
    """Request handler for topics generation"""
    topicmodel_generator_handler.client_id = item.client_id
    topicmodel_generator_handler.entries_url = item.entries_url
    topicmodel_generator_handler.topicmodel_id = item.topicmodel_id
    topicmodel_generator_handler.callback_url = item.callback_url
    topicmodel_generator_handler.max_cluster_num = item.max_cluster_num
    topicmodel_generator_handler.cluster_size = item.cluster_size
    topicmodel_generator_handler.umap_components = item.umap_components

    topicmodel_generator_handler.initiation_tasks()

    background_tasks.add_task(topicmodel_generator_handler)

    return {"message": "Task received and running in background."}


class TopicModelGeneratorHandler:
    """
    TopicModel class to generate clusters from the excerpts
    """

    def __init__(self):
        self.entries_url = None
        self.client_id = None
        self.callback_url = None
        self.topicmodel_id = None

        self.max_cluster_num = None
        self.cluster_size = None
        self.umap_components = None

        self.entries_df = pd.DataFrame([], columns=["excerpts", "entry_id"])
        self.embeddings = np.vstack([[]])

        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get(
            "SIGNED_URL_EXPIRY_SECS", 86400
        )  # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)

        self.headers = {"Content-Type": "application/json"}

        # db
        self.db_config = {
            "endpoint": os.environ.get("DB_HOST"),
            "database": os.environ.get("DB_NAME"),
            "username": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PWD"),
            "port": os.environ.get("DB_PORT"),
        }

        self.db_table_name = os.environ.get("DB_TABLE_NAME", None)
        self.db_table_callback_tracker = os.environ.get(
            "DB_TABLE_CALLBACK_TRACKER", None
        )

        self.topic_tags = []
        self.group_tags_handler = GroupTags()

        if not self.db_table_name:
            logging.error("Database table name is not found.")

    def initiation_tasks(self):
        """Execute initial tasks"""
        self.entries_df = self._download_prepare_entries()
        # Preprocessing
        self.entries_df["Document"] = self.entries_df.Document.apply(preprocess_text)
        self.entries_df = self.entries_df[self.entries_df["Document"] != ""]
        self.entries_df.reset_index(drop=True, inplace=True)
        logging.info(
            f"Size of entries dataframe after preprocessing: {len(self.entries_df)}"
        )

        if self.entries_df.empty:
            self.embeddings = np.array([])
        else:
            self.embeddings = self._get_embeddings(self.entries_df.Document)

    def _download_prepare_entries(self, req_timeout: int = 30):
        """
        The json format (*.json) in the link file should be
        {
            data: [{
                "entry_id": int,
                "excerpt": str
            }],
            tags: [str]
        }
        """
        if self.entries_url:
            logging.info("The request url is %s", self.entries_url)
            try:
                response = requests.get(self.entries_url, timeout=req_timeout)
                response_data = response.json()
                if response.status_code == 200:
                    df = pd.DataFrame(response_data["data"])
                    self.topic_tags = response_data["tags"]
                    self.rename_columns(df)
                    return df
            except requests.exceptions.Timeout as texc:
                logging.error("Error occurred: %s", str(texc))
            except requests.exceptions.ConnectionError as cexc:
                logging.error("Request connection error: %s", str(cexc))
        return pd.DataFrame([], columns=["excerpts", "entry_id"])

    def _get_embeddings(
        self,
        excerpts: list,
        model_name: str = "main-model-cpu",
        pooling_type: str = "['cls']",
        finetuned_task: str = "['subpillars']",
        return_type: str = "default_analyis",
        embeddings_return_type: str = "array",
        batch_size: int = 100,
    ):
        """
        Calculates the embeddings of the entries
        """
        total = []

        client = boto3.client("sagemaker-runtime", region_name=self.aws_region)

        for i in range(0, len(excerpts), batch_size):
            batch = excerpts[i: i + batch_size]

            req = {
                "excerpt": batch,
                "output_backbone_embeddings": True,
                "return_prediction_labels": False,
                "interpretability": False,
                "pooling_type": pooling_type,
                "finetuned_task": finetuned_task,
                "return_type": return_type,
                "embeddings_return_type": embeddings_return_type,
            }

            try:
                response = client.invoke_endpoint(
                    EndpointName=model_name,
                    Body=pd.DataFrame(req).to_json(orient="split"),
                    ContentType="application/json; format=pandas-split",
                )
            except ClientError as cexc:
                logging.error(
                    "Error occurred while invoking sagemaker endpoint: %s", {str(cexc)}
                )
                return np.vstack([[]])

            output = literal_eval(response["Body"].read().decode("ascii"))
            total.append(output["output_backbone"])

        return np.vstack([x for b in total for x in b])

    def rename_columns(self, df: pd.DataFrame):
        """
        Renames the column names
        """
        df.rename(columns={"excerpt": "Document"}, inplace=True)

    def get_topic_list(self):
        """Get the grouped topic list"""
        self.group_tags_handler.set_excerpts(self.topic_tags)
        return self.group_tags_handler.generate_tag_groups()

    def generate_topics(
        self, entries, entries_embeddings, n_topics=10, umap_n_components=3
    ):
        """
        Generates the topic predicted by the Bertopic library
        """
        topic_model = TopicGenerator(excerpts=entries, embeddings=entries_embeddings)
        topic_list = self.get_topic_list()
        topic_model.get_total_topics(
            n_topics=n_topics,
            umap_n_components=umap_n_components,
            topic_list=topic_list,
        )
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
        outlier_df = dataframe[dataframe["Topic"] != topic_value]
        logging.info(f"Outliers dataframe shape: {outlier_df.shape}")
        return outlier_df

    def select_most_relevant_excerpts(self, df):
        """
        Select only the most relevant excerpts if it exceeds the cluster size
        """
        df_per_topic_nlargest = (
            df.groupby("Topic")
            .apply(pd.DataFrame.nlargest, n=self.cluster_size, columns="Probability")
            .reset_index(drop=True)
        )
        df_per_topic_nlargest["Representation"] = (
            df_per_topic_nlargest.Representation.apply(", ".join)
        )
        data_json = json.loads(
            df_per_topic_nlargest.groupby("Topic")[
                ["Document", "Representation", "entry_id"]
            ]
            .apply(lambda x: x.to_dict("list"))
            .to_json()
        )
        for v in data_json.values():
            v["Representation"] = " ".join(set(v["Representation"]))
        new_df = pd.DataFrame.from_dict(data_json, orient="index")
        new_df["label"] = new_df.apply(self.generate_llm_topic, axis=1)
        new_df.drop(columns=["Representation", "Document"], inplace=True)
        return new_df.to_dict(orient="index")

    def generate_llm_topic(self, x: pd.DataFrame, max_excerpts: int = 20):
        """
        Generate the short topic using LLM based on keywords
        The excerpts are restricted to first 20 (default)
        """
        topic_generation = TopicGenerationLLM(
            x["Document"][:max_excerpts], x["Representation"]
        )
        return topic_generation.topic_generator_handler()

    def dispatch_results(self, status, presigned_url=None):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": self.client_id,
            "presigned_s3_url": presigned_url,
            "status": status,
        }

        if self.callback_url:
            callback_response = send_request_on_callback(
                self.callback_url, response_data=response_data, headers=self.headers
            )
            if not callback_response:
                db_client = Database(**self.db_config)
                db_conn, db_cursor = db_client.db_connection()
                update_db_table_callback_retry(
                    db_conn,
                    db_cursor,
                    self.topicmodel_id,
                    self.db_table_callback_tracker,
                )
        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if presigned_url and self.db_table_name:  # update for presigned url
            sql_statement = prepare_sql_statement_success(
                self.topicmodel_id, self.db_table_name, status, response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                self.topicmodel_id, self.db_table_name, status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error(
                "Callback url / presigned s3 url / Database table name are not found."
            )

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
                    umap_n_components=self.umap_components,
                )
            except Exception as exc:
                logging.error(
                    "Error occurred during processing of topics. %s", str(exc)
                )

            if not df_topics.empty:
                df_merged = self.create_complete_df(self.entries_df, df_topics)
                df_merged = self.exclude_topic_clusters(df_merged)
                if df_merged.empty:
                    logging.warning("The clusters could not be formed.")
                    topics_dict = {}
                else:
                    topics_dict = self.select_most_relevant_excerpts(df_merged)
            else:
                topics_dict = {}

            date_today = date.today().isoformat()
            try:
                presigned_url = upload_to_s3(
                    contents=json.dumps(topics_dict),
                    contents_type="application/json",
                    bucket_name=self.bucket_name,
                    key=f"topicmodel/{date_today}/{self.topicmodel_id}/topicmodel.json",
                    aws_region=self.aws_region,
                    signed_url_expiry_secs=self.signed_url_expiry_secs,
                )
            except ClientError as exc:
                logging.error("Error occurred while uploading data to s3. %s", str(exc))
                presigned_url = None

            if presigned_url:
                self.dispatch_results(
                    status=StateHandler.SUCCESS.value, presigned_url=presigned_url
                )
            else:
                self.dispatch_results(status=StateHandler.FAILED.value)
        else:
            logging.error(
                "Excerpts embeddings are empty. The embedding model might not be available."
            )
            self.dispatch_results(status=StateHandler.FAILED.value)


topicmodel_generator_handler = TopicModelGeneratorHandler()
