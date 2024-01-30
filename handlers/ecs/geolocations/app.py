import os
import json
import logging
# import tarfile
# import gzip
# import shutil
import requests
import sentry_sdk
import warnings
from datetime import date
from typing import Optional
from pathlib import Path
from cloudpathlib import CloudPath
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from geolocation_generator import GeolocationGenerator
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

warnings.filterwarnings("ignore")

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

class RequestSchema(BaseModel):
    """ Request Schema """
    client_id: Optional[str]=None
    entries_url: Optional[str]=None
    geolocation_id: Optional[str]=None
    callback_url: Optional[str]=None
    entries_list: Optional[list]=None

ecs_app = FastAPI()

@ecs_app.get("/")
def home():
    """ Returns index page message """
    return "This is Geolocation ECS Task page."

@ecs_app.get("/healthcheck")
async def healthcheckup():
    """ Health checkup endpoint """
    return "The instance is ok and running."

@ecs_app.post("/get_geolocations")
async def extract_geolocations(
    item: RequestSchema,
    background_tasks: BackgroundTasks
):
    """ Request handler """
    client_id = item.client_id
    url = item.entries_url
    geolocation_id = item.geolocation_id
    callback_url = item.callback_url
    entries_list = item.entries_list

    if not any([url, entries_list]):
        logging.error("Request parameter either url or entries_list is missing.")
        return "Cannot process the request", 422

    if url:
        geolocation_handler.entries = geolocation_handler.download_prepare_entries(url=url)
    else:
        geolocation_handler.entries = entries_list

    geolocation_handler.client_id = client_id
    geolocation_handler.geolocation_id = geolocation_id
    geolocation_handler.callback_url = callback_url

    if not callback_url and not geolocation_id:
        response_data = geolocation_handler(resources_info_dict)
        logging.info("Sending the response data: %s", json.dumps(response_data))
        return response_data

    background_tasks.add_task(
        geolocation_handler,
        resources_info_dict
    )
    return {
        "message": "Task received and running in background."
    }


class GeoLocationGeneratorHandler:
    """
    Geolocation class to extract geolocations from the excerpts
    """
    def __init__(self):
        self.entries = None
        self.client_id = None
        self.callback_url = None
        self.geolocation_id = None

        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)
        self.geoname_api_user = os.environ.get("GEONAME_API_USER", None)

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

    def download_prepare_entries(self, url: str, req_timeout: int=30):
        """
        The json format (*.json) in the link file should be
        [
            {
                "entry_id": int,
                "excerpt": str
            }
        ]
        """
        if url:
            logging.info("The request url is %s", url)
            try:
                response = requests.get(url, timeout=req_timeout)
                if response.status_code == 200:
                    return response.json()
            except Exception as exc:
                logging.error("Error occurred: %s", str(exc))
        return None

    def download_spacy_model(
        self,
        s3_spacy_path: str="s3://deep-geolocation-extraction/models/spacy_finetuned_100doc_5epochs/spacy_finetuned_100doc_5epochs",
    ):
        """
        Downloads the spacy model and stores it in the EFS
        """
        resources_info = {}
        resources_path = Path("/models/geolocation")
        resources_info_path = resources_path / "resources_info.json"

        if not os.path.exists(resources_path):
            os.makedirs(resources_path)

        if not any(os.listdir(resources_path)):
            logging.info("Downloading the geolocation resources.")
            efs_spacy_path = resources_path / "models"
            cloudpath_spacy = CloudPath(s3_spacy_path)
            cloudpath_spacy.download_to(efs_spacy_path)

            resources_info = {
                "spacy_path": str(efs_spacy_path)
            }
            with open(resources_info_path, "w", encoding="utf-8") as resources_info_f:
                json.dump(resources_info, resources_info_f)
        else:
            if os.path.exists(resources_info_path):
                logging.info("Resources already exist in the EFS.")
                with open(resources_info_path, "r", encoding="utf-8") as resources_info_f:
                    resources_info = json.load(resources_info_f)
                    logging.info(resources_info)
            else:
                return {}
        return resources_info


    # def download_resources(
    #     self,
    #     s3_spacy_path: str="s3://deep-geolocation-extraction/models/spacy_finetuned_100doc_5epochs/spacy_finetuned_100doc_5epochs",
    #     s3_locationdata_path: str="s3://deep-geolocation-extraction/geonames/locationdata.tsv.gz",
    #     s3_locdictionary_path: str="s3://deep-geolocation-extraction/geonames/locdictionary_unicode.json.gz",
    #     s3_indexdir_path: str="s3://deep-geolocation-extraction/geonames/indexdir.tar.gz"
    # ):
    #     """
    #     Downloads the resources and store them in the EFS
    #     """
    #     resources_info = {}
    #     resources_path = Path("/geolocations")
    #     resources_info_path = resources_path / "resources_info.json"

    #     if not any(os.listdir(resources_path)):
    #         logging.info("Downloading the geolocation resources.")
    #         efs_spacy_path = resources_path / "models"
    #         efs_locationdata_path = resources_path / "locationdata.tsv.gz"
    #         efs_locdictionary_path = resources_path / "locdictionary_unicode.json.gz"
    #         efs_locdictionary_path_final = resources_path / "locdictionary_unicode.json"
    #         efs_indexdir_path = resources_path / "indexdir.tar.gz"
    #         efs_indexdir_path_final = resources_path / "indexdir"

    #         cloudpath_spacy = CloudPath(s3_spacy_path)
    #         cloudpath_locationdata = CloudPath(s3_locationdata_path)
    #         cloudpath_locdictionary = CloudPath(s3_locdictionary_path)
    #         cloudpath_indexdir = CloudPath(s3_indexdir_path)

    #         cloudpath_spacy.download_to(efs_spacy_path)
    #         cloudpath_locationdata.download_to(efs_locationdata_path)
    #         cloudpath_locdictionary.download_to(efs_locdictionary_path)
    #         cloudpath_indexdir.download_to(efs_indexdir_path)

    #         # Unzip file
    #         with gzip.open(efs_locdictionary_path, "r") as f_in, open(efs_locdictionary_path_final, "wb") as f_out:
    #             shutil.copyfileobj(f_in, f_out)

    #         # Untar the file
    #         with tarfile.open(efs_indexdir_path, "r:gz") as tar_f:
    #             tar_f.extractall(path=resources_path)

    #         resources_info = {
    #             "spacy_path": str(efs_spacy_path),
    #             "locationdata_path": str(efs_locationdata_path),
    #             "locdictionary_path": str(efs_locdictionary_path_final),
    #             "indexdir_path": str(efs_indexdir_path_final)
    #         }
    #         with open(resources_info_path, "w", encoding="utf-8") as resources_info_f:
    #             json.dump(resources_info, resources_info_f)
    #     else:
    #         if os.path.exists(resources_info_path):
    #             logging.info("Resources already exist in the EFS.")
    #             with open(resources_info_path, "r", encoding="utf-8") as resources_info_f:
    #                 resources_info = json.load(resources_info_f)
    #                 logging.info(resources_info)
    #         else:
    #             return {}
    #     return resources_info

    def dispatch_results(self,
        status: int,
        presigned_url: str=None
    ):
        """
        Dispatch results to callback url or write to database
        """
        response_data = {
            "client_id": self.client_id,
            "presigned_s3_url": presigned_url,
            "status": status
        }
        if self.callback_url:
            callback_response = send_request_on_callback(
                self.callback_url,
                response_data=response_data,
                headers=self.headers
            )
            if not callback_response:
                db_client = Database(**self.db_config)
                db_conn, db_cursor = db_client.db_connection()
                update_db_table_callback_retry(
                    db_conn,
                    db_cursor,
                    self.geolocation_id,
                    self.db_table_callback_tracker
                )
        
        # Setup database connections
        db_client = Database(**self.db_config)
        db_conn, db_cursor = db_client.db_connection()

        if presigned_url and self.db_table_name: # update for presigned url
            sql_statement = prepare_sql_statement_success(
                self.geolocation_id,
                self.db_table_name,
                status,
                response_data
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            sql_statement = prepare_sql_statement_failure(
                self.geolocation_id,
                self.db_table_name,
                status
            )
            status_update_db(db_conn, db_cursor, sql_statement)
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")


    def __call__(self, resources_info: dict, use_search_engine: bool=True):
        processed_results = []

        if not self.entries:
            logging.error("Input data not available.")
            self.dispatch_results(status=StateHandler.INPUT_URL_PROCESS_FAILED.value)
            return

        try:
            geolocation = GeolocationGenerator(spacy_path=resources_info["spacy_path"])
            # Below method not in use
            # geolocation_results = geolocation.get_geolocation(
            #     raw_data=[in_entries_dict["excerpt"] for in_entries_dict in self.entries],
            #     locationdata_path=resources_info["locationdata_path"],
            #     locdictionary_path=resources_info["locdictionary_path"],
            #     indexdir=resources_info["indexdir_path"],
            #     use_search_engine=use_search_engine
            # )
            geolocation_results = geolocation.get_geolocation_api(
                raw_data=[
                    in_entries["excerpt"] if "excerpt" in in_entries else in_entries
                    for in_entries in self.entries
                ],
                geonames_username=self.geoname_api_user
            )
        except Exception as exc:
            logging.error("Geolocation processing failed. %s", str(exc))
            geolocation_results = []

        if geolocation_results:
            # Note: self.entries is either a dict or a list
            processed_results = [{
                **({"entry_id": x["entry_id"]} if "entry_id" in x else {"excerpt": x}),
                "entities": y["entities"]
                } for x, y in zip(self.entries, geolocation_results)
            ]
        # If callback_url is not available, directly return the response data in ack response.
        if not self.callback_url:
            return processed_results

        date_today = date.today().isoformat()
        try:
            presigned_url = upload_to_s3(
                contents=json.dumps(processed_results),
                contents_type="application/json",
                bucket_name=self.bucket_name,
                key=f"geolocations/{date_today}/{self.geolocation_id}/geolocation.json",
                aws_region=self.aws_region,
                signed_url_expiry_secs=self.signed_url_expiry_secs
            )
        except Exception as exc:
            logging.error("Could not upload to s3 due to following error: %s", str(exc))
            processed_results = []
            presigned_url = None

        if presigned_url:
            self.dispatch_results(status=StateHandler.SUCCESS.value, presigned_url=presigned_url)
        else:
            self.dispatch_results(status=StateHandler.FAILED.value)

geolocation_handler = GeoLocationGeneratorHandler()
resources_info_dict = geolocation_handler.download_spacy_model()
#geolocation_handler(resources_info=resources_info_dict)
