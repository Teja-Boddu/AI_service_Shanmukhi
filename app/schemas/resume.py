from pydantic import BaseModel


class ParsedResume(BaseModel):
    file_name: str
    text: str