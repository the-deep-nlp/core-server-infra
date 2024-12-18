import json
import logging
import os
from datetime import date
from typing import Optional

import boto3
import requests
from botocore.client import Config
from nlp_modules_utils import (Database, StateHandler, add_metric_data,
                               prepare_sql_statement_failure,
                               prepare_sql_statement_success,
                               send_request_on_callback, status_update_db,
                               update_db_table_callback_retry, upload_to_s3)
from summarizer_llm import LLMSummarization

logging.getLogger().setLevel(logging.INFO)

# Note: boto3 initialization outside class to make it thread safe.
# s3_client for generating presigned Url.
s3_client = boto3.client(
    "s3",
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

cloudwatch_client = boto3.client(
    "cloudwatch", region_name=os.environ.get("AWS_REGION", "us-east-1")
)


class ReportsGeneratorHandler:
    """
    Summarization class to generate summary of the excerpts
    """

    def __init__(self):
        self.signed_url_expiry_secs = os.environ.get(
            "SIGNED_URL_EXPIRY_SECS", 86400
        )  # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)
        self.environment = os.environ.get("ENVIRONMENT", "staging")

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

        if not self.db_table_name:
            logging.error("Database table name is not found.")

    def download_prepare_entries(self, entries_url: str, req_timeout: int = 30):
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
                response = requests.get(entries_url, timeout=req_timeout)
                response_data = response.json()
                if response.status_code == 200:
                    return (
                        [x["excerpt"] for x in response_data["data"]],
                        response_data["tags"],
                    )
            except Exception as exc:
                logging.error("Error occurred: %s", str(exc))
        return [], []

    def dispatch_results(
        self,
        client_id: str,
        summarization_id: str,
        callback_url: str,
        status: int,
        presigned_url: Optional[str] = None,
    ):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": client_id,
            "presigned_s3_url": presigned_url,
            "status": status,
        }
        if callback_url:
            callback_response = send_request_on_callback(
                callback_url, response_data=response_data, headers=self.headers
            )
            if not callback_response:
                db_client = Database(**self.db_config)
                db_conn, db_cursor = db_client.db_connection()
                update_db_table_callback_retry(
                    db_conn, db_cursor, summarization_id, self.db_table_callback_tracker
                )
        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if presigned_url and self.db_table_name:  # update for presigned url
            sql_statement = prepare_sql_statement_success(
                summarization_id, self.db_table_name, status, response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                summarization_id, self.db_table_name, status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error(
                "Callback url / presigned s3 url / Database table name are not found."
            )

    def __call__(
        self,
        client_id: str,
        entries: list,
        tags: list,
        summarization_id: str,
        callback_url: str,
        max_entries_items: int = 100,
    ):
        if not entries:
            self.dispatch_results(
                client_id,
                summarization_id,
                callback_url,
                status=StateHandler.INPUT_URL_PROCESS_FAILED.value,
            )
            return

        merged_entries = " ".join(entries[:max_entries_items])
        llm_summarizer = LLMSummarization(texts=merged_entries)
        if llm_summarizer:
            summary, summary_meta = llm_summarizer.summarizer(tags=tags)
            analytical_statement, analytical_statement_meta = (
                llm_summarizer.generate_analytical_statement(summary=summary)
            )
            info_gaps, info_gaps_meta = llm_summarizer.generate_information_gaps(
                entries=entries[:max_entries_items], topics=tags
            )
            # Adding the metric values
            for meta_information in [
                summary_meta,
                analytical_statement_meta,
                info_gaps_meta,
            ]:
                if meta_information:
                    for metric_name, metric_value in meta_information.items():
                        add_metric_data(
                            cw_client=cloudwatch_client,
                            metric_name=metric_name,
                            metric_value=metric_value,
                            dimension_name="Module",
                            dimension_value="Summarization",
                            environment=self.environment,
                        )

            date_today = date.today().isoformat()
            data = {
                "summary": summary,
                "analytical_statement": analytical_statement,
                "info_gaps": info_gaps,
            }

            try:
                presigned_url = upload_to_s3(
                    contents=json.dumps(data),
                    contents_type="application/json",
                    bucket_name=self.bucket_name,
                    key=f"summarization/{date_today}/{summarization_id}/summary.json",
                    aws_region=os.environ.get("AWS_REGION", "us-east-1"),
                    s3_client=s3_client,
                    signed_url_expiry_secs=self.signed_url_expiry_secs,
                )
            except Exception as exc:
                logging.error(
                    "Cannot upload the file to s3. Presigned url generation failed. %s",
                    str(exc),
                )
                presigned_url = None

            if presigned_url:
                self.dispatch_results(
                    client_id,
                    summarization_id,
                    callback_url,
                    status=StateHandler.SUCCESS.value,
                    presigned_url=presigned_url,
                )
            else:
                self.dispatch_results(
                    client_id,
                    summarization_id,
                    callback_url,
                    status=StateHandler.FAILED.value,
                )
        else:
            self.dispatch_results(
                client_id,
                summarization_id,
                callback_url,
                status=StateHandler.FAILED.value,
            )
            logging.warning("Summarization LLM could not be loaded.")
