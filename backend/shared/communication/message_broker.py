
from typing import Dict, Any, Callable, List
import asyncio
from redis_service.base import BaseRedis
from ..schemas.events import ServiceEvent, ServiceType
from ..config.settings import get_settings

class MessageBroker(BaseRedis):
    """
    Handles inter-service message routing and event distribution
    """
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.subscribers: Dict[str, List[Callable]] = {}
        
    async def publish_event(self, event: ServiceEvent):
        """
        Publish event to appropriate channel
        """
        channel = f"service_events:{event.target.value}"
        await self.publish(channel, event.dict())
        
        # Store event for history
        await self.store_event_history(event)
        
    async def subscribe_to_events(
        self,
        service_type: ServiceType,
        handler: Callable
    ):
        """
        Subscribe to events for specific service
        """
        channel = f"service_events:{service_type.value}"
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(handler)
        
        async def listener():
            await self.pubsub.subscribe(channel)
            while True:
                try:
                    message = await self.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message:
                        event = ServiceEvent(**message['data'])
                        for h in self.subscribers[channel]:
                            await h(event)
                except Exception as e:
                    print(f"Error processing message: {e}")
                await asyncio.sleep(0.1)
                
        asyncio.create_task(listener())
        
    async def store_event_history(self, event: ServiceEvent):
        """
        Store event in history with TTL
        """
        key = f"event_history:{event.correlation_id}"
        await self.set_data(
            key,
            event.dict(),
            expires=86400  # 24 hours
        )