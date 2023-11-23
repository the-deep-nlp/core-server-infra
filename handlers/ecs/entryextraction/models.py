from pydantic import BaseModel, AnyUrl
from typing import List, Union, Optional


class DocumentWithUrl(BaseModel):
    
    url: AnyUrl
    client_id: str

class DocumentWithId(BaseModel):

    textextraction_id: str
    client_id: str


class InputStructure(BaseModel):

    client_id: str
    url: AnyUrl = None
    text_extraction_id: str = None
    entryextraction_id: str = None
    callback_url: Optional[str] = None
