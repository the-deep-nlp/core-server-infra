import os
import json
import logging
import requests
import boto3
import sentry_sdk
from pathlib import Path
from datetime import date
from botocore.client import Config
from huggingface_hub import snapshot_download
from reports_generator import ReportsGenerator

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Union
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

    def dispatch_results(self, client_id, summarization_id, callback_url, status, presigned_url=None):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": client_id,
            "presigned_s3_url": presigned_url,
            "status": status
        }
        if callback_url:
            callback_response = send_request_on_callback(
                callback_url,
                response_data=response_data,
                headers=self.headers
            )
            if not callback_response:
                db_client = Database(**self.db_config)
                db_conn, db_cursor = db_client.db_connection()
                update_db_table_callback_retry(
                    db_conn,
                    db_cursor,
                    summarization_id,
                    self.db_table_callback_tracker
                )
        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if presigned_url and self.db_table_name: # update for presigned url
            sql_statement = prepare_sql_statement_success(
                summarization_id,
                self.db_table_name,
                status,
                response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                summarization_id,
                self.db_table_name,
                status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
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
            self.dispatch_results(client_id, summarization_id, callback_url, status=StateHandler.INPUT_URL_PROCESS_FAILED.value)
            return

        if self.repgenerator:
            summary = self.repgenerator(entries)
            date_today = date.today().isoformat()
            presigned_url = upload_to_s3(
                contents=summary,
                contents_type="text/plain; charset=utf-8",
                bucket_name=self.bucket_name,
                key=f"summarization/{date_today}/{summarization_id}/summary.txt",
                aws_region=os.environ.get("AWS_REGION", "us-east-1"),
                s3_client=s3_client,
                signed_url_expiry_secs=self.signed_url_expiry_secs
            )

            if presigned_url:
                self.dispatch_results(client_id, summarization_id, callback_url, status=StateHandler.SUCCESS.value, presigned_url=presigned_url)
            else:
                self.dispatch_results(client_id, summarization_id, callback_url, status=StateHandler.FAILED.value)
        else:
            self.dispatch_results(client_id, summarization_id, callback_url, status=StateHandler.FAILED.value)
            logging.warning("Summarization models could not be loaded.")


reports_generator_handler = ReportsGeneratorHandler()
model_info_dict = reports_generator_handler.download_models()
reports_generator_handler.load_model(model_info_dict)
