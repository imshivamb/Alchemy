from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ServiceType(Enum):
    DJANGO = "django"
    FASTAPI = "fastapi"
    REDIS = "redis"
    
class EventType(Enum):
    WORKFLOW_UPDATE = "workflow_update"
    AI_TASK_UPDATE = "ai_task_update"
    WEBHOOK_RECEIVED = "webhook_received"
    STATE_CHANGE = "state_change"
    ERROR = "error"
    
class ServiceEvent(BaseModel):
    """
    Base event schema for service communication
    """
    event_type: EventType
    source: ServiceType
    target: ServiceType
    timestamp: datetime = datetime.utcnow()
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None