import json
import logging
import os
from datetime import date

import requests
import sentry_sdk
from ngrams_generator import NGramsGenerator
from nlp_modules_utils import (Database, StateHandler,
                               prepare_sql_statement_failure,
                               prepare_sql_statement_success,
                               send_request_on_callback, status_update_db,
                               update_db_table_callback_retry, upload_to_s3)

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(
    SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0
)


class NGramsGeneratorHandler:
    """
    NGrams class to generate n-grams of the excerpts
    """

    def __init__(self):
        self.entries_url = os.environ.get("ENTRIES_URL", None)
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.callback_url = os.environ.get("CALLBACK_URL", None)
        self.ngrams_id = os.environ.get("NGRAMS_ID", None)
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get(
            "SIGNED_URL_EXPIRY_SECS", 86400
        )  # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)
        self.mock = os.environ.get("NGRAMS_MOCK", False)

        # N-Grams config
        self.generate_unigrams = os.environ.get("GENERATE_UNIGRAMS", "False")
        self.generate_bigrams = os.environ.get("GENERATE_BIGRAMS", "False")
        self.generate_trigrams = os.environ.get("GENERATE_TRIGRAMS", "False")
        self.enable_stopwords = os.environ.get("ENABLE_STOPWORDS", "False")
        self.enable_stemming = os.environ.get("ENABLE_STEMMING", "False")
        self.enable_case_sensitive = os.environ.get("ENABLE_CASE_SENSITIVE", "True")
        self.enable_end_of_sentence = os.environ.get("ENABLE_END_OF_SENTENCE", "True")
        self.max_ngrams_tokens = os.environ.get("MAX_NGRAMS_ITEMS", 10)

        self.generate_unigrams = True if self.generate_unigrams == "True" else False
        self.generate_bigrams = True if self.generate_bigrams == "True" else False
        self.generate_trigrams = True if self.generate_trigrams == "True" else False
        self.enable_stopwords = True if self.enable_stopwords == "True" else False
        self.enable_stemming = True if self.enable_stemming == "True" else False
        self.enable_case_sensitive = (
            True if self.enable_case_sensitive == "True" else False
        )
        self.enable_end_of_sentence = (
            True if self.enable_end_of_sentence == "True" else False
        )
        self.max_ngrams_tokens = int(self.max_ngrams_tokens)
        self.mock = True if self.mock == "True" else False

        # db table
        self.db_table_name = os.environ.get("DB_TABLE_NAME", None)
        self.db_table_callback_tracker = os.environ.get(
            "DB_TABLE_CALLBACK_TRACKER", None
        )

        self.entries = self._download_prepare_entries()

        self.headers = {"Content-Type": "application/json"}

        # db
        self.db_config = {
            "endpoint": os.environ.get("DB_HOST"),
            "database": os.environ.get("DB_NAME"),
            "username": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PWD"),
            "port": os.environ.get("DB_PORT"),
        }

        if not self.db_table_name:
            logging.error("Database table name is not found.")

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
                    return [x["excerpt"] for x in response.json()]
            except Exception as exc:
                logging.error("Error occurred: %s", str(exc))
        return None

    def ngrams_summary_store_local(self, ngrams_summary):
        """
        Store the result in tmp directory
        """
        filepath = f"/tmp/ngrams/{self.client_id}"
        with open(filepath, "w") as f:
            f.write(ngrams_summary)

        return filepath

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
                    db_conn, db_cursor, self.ngrams_id, self.db_table_callback_tracker
                )

        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if presigned_url and self.db_table_name:  # update for presigned url
            sql_statement = prepare_sql_statement_success(
                self.ngrams_id, self.db_table_name, status, response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                self.ngrams_id, self.db_table_name, status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error(
                "Callback url / presigned s3 url / Database table name are not found."
            )

    def __call__(self):
        if not self.entries:
            logging.error("The input data is not available.")
            self.dispatch_results(status=StateHandler.INPUT_URL_PROCESS_FAILED.value)
            return

        ngrams_gen = NGramsGenerator(
            max_ngrams_items=self.max_ngrams_tokens,
            generate_unigrams=self.generate_unigrams,
            generate_bigrams=self.generate_bigrams,
            generate_trigrams=self.generate_trigrams,
            enable_stopwords=self.enable_stopwords,
            enable_stemming=self.enable_stemming,
            enable_case_sensitive=self.enable_case_sensitive,
            enable_end_of_sentence=self.enable_end_of_sentence,
        )

        ng_output = ngrams_gen(self.entries)

        date_today = date.today().isoformat()
        if not self.mock:
            presigned_url = upload_to_s3(
                contents=json.dumps(ng_output),
                contents_type="application/json",
                bucket_name=self.bucket_name,
                key=f"ngrams/{date_today}/{self.ngrams_id}/ngrams.json",
                aws_region=self.aws_region,
                signed_url_expiry_secs=self.signed_url_expiry_secs,
            )
        else:
            presigned_url = self.ngrams_summary_store_local(
                ngrams_summary=json.dumps(ng_output)
            )
        if presigned_url:
            self.dispatch_results(
                status=StateHandler.SUCCESS.value, presigned_url=presigned_url
            )
        else:
            self.dispatch_results(status=StateHandler.FAILED.value)


if __name__ == "__main__":
    ngrams_generator_handler = NGramsGeneratorHandler()
    ngrams_generator_handler()
