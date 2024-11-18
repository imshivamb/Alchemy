from typing import List, Optional, Dict, Any, Literal
from pydantic import EmailStr, BaseModel
from enum import Enum

class GmailActionType(Enum):
    SEND_EMAIL = "send_email"
    READ_EMAILS = "read_emails"
    WATCH_MAILBOX = "watch_mailbox"
    UPDATE_LABELS = "update_labels"
    
class EmailAttachment(BaseModel):
    filename: str
    content_type: str
    data: str  # Base64 encoded string
    
class EmailMessage(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    body_type: Literal["text", "html"] = "text"
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[EmailAttachment]] = None
    
class GmailFilter(BaseModel):
    from_: Optional[str] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    has_attachment: Optional[bool] = None
    label: Optional[str] = None
    after: Optional[str] = None
    before: Optional[str] = None
