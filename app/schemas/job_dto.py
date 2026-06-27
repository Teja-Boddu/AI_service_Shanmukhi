from pydantic import BaseModel


class JobDTO(BaseModel):

    title: str = ""

    company: str = ""

    location: str = ""

    employment_type: str = ""

    experience: str = ""

    education: str = ""

    skills: list[str] = []

    responsibilities: list[str] = []

    qualifications: list[str] = []

    nice_to_have: list[str] = []