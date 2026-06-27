from fastapi import APIRouter, HTTPException

from app.services.mongodb_service import MongoDBService

router = APIRouter(
    prefix="/progress",
    tags=["Upload Progress"],
)


@router.get("/{job_id}")
def get_progress(job_id: str):

    mongo = MongoDBService()

    job = mongo.get_upload_job(job_id)

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Upload Job not found.",
        )

    total = job.get("total_files", 0)

    processed = job.get("processed_files", 0)

    failed = job.get("failed_files", 0)

    if total == 0:

        progress = 0.0

    else:

        progress = round(
            (processed / total) * 100,
            2,
        )

    return {

        "job_id": job["job_id"],

        "status": job["status"],

        "total_files": total,

        "processed_files": processed,

        "failed_files": failed,

        "remaining_files": max(
            total - processed - failed,
            0,
        ),

        "progress_percentage": progress,

        "created_at": job.get("created_at"),

        "started_at": job.get("started_at"),

        "completed_at": job.get("completed_at"),

        "updated_at": job.get("updated_at"),

    }