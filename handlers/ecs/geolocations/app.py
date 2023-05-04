import os
import io
import json
import logging
import tarfile
import gzip
import shutil
import psycopg2
import requests
import boto3
import sentry_sdk
import warnings
from pathlib import Path
from cloudpathlib import CloudPath
from datetime import date, datetime
from enum import Enum
from botocore.client import Config
from botocore.exceptions import ClientError
from geolocation_generator import GeolocationGenerator

warnings.filterwarnings("ignore")

logging.getLogger().setLevel(logging.INFO)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT, attach_stacktrace=True, traces_sample_rate=1.0)

class ReportStatus(Enum):
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


class GeoLocationGeneratorHandler:
    """
    Geolocation class to extract geolocations from the excerpts
    """
    def __init__(self):
        self.entries_url = os.environ.get("ENTRIES_URL", None)
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.callback_url = os.environ.get("CALLBACK_URL", None)
        self.geolocation_id = os.environ.get("GEOLOCATION_ID", None)
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.signed_url_expiry_secs = os.environ.get("SIGNED_URL_EXPIRY_SECS", 86400) # 1 day
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", None)
        self.geoname_api_user = os.environ.get("GEONAME_API_USER", None)

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

        self.db_table_name = os.environ.get("DB_TABLE_NAME", None)
        self.db_table_callback_tracker = os.environ.get("DB_TABLE_CALLBACK_TRACKER", None)

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
                    return response.json()
            except Exception as exc:
                logging.error("Error occurred: %s", str(exc))
        return None

    def download_spacy_model(
        self,
        s3_spacy_path = "s3://deep-geolocation-extraction/models/spacy_finetuned_100doc_5epochs/spacy_finetuned_100doc_5epochs",
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


    def download_resources(
        self,
        s3_spacy_path = "s3://deep-geolocation-extraction/models/spacy_finetuned_100doc_5epochs/spacy_finetuned_100doc_5epochs",
        s3_locationdata_path = "s3://deep-geolocation-extraction/geonames/locationdata.tsv.gz",
        s3_locdictionary_path = "s3://deep-geolocation-extraction/geonames/locdictionary_unicode.json.gz",
        s3_indexdir_path = "s3://deep-geolocation-extraction/geonames/indexdir.tar.gz"
    ):
        """
        Downloads the resources and store them in the EFS
        """
        resources_info = {}
        resources_path = Path("/geolocations")
        resources_info_path = resources_path / "resources_info.json"

        if not any(os.listdir(resources_path)):
            logging.info("Downloading the geolocation resources.")
            efs_spacy_path = resources_path / "models"
            efs_locationdata_path = resources_path / "locationdata.tsv.gz"
            efs_locdictionary_path = resources_path / "locdictionary_unicode.json.gz"
            efs_locdictionary_path_final = resources_path / "locdictionary_unicode.json"
            efs_indexdir_path = resources_path / "indexdir.tar.gz"
            efs_indexdir_path_final = resources_path / "indexdir"

            cloudpath_spacy = CloudPath(s3_spacy_path)
            cloudpath_locationdata = CloudPath(s3_locationdata_path)
            cloudpath_locdictionary = CloudPath(s3_locdictionary_path)
            cloudpath_indexdir = CloudPath(s3_indexdir_path)

            cloudpath_spacy.download_to(efs_spacy_path)
            cloudpath_locationdata.download_to(efs_locationdata_path)
            cloudpath_locdictionary.download_to(efs_locdictionary_path)
            cloudpath_indexdir.download_to(efs_indexdir_path)

            # Unzip file
            with gzip.open(efs_locdictionary_path, "r") as f_in, open(efs_locdictionary_path_final, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            
            # Untar the file
            with tarfile.open(efs_indexdir_path, "r:gz") as tar_f:
                tar_f.extractall(path=resources_path)

            resources_info = {
                "spacy_path": str(efs_spacy_path),
                "locationdata_path": str(efs_locationdata_path),
                "locdictionary_path": str(efs_locdictionary_path_final),
                "indexdir_path": str(efs_indexdir_path_final)
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

    def geolocations_store_s3(
        self,
        geolocation_data,
        bucket_name="test-ecs-parser11",
        key="geolocation.json"
    ):
        """
        Stores the geolocations in s3
        """
        try:
            session = boto3.Session()
            s3_resource = session.resource("s3")
            bucket = s3_resource.Bucket(bucket_name)
            summary_bytes = bytes(geolocation_data, "utf-8")
            summary_bytes_obj = io.BytesIO(summary_bytes)
            bucket.upload_fileobj(
                summary_bytes_obj,
                key,
                ExtraArgs={"ContentType": "application/json"}
            )
            return self.generate_presigned_url(bucket_name, key)
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

    def _update_db_table_callback_retry(self):
        """
        Updates the table whenever the callback fails
        """
        if self.db_table_callback_tracker and self.geolocation_id:
            now_date = datetime.now().isoformat()
            self.status_update_db(
                sql_statement=f""" INSERT INTO {self.db_table_callback_tracker} 
                                (request_unique_id, created_at, modified_at, retries_count, status) 
                                VALUES ('{self.geolocation_id}', '{now_date}', '{now_date}', 0, 3) """  # status = 3(Retrying)
            )
            logging.info("Updated the db table for callback retries.")

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
            self._update_db_table_callback_retry()
        if response.status_code == 200:
            logging.info("Successfully sent the request on callback url")
        else:
            logging.error("Error while sending the request on callback url")
            self._update_db_table_callback_retry()

    def dispatch_results(self, status, presigned_url=None):
        """
        Dispatch results to callback url or write to database
        """
        if self.callback_url:
            self.send_request_on_callback(presigned_url=presigned_url, status=status)
        if presigned_url and self.db_table_name: # update for presigned url
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}', result_s3_link='{presigned_url}' WHERE unique_id='{self.geolocation_id}' """
            )
            logging.info("Updated the db table with event status %s", str(status))
        elif self.db_table_name:
            # Presigned url generation failed
            self.status_update_db(
                sql_statement=f""" UPDATE {self.db_table_name} SET status='{status}' WHERE unique_id='{self.geolocation_id}' """
            )
            logging.info("Updated the db table with event status %s", str(status))
        else:
            logging.error("Callback url / presigned s3 url / Database table name are not found.")


    def __call__(self, resources_info, use_search_engine=True):
        if not self.entries:
            logging.error("Input data not available.")
            self.dispatch_results(status=ReportStatus.INPUT_URL_PROCESS_FAILED.value)
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
                raw_data=[in_entries_dict["excerpt"] for in_entries_dict in self.entries],
                geonames_username=self.geoname_api_user
            )
            processed_results = [{
                "entry_id": x["entry_id"],
                "entities": y["entities"]
                } for x, y in zip(self.entries, geolocation_results)
            ]
            date_today = date.today().isoformat()
            presigned_url = self.geolocations_store_s3(
                geolocation_data=json.dumps(processed_results),
                bucket_name=self.bucket_name,
                key=f"geolocations/{date_today}/{self.geolocation_id}/geolocation.txt"
            )
        except Exception as exc:
            logging.error("Geolocation processing failed. %s", str(exc))
            processed_results = []
            presigned_url = None

        if presigned_url:
            self.dispatch_results(status=ReportStatus.SUCCESS.value, presigned_url=presigned_url)
        else:
            self.dispatch_results(status=ReportStatus.FAILED.value)

geolocation_generator_handler = GeoLocationGeneratorHandler()
resources_info_dict = geolocation_generator_handler.download_spacy_model()
geolocation_generator_handler(resources_info=resources_info_dict)
