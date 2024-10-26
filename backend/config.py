from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TASK_TTL: int = 86400  # 24 hours in seconds

    class Config:
        env_file = ".env"

settings = Settings()
