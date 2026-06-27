from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import logger
# from app.database.base import Base
# from app.database.session import engine
from app.api import upload_router
from app.api import (
    upload_router,
    progress_router,
    job_router
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)
app.include_router(upload_router)
app.include_router(progress_router)
app.include_router(job_router)
# @app.on_event("startup")
# def startup():

#     logger.info("Creating database tables...")

#     Base.metadata.create_all(bind=engine)

#     logger.info("Application Started Successfully")


@app.get("/")
def home():

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running"
    }


@app.get("/health")
def health():

    return {
        "status": "Healthy"
    }