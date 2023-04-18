import os
import io
import json
import logging
import psycopg2
import requests
import boto3
import sentry_sdk
from datetime import datetime
from enum import Enum
from botocore.client import Config
from botocore.exceptions import ClientError
from ngrams_generator import NGramsGenerator

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

class NGramsStatus(Enum):
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
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
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
        self.enable_case_sensitive = True if self.enable_case_sensitive == "True" else False
        self.enable_end_of_sentence = True if self.enable_end_of_sentence == "True" else False
        self.max_ngrams_tokens = int(self.max_ngrams_tokens)
        self.mock = True if self.mock == "True" else False

        # db table
        self.db_table_name = os.environ.get("DB_TABLE_NAME", None)

        self.entries = self._download_prepare_entries()

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
                    entries_data = json.loads(response.text)
                    return [x["excerpt"] for x in entries_data]
            except Exception as exc:
                logging.error("Error occurred: %s", str(exc))
        return None

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

    def ngrams_summary_store_s3(
        self,
        ngrams_summary,
        bucket_name="test-ecs-parser11",
        key="ngrams.json"
    ):
        """
        Stores the summary in s3
        """
        try:
            session = boto3.Session()
            s3_resource = session.resource("s3")
            bucket = s3_resource.Bucket(bucket_name)
            ngrams_bytes = bytes(ngrams_summary, "utf-8")
            ngrams_bytes_obj = io.BytesIO(ngrams_bytes)
            bucket.upload_fileobj(
                ngrams_bytes_obj,
                key,
                ExtraArgs={"ContentType": "application/json"}
            )
            return self.generate_presigned_url(bucket_name, key)
        except ClientError as cexc:
            logging.error(str(cexc))
            return None

    def ngrams_summary_store_local(self, ngrams_summary):
        filepath = f"/tmp/ngrams/{self.client_id}"
        with open(filepath, "w") as f:
            f.write(ngrams_summary)

        return filepath


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
            logging.error("Exception occurred while sending request %s", str(rexc))
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
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}', result_s3_link='{presigned_url}' WHERE unique_id='{self.ngrams_id}' """
            )
        elif self.db_table_name:
            # Presigned url generation failed
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}' WHERE unique_id='{self.ngrams_id}' """
            )
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")

    def __call__(self):
        if not self.entries:
            self.dispatch_results(status=NGramsStatus.INPUT_URL_PROCESS_FAILED.value)
            return

        ngrams_gen = NGramsGenerator(
            max_ngrams_items=self.max_ngrams_tokens,
            generate_unigrams=self.generate_unigrams,
            generate_bigrams=self.generate_bigrams,
            generate_trigrams=self.generate_trigrams,
            enable_stopwords=self.enable_stopwords,
            enable_stemming=self.enable_stemming,
            enable_case_sensitive=self.enable_case_sensitive,
            enable_end_of_sentence=self.enable_end_of_sentence
        )

        ng_output = ngrams_gen(self.entries)

        date_today = str(datetime.now().date())
        if not self.mock:
            presigned_url = self.ngrams_summary_store_s3(
                ngrams_summary=json.dumps(ng_output),
                bucket_name=self.bucket_name,
                key=f"ngrams/{date_today}/{self.ngrams_id}/ngrams.json"
            )
        else:
            presigned_url = self.ngrams_summary_store_local(
                ngrams_summary=json.dumps(ng_output)
            )
        if presigned_url:
            self.dispatch_results(status=NGramsStatus.SUCCESS.value, presigned_url=presigned_url)
        else:
            self.dispatch_results(status=NGramsStatus.FAILED.value)

if __name__ == "__main__":
    ngrams_generator_handler = NGramsGeneratorHandler()
    ngrams_generator_handler()
