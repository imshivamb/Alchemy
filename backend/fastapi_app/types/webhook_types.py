from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl

class WebhookMethod(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

class WebhookStatus(str, Enum):
    ACTIVE ='active'
    INACTIVE = 'inactive'
    FAILED = 'failed'
    DELETED = 'deleted'
    PENDING = 'pending'
    
class RetryStrategy(BaseModel):
    max_retries: int = Field(default=3, ge=0)
    initial_interval: int = Field(default=60,description="Seconds")
    max_interval: int = Field(default=3600,description="Seconds")
    multiplier: float = Field(default=2.0, description="Exponential Backoff")
    
    
class WebhookConfig(BaseModel):
    url: str
    method: WebhookMethod = WebhookMethod.POST
    headers: Dict[str, str] = {}
    authentication: Optional[Dict[str, str]] = None
    retry_strategy: RetryStrategy = Field(default_factory=RetryStrategy)
    timeout: int = Field(default=30, ge=1, le=300)
    verify_ssl: bool = True
    
class WebhookSecret(BaseModel):
    key: str
    header_name: str = "X-Webhook-Signature"
    hash_algorithm: str = "sha256"

