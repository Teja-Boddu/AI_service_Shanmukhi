from pydantic import BaseModel


class ExperienceDTO(BaseModel):

    company: str = ""

    designation: str = ""

    start_date: str = ""

    end_date: str = ""

    duration: str = ""

    description: str = ""