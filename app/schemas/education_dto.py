from pydantic import BaseModel


class EducationDTO(BaseModel):

    degree: str = ""

    institution: str = ""

    specialization: str = ""

    start_year: str = ""

    end_year: str = ""

    cgpa: str = ""