# backend/fastapi_app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:8000", "http://localhost:3000"]
    
    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()