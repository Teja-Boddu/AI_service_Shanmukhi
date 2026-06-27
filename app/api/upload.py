from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.core.config import settings
from app.core.logging import logger

from app.schemas.upload import UploadResponse

from app.services.mongodb_service import MongoDBService

from app.background.resume_processor import run_upload

router = APIRouter(
    prefix="/upload",
    tags=["Resume Upload"],
)


@router.post(
    "",
    response_model=UploadResponse,
)
async def upload_zip(
    file: UploadFile = File(...),
):

    if not file.filename.lower().endswith(".zip"):

        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed.",
        )

    upload_dir = Path(settings.UPLOAD_DIR)

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    mongo = MongoDBService()

    job_id = mongo.create_upload_job()

    zip_path = upload_dir / f"{job_id}.zip"

    with open(
        zip_path,
        "wb",
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    mongo.job_collection.update_one(
        {"job_id": job_id},
        {
            "$set": {
                "zip_file": str(zip_path),
            }
        },
    )

    logger.info(
        f"ZIP saved : {zip_path}"
    )

    run_upload(job_id)

    logger.info(
        f"Background Job Started : {job_id}"
    )

    return UploadResponse(
        job_id=job_id,
        status="PROCESSING",
    )