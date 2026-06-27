from pydantic import BaseModel, Field


class ProjectDTO(BaseModel):

    title: str = ""

    description: str = ""

    technologies: list[str] = Field(default_factory=list)