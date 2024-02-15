import os
import logging
import requests
import boto3
import json
import sentry_sdk

from typing import List
from pathlib import Path
from datetime import date
from botocore.client import Config
from fastapi import FastAPI, BackgroundTasks

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

from models import InputStructure
from extraction import entry_extraction_model

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
GEOLOCATION_ECS_ENDPOINT = os.environ.get("GEOLOCATION_ECS_ENDPOINT", None)

sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

s3_client = boto3.client("s3", region_name=AWS_REGION)
s3_client_presigned_url = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)

ecs_app = FastAPI()

@ecs_app.get("/")
def home():
    """ Returns index page message """
    return "This is Entry Extraction ECS Task page."

@ecs_app.get("/healthcheck")
async def healthcheckup():
    """ Health checkup endpoint """
    return "The instance is ok and running."

@ecs_app.post("/extract_entries")
async def extract_texts(item: InputStructure, background_tasks: BackgroundTasks):
    """Generate reports"""
    client_id = item.client_id
    url = item.url
    text_extraction_id = item.text_extraction_id
    entry_extraction_id = item.entryextraction_id
    callback_url = item.callback_url

    background_tasks.add_task(
        entry_extraction_handler,
        client_id,
        entry_extraction_id,
        callback_url,
        url,
        text_extraction_id,
    )

    return {
        "message": "Task received and running in background."
    }


class EntryExtractionHandler:
    """ Entry extraction handler """
    def __init__(self):

        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400)
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)

        self.db_config = {
            "endpoint": os.environ.get("DB_HOST"),
            "database": os.environ.get("DB_NAME"),
            "username": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PWD"),
            "port": os.environ.get("DB_PORT")
        }

        self.headers = {
            "Content-Type": "application/json",
            "user-agent": ("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1")
        }

        self.db_table_name = os.environ.get("DB_TABLE_NAME", None)
        self.db_table_callback_tracker = os.environ.get("DB_TABLE_CALLBACK_TRACKER", None)

        if not self.db_table_name:
            logging.error("Database table name is not found.")

    def _handler(self):
        pass

    def get_geolocations(self, excerpts: List[str], req_timeout: int=60):
        """ Get geolocations from excerpts by requesting from geolocation module """
        if not GEOLOCATION_ECS_ENDPOINT:
            logging.error("The geolocation module endpoint not found.")
            return None
        data = {"entries_list": excerpts}
        try:
            response = requests.post(
                GEOLOCATION_ECS_ENDPOINT + "/get_geolocations",
                json=data,
                timeout=req_timeout
            )
            return response.json()
        except requests.exceptions.Timeout as terr:
            logging.error("Request timeout to the geolocation endpoint. %s", str(terr))
        except requests.exceptions.ConnectionError as cerr:
            logging.error("Request connection error occurred. %s", str(cerr))
        return None


    def __call__(self,
        client_id,
        entry_extraction_id,
        callback_url,
        url = None,
        text_extraction_id = None,
        filename = "extracted_text.json"
    ):
        structured_text = None
        try:
            if url:
                structured_text = json.loads(requests.get(url, timeout=30).content)

            elif text_extraction_id:
                response = s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=f"textextraction/structured/{text_extraction_id}/{filename}"
                    )
                structured_text = json.loads(response['Body'].read())
            else:
                logging.error("The url or text_extraction_id is missing. Extraction failed.")
                self.dispatch_results(
                    client_id=client_id,
                    entry_extraction_id=entry_extraction_id,
                    callback_url=callback_url,
                    status=StateHandler.FAILED.value
                )
        except Exception as exc:
            logging.error("Fail getting input data: %s", str(exc), exc_info=True)
            self.dispatch_results(
                client_id=client_id,
                entry_extraction_id=entry_extraction_id,
                callback_url=callback_url,
                status=StateHandler.FAILED.value
            )

        try:
            if structured_text:
                entry_extraction = entry_extraction_model.predict(document=structured_text)
                excerpts = [
                    block["text"] if block["relevant"] else ""
                    for block in entry_extraction["blocks"]
                ]
                geolocations = self.get_geolocations(excerpts)
                if geolocations:
                    for idx, block in enumerate(entry_extraction["blocks"]):
                        block.update({
                            "geolocations": geolocations[idx]["locations"]
                        })
                else:
                    logging.error("Geolocations cannot be retrieved due to API error.")
                    for idx, block in enumerate(entry_extraction["blocks"]):
                        block.update({
                            "geolocations": []
                        })
                # Add more meta info
                entry_extraction.update({
                    "client_id": client_id,
                    "entry_extraction_id": entry_extraction_id,
                    "text_extraction_id": text_extraction_id
                })
                entry_extraction_presigned_url = upload_to_s3(
                    contents=json.dumps(entry_extraction),
                    contents_type="application/json",
                    bucket_name=self.bucket_name,
                    key=f"entryextraction/{date.today().isoformat()}/{entry_extraction_id}/entry_extraction.json",
                    aws_region=AWS_REGION,
                    s3_client=s3_client_presigned_url,
                    signed_url_expiry_secs=self.signed_url_expiry_secs
                )

                self.dispatch_results(
                    client_id,
                    text_extraction_id=text_extraction_id,
                    entry_extraction_id=entry_extraction_id,
                    entry_extraction_presigned_url=entry_extraction_presigned_url,
                    callback_url=callback_url,
                    status=StateHandler.SUCCESS.value,
                )
            else:
                logging.error("The structured text was not retrieved from s3.")

        except Exception as exc:
            logging.error("Entry extraction failed: %s", str(exc), exc_info=True)
            self.dispatch_results(
                client_id=client_id,
                entry_extraction_id=entry_extraction_id,
                callback_url=callback_url,
                status=StateHandler.FAILED.value
            )
            return


    def dispatch_results(
        self,
        client_id,
        entry_extraction_id,
        callback_url,
        status,
        text_extraction_id=None, # text_extraction_id can also be not present
        entry_extraction_presigned_url=None
    ):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": client_id,
            "entry_extraction_id": entry_extraction_id,
            "text_extraction_id": text_extraction_id, 
            "entry_extraction_classification_path": entry_extraction_presigned_url,
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
                    entry_extraction_id,
                    self.db_table_callback_tracker
                )
        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if entry_extraction_presigned_url and self.db_table_name: # update for presigned url
            sql_statement = prepare_sql_statement_success(
                entry_extraction_id,
                self.db_table_name,
                status,
                response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                entry_extraction_id,
                self.db_table_name,
                status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")

entry_extraction_handler = EntryExtractionHandler()
