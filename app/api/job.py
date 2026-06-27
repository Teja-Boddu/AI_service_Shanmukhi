from fastapi import APIRouter

from app.schemas.job_request import JobRequest
from app.services.job_service import JobService

router = APIRouter(
    prefix="/job",
    tags=["Job Matching"],
)

job_service = JobService()


@router.post("")
def upload_job(
    request: JobRequest,
):

    result = job_service.process_job(

        job_description=request.job_description,

        top_k=request.top_k,

        filters=request.filters,

    )

    return result