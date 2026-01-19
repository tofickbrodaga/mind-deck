from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "MindDeck"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = Field(..., env="DATABASE_URL")
    database_url_sync: str = Field(..., env="DATABASE_URL_SYNC")

    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    google_cloud_api_key: Optional[str] = Field(None, env="GOOGLE_CLOUD_API_KEY")
    tts_language: str = Field("ru", env="TTS_LANGUAGE")

    redis_url: Optional[str] = Field(None, env="REDIS_URL")

    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field("logs/app.log", env="LOG_FILE")

    max_upload_size: int = 10485760
    upload_dir: str = Field("uploads", env="UPLOAD_DIR")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
