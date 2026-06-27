# from concurrent.futures import ProcessPoolExecutor, as_completed
# from pathlib import Path
# import traceback

# from app.core.config import settings
# from app.core.logging import logger

# from app.services.zip_service import ZipService
# from app.services.llm_service import LLMService
# from app.services.embedding_service import EmbeddingService
# from app.services.mongodb_service import MongoDBService

# from app.utils.hash import generate_hash
# from app.utils.parser import process_single_resume


# def process_upload(job_id: str):

#     logger.info("=" * 60)
#     logger.info(f"Started Upload Job : {job_id}")
#     logger.info("=" * 60)

#     mongo = MongoDBService()

#     llm = LLMService()

#     embedding_service = EmbeddingService()

#     processed = 0

#     failed = 0

#     try:

#         mongo.update_job_status(
#             job_id,
#             "PROCESSING",
#         )

#         zip_path = (
#             Path(settings.UPLOAD_DIR)
#             / f"{job_id}.zip"
#         )

#         if not zip_path.exists():

#             raise FileNotFoundError(
#                 f"{zip_path} not found."
#             )

#         resumes = ZipService.extract(
#             zip_path,
#             job_id,
#         )

#         total_files = len(resumes)

#         logger.info(
#             f"Found {total_files} resumes."
#         )

#         mongo.update_progress(
#             job_id,
#             total_files=total_files,
#         )

#         with ProcessPoolExecutor() as executor:

#             futures = [

#                 executor.submit(
#                     process_single_resume,
#                     resume_path,
#                 )

#                 for resume_path in resumes

#             ]

#             for future in as_completed(futures):

#                 try:

#                     parsed_resume = future.result()

#                     raw_text = parsed_resume["raw_text"]

#                     file_name = parsed_resume["file_name"]

#                     logger.info(
#                         f"Processing : {file_name}"
#                     )

#                     file_hash = generate_hash(
#                         raw_text
#                     )

#                     if mongo.resume_exists(
#                         file_hash
#                     ):

#                         logger.warning(
#                             f"Duplicate Resume : {file_name}"
#                         )

#                         processed += 1

#                         mongo.update_progress(
#                             job_id,
#                             processed_files=processed,
#                         )

#                         continue

#                     resume = llm.extract_resume(
#                         raw_text
#                     )

#                     resume.file_name = file_name

#                     resume.file_hash = file_hash

#                     resume.raw_text = raw_text

#                     logger.info(
#                         f"Generating Embedding : {file_name}"
#                     )

#                     embedding = (
#                         embedding_service.generate_embedding(
#                             resume
#                         )
#                     )

#                     mongo.save_resume(

#                         job_id=job_id,

#                         resume=resume,

#                         embedding=embedding,

#                     )

#                     processed += 1

#                     mongo.update_progress(

#                         job_id,

#                         processed_files=processed,

#                     )

#                     logger.info(
#                         f"Completed : {file_name}"
#                     )

#                 except Exception as e:

#                     failed += 1

#                     traceback.print_exc()

#                     logger.exception(e)

#                     mongo.update_progress(

#                         job_id,

#                         failed_files=failed,

#                     )

#         mongo.update_job_status(

#             job_id,

#             "COMPLETED",

#         )

#         logger.info(
#             "=" * 60
#         )

#         logger.info(
#             f"Upload Completed : {job_id}"
#         )

#         logger.info(
#             "=" * 60
#         )

#     except Exception as e:

#         traceback.print_exc()

#         logger.exception(e)

#         mongo.update_job_status(

#             job_id,

#             "FAILED",

#         )


# def parse_all_resumes(resume_paths):

#     parsed_resumes = []

#     with ProcessPoolExecutor(max_workers=4) as executor:

#         futures = [
#             executor.submit(
#                 process_single_resume,
#                 path,
#             )
#             for path in resume_paths
#         ]

#         for future in as_completed(futures):
#             parsed_resumes.append(
#                 future.result()
#             )

#     return parsed_resumes


# def extract_resume(
#     parsed_resume,
# ):

#     llm = LLMService()

#     raw_text = parsed_resume["raw_text"]

#     resume = llm.extract_resume(
#         raw_text
#     )

#     resume.file_name = parsed_resume["file_name"]

#     resume.file_hash = generate_hash(
#         raw_text
#     )

#     resume.raw_text = raw_text

#     return resume


# def save_resume(
#     mongo,
#     embedding_service,
#     job_id,
#     resume,
# ):

#     embedding = (
#         embedding_service.generate_embedding(
#             resume
#         )
#     )

#     mongo.save_resume(
#         job_id,
#         resume,
#         embedding,
#     )









from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)

from pathlib import Path
import threading
import traceback

from app.core.config import settings
from app.core.logging import logger

from app.services.zip_service import ZipService
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.mongodb_service import MongoDBService

from app.utils.hash import generate_hash
from app.utils.parser import process_single_resume


# ---------------------------------------------------------
# Thread Local LLM
# (One Gemma client per thread)
# ---------------------------------------------------------

_thread_local = threading.local()


def get_llm():

    if not hasattr(_thread_local, "llm"):

        logger.info(
            "Initializing Gemma for worker thread..."
        )

        _thread_local.llm = LLMService()

    return _thread_local.llm


# ---------------------------------------------------------
# Stage 1
# Parallel Resume Parsing
# ---------------------------------------------------------

def parse_all_resumes(
    resume_paths,
):

    parsed_resumes = []

    with ProcessPoolExecutor(
        max_workers=4,
    ) as executor:

        futures = [

            executor.submit(
                process_single_resume,
                path,
            )

            for path in resume_paths

        ]

        for future in as_completed(
            futures
        ):

            try:

                parsed_resumes.append(
                    future.result()
                )

            except Exception as e:

                logger.exception(e)

    return parsed_resumes


# ---------------------------------------------------------
# Stage 2
# Gemma Extraction
# ---------------------------------------------------------

def extract_resume(
    parsed_resume,
):

    llm = get_llm()

    raw_text = parsed_resume["raw_text"]

    file_name = parsed_resume["file_name"]

    logger.info(
        f"Running Gemma : {file_name}"
    )

    resume = llm.extract_resume(
        raw_text
    )

    resume.file_name = file_name

    resume.file_hash = generate_hash(
        raw_text
    )

    resume.raw_text = raw_text

    return resume


# ---------------------------------------------------------
# Stage 3
# Embedding + Mongo
# ---------------------------------------------------------

def save_resume(
    mongo,
    embedding_service,
    job_id,
    resume,
):

    if mongo.resume_exists(
        resume.file_hash
    ):

        logger.warning(
            f"Duplicate Resume : {resume.file_name}"
        )

        return False

    logger.info(
        f"Generating Embedding : {resume.file_name}"
    )

    embedding = (
        embedding_service.generate_embedding(
            resume
        )
    )

    mongo.save_resume(

        job_id=job_id,

        resume=resume,

        embedding=embedding,

    )

    return True


# =========================================================
# Main Upload Pipeline
# =========================================================
def process_upload(
    job_id: str,
):
    logger.info("=" * 60)
    logger.info(f"Started Upload Job : {job_id}")
    logger.info("=" * 60)

    mongo = MongoDBService()

    embedding_service = EmbeddingService()

    processed = 0
    failed = 0

    try:

        # -----------------------------------------
        # Update Job Status
        # -----------------------------------------

        mongo.update_job_status(
            job_id,
            "PROCESSING",
        )

        zip_path = (
            Path(settings.UPLOAD_DIR)
            / f"{job_id}.zip"
        )

        if not zip_path.exists():

            raise FileNotFoundError(
                f"{zip_path} not found."
            )

        # -----------------------------------------
        # Extract ZIP
        # -----------------------------------------

        resumes = ZipService.extract(
            zip_path,
            job_id,
        )

        total_files = len(
            resumes
        )

        logger.info(
            f"Found {total_files} resumes."
        )

        mongo.update_progress(
            job_id,
            total_files=total_files,
        )

        # =========================================
        # Stage 1
        # Parallel Resume Parsing
        # =========================================

        parsed_resumes = parse_all_resumes(
            resumes
        )

        logger.info(
            f"Successfully parsed {len(parsed_resumes)} resumes."
        )

        # =========================================
        # Stage 2
        # Parallel Gemma Extraction
        # =========================================

        with ThreadPoolExecutor(
            max_workers=2,
        ) as executor:

            futures = {

                executor.submit(
                    extract_resume,
                    parsed_resume,
                ): parsed_resume

                for parsed_resume
                in parsed_resumes

            }

            for future in as_completed(
                futures
            ):

                try:

                    resume = future.result()

                    inserted = save_resume(

                        mongo,

                        embedding_service,

                        job_id,

                        resume,

                    )

                    if inserted:

                        processed += 1

                    else:

                        processed += 1

                    mongo.update_progress(

                        job_id,

                        processed_files=processed,

                    )

                    logger.info(
                        f"Completed : {resume.file_name}"
                    )

                except Exception as e:

                    failed += 1

                    traceback.print_exc()

                    logger.exception(e)

                    mongo.update_progress(

                        job_id,

                        failed_files=failed,

                    )

        # =========================================
        # Finish
        # =========================================

        mongo.update_job_status(

            job_id,

            "COMPLETED",

        )

        logger.info("=" * 60)

        logger.info(
            f"Upload Completed : {job_id}"
        )

        logger.info("=" * 60)

    except Exception as e:

        traceback.print_exc()

        logger.exception(e)

        mongo.update_job_status(

            job_id,

            "FAILED",

        )