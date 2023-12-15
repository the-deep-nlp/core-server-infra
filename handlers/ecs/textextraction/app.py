import os
import uuid
import json
import base64
import logging
import requests
import boto3
import sentry_sdk
from pathlib import Path
from datetime import date
from botocore.client import Config

from fastapi import FastAPI, BackgroundTasks
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
    invoke_conversion_lambda
)
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
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

# Note: boto3 initialization outside class to make it thread safe.
s3_client = boto3.client("s3", region_name=AWS_REGION)
s3_client_presigned_url = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)

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
async def extract_texts(item: InputStructure, background_tasks: BackgroundTasks):
    """Generate reports"""
    client_id = item.client_id
    url = item.url
    textextraction_id = item.textextraction_id
    callback_url = item.callback_url

    background_tasks.add_task(
        text_extraction_handler,
        client_id,
        url,
        textextraction_id,
        callback_url
    )

    return {
        "message": "Task received and running in background."
    }

class TextExtractionHandler:
    """
    Text extraction from the documents(e.g. pdf, docx, xlsx, pptx) or websites
    """
    def __init__(self):
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
        total_pages = len(entries)
        date_today = date.today().isoformat()

        text_presigned_url = upload_to_s3(
            contents=extracted_text,
            contents_type="text/plain; charset=utf-8",
            bucket_name=self.bucket_name,
            key=f"textextraction/{date_today}/{textextraction_id}/extracted_text.txt",
            aws_region=AWS_REGION,
            s3_client=s3_client_presigned_url,
            signed_url_expiry_secs=self.signed_url_expiry_secs
        )

        # the idea is to push another format of the same text in a structured format. 
        # the problem is that the text/plain version can't be reversed in its original 
        # structured format. Another thing: the {date_today} create a problem in retrieving 
        # the document with only the textextraction_id, so it's tricky to known where it's located without the date,
        # so i prefer to save every structured text in the same directory, considering that textextraction_id
        # is a uuid.
        structured_text_presigned_url = upload_to_s3(
            contents=json.dumps(entries),
            contents_type="application/json",
            bucket_name=self.bucket_name,
            key=f"textextraction/structured/{textextraction_id}/extracted_text.json",
            aws_region=AWS_REGION,
            s3_client=s3_client_presigned_url,
            signed_url_expiry_secs=self.signed_url_expiry_secs
        )

        # during text extraction, also the structured version is stored on s3
        # and sent to the database with a "structured_text_presigned_url"
        if text_presigned_url:
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=StateHandler.SUCCESS.value,
                text_presigned_url=text_presigned_url,
                structured_text_presigned_url=structured_text_presigned_url,
                total_pages=total_pages,
                total_words_count=total_words_count
            )
        else:
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=StateHandler.FAILED.value
            )

    def handle_pdf_text_from_url(self, url, client_id, textextraction_id, callback_url):
        """ Extract texts from url link which is a pdf document """
        try:
            document = TextFromFile(stream=None, ext="pdf", from_web=True, url=url)
            entries, _ = document.extract_text(output_format="list")
        except Exception as exc:
            logging.error("Extraction failed: %s", str(exc), exc_info=True)
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=StateHandler.FAILED.value
            )
            return

        total_pages = len(entries)
        self._common_doc_handler(entries, client_id, textextraction_id, callback_url, total_pages=total_pages)


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
                status=StateHandler.FAILED.value
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
                status=StateHandler.FAILED.value
            )
            return

        self._common_doc_handler(entries, client_id, textextraction_id, callback_url)

    def __call__(self, client_id, url, textextraction_id, callback_url, file_name="extract_text.txt"):
        content_type = self.extract_content_type.get_content_type(url, self.headers)

        if content_type == UrlTypes.PDF.value:  # assume it is http/https pdf weblink
            self.handle_pdf_text_from_url(url, client_id, textextraction_id, callback_url)
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
                    lambda_client,
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

                    if download_file(s3_client, file_path, bucket_name, f"/tmp/{filename}"):
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
                    status=StateHandler.FAILED.value
                )
                # s3_file_path, s3_images_path, total_pages, total_words_count = None, None, -1, -1
                # extraction_status = StateHandler.FAILED.value
        elif content_type == UrlTypes.IMG.value:
            logging.warning("Text extraction from Images is not available.")
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=StateHandler.FAILED.value
            )
        else:
            logging.error("Text extraction is not available for this content type - %s", content_type)
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=StateHandler.FAILED.value
            )

    def dispatch_results(
        self,
        client_id,
        textextraction_id,
        callback_url,
        status,
        text_presigned_url=None,
        structured_text_presigned_url=None,
        total_pages=None,
        total_words_count=None
    ):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": client_id,
            "text_path": text_presigned_url,
            "structured_text_path": structured_text_presigned_url,
            "images_path": [],
            "total_pages": total_pages,
            "total_words_count": total_words_count,
            "status": status,
            "text_extraction_id": textextraction_id
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
                    textextraction_id,
                    self.db_table_callback_tracker
                )
        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if text_presigned_url and self.db_table_name: # update for presigned url
            sql_statement = prepare_sql_statement_success(
                textextraction_id,
                self.db_table_name,
                status,
                response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                textextraction_id,
                self.db_table_name,
                status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")

text_extraction_handler = TextExtractionHandler()
