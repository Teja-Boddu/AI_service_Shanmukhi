from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.schemas.resume_dto import ResumeDTO


class ResumeService:
    """
    Handles all Resume database operations.
    """

    @staticmethod
    def get_by_hash(
        db: Session,
        file_hash: str,
    ) -> Resume | None:

        return (
            db.query(Resume)
            .filter(Resume.file_hash == file_hash)
            .first()
        )

    @staticmethod
    def resume_exists(
        db: Session,
        file_hash: str,
    ) -> bool:

        return (
            ResumeService.get_by_hash(
                db,
                file_hash,
            )
            is not None
        )

    @staticmethod
    def save_resume(
        db: Session,
        job_id,
        resume: ResumeDTO,
    ) -> Resume:

        db_resume = Resume(

            job_id=job_id,

            file_name=resume.file_name,

            file_hash=resume.file_hash,

            candidate_name=resume.candidate_name,

            email=resume.email,

            phone=resume.phone,

            raw_text=resume.raw_text,

            structured_json=resume.model_dump(
                exclude={
                    "file_name",
                    "file_hash",
                    "raw_text",
                }
            ),

            processing_status="COMPLETED",
        )

        db.add(db_resume)

        db.commit()

        db.refresh(db_resume)

        return db_resume
    @staticmethod
    def get_resume(
        db: Session,
        resume_id,
    ) -> Resume | None:

        return (
            db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    @staticmethod
    def update_resume(
        db: Session,
        resume: Resume,
        **kwargs,
    ) -> Resume:

        for key, value in kwargs.items():

            setattr(
                resume,
                key,
                value,
            )

        db.commit()

        db.refresh(resume)

        return resume

    @staticmethod
    def delete_resume(
        db: Session,
        resume: Resume,
    ):

        db.delete(resume)

        db.commit()