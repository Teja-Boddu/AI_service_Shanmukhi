class SearchRequest(BaseModel):

    job_id: str

    top_k: int = 10

    location: str | None = None

    minimum_experience: int | None = None

    required_skills: list[str] = []

    education: str | None = None