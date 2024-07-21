import logging
from enum import Enum
import httpx
from wget import download

logging.getLogger().setLevel(logging.INFO)

class UrlTypes(str, Enum):
    """ Common URL types """
    HTML = 'html'
    PDF = 'pdf'
    DOCX = 'docx'
    PPTX = 'pptx'
    PPT = 'ppt'
    MSWORD = 'doc'
    XLSX = 'xlsx'
    XLS = 'xls'
    IMG = 'img'

extension_to_enum_map = {
    "pdf": UrlTypes.PDF,
    "docx": UrlTypes.DOCX,
    "doc": UrlTypes.MSWORD,
    "xlsx": UrlTypes.XLSX,
    "xls": UrlTypes.XLS,
    "pptx": UrlTypes.PPTX,
    "ppt": UrlTypes.PPT,
    # Images
    "jpg": UrlTypes.IMG,
    "jpeg": UrlTypes.IMG,
    "png": UrlTypes.IMG,
    "gif": UrlTypes.IMG,
    "bmp": UrlTypes.IMG,
}

class ExtractContentType:
    """
    Gets the content type of the file from the link
    """
    def __init__(self):
        self.content_types_pdf = ('application/pdf', 'pdf')
        self.content_types_html = ('text/html', 'text/html; charset=utf-8', 'text/html;charset=UTF-8',
                                   'text/html; charset=UTF-8', 'text/html;charset=utf-8', 'text/plain')
        self.content_types_docx = ('application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.content_types_doc = ('application/msword')
        self.content_types_pptx = ('application/vnd.openxmlformats-officedocument.presentationml.presentation')
        self.content_types_ppt = ('application/vnd.ms-powerpoint')
        self.content_types_xlsx = ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.content_types_xls = ('application/vnd.ms-excel')
        self.content_types_img = ('image/jpeg', 'image/gif', 'image/png', 'image/svg+xml', 'image/webp', 'image/bmp', 'image/tiff')

    async def get_content_type(self, url: str, req_headers: dict, timeout: int=30):
        """
        Retrieve the content type of the url
        """
        try:
            async with httpx.AsyncClient() as httpx_client:
                response = await httpx_client.head(url, headers=req_headers, timeout=timeout)
            content_type = response.headers.get("Content-Type", None)
            if not content_type:
                return None
        except httpx.InvalidURL as url_err:
            logging.error("The URL is invalid %s", str(url_err))
            return None
        except httpx.TimeoutException as timeout_err:
            logging.warning("Timeout occurred: %s", str(timeout_err))
            return None
        except httpx.HTTPError as httperr:
            logging.warning("Error occurred while requesting information from the url. %s", str(httperr))
            return None
        except Exception as exc:
            logging.warning("Error occurred while requesting information from the url. %s", str(exc))
            return None

        logging.info("The content type of %s is %s", url, content_type)

        if url.endswith(".pdf"):
            return UrlTypes.PDF.value
        elif content_type in self.content_types_pdf:
            return UrlTypes.PDF.value
        elif url.endswith(".docx") or content_type in self.content_types_docx:
            return UrlTypes.DOCX.value
        elif url.endswith(".doc") or content_type in self.content_types_doc:
            return UrlTypes.MSWORD.value
        elif url.endswith(".xlsx") or content_type in self.content_types_xlsx:
            return UrlTypes.XLSX.value
        elif url.endswith(".xls") or content_type in self.content_types_xls:
            return UrlTypes.XLS.value
        elif url.endswith(".pptx") or content_type in self.content_types_pptx:
            return UrlTypes.PPTX.value
        elif url.endswith(".ppt") or content_type in self.content_types_ppt:
            return UrlTypes.PPT.value
        elif content_type in self.content_types_html:
            return UrlTypes.HTML.value
        elif (content_type in self.content_types_img or
            any([
                url.endswith(f".{extension}") for extension in [
                    "jpg", "jpeg", "png", "gif", "bmp"
                ]
            ])
        ):
            return UrlTypes.IMG.value
        else:
            try:
                logging.info("Downloading the file to check for the extension.")
                temp_filepath = download(url, out="/tmp/")
            except Exception:
                logging.error("Error while downloading the file from %s to check the file extension.", url)
                return None

            file_extension = temp_filepath.split(".")[-1]
            if file_extension not in extension_to_enum_map:
                logging.warning("Could not determine the content-type of the %s", url)
                return None
            return extension_to_enum_map[file_extension].value
