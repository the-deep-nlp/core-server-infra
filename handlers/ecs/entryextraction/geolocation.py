import os
import logging
from pathlib import Path
from cloudpathlib import CloudPath
from geolocation_generator import GeolocationGenerator

logging.getLogger().setLevel(logging.INFO)

def download_spacy_model(
    s3_spacy_path = "s3://deep-geolocation-extraction/models/spacy_finetuned_100doc_5epochs/spacy_finetuned_100doc_5epochs",
):
    """
    Downloads the spacy model and stores it in the EFS
    """
    resources_path = Path("/models/geolocation")

    if not os.path.exists(resources_path):
        os.makedirs(resources_path)

    efs_spacy_path = resources_path / "models"
    if not any(os.listdir(resources_path)):
        logging.info("Downloading the geolocation resources.")
        cloudpath_spacy = CloudPath(s3_spacy_path)
        cloudpath_spacy.download_to(efs_spacy_path)

    return efs_spacy_path

def get_geolocations(
    entries,
    geoname_api_user
):
    """ Get the geolocations from the Geonames API """
    try:
        spacy_path = download_spacy_model()
        geolocation = GeolocationGenerator(spacy_path=spacy_path)

        geolocation_results = geolocation.get_geolocation_api(
            raw_data=entries,
            geonames_username=geoname_api_user
        )
        processed_results = [{
            "entry": x,
            "locations": [o["ent"] for o in y["entities"]]
            } for x, y in zip(entries, geolocation_results)
        ]
    except Exception as exc:
        logging.error("Geolocation processing failed. %s", str(exc))
        processed_results = []
    return processed_results
