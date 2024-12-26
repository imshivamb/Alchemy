from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi_app.services.integrations.calendar.calendar_service import CalendarService
from fastapi_app.services.integrations.calendar.types import (
    CalendarEvent,
    EventTime,
    Attendee,
    EventReminder
)
from fastapi_app.core.auth import get_current_user

router = APIRouter( tags=["Google Calendar"])
calendar_service = CalendarService()

class CreateEventRequest(CalendarEvent):
    calendar_id: Optional[str] = 'primary'
    
class UpdateEventRequest(CalendarEvent):
    calendar_id: Optional[str] = 'primary'
    
class WatchRequest(BaseModel):
    channel_id: str
    webhook_url: str
    calendar_id: Optional[str] = 'primary'
    
@router.post("/events")
async def create_event(
    request: CreateEventRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new calendar event"""
    try:
        result = await calendar_service.create_event(
            user_id=current_user['user_id'],
            event=request,
            calendar_id=request.calendar_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/events/{event_id}")
async def update_event(
    event_id: str,
    request: UpdateEventRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing calendar event"""
    try:
        result = await calendar_service.update_event(
            user_id=current_user['user_id'],
            event=request,
            event_id=event_id,
            calendar_id=request.calendar_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    calendar_id: Optional[str] = 'primary',
    current_user: dict = Depends(get_current_user)
):
    """Delete an existing calendar event"""
    try:
        await calendar_service.delete_event(
            user_id=current_user['user_id'],
            event_id=event_id,
            calendar_id=calendar_id
        )
        return {"message": "Event deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/events")
async def list_events(
    calendar_id: Optional[str] = 'primary',
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user),
    q: Optional[str] = None,
    max_results: int = Query(default=10, le=100)
):
    """List all calendar events"""
    try:
        result = await calendar_service.get_events(
            user_id=current_user['user_id'],
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            q=q,    
            max_results=max_results
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/watch")
async def watch_events(
    request: WatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Setup calendar push notifications"""
    try:
        result = await calendar_service.watch_calendar(
            user_id=current_user['user_id'],
            channel_id=request.channel_id,
            webhook_url=request.webhook_url,
            calendar_id=request.calendar_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
