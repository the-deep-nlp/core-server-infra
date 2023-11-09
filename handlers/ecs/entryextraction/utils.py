import re
import logging
from botocore.exceptions import ClientError

logging.getLogger().setLevel(logging.INFO)


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


def generate_presigned_url(
    s3_client_presigned_url,
    bucket_name,
    key,
    signed_url_expiry_secs
):
    """
    Generates a presigned url of the file stored in s3
    """
    # Note that the bucket and service(e.g. summarization) should run on the same aws region
    try:
        url = s3_client_presigned_url.generate_presigned_url(
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

