from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Drive2"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_CACHE_DB: int = 0
    REDIS_CELERY_DB: int = 1

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Qdrant
    QDRANT_URL: str
    QDRANT_COLLECTION_NAME: str = "drive2_files"
    QDRANT_VECTOR_SIZE: int = 768

    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str = "drive2-files"
    MINIO_SECURE: bool = False

    # LINE
    LINE_CHANNEL_SECRET: str
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_LIFF_ID: str

    # Gemini AI
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    ALLOWED_ORIGINS: List[str] = ["*"]

    # File Processing
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: str = "pdf,doc,docx,txt,jpg,jpeg,png,gif,mp4,zip"
    THUMBNAIL_SIZE: int = 300
    OCR_LANGUAGE: str = "eng+tha"

    # Rate Limiting
    GEMINI_RPM_LIMIT: int = 15
    GEMINI_DAILY_LIMIT: int = 1500

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
