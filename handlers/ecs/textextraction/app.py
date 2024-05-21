import os
import uuid
import json
import logging
import copy
import operator
from enum import Enum
from datetime import date
from typing import Optional
import asyncio
import boto3

import sentry_sdk

from botocore.client import Config

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from deep_parser import TextFromFile, TextFromWeb
from deep_parser.helpers.errors import ScannedDocumentError

from nlp_modules_utils import (
    Database,
    StateHandler,
    prepare_sql_statement_success,
    prepare_sql_statement_failure,
    status_update_db,
    upload_to_s3,
    send_request_on_callback,
    update_db_table_callback_retry,
    generate_presigned_url
)

from ocr_extractor import OCRProcessor

from utils import (
    create_async_tempfile,
    get_words_count,
    preprocess_extracted_texts,
    invoke_conversion_lambda,
    beautify_extracted_text,
    beautify_ocr_text,
    download_models,
    filter_file_by_size,
    handle_scanned_doc_or_image,
    uploadfile_s3
)

from content_types import ExtractContentType, UrlTypes
from s3handler import Storage

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

# Note: boto3 initialization outside class to make it thread safe.

s3_client_presigned_url = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)

class RequestType(Enum):
    """ Request Types """
    SYSTEM = 0
    USER = 1

class RequestSchema(BaseModel):
    """ Request Schema """
    client_id: str
    url: str
    textextraction_id: str
    callback_url: Optional[str] = None
    request_type: int

ecs_app = FastAPI()
ecs_app.fifo_queue = asyncio.Queue(maxsize=-1)

async def fifo_worker():
    """ Handles the queue for non-priority requests """
    logging.info("Starting the FIFO Worker")
    while True:
        logging.info("The size of the queue is %s", ecs_app.fifo_queue.qsize())
        handler, client_id, url, textextraction_id, callback_url = await ecs_app.fifo_queue.get()
        await handler(client_id, url, textextraction_id, callback_url)

@ecs_app.on_event("startup")
async def start_db():
    """ Creates task during startup """
    asyncio.create_task(fifo_worker())

@ecs_app.get("/")
def home():
    """ Home page message for test """
    return "This is Text Extraction ECS Task"

@ecs_app.get("/healthcheck")
async def healthcheckup():
    """ Health check up endpoint """
    return "The task is ok and running."

@ecs_app.post("/extract_document")
async def extract_texts(item: RequestSchema, background_tasks: BackgroundTasks):
    """Generate reports"""
    client_id = item.client_id
    url = item.url
    textextraction_id = item.textextraction_id
    callback_url = item.callback_url
    request_type = item.request_type

    if request_type == RequestType.SYSTEM.value:
        logging.info("Queueing a non-priority request job.")

        await ecs_app.fifo_queue.put((text_extraction_handler, client_id, url, textextraction_id, callback_url))
    else:
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

class OCRContentTypes(str, Enum):
    """ Types of contents for scanned docs """
    TEXT = "text"
    IMAGE = "image"

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
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1"
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

    def _add_page_info(self, entries_lst):
        entries_with_page_info = copy.deepcopy(entries_lst)
        try:
            for idx, item in enumerate(entries_with_page_info):
                item.insert(0, f"********* [PAGE {idx + 1} START] *********")
                item.append(f"********* [PAGE {idx + 1} END] *********")
            return entries_with_page_info
        except Exception as exc:
            logging.error(f"Error occurred {exc}. Returning the source entries list", exc_info=True)
            return entries_lst

    def _common_doc_handler(
        self,
        entries,
        client_id,
        textextraction_id,
        callback_url,
        webpage_extraction=False
    ):
        """
        Common doc handler for pdf and webpages
        """
        entries_with_page_info = self._add_page_info(entries)
        entries_list = [item for sublist in entries_with_page_info for item in sublist]

        extracted_text = "\n\n".join(entries_list)
        extracted_text = preprocess_extracted_texts(extracted_text)
        total_words_count = get_words_count(extracted_text)

        total_pages = 1 if webpage_extraction else len(entries)
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
    
    def _common_doc_handler_2(
        self,
        text_contents,
        structured_text,
        table_contents,
        images_lst,
        client_id,
        textextraction_id,
        callback_url,
        webpage_extraction=False
    ):
        """
        Common doc handler for pdf and webpages
        """
        extracted_text = preprocess_extracted_texts(text_contents)
        total_words_count = get_words_count(extracted_text)

        total_pages = 1 if webpage_extraction else len(structured_text)
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
            contents=json.dumps(structured_text),
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
                total_words_count=total_words_count,
                table_contents=table_contents if table_contents else None,
                images_contents=images_lst
            )
        else:
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=StateHandler.FAILED.value
            )

    async def handle_table_elements(self, url, textextraction_id):
        """ Handle Table elements from the document """
        date_today = date.today().isoformat()

        tempf = await create_async_tempfile(url=url, headers=self.headers, timeout=30)
        model_filepath = download_models()
        try:
            ocr_table_engine = OCRProcessor(
                extraction_type=2,
                show_log=False,
                use_s3=True,
                s3_bucket_name=self.bucket_name,
                s3_bucket_key=f"textextraction/{date_today}/{textextraction_id}/tables",
                **model_filepath
            )
            ocr_table_engine.load_file(file_path=tempf.name, is_image=False)
            ocr_results = await ocr_table_engine.handler()
            table_contents = ocr_results["table"]
            return table_contents
        except Exception as exc:
            logging.warning("Exception occurred while extracting tables %s", exc)
            return None


    async def handle_block_elements(self, blocks, images_dir, textextraction_id):
        """ Handles block elements """
        page_num = 0
        final_text_contents = ""
        temp_texts = ""
        flag = False
        structured_text = []
        structured_text_temp = []
        images_lst = []

        model_filepath = download_models()
        ocr_processor = OCRProcessor(
            extraction_type=1,
            show_log=False,
            use_s3=False,
            **model_filepath
        )
        # Sort blocks by 'page', y0 and then x0
        block_items = sorted(blocks, key=operator.itemgetter("page", "y0", "x0"))
        for block in block_items:
            if block["page"] == page_num:
                flag = True
                if block["type"] == OCRContentTypes.TEXT:
                    temp_texts += "\n\n\n" + block["text"] + "\n\n\n"
                    structured_text_temp.append(block["text"])
                if block["type"] == OCRContentTypes.IMAGE:
                    imgfile_path = f"{images_dir}/{block['imageLink']}"
                    if os.path.isfile(imgfile_path) and filter_file_by_size(imgfile_path):
                        presigned_url = await uploadfile_s3(
                            imgfile_path,
                            self.bucket_name,
                            textextraction_id,
                            s3_client_presigned_url
                        )
                        if presigned_url:
                            images_lst.append(presigned_url)
                        ocr_processor.load_file(file_path=imgfile_path, is_image=True)
                        ocr_results = await ocr_processor.handler()
                        text_contents = ocr_results["text"]
                        ocr_texts = ""
                        for item in text_contents:
                            ocr_texts += item["content"] + "\n\n"
                        if ocr_texts:
                            temp_texts += beautify_ocr_text(ocr_texts)
                            structured_text_temp.append(ocr_texts)
            else:
                flag = False
                final_text_contents += beautify_extracted_text(temp_texts, page_num+1)
                structured_text.append(structured_text_temp)
                structured_text_temp = []
                temp_texts = ""
                if block["type"] == OCRContentTypes.TEXT:
                    temp_texts += "\n\n\n" + block["text"] + "\n\n\n"
                    structured_text_temp.append(block["text"])
                page_num += 1
        if flag:
            final_text_contents += beautify_extracted_text(temp_texts, page_num+1)
            structured_text.append(structured_text_temp)
        return final_text_contents, structured_text, images_lst


    async def handle_pdf_text_from_url(self, url, client_id, textextraction_id, callback_url):
        """ Extract texts from url link which is a pdf document """
        try:
            document = TextFromFile(stream=None, ext="pdf", from_web=True, url=url)
            deepex_op = document.extract()
            temp_img_dir = os.path.join("/tmp", uuid.uuid4().hex)
            os.makedirs(temp_img_dir, exist_ok=True)
            deepex_op.save_pics(temp_img_dir)
            deepex_op = deepex_op.to_json()
            block_items = deepex_op["blocks"]
            text_contents, structured_text, images_lst = await self.handle_block_elements(block_items, temp_img_dir, textextraction_id)
            table_contents = await self.handle_table_elements(url, textextraction_id)
        except ScannedDocumentError:
            logging.warning("Scanned document found. Applying OCR on this document")
            text_contents, structured_text, table_contents = await handle_scanned_doc_or_image(
                url=url,
                is_image=False,
                s3_bucket_name=self.bucket_name,
                textextraction_id=textextraction_id,
                headers=self.headers
            )
            images_lst = []  # TODO
        except Exception as exc:
            logging.error("Extraction failed: %s", str(exc), exc_info=True)
            self.dispatch_results(
                client_id,
                textextraction_id,
                callback_url,
                status=StateHandler.FAILED.value
            )
            return
        self._common_doc_handler_2(text_contents, structured_text, table_contents, images_lst, client_id, textextraction_id, callback_url)

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
        #TODO: use extract all to use blocks
        self._common_doc_handler(entries, client_id, textextraction_id, callback_url, webpage_extraction=True)

    async def __call__(self, client_id, url, textextraction_id, callback_url, file_name="extract_text.txt"):
        content_type = await self.extract_content_type.get_content_type(url, self.headers)

        if content_type == UrlTypes.PDF.value:  # assume it is http/https pdf weblink
            await self.handle_pdf_text_from_url(url, client_id, textextraction_id, callback_url)
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

            s3_uploader = Storage(self.docs_conversion_bucket_name, "")
            tempf = await create_async_tempfile(url=url, headers=self.headers, timeout=60)
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

                    presigned_url = generate_presigned_url(
                        bucket_name=bucket_name,
                        key=file_path,
                        s3_client=s3_client_presigned_url
                    )
                    if presigned_url:
                        await self.handle_pdf_text_from_url(
                            url=presigned_url,
                            client_id=client_id,
                            textextraction_id=textextraction_id,
                            callback_url=callback_url
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
        elif content_type == UrlTypes.IMG.value:
            logging.info("The input document is an image file. Applying OCR on this document.")
            text_contents, structured_text, table_contents = await handle_scanned_doc_or_image(
                url=url,
                is_image=True,
                s3_bucket_name=self.bucket_name,
                textextraction_id=textextraction_id,
                headers=self.headers
            )
            image_lst = []
            self._common_doc_handler_2(text_contents, structured_text, table_contents, image_lst, client_id, textextraction_id, callback_url)
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
        total_words_count=None,
        table_contents=None,
        images_contents=None
    ):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": client_id,
            "text_path": text_presigned_url,
            "structured_text_path": structured_text_presigned_url,
            "images_path":  images_contents or [],
            "tables_path": table_contents if table_contents else [],
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
