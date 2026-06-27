from pydantic import BaseModel, Field

from app.schemas.education_dto import EducationDTO
from app.schemas.experience_dto import ExperienceDTO
from app.schemas.project_dto import ProjectDTO
from app.schemas.certification_dto import CertificationDTO


class ResumeDTO(BaseModel):

    file_name: str = ""

    file_hash: str = ""

    raw_text: str = ""

    candidate_name: str = ""

    email: str = ""

    phone: str = ""

    location: str = ""

    linkedin: str = ""

    github: str = ""

    portfolio: str = ""

    total_experience: str = ""

    skills: list[str] = Field(default_factory=list)

    education: list[EducationDTO] = Field(default_factory=list)

    experience: list[ExperienceDTO] = Field(default_factory=list)

    projects: list[ProjectDTO] = Field(default_factory=list)

    certifications: list[CertificationDTO] = Field(default_factory=list)