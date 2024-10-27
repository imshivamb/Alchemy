from shared.communication.service_bridge import ServiceBridge
from shared.schemas.events import ServiceType, EventType
from django.conf import settings

class DjangoServiceIntegration:
    """
    Django service integration handler
    """
    def __init__(self):
        self.service_bridge = ServiceBridge()

    async def initialize(self):
        await self.service_bridge.initialize()
        self.setup_handlers()

    def setup_handlers(self):
        """
        Setup event handlers for Django service
        """
        self.service_bridge.register_handler(
            EventType.AI_TASK_UPDATE,
            self.handle_ai_task_update
        )
        self.service_bridge.register_handler(
            EventType.WEBHOOK_RECEIVED,
            self.handle_webhook_received
        )
    async def notify_workflow_update(
        self,
        workflow_id: str,
        status: str,
        user_id: str
    ):
        """
        Notify other services about workflow updates
        """
        await self.bridge.emit_event(
            EventType.WORKFLOW_UPDATE,
            ServiceType.DJANGO,
            ServiceType.FASTAPI,
            {
                'workflow_id': workflow_id,
                'status': status
            },
            user_id=user_id
        )