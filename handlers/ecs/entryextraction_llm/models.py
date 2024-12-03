from pydantic import BaseModel, AnyUrl
from typing import Optional


class DocumentWithUrl(BaseModel):
    
    url: AnyUrl
    client_id: str

class DocumentWithId(BaseModel):

    textextraction_id: str
    client_id: str


class InputStructure(BaseModel):

    client_id: str
    url: AnyUrl = None
    af_id: int = None
    project_id: int = None
    text_extraction_id: str = None
    entryextraction_id: str = None
    callback_url: Optional[str] = None
