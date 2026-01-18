from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "MindDeck"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "postgresql+asyncpg://minddeck_user:minddeck_password@localhost:5432/minddeck_db"
    database_url_sync: str = "postgresql://minddeck_user:minddeck_password@localhost:5432/minddeck_db"

    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    google_cloud_api_key: Optional[str] = None
    tts_language: str = "ru"

    redis_url: Optional[str] = "redis://localhost:6379/0"

    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    max_upload_size: int = 10485760
    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
