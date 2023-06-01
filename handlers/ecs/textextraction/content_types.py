import requests
import logging
from enum import Enum
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

    def get_content_type(self, url, req_headers):
        """
        Retrieve the content type of the url
        """
        try:
            response = requests.head(url, headers=req_headers, timeout=30)
            content_type = response.headers['Content-Type']

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
                    temp_filepath = download(url, out="/tmp/")
                except Exception:
                    logging.error("Error while downloading the file from %s to check the file extension.", url)
                    return None
                
                file_extension = temp_filepath.split(".")[-1]
                if file_extension not in extension_to_enum_map:
                    logging.warning("Could not determine the content-type of the %s", url)
                    return None
                return extension_to_enum_map[file_extension].value
        except requests.exceptions.RequestException as rexc:
            logging.error(f"Exception occurred: {str(rexc)}. Could not determine the content-type of the {url}.", exc_info=True)
            return None
