import os
import json
import requests
import logging
from random import shuffle
from math import ceil
from flask import Flask, request

from handlers.ecs.ngrams.app import NGramsGeneratorHandler

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)

def get_entries_data(url):
    try:
        response = requests.get(url)
        entries_data = json.loads(response.text)
        return entries_data
    except Exception as e:
        raise e

def save_data_local(dir_name, client_id, data):
    parent_dirpath = f"/tmp/{dir_name}"
    if not os.path.exists(parent_dirpath):
        os.makedirs(parent_dirpath)
    filepath = parent_dirpath + f"/{client_id}.json"
    
    with open(filepath, "w") as f:
        f.write(json.dumps(data))
    return filepath

def send_callback_url_request(callback_url, client_id, filepath):
    if callback_url:
        response_callback_url = requests.post(
            callback_url,
            data=json.dumps({
                "client_id": client_id,
                "presigned_s3_url": filepath
            })
        )
        if response_callback_url.status_code == 200:
            logging.info("Request sent successfully.")
            return json.dumps({
                "status": "Request sent successfully."
            })
        else:
            logging.info(f"Some errors occurred. StatusCode: {response_callback_url.status_code}")
            return json.dumps({
                "status": f"Error occurred with statuscode: {response_callback_url.status_code}"
            })
    
    logging.error("No callback url found.")
    return json.dumps({
        "status": "No callback url found."
    }), 400

@app.route('/')
def homepage():
    return json.dumps({
        "status": "Welcome to analysis module mock server"
    })

@app.route('/mock/ngrams')
def ngramsmodel():
    body = request.get_json()
    
    request_body = body if isinstance(body, dict) else json.loads(body)

    os.environ["CLIENT_ID"] = request_body.get("client_id", "")
    os.environ["ENTRIES_URL"] = request_body.get("entries_url", "")
    os.environ["CALLBACK_URL"] = request_body.get("callback_url", "")
    os.environ["GENERATE_UNIGRAMS"] = request_body["ngrams_config"].get("generate_unigrams", "False")
    os.environ["GENERATE_BIGRAMS"] = request_body["ngrams_config"].get("generate_bigrams", "False")
    os.environ["GENERATE_TRIGRAMS"] = request_body["ngrams_config"].get("generate_trigrams", "False")
    os.environ["ENABLE_STOPWORDS"] = request_body["ngrams_config"].get("enable_stopwords", "False")
    os.environ["ENABLE_STEMMING"] = request_body["ngrams_config"].get("enable_stemming", "False")
    os.environ["ENABLE_CASE_SENSITIVE"] = request_body["ngrams_config"].get("enable_case_sensitive", "False")
    os.environ["MAX_NGRAMS_TOKENS"] = request_body["ngrams_config"].get("max_ngrams_items", "10")
    os.environ["NGRAMS_MOCK"] = "True"

    ng = NGramsGeneratorHandler()
    ng()

    return json.dumps({
        "status": "Successfully received the request."
    }), 200


@app.route("/mock/summarization")
def summarizationmodel():
    body = request.get_json()
    request_body = body if isinstance(body, dict) else json.loads(body)

    client_id = request_body.get("client_id")
    entries_url = request_body.get("entries_url")
    callback_url = request_body.get("callback_url")

    excerpts = [
        x["excerpt"] for x in get_entries_data(entries_url)
    ]
    
    data = " ".join(["This is a fake response.\n"] + excerpts)
    filepath = save_data_local(
        dir_name="summarization",
        client_id=client_id,
        data=data
    )

    send_callback_url_request(
        callback_url=callback_url,
        client_id=client_id,
        filepath=filepath
    )
    
    return json.dumps({
        "status": "Successfully received the request."
    }), 200


@app.route("/mock/topicmodeling")
def topicmodelingmodel():
    clusters = 5

    body = request.get_json()
    request_body = body if isinstance(body, dict) else json.loads(body)

    client_id = request_body.get("client_id")
    entries_url = request_body.get("entries_url")
    callback_url = request_body.get("callback_url")

    excerpt_ids = [
        x["entry_id"] for x in get_entries_data(entries_url)
    ]

    shuffle(excerpt_ids)

    data = [
        excerpt_ids[x:x+ceil(len(excerpt_ids)/clusters)] 
        for x in range(0, len(excerpt_ids), ceil(len(excerpt_ids)/clusters))
    ]

    data = {key: val for key, val in enumerate(data)}

    filepath = save_data_local(
        dir_name="topicmodel",
        client_id=client_id,
        data=data
    )

    send_callback_url_request(
        callback_url=callback_url,
        client_id=client_id,
        filepath=filepath
    )

    return json.dumps({
        "status": "Successfully received the request."
    }), 200

app.run(host="0.0.0.0", port=8081)