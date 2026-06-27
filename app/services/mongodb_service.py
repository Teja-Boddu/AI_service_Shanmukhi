from datetime import datetime
from typing import Optional

from pymongo import MongoClient

from app.core.config import settings
from app.core.logging import logger
from app.schemas.resume_dto import ResumeDTO
from app.schemas.job_dto import JobDTO
from datetime import datetime

class MongoDBService:

    _client = None

    def __init__(self):

        if MongoDBService._client is None:

            logger.info("Connecting to MongoDB Atlas...")

            MongoDBService._client = MongoClient(
                settings.MONGODB_URL
            )

            logger.info("MongoDB Connected Successfully.")

        self.client = MongoDBService._client

        # Create the database FIRST
        self.db = self.client[
            settings.MONGODB_DATABASE
        ]

        # Then create collections
        self.resume_collection = self.db[
            "resumes"
        ]

        self.job_collection = self.db[
            "jobs"
        ]

        self.upload_collection = self.db[
            "upload_jobs"
        ]
    # ===================================================
    # Upload Jobs
    # ===================================================

    def create_upload_job(self) -> str:

        import uuid

        job_id = str(uuid.uuid4())

        logger.info("Creating upload job...")
        logger.info(f"Generated Job ID: {job_id}")

        result = self.upload_collection.insert_one(
            {
                "job_id": job_id,
                "status": "PENDING",
                "zip_file": "",
                "total_files": 0,
                "processed_files": 0,
                "failed_files": 0,
                "created_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None,
                "updated_at": datetime.utcnow(),
            }
        )

        logger.info(
            f"Inserted Mongo _id: {result.inserted_id}"
        )

        return job_id

    def get_upload_job(
        self,
        job_id: str,
    ) -> Optional[dict]:

        return self.upload_collection.find_one(
            {
                "job_id": job_id
            }
        )

    def update_job_status(
        self,
        job_id: str,
        status: str,
    ):

        update = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }

        if status == "PROCESSING":

            update["started_at"] = datetime.utcnow()

        elif status == "COMPLETED":

            update["completed_at"] = datetime.utcnow()

        self.upload_collection.update_one(
            {
                "job_id": job_id
            },
            {
                "$set": update
            },
        )

    def update_progress(
        self,
        job_id: str,
        processed_files: int = None,
        failed_files: int = None,
        total_files: int = None,
    ):

        update = {
            "updated_at": datetime.utcnow()
        }

        if processed_files is not None:
            update["processed_files"] = processed_files

        if failed_files is not None:
            update["failed_files"] = failed_files

        if total_files is not None:
            update["total_files"] = total_files

        self.upload_collection.update_one(
            {
                "job_id": job_id
            },
            {
                "$set": update
            },
        )

    # ===================================================
    # Resume APIs
    # ===================================================
    def save_job(
    self,
    job,
    embedding,
    ):

        document = {

            "title": job.title,

            "company": job.company,

            "location": job.location,

            "employment_type": job.employment_type,

            "experience": job.experience,

            "education": job.education,

            "skills": job.skills,

            "responsibilities": job.responsibilities,

            "qualifications": job.qualifications,

            "nice_to_have": job.nice_to_have,

            "embedding": embedding,

            "created_at": datetime.utcnow(),

        }

        result = self.job_collection.insert_one(
            document
        )

        return str(result.inserted_id)
    def resume_exists(
        self,
        file_hash: str,
    ) -> bool:

        return (
            self.resume_collection.find_one(
                {
                    "file_hash": file_hash
                }
            )
            is not None
        )

    def save_resume(
        self,
        job_id: str,
        resume: ResumeDTO,
        embedding: list[float],
    ) -> str:

        document = {

            "job_id": job_id,

            "file_name": resume.file_name,

            "file_hash": resume.file_hash,

            "raw_text": resume.raw_text,

            "candidate_name": resume.candidate_name,

            "email": resume.email,

            "phone": resume.phone,

            "location": resume.location,

            "linkedin": resume.linkedin,

            "github": resume.github,

            "portfolio": resume.portfolio,

            "total_experience": resume.total_experience,

            "skills": resume.skills,

            "education": [
                item.model_dump()
                for item in resume.education
            ],

            "experience": [
                item.model_dump()
                for item in resume.experience
            ],

            "projects": [
                item.model_dump()
                for item in resume.projects
            ],

            "certifications": [
                item.model_dump()
                for item in resume.certifications
            ],

            "embedding_model": "BAAI/bge-m3",

            "embedding": embedding,

            "created_at": datetime.utcnow(),
        }

        result = self.resume_collection.insert_one(
            document
        )

        return str(result.inserted_id)

    def get_all_resumes(
    self,
    filters=None,
    ):
        """
        Fetch resumes with optional filters.
        """

        query = {}

        if filters:

            if filters.get("location"):
                query["location"] = filters["location"]

            if filters.get("experience"):
                query["total_experience"] = filters["experience"]

            if filters.get("skills"):
                query["skills"] = {
                    "$in": filters["skills"]
                }

        return list(
            self.resume_collection.find(query)
        )
    # ===================================================
    # Job APIs
    # ===================================================

    def save_job(
        self,
        job: JobDTO,
        embedding: list[float],
    ) -> str:

        document = {

            "title": job.title,

            "company": job.company,

            "location": job.location,

            "employment_type": job.employment_type,

            "experience": job.experience,

            "education": job.education,

            "skills": job.skills,

            "responsibilities": job.responsibilities,

            "qualifications": job.qualifications,

            "nice_to_have": job.nice_to_have,

            "embedding_model": "BAAI/bge-m3",

            "embedding": embedding,

            "created_at": datetime.utcnow(),
        }

        result = self.job_collection.insert_one(
            document
        )

        return str(result.inserted_id)

    def get_job(
        self,
        job_id: str,
    ):

        return self.job_collection.find_one(
            {
                "_id": job_id
            }
        )

    def get_all_jobs(self):

        return list(
            self.job_collection.find()
        )