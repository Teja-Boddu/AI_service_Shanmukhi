from pydantic import BaseModel


class JobRequest(BaseModel):

    job_description: str

    top_k: int = 5

    filters: dict | None = None