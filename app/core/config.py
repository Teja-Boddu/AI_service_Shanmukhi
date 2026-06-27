from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ----------------------------
    # App
    # ----------------------------
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    # ----------------------------
    # Uploads
    # ----------------------------
    UPLOAD_DIR: str
    EXTRACT_DIR: str

    # ----------------------------
    # LLM
    # ----------------------------
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str


    # ----------------------------
    # Logging
    # ----------------------------
    LOG_LEVEL: str

    UPLOAD_DIR: str
    EXTRACT_DIR: str


    MONGODB_URL: str

    MONGODB_DATABASE: str

    MONGODB_COLLECTION: str


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()

