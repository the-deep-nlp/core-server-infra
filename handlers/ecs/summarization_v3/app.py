import os
import logging
from enum import Enum
from typing import Optional
from datetime import date

import requests
import boto3
import sentry_sdk

from botocore.client import Config

from langchain import OpenAI, PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from langchain.chains.summarize import load_summarize_chain

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

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
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
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
    entries_url: Optional[str] = None
    client_id: Optional[str] = None
    callback_url: Optional[str] = None
    summarization_id: Optional[str] = None

ecs_app = FastAPI()

@ecs_app.get("/")
def home():
    """ Test endpoint """
    return "Welcome to the ECS Task of Summarization Module v3."

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


class ChainTypes(Enum):
    """ Chain Types """
    STUFF = 0
    MAP_REDUCE = 1
    REFINE = 2

class Summarization:
    """ Summarization Module """
    def __init__(
        self,
        temperature: float = 0.1,
        max_tokens: int = 512,
        model_name: str = "text-davinci-003"
    ):
        self.llm = OpenAI(
            temperature=temperature,
            model=model_name,
            max_tokens=max_tokens,
        )

    def textsplitter(self):
        """ Text Splitter """
        return RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=25,
            separators=["\n\n", "\n", "\t"]
        )

    def create_docs(self, texts: str):
        """ Create Docs """
        text_splitter = self.textsplitter()
        texts = text_splitter.split_text(texts)
        docs = [Document(page_content=t) for t in texts]
        return docs

    def generate_prompt(self):
        """ Generate Prompts """
        prompt_template = """You are a humanitarian analyst and has a strong domain knowledge.
        Write a concise summary of the following including key points:

        {text}

        CONCISE SUMMARY:
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        return prompt

    def generate_refine_prompt(self):
        """ Generate Refine Prompt """
        refine_template = (
            "Your job is to produce a final summary\n"
            "We have provided an existing summary up to a certain point: {existing_answer}\n"
            "We have the opportunity to refine the existing summary\n"
            "(only if needed) with some more context below.\n"
            "----------------\n"
            "{text}\n"
            "----------------\n"
            "Given the new context, refine the original summary\n"
            "If the context isn't useful, return the original summary"
        )
        refine_prompt = PromptTemplate(
            template=refine_template,
            input_variables=["existing_answer", "text"]
        )
        return refine_prompt

    def generate_summary(
        self,
        docs,
        prompt,
        chain_type=ChainTypes.MAP_REDUCE,
        verbose=False
    ):
        """ Generate Summary """
        if chain_type==ChainTypes.MAP_REDUCE:
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="map_reduce",
                verbose=verbose,
                map_prompt=prompt,
                combine_prompt=prompt
            )
        elif chain_type==ChainTypes.REFINE:
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="refine",
                verbose=verbose,
                question_prompt=prompt,
                refine_prompt=self.generate_refine_prompt()
            )
        else:
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type=chain_type,
                verbose=verbose
            )
        return chain.run(docs) # summary


class ReportsGeneratorHandler:
    """
    Summarization class to generate summary of the excerpts
    """
    def __init__(self):
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)

        self.headers = {
            "Content-Type": "application/json"
        }

        self.llm_summarizer = Summarization()

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

    def download_prepare_entries(self, entries_url: str):
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

    def dispatch_results(
        self,
        client_id: str,
        summarization_id: str,
        callback_url: str,
        status: int,
        presigned_url: Optional[str]=None
    ):
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

    def __call__(self, client_id: str, entries: list, summarization_id: str, callback_url: str):
        if not entries:
            self.dispatch_results(client_id, summarization_id, callback_url, status=StateHandler.INPUT_URL_PROCESS_FAILED.value)
            return

        if self.llm_summarizer:
            docs = self.llm_summarizer.create_docs(" ".join(entries))
            prompt = self.llm_summarizer.generate_prompt()
            summary = self.llm_summarizer.generate_summary(docs, prompt)
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
            logging.warning("Summarization LLM could not be loaded.")


reports_generator_handler = ReportsGeneratorHandler()
