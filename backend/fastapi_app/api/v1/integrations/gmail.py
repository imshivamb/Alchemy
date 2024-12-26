from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr
from fastapi_app.services.integrations.gmail.gmail_service import GmailService
from fastapi_app.services.integrations.gmail.types import EmailMessage, GmailActionType, EmailAttachment, GmailFilter
from fastapi_app.core.auth import get_current_user

router = APIRouter( tags=["Gmail"])
gmail_service = GmailService()

class SendEmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    body_type: Literal["text", "html"] = "text"
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[EmailAttachment]] = None
    
class ReadEmailsRequest(BaseModel):
    filter: GmailFilter
    max_results: int = 10
    
class UpdateLabelsRequest(BaseModel):
    message_id: str
    add_labels: Optional[List[str]] = None
    remove_labels: Optional[List[str]] = None

class WatchRequest(BaseModel):
    topic_name: str
    label_ids: Optional[List[str]] = None
    
    
@router.post("/send")
async def send_email(
    request: SendEmailRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send an email"""
    try:
        message = EmailMessage(**request.dict())
        result = await gmail_service.send_email(
            user_id=current_user["user_id"],
            message=message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/read")
async def read_emails(
    request: ReadEmailsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Read emails"""
    try:
        result = await gmail_service.read_emails(
            user_id=current_user["user_id"],
            filter_params=request.filter,
            max_results=request.max_results
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/messages/{message_id}')
async def get_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a message by ID"""
    try:
        result = await gmail_service.get_message(
            user_id=current_user["user_id"],
            message_id=message_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/labels")
async def update_labels(
    request: UpdateLabelsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update labels for a message"""
    try:
        result = await gmail_service.update_labels(
            user_id=current_user["user_id"],
            message_id=request.message_id,
            add_labels=request.add_labels,
            remove_labels=request.remove_labels
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/labels")
async def get_labels(
    current_user: dict = Depends(get_current_user)
):
    """Get labels"""
    try:
        result = await gmail_service.list_labels(user_id=current_user["user_id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/watch")
async def watch_mailbox(
    request: WatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Setup Gmail Push Notifications"""
    try:
        result = await gmail_service.watch_mailbox(
            user_id=current_user["user_id"],
            topic_name=request.topic_name,
            label_ids=request.label_ids
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/watch/stop")
async def stop_watching(
    current_user: dict = Depends(get_current_user)
):
    """Stop Gmail push notifications"""
    try:
        await gmail_service.stop_watching(
            user_id=current_user["user_id"]
        )
        return {"message": "Watching stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
