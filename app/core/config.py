from pydantic_settings import BaseSettings
from typing import List, Optional
import json

class Settings(BaseSettings):
    # App
    APP_NAME: str = "TERA AI Editor"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here"
    API_VERSION: str = "v1"
    
    # Database
    DATABASE_URL: str = "postgresql://tera_user:tera_pass@localhost:5432/tera_ai"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_WORKER_CONCURRENCY: int = 4
    
    # Storage
    STORAGE_TYPE: str = "local"
    MAX_UPLOAD_SIZE: int = 1073741824
    ALLOWED_VIDEO_TYPES: List[str] = ["mp4", "mov", "avi", "mkv", "webm"]
    ALLOWED_IMAGE_TYPES: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    
    # JWT
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    ERROR_LOG_FILE: str = "logs/error.log"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
