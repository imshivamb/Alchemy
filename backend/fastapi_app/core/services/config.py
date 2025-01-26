# fastapi_app/core/services/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend folder
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

# Set Django settings module BEFORE the Settings class
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.core.settings')

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:8000", "http://localhost:3000, https://webhook.site/"]
    
    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Use the same secret key as Django
    SECRET_KEY: str = os.getenv("SECRET_KEY", "django-insecure-$8gmzi6rxj_9x@$ffh9b3mx5ha9kv@h-d506w%vwmx06jon5c")
    
    class Config:
        case_sensitive = True
        env_file = str(env_path)
        # Add this to allow extra fields
        extra = 'allow'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()