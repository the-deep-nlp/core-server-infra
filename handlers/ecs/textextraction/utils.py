import re
import json
import tempfile
import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

logging.getLogger().setLevel(logging.INFO)

def create_tempfile(response):
    """
    Creates a temporary file
    """
    tempf = tempfile.NamedTemporaryFile(mode="w+b")
    for chunk in response.iter_content(chunk_size=128):
        tempf.write(chunk)
    tempf.seek(0)
    return tempf

def get_words_count(text):
    """
    Counts the words in the text
    """
    if text:
        w = re.sub(r'[^\w\s]', '', text)
        w = re.sub(r'_', '', w)
        return len(w.split())
    return 0

def preprocess_extracted_texts(text):
    """
    Performs some initial pre-processing
    """
    extracted_text = text.replace("\x00", "")  # remove null chars
    extracted_text = extracted_text.encode('utf-8', 'ignore').decode('utf-8')
    return extracted_text

def download_file(aws_region, filename_s3, bucketname, filename_local):
    """
    Downloads the file
    """
    s3_client = boto3.client("s3", region_name=aws_region)
    try:
        s3_client.download_file(
            bucketname,
            filename_s3,
            filename_local
        )
        logging.info("The file is downloaded in the lambda /tmp directory.")
    except ClientError as cexc:
        logging.error("Client error occurred. %s", str(cexc))
        return False
    return True

def generate_presigned_url(
    aws_region,
    bucket_name,
    key,
    signed_url_expiry_secs
):
    """
    Generates a presigned url of the file stored in s3
    """
    # Note that the bucket and service(e.g. summarization) should run on the same aws region
    try:
        s3_client = boto3.client(
            "s3",
            region_name=aws_region,
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
            ExpiresIn=signed_url_expiry_secs
        )
    except ClientError as cexc:
        logging.error("Error while generating presigned url %s", cexc)
        return None
    return url

def invoke_conversion_lambda(
    aws_region,
    docs_conversion_bucket_name,
    docs_convert_lambda_fn_name,
    tmp_filename,
    ext_type
):
    """
    Invoke lambda function to convert documents(docx, pptx, xlsx) to pdf
    """
    logging.info("File conversion request initiated.")
    lambda_client = boto3.client('lambda', region_name=aws_region)
    payload = json.dumps({
        "file": tmp_filename,
        "bucket": docs_conversion_bucket_name,
        "ext": ext_type,
        "fromS3": 1
    })

    docs_conversion_lambda_response = lambda_client.invoke(
        FunctionName=docs_convert_lambda_fn_name,
        InvocationType="RequestResponse",
        Payload=payload
    )
    docs_conversion_lambda_response_json = json.loads(
        docs_conversion_lambda_response["Payload"].read().decode("utf-8")
    )
    return docs_conversion_lambda_response_json
