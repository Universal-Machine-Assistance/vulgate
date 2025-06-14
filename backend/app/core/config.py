from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vulgate API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    SQLITE_DB_PATH: str = str(Path(__file__).parent.parent.parent.parent / "db" / "vulgate.db")
    DATABASE_URL: str = f"sqlite:///{SQLITE_DB_PATH}"
    
    # Audio storage
    AUDIO_STORAGE_PATH: str = str(Path(__file__).parent.parent.parent.parent / "static" / "audio")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # RapidAPI for Bhagavad Gita
    RAPIDAPI_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure required directories exist
os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH), exist_ok=True)
os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True) 