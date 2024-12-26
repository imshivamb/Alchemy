from fastapi import APIRouter, Depends, HTTPException, File, BackgroundTasks, Request
from typing import List, Dict, Optional, Any
from fastapi_app.services.integrations.slack.slack_service import SlackService
from fastapi_app.services.integrations.slack.types import (
    SlackMessage,
    FileUpload,
    ChannelCreate,
    MessageBlock,
    SlackEventType,
    SlackEvent
)

from fastapi_app.core.auth import get_current_user

router = APIRouter()
slack_service = SlackService()

@router.post("/message")
async def send_message(
    message: SlackMessage,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send a message to Slack"""
    try:
        result = await slack_service.send_message(current_user["user_id"], message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/channels")
async def create_channel(
    channel: ChannelCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a slack channel"""
    try:
        result = await slack_service.create_channel(current_user["user_id"], channel)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/files")
async def upload_file(
    file: FileUpload,
    current_user: dict = Depends(get_current_user)
):
    """Upload a file to Slack"""
    try:
        result = await slack_service.upload_file(current_user["user_id"], file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/messages/{channel}/{message_ts}")
async def update_message(
    channel: str,
    message_ts: str,
    message: SlackMessage,
    blocks: Optional[List[MessageBlock]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update a message in Slack"""
    try:
        result = await slack_service.update_message(current_user["user_id"], channel, message_ts, message, blocks)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reactions")
async def add_reaction(
    channel: str,
    timestamp: str,
    emoji: str,
    current_user: dict = Depends(get_current_user)
):
    """Add a reaction to a message in Slack"""
    try:
        result = await slack_service.add_reaction(current_user["user_id"], channel, timestamp, emoji)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/channels/{channel_id}")
async def get_channel_info(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get information about a Slack channel"""
    try:
        result = await slack_service.get_channel_info(current_user["user_id"], channel_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/channels/{channel_id}/invite")
async def invite_to_channel(
    channel_id: str,
    user_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Invite a user to a Slack channel"""
    try:
        result = await slack_service.invite_to_channel(current_user["user_id"], channel_id, user_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/events/subscribe")
async def subscribe_to_events(
    callback_url: str,
    events: List[SlackEventType],
    current_user: dict = Depends(get_current_user)
):
    """Subscribe to Slack events"""
    try:
        result = await slack_service.register_event_subscription(
            user_id=current_user["user_id"],
            callback_url=callback_url,
            events=events
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/webhook")
async def webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle incoming Slack events"""
    try:
        # Verify the request is from Slack
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        signature = request.headers.get("X-Slack-Signature")
        body = await request.body()
        
        if not await slack_service.verify_webhook_signature(
            timestamp,
            signature,
            body.decode()
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle URL verification challenge
        data = await request.json()
        if data.get("type") == "url_verification":
            return {"challenge": data["challenge"]}

        # Process the event
        event = SlackEvent(
            type=data["event"]["type"],
            event_id=data["event_id"],
            team_id=data["team_id"],
            event_time=data["event_time"],
            event_data=data["event"]
        )

        # Process event in background
        background_tasks.add_task(
            slack_service.process_event,
            event=event,
            user_id=data.get("authorizations")[0].get("user_id")
        )

        return {"status": "processing"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))