from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ...oauth.token_manager import TokenManager
from google.oauth2.credentials import Credentials
from fastapi_app.types.oauth_types import OAuthProvider
from django.conf import settings
from .types import (
    CalendarEvent,
    EventStatus,
    CalendarActionType,
    EventTime
)

class CalendarService:
    def __init__(self):
        self.token_manager = TokenManager()
        
    async def get_client(self, user_id: str) -> build:
        """Get Authenticated Google Calendar Client"""
        token = await self.token_manager.get_valid_token(
            user_id,
            OAuthProvider.GOOGLE
        )
        if not token:
            raise ValueError("No valid token found")
        
        return build(
            'calendar',
            'v3',
            credentials=Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
        )
        
    async def create_event(
        self,
        user_id: str,
        event: CalendarEvent,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Create calendar event"""
        try:
            service = await self.get_client(user_id)
            
            event_body = {
                "summary": event.summary,
                "description": event.description,
                "location": event.location,
                "start": {
                    "dateTime": event.time.start_time.isoformat(),
                    "timeZone": event.time.timezone
                },
                "end": {
                    "dateTime": event.time.end_time.isoformat(),
                    "timeZone": event.time.timezone
                }
            }
            if event.attendees:
                event_body["attendees"] = [
                    {
                        "email": attendee.email,
                        "optional": attendee.optional
                    }
                    for attendee in event.attendees
                ]
                
            if event.reminders:
                event_body["reminders"] = {
                    'useDefault': False,
                    'overrides': [
                        {
                            'method': reminder.method,
                            'minutes': reminder.minutes
                        }
                        for reminder in event.reminders
                    ]
                }

            if event.recurrence:
                event_body["recurrence"] = event.recurrence

            if event.conference_data:
                event_body["conferenceData"] = {
                    'createRequest': {
                        'requestId': f"{user_id}-{datetime.utcnow().timestamp()}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                }
            
            if event.color_id:
                event_body["colorId"] = event.color_id
                
            created_event = service.events().insert(
                calendarId=calendar_id,
                body=event_body,
                conferenceDataVersion=1 if event.conference_data else 0,
                sendUpdates="all" if event.attendees else "none"
            ).execute()
            
            return self._parse_event(created_event)
        
        except HttpError as e:
            raise Exception(f"Failed to create event: {e}")

    async def update_event(
        self,
        user_id: str,
        event_id: str,
        event: CalendarEvent,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Update calendar event"""
        try:
            service = await self.get_client(user_id)
            
            existing_event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            event_body = {
                **existing_event,
                "summary": event.summary,
                "description": event.description,
                "location": event.location,
                "start": {
                    "dateTime": event.time.start_time.isoformat(),
                    "timeZone": event.time.timezone or existing_event["start"].get("timeZone")
                },
                "end": {
                    "dateTime": event.time.end_time.isoformat(),
                    "timeZone": event.time.timezone or existing_event["end"].get("timeZone")
                }
            }
            
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_body,
                sendUpdates="all" if event.attendees else "none"
            ).execute()
            
            return self._parse_event(updated_event)
        
        except HttpError as e:
            raise Exception(f"Failed to update event: {e}")
        
    async def delete_event(
        self,
        user_id: str,
        event_id: str,
        calendar_id: str = "primary"
    ) -> None:
        """Delete calendar event"""
        try:
            service = await self.get_client(user_id)
            
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates="all"
            ).execute()
            
        except HttpError as e:
            raise Exception(f"Failed to delete event: {e}")
        
    async def get_events(
        self,
        user_id: str,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10,
        order_by: str = "startTime",
        q: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get calendar events"""
        try:
            service = await self.get_client(user_id)
            
            if not time_min:
                time_min = datetime.utcnow()
                
            if not time_max:
                time_max = time_min + timedelta(days=30)
            
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() if time_min else None,
                timeMax=time_max.isoformat() if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy=order_by,
                q=q
            ).execute()
            
            return [self._parse_event(event) for event in events_result.get("items", [])]
        
        except HttpError as e:
            raise Exception(f"Failed to get events: {e}")
        
    async def watch_calendar(
        self,
        user_id: str,
        channel_id: str,
        webhook_url: str,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Setup calendar push notifications"""
        try:
            service = await self.get_client(user_id)
            
            channel_body = {
                'id': channel_id,
                'type': 'web_hook',
                'address': webhook_url
            }
            
            response = service.events().watch(
                calendarId=calendar_id,
                body=channel_body
            ).execute()
            
            return {
                'channel_id': response['id'],
                'resource_id': response['resourceId'],
                'expiration': response['expiration']
            }
        
        except HttpError as e:
            raise Exception(f"Failed to watch calendar: {e}")
        
    def _parse_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google Calendar event into structured format"""
        return {
            'id': event['id'],
            'summary': event.get('summary', ''),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'end': event['end'].get('dateTime', event['end'].get('date')),
            'status': event.get('status', ''),
            'html_link': event.get('htmlLink', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', ''),
            'attendees': event.get('attendees', []),
            'organizer': event.get('organizer', {}),
            'recurrence': event.get('recurrence', []),
            'conference_data': event.get('conferenceData', None)
        }
            
