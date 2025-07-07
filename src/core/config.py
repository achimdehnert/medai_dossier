"""Application configuration settings."""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "MedAI Dossier"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/medai_dossier"
    TEST_DATABASE_URL: str = "postgresql://user:password@localhost/medai_dossier_test"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # File Storage
    UPLOAD_DIRECTORY: str = "data/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".docx", ".xlsx", ".csv", ".json"
    ]
    
    # HTA Configuration
    SUPPORTED_HTA_FRAMEWORKS: List[str] = [
        "AMCP",
        "EUnetHTA", 
        "G-BA",
        "NICE",
        "HAS"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # External APIs (if needed)
    CLINICALTRIALS_GOV_API: Optional[str] = None
    EMA_API_KEY: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
