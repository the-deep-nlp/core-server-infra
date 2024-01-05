import random
import timeout_decorator
from deep_parser import TextFromFile, TextFromWeb
from deep_parser.helpers.errors import (
    DocumentProcessingError, 
    ContentTypeError
    )
random.seed = 42

@timeout_decorator.timeout(5 * 60)
def extract_pdf(url, lead_id):
    try:
        parser = TextFromFile(url=url, from_web=True)
        text, _ = parser.extract_text(output_format="list")
        if text:
            print(f"lead-id: {lead_id}, type: pdf. correctly processed")
            return text
    except TimeoutError:
        raise TimeoutError
    except (RuntimeError, DocumentProcessingError, Exception) as e:
        raise e


@timeout_decorator.timeout(20)         
def extract_website(url, lead_id): 
    # here some research in text segmentation is needed, because in the html scenario we actually doesn't have
    # layout infos
    try:
        parser = TextFromWeb(url=url)
        text = parser.extract_text(output_format="list")
        parser.close()
        if text:
            print(f"lead-id: {lead_id}, type: website. correctly processed")
            return text
    except TimeoutError:
        raise TimeoutError
    except (RuntimeError, DocumentProcessingError, Exception) as e:
        raise e


def process(url, lead_id):

    if url.endswith(".pdf"):
        print(f"{url} is a PDF!")
        try:
            text = extract_pdf(url, lead_id)
            return text
        except TimeoutError:
            print(f"Timeout error. lead-id: {lead_id}")
        except (RuntimeError, DocumentProcessingError, Exception) as e:
            print(f"Error {e}, lead-id: {lead_id}")
    else:
        try:
            text = extract_website(url, lead_id)
            return text
        except ContentTypeError:
            print(f"ContentType error, lead-id: {lead_id}")
            try:
                text = extract_pdf(url, lead_id)
                return text
            except Exception as e:
                print(f"Error: {e}. lead-id: {lead_id}")
                raise e
        except TimeoutError:
            print(f"Timeout error. lead-id: {lead_id}")
            raise e
        except (RuntimeError, DocumentProcessingError, Exception) as e:
            print(f"Error {e}. lead-id: {lead_id}")
            raise e 
        

