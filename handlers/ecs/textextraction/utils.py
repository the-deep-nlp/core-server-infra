import os
import re
import json
import tempfile
import logging
import tarfile
from datetime import date
from PIL import Image
import httpx
import aiofiles
import numpy as np
from wget import download
from botocore.exceptions import ClientError, ReadTimeoutError, ConnectTimeoutError

from ocr_extractor import OCRProcessor

from nlp_modules_utils import generate_presigned_url

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

async def create_async_tempfile(url: str, headers: dict, timeout: int=30):
    """ Creates a async tempfile """
    client = httpx.AsyncClient()
    tempf = tempfile.NamedTemporaryFile(mode="w+b")
    async with client.stream("GET", url=url, headers=headers, timeout=timeout) as response:
        async for chunk in response.aiter_bytes():
            tempf.write(chunk)
        tempf.seek(0)
    await client.aclose()
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

def download_file(s3_client, filename_s3, bucketname, filename_local):
    """
    Downloads the file
    """
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

def invoke_conversion_lambda(
    lambda_client,
    docs_conversion_bucket_name,
    docs_convert_lambda_fn_name,
    tmp_filename,
    ext_type
):
    """
    Invoke lambda function to convert documents(docx, pptx, xlsx) to pdf
    """
    logging.info("File conversion request initiated.")
    payload = json.dumps({
        "file": tmp_filename,
        "bucket": docs_conversion_bucket_name,
        "ext": ext_type,
        "fromS3": 1
    })
    try:
        docs_conversion_lambda_response = lambda_client.invoke(
            FunctionName=docs_convert_lambda_fn_name,
            InvocationType="RequestResponse",
            Payload=payload
        )
    except ClientError as cexc:
        logging.error("Error occurred during lambda invocation. %s", str(cexc))
        return {}
    except (ReadTimeoutError, ConnectTimeoutError) as texc:
        logging.error("Error occurred during lambda invocation. %s", str(texc))
        return {}
    docs_conversion_lambda_response_json = json.loads(
        docs_conversion_lambda_response["Payload"].read().decode("utf-8")
    )
    return docs_conversion_lambda_response_json


def append_text(f):
    def inner(main_txt, pgnum):
        start_text = f"********* [PAGE {pgnum} START] *********"
        end_text = f"********* [PAGE {pgnum} END] *********"
        final_data = start_text + "\n" + main_txt + "\n" + end_text + "\n"
        return f(final_data, pgnum)
    return inner


def append_ocr_text(f):
    def inner(main_txt):
        start_text = "********* [OCR CONTENT START] *********"
        end_text = "********* [OCR CONTENT END]  *********"
        final_data = start_text + "\n" + main_txt + "\n" + end_text + "\n"
        return f(final_data)
    return inner


@append_text
def beautify_extracted_text(text, pgnum):
    return text

@append_ocr_text
def beautify_ocr_text(text):
    return text

def download_models():
    model_urls = [
        "https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar",
        "https://paddleocr.bj.bcebos.com/PP-OCRv4/english/en_PP-OCRv4_rec_infer.tar",
        "https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar",
        "https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/en_ppstructure_mobile_v2.0_SLANet_infer.tar",
        "https://paddleocr.bj.bcebos.com/ppstructure/models/layout/picodet_lcnet_x1_0_fgd_layout_infer.tar",
        "https://paddle-model-ecology.bj.bcebos.com/model/layout-parser/ppyolov2_r50vd_dcn_365e_publaynet.tar"
    ]

    tar_files = [
        "en_PP-OCRv3_det_infer.tar",
        "en_PP-OCRv4_rec_infer.tar",
        "ch_ppocr_mobile_v2.0_cls_infer.tar",
        "en_ppstructure_mobile_v2.0_SLANet_infer.tar",
        "picodet_lcnet_x1_0_fgd_layout_infer.tar",
        "ppyolov2_r50vd_dcn_365e_publaynet.tar"
    ]

    file_paths = {
        "det_model_dir": "/ocr/models/en_PP-OCRv3_det_infer",
        "rec_model_dir": "/ocr/models/en_PP-OCRv4_rec_infer",
        "cls_model_dir": "/ocr/models/ch_ppocr_mobile_v2.0_cls_infer",
        "table_model_dir": "/ocr/models/en_ppstructure_mobile_v2.0_SLANet_infer",
        "layout_model_dir": "/ocr/models/picodet_lcnet_x1_0_fgd_layout_infer"
    }

    models_path = "/ocr/models"
    if not os.path.exists(models_path):
        os.makedirs(models_path)

        for url in model_urls:
            logging.info("Downloading the model %s", url)
            download(url=url, out=models_path)

        for tar_file in tar_files:
            with tarfile.open(f"{models_path}/{tar_file}") as tar:
                tar.extractall(models_path)
    else:
        logging.info("OCR models path exist.")
    return file_paths

def filter_file_by_size(file_path: str, filesize:int=100_000):
    """ Filters images/files based on the file size """
    img = np.array(Image.open(file_path))
    if img.size >= filesize:
        return True
    return False


async def handle_scanned_doc_or_image(
    url: str,
    is_image: bool,
    s3_bucket_name: str,
    textextraction_id: str,
    headers: str,
    req_timeout: int=30
):
    """ Handles complete scanned document or image """
    model_filepath = download_models()
    date_today = date.today().isoformat()
    tempf = await create_async_tempfile(url=url, headers=headers, timeout=req_timeout)
    try:
        ocr_engine = OCRProcessor(
            extraction_type=3,
            show_log=False,
            use_s3=True,
            s3_bucket_name=s3_bucket_name,
            s3_bucket_key=f"textextraction/{date_today}/{textextraction_id}/tables",
            **model_filepath
        )
        ocr_engine.load_file(file_path=tempf.name, is_image=is_image)
        results = await ocr_engine.handler()
    except Exception as exc:
        logging.warning("Exception occurred while extracting contents %s", str(exc))
        return "", [[]], []

    tables = results["table"]
    texts = ""
    temp_texts = ""
    structured_text = []
    structured_text_temp = []
    page_num = 0
    for text_block in results["text"]:
        if text_block["page_number"] == page_num:
            temp_texts += text_block["content"] + "\n\n\n"
            structured_text_temp.append(text_block["content"])
        else:
            temp_texts = beautify_ocr_text(temp_texts)
            texts += beautify_extracted_text(temp_texts, page_num + 1)
            temp_texts = ""
            temp_texts += text_block["content"] + "\n\n\n"
            structured_text.append(structured_text_temp)
            structured_text_temp = []
            structured_text_temp.append(text_block["content"])
            page_num += 1
    if texts or temp_texts:
        temp_texts = beautify_ocr_text(temp_texts)
        texts += beautify_extracted_text(temp_texts, page_num + 1)
        structured_text.append(structured_text_temp)

    return texts, structured_text, tables


async def uploadfile_s3(
    filepath: str,
    bucket_name: str,
    textextraction_id: str,
    s3_client
):
    """ Upload file in s3 """
    date_today = date.today().isoformat()
    filename = filepath.split("/")[-1]
    async with aiofiles.open(filepath, "rb") as f:
        contents = await f.read()
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"textextraction/{date_today}/{textextraction_id}/images/{filename}",
            Body=contents,
            ContentType="image/png"
        )
    image_presigned_url = generate_presigned_url(
        bucket_name=bucket_name,
        key=f"textextraction/{date_today}/{textextraction_id}/images/{filename}",
        s3_client=s3_client
    )
    return image_presigned_url
