from sentence_transformers import SentenceTransformer

from app.core.logging import logger
from app.schemas.resume_dto import ResumeDTO


class EmbeddingService:
    """
    Generates semantic embeddings using BAAI/BGE-M3.
    The model is loaded only once.
    """

    _model = None

    def __init__(self):

        if EmbeddingService._model is None:

            logger.info("Loading BGE-M3 embedding model...")

            EmbeddingService._model = SentenceTransformer(
                "BAAI/bge-m3"
            )

            logger.info("BGE-M3 model loaded successfully.")

        self.model = EmbeddingService._model

    def build_embedding_text(self, resume):

        education = "\n".join(
            f"{e.degree} {e.specialization} {e.institution}"
            for e in resume.education
        )

        experience = "\n".join(
        f"{e.company} {e.designation} {e.description}"
        for e in resume.experience
    )

        projects = "\n".join(
            f"{p.title} {p.description} {' '.join(p.technologies)}"
            for p in resume.projects
        )

        certifications = "\n".join(
            f"{c.name} {c.issuer} {c.year}"
            for c in resume.certifications
        )

        text = f"""
    Candidate:
    {resume.candidate_name}

    Experience:
    {resume.total_experience}

    Skills:
    {' '.join(resume.skills)}

    Education:
    {education}

    Experience Details:
    {experience}

    Projects:
    {projects}

    Certifications:
    {certifications}
    """

        return text.strip()
    
    def build_job_text(
    self,
    job,
    ):

        return f"""
    Title:
    {job.title}

    Skills:
    {' '.join(job.skills)}

    Responsibilities:
    {' '.join(job.responsibilities)}

    Qualifications:
    {' '.join(job.qualifications)}

    Nice To Have:
    {' '.join(job.nice_to_have)}

    Experience:
    {job.experience}

    Education:
    {job.education}
    """
    def build_job_embedding_text(
    self,
    job,
) -> str:

        return f"""
    Job Title:
    {job.title}

    Company:
    {job.company}

    Location:
    {job.location}

    Employment Type:
    {job.employment_type}

    Experience:
    {job.experience}

    Education:
    {job.education}

    Skills:
    {' '.join(job.skills)}

    Responsibilities:
    {' '.join(job.responsibilities)}

    Qualifications:
    {' '.join(job.qualifications)}

    Nice To Have:
    {' '.join(job.nice_to_have)}
    """.strip()


    def generate_job_embedding(
    self,
    job,
    ):

        text = self.build_job_text(job)

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def generate_embedding(
        self,
        resume: ResumeDTO,
    ) -> list[float]:
        """
        Generate embedding vector.
        """

        embedding_text = self.build_embedding_text(
            resume
        )

        embedding = self.model.encode(
            embedding_text,
            normalize_embeddings=True,
        )

        return embedding.tolist()