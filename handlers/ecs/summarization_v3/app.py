import os
import logging
from typing import Optional

import sentry_sdk

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from summary_generator import ReportsGeneratorHandler

logging.getLogger().setLevel(logging.INFO)

logging.info("Loaded module as ecs task.")

SENTRY_DSN = os.environ.get("SENTRY_DSN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

reports_generator_handler = ReportsGeneratorHandler()

class RequestSchema(BaseModel):
    """ Request Schema """
    entries_url: Optional[str] = None
    client_id: Optional[str] = None
    callback_url: Optional[str] = None
    summarization_id: Optional[str] = None

ecs_app = FastAPI()

@ecs_app.get("/")
def home():
    """ Test endpoint """
    return "Welcome to the ECS Task of Summarization Module using LLM."

@ecs_app.get("/healthcheck")
async def healthcheckup():
    """ Health checkup endpoint """
    return "The instance is ok and running."

@ecs_app.post("/generate_report")
async def generate_summary(item: RequestSchema, background_tasks: BackgroundTasks):
    """ Handler to generate the summaries"""
    entries_url = item.entries_url
    client_id = item.client_id
    callback_url = item.callback_url
    summarization_id = item.summarization_id

    entries, tags = reports_generator_handler.download_prepare_entries(entries_url=entries_url)

    background_tasks.add_task(
        reports_generator_handler,
        client_id,
        entries,
        tags,
        summarization_id,
        callback_url
    )

    return {
        "message": "Task received and running in background."
    }
