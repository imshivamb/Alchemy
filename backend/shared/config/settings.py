from pydantic_settings import BaseSettings
from functools import lru_cache

class ServiceSettings(BaseSettings):
    """
    Shared settings for service communication
    """
    DJANGO_BASE_URL: str = "http://localhost:8000"
    FASTAPI_BASE_URL: str = "http://localhost:8001"
    
     # Service security
    SERVICE_SECRET_KEY: str = "your-service-secret-key"
    
    # Timeouts
    REQUEST_TIMEOUT: int = 30
    LONG_POLLING_TIMEOUT: int = 60
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return ServiceSettings()