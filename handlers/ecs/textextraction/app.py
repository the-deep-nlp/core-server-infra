import os
import io
import json
import uuid
import base64
import logging
import psycopg2
import requests
import boto3
import sentry_sdk
from enum import Enum
from pathlib import Path
from datetime import date, datetime
from botocore.exceptions import ClientError

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from deep_parser import TextFromFile, TextFromWeb
from content_types import ExtractContentType, UrlTypes

from s3handler import Storage
from utils import (
    create_tempfile,
    get_words_count,
    preprocess_extracted_texts,
    download_file,
    generate_presigned_url,
    invoke_conversion_lambda
)

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

class InputStructure(BaseModel):
    """Input Structure """
    client_id: str
    url: str
    textextraction_id: str
    callback_url: Optional[str] = None

ecs_app = FastAPI()

@ecs_app.get("/")
def home():
    """Home page message for test"""
    return "This is Text Extraction ECS Task"

@ecs_app.post("/extract_document")
def extract_texts(item: InputStructure):
    """Generate reports"""
    client_id = item.client_id
    url = item.url
    textextraction_id = item.textextraction_id
    callback_url = item.callback_url

    text_extraction_handler(client_id, url, textextraction_id, callback_url)

    return {
        "output": "Processed successfully"
    }


class TextExtractionStatus(Enum):
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


class TextExtractionHandler:
    """
    Text extraction from the documents(e.g. pdf, docx, xlsx, pptx) or websites
    """
    def __init__(self):
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)
        self.docs_conversion_bucket_name = os.environ.get("DOCS_CONVERSION_BUCKET_NAME", None)
        self.docs_convert_lambda_fn_name = os.environ.get("DOCS_CONVERT_LAMBDA_FN_NAME", None)

        self.extract_content_type = ExtractContentType()

        self.headers = {
            "Content-Type": "application/json",
            "user-agent": ("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1")
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

    def _common_doc_handler(
        self,
        entries,
        client_id,
        textextraction_id,
        callback_url,
        total_pages=1
    ):
        """
        Common doc handler for pdf and webpages
        """
        entries_list = [item for sublist in entries for item in sublist]
        extracted_text = "\n".join(entries_list)
        extracted_text = preprocess_extracted_texts(extracted_text)
        total_words_count = get_words_count(extracted_text)
        date_today = date.today().isoformat()

        text_presigned_url = self.upload_text_in_s3(
            extracted_text=extracted_text,
            bucket_name=self.bucket_name,
            key=f"textextraction/{date_today}/{textextraction_id}/summary.txt"
        )

        if text_presigned_url:
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=TextExtractionStatus.SUCCESS.value,
                text_presigned_url=text_presigned_url,
                total_pages=total_pages,
                total_words_count=total_words_count
            )
        else:
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=TextExtractionStatus.FAILED.value
            )


    def handle_pdf_text(self, file_path, file_name, client_id, textextraction_id, callback_url):
        """ Extract texts from pdf documents """
        try:
            with open(Path(file_path), "rb") as f:
                binary = base64.b64encode(f.read())

            document = TextFromFile(stream=binary, ext="pdf")
            entries, _ = document.extract_text(output_format="list")
        except Exception as exc:
            logging.error("Extraction failed: %s", str(exc), exc_info=True)
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=TextExtractionStatus.FAILED.value
            )
            return
        
        total_pages = len(entries)

        self._common_doc_handler(entries, client_id, textextraction_id, callback_url, total_pages=total_pages)

    def handle_html_text(self, url, file_name, client_id, textextraction_id, callback_url):
        """ Extract html texts """
        try:
            web_text = TextFromWeb(url=url)
            entries = web_text.extract_text(output_format="list", url=url)
        except Exception as exc:
            logging.error("Extraction from website failed. %s", str(exc), exc_info=True)
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=TextExtractionStatus.FAILED.value
            )
            return

        self._common_doc_handler(entries, client_id, textextraction_id, callback_url)

    def __call__(self, client_id, url, textextraction_id, callback_url, file_name="extract_text.txt"):
        content_type = self.extract_content_type.get_content_type(url, self.headers)

        if content_type == UrlTypes.PDF.value:  # assume it is http/https pdf weblink
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            tempf = create_tempfile(response)

            self.handle_pdf_text(
                tempf.name, file_name, client_id, textextraction_id, callback_url
            )
        elif content_type == UrlTypes.HTML.value:  # assume it is a static webpage
            self.handle_html_text(
                url, file_name, client_id, textextraction_id, callback_url
            )
        elif content_type in [
            UrlTypes.DOCX.value,
            UrlTypes.MSWORD.value,
            UrlTypes.XLSX.value,
            UrlTypes.XLS.value,
            UrlTypes.PPTX.value,
            UrlTypes.PPT.value
        ]:
            ext_type = content_type
            tmp_filename = f"{uuid.uuid4().hex}.{ext_type}"
            flag = False
            response = requests.get(url, headers=self.headers, stream=True, timeout=60)

            s3_uploader = Storage(self.docs_conversion_bucket_name, "")
            tempf = create_tempfile(response)
            with open(tempf.name, "rb") as tmpf:
                s3_uploader.upload(tmp_filename, tmpf)
                # Converts docx, xlsx, doc, xls, ppt, pptx type files to pdf using lambda
                docs_conversion_lambda_response_json = invoke_conversion_lambda(
                    self.aws_region,
                    self.docs_conversion_bucket_name,
                    self.docs_convert_lambda_fn_name,
                    tmp_filename,
                    ext_type
                )

                if ("statusCode" in docs_conversion_lambda_response_json and
                        docs_conversion_lambda_response_json["statusCode"] == 200):
                    bucket_name = docs_conversion_lambda_response_json["bucket"]
                    file_path = docs_conversion_lambda_response_json["file"]
                    filename = file_path.split("/")[-1]

                    if download_file(self.aws_region, file_path, bucket_name, f"/tmp/{filename}"):
                        self.handle_pdf_text(
                            f"/tmp/{filename}", file_name, client_id, textextraction_id, callback_url
                        )
                    else:
                        flag = True
                else:
                    logging.error("Error occurred during file conversion. %s", docs_conversion_lambda_response_json['error'])
                    flag = True
            if flag:
                self.dispatch_results(
                    client_id,
                    textextraction_id,
                    callback_url,
                    status=TextExtractionStatus.FAILED.value
                )
                # s3_file_path, s3_images_path, total_pages, total_words_count = None, None, -1, -1
                # extraction_status = TextExtractionStatus.FAILED.value
        elif content_type == UrlTypes.IMG.value:
            logging.warning("Text extraction from Images is not available.")
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=TextExtractionStatus.FAILED.value
            )
        else:
            logging.error("Text extraction is not available for this content type - %s", content_type)
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=TextExtractionStatus.FAILED.value
            )

    def upload_text_in_s3(self, extracted_text, bucket_name="test-ecs-parser11", key="extracted_text.txt"):
        """
        Stores the extracted text in s3
        """
        try:
            session = boto3.Session()
            s3_resource = session.resource("s3")
            bucket = s3_resource.Bucket(bucket_name)
            extracted_text_bytes = bytes(extracted_text, "utf-8")
            extracted_text_bytes_obj = io.BytesIO(extracted_text_bytes)
            bucket.upload_fileobj(
                extracted_text_bytes_obj,
                key,
                ExtraArgs={"ContentType": "text/plain; charset=utf-8"}
            )
            return generate_presigned_url(
                self.aws_region,
                bucket_name,
                key,
                self.signed_url_expiry_secs
            )
        except ClientError as cexp:
            logging.error(str(cexp))
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
    
    def _update_db_table_callback_retry(self, id):
        """
        Updates the table whenever the callback fails
        """
        if self.db_table_callback_tracker and id:
            now_date = datetime.now().isoformat()
            self.status_update_db(
                sql_statement=f""" INSERT INTO {self.db_table_callback_tracker} 
                                (request_unique_id, created_at, modified_at, retries_count, status) 
                                VALUES ('{id}', '{now_date}', '{now_date}', 0, 3) """  # status = 3(Retrying)
            )
            logging.info("Updated the db table for callback retries.")

    def send_request_on_callback(
        self,
        client_id,
        callback_url,
        textextraction_id,
        status,
        text_presigned_url,
        total_pages,
        total_words_count
    ):
        """
        Sends the results in a callback url
        """
        try:
            response = requests.post(
                callback_url,
                headers=self.headers,
                data=json.dumps({
                    "client_id": client_id,
                    "text_presigned_url": text_presigned_url,
                    "images_presigned_url": None,
                    "total_pages": total_pages,
                    "total_words_count": total_words_count,
                    "extraction_status": status
                }),
                timeout=30
            )
        except requests.exceptions.RequestException as rexc:
            logging.error("Exception occurred while sending request %s", str(rexc))
            self._update_db_table_callback_retry(textextraction_id)
        if response.status_code == 200:
            logging.info("Successfully sent the request on callback url")
        else:
            logging.error("Error while sending the request on callback url")
            self._update_db_table_callback_retry(textextraction_id)

    def dispatch_results(
        self,
        client_id,
        textextraction_id,
        callback_url,
        status,
        text_presigned_url=None,
        total_pages=None,
        total_words_count=None
    ):
        """
        Dispatch results to callback url or write to database
        """
        if callback_url:
            self.send_request_on_callback(
                client_id,
                callback_url,
                textextraction_id,
                status=status,
                text_presigned_url=text_presigned_url,
                total_pages=total_pages,
                total_words_count=total_words_count
            )
        if text_presigned_url and self.db_table_name: # update for presigned url
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}', result_s3_link='{text_presigned_url}' WHERE unique_id='{textextraction_id}' """
            )
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}' WHERE unique_id='{textextraction_id}' """
            )
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")

text_extraction_handler = TextExtractionHandler()
