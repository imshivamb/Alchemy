from typing import Dict, Any, Optional, Callable
import httpx
import asyncio
from .message_broker import MessageBroker
from ..schemas.events import ServiceEvent, ServiceType, EventType
from ..config.settings import get_settings

class ServiceBridge:
    """
    Handles communication between services
    """
    def __init__(self):
        self.settings = get_settings()
        self.message_broker = MessageBroker()
        self.event_handlers: Dict[EventType, Callable] = {}
        
    async def initialize(self):
        """
        Initialize service bridge and set up event handlers
        """
        await self.setup_event_handlers()
        await self.message_broker.subscribe_to_events(
            ServiceType.DJANGO,
            self.handle_event
        )
        await self.message_broker.subscribe_to_events(
            ServiceType.FASTAPI,
            self.handle_event
        )
        
    async def send_to_service(self, 
        target: ServiceType,
        endpoint: str,
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Send request to specific service
        """
        base_url = (
            self.settings.DJANGO_BASE_URL
            if target == ServiceType.DJANGO
            else self.settings.FASTAPI_BASE_URL
        )
        
        async with httpx.AsyncClient(timeout=self.settings.REQUEST_TIMEOUT) as client:
            response = await client.request(
                method,
                f"{base_url}/{endpoint}",
                json=data,
                headers={
                    "X-Service-Key": self.settings.SERVICE_SECRET_KEY
                }
            )
            response.raise_for_status()
            return response.json()
        
    async def emit_event(self, event_type: EventType, source: ServiceType,target: ServiceType, payload: Dict[str, Any], user_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """
        Emit event to other services
        """
        event = ServiceEvent(
            event_type=event_type,
            source=source,
            target=target,
            payload=payload,
            user_id=user_id,
            correlation_id=correlation_id
        )
        await self.message_broker.publish_event(event)
        
    async def handle_event(self, event: ServiceEvent):
        """
        Handle incoming events
        """
        if event.event_type in self.event_handlers:
            await self.event_handlers[event.event_type](event)
            
    def register_handler(
        self,
        event_type: EventType,
        handler: Callable
    ):
        """
        Register event handler
        """
        self.event_handlers[event_type] = handler