from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OAuthProvider(Enum):
    GOOGLE = "google"
    SLACK = "slack"
    NOTION = "notion"
    
class OAuthTokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    
class OAuthToken(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_at: datetime
    scope: List[str]
