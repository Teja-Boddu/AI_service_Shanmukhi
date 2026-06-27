from typing import Optional

from fastapi import APIRouter, Query

from app.services.job_service import JobService


router = APIRouter(
    prefix="/job",
    tags=["Job Matching"],
)

job_service = JobService()


@router.post("")
def upload_job(

    job_description: str,

    top_k: int = Query(
        default=5,
        ge=1,
        le=50,
    ),

    location: Optional[str] = Query(
        default=None,
    ),

):

    result = job_service.match_job(

        job_description=job_description,

        top_k=top_k,

        filters={
            "location": location,
        }
        if location
        else None,

    )

    return {

        "message": "Matching Completed",

        "job": result["job"].model_dump(),

        "total_candidates": result["total_candidates"],

        "retrieved_candidates": result["retrieved"],

        "top_k": result["returned"],

        "matches": result["matches"],

    }