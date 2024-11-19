from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal   
from datetime import datetime
from enum import Enum

class EventStatus(str, Enum):
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"

class CalendarActionType(str, Enum):
    CREATE_EVENT = "create_event"
    UPDATE_EVENT = "update_event"
    DELETE_EVENT = "delete_event"
    GET_EVENTS = "get_events"
    WATCH_EVENTS = "watch_events"

class Attendee(BaseModel):
    email: str
    optional: bool = False
    response_status: Optional[str] = None

class EventReminder(BaseModel):
    method: Literal["email", "popup"] = "popup"
    minutes: int = 30

class EventTime(BaseModel):
    start_time: datetime
    end_time: datetime
    timezone: Optional[str] = None

class CalendarEvent(BaseModel):
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    time: EventTime
    attendees: Optional[List[Attendee]] = None
    reminders: Optional[List[EventReminder]] = None
    recurrence: Optional[List[str]] = None  # RRULE strings
    conference_data: Optional[Dict[str, Any]] = None
    color_id: Optional[str] = None

