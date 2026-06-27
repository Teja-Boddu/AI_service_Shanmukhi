# from concurrent.futures import ThreadPoolExecutor

# from app.background.process_upload import process_upload

# executor = ThreadPoolExecutor(max_workers=2)


# def run_upload(job_id: str):

#     executor.submit(
#         process_upload,
#         job_id,
#     )
from concurrent.futures import ThreadPoolExecutor
import traceback

from app.core.logging import logger
from app.background.process_upload import process_upload

executor = ThreadPoolExecutor(max_workers=2)


def run_upload(job_id: str):

    logger.info(f"Submitting upload job: {job_id}")

    future = executor.submit(process_upload, job_id)

    try:
        future.add_done_callback(
            lambda f: logger.exception(f.exception()) if f.exception() else logger.info(f"Job {job_id} finished")
        )
    except Exception:
        traceback.print_exc()