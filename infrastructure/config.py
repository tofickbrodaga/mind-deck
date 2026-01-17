from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "MindDeck"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://minddeck_user:minddeck_password@localhost:5432/minddeck_db"
    database_url_sync: str = "postgresql://minddeck_user:minddeck_password@localhost:5432/minddeck_db"

    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # External APIs
    google_cloud_api_key: Optional[str] = None
    tts_language: str = "ru"

    # Redis
    redis_url: Optional[str] = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # File Upload
    max_upload_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
