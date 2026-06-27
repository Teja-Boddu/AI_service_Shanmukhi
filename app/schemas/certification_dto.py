from pydantic import BaseModel


class CertificationDTO(BaseModel):

    name: str = ""

    issuer: str = ""

    year: str = ""