from shared.communication.service_bridge import ServiceBridge
from shared.schemas.events import ServiceType, EventType
from fastapi import FastAPI
from typing import Callable

class FastAPIServiceIntegration:
    """
    FastAPI service integration handler
    """
    def __init__(self, app: FastAPI):
        self.app = app
        self.bridge = ServiceBridge()
        
    async def initialize(self):
        await self.bridge.initialize()
        self.setup_handlers()
        self.setup_middleware()
        
    def setup_handlers(self):
        """
        Setup event handlers for FastAPI service
        """
        self.bridge.register_handler(
            EventType.WORKFLOW_UPDATE,
            self.handle_workflow_update
        )
        
    def setup_middleware(self):
        """
        Setup middleware for service communication
        """
        @self.app.middleware("http")
        async def service_communication_middleware(request, call_next):
            # Verify service requests
            if request.headers.get("X-Service-Key") == self.bridge.settings.SERVICE_SECRET_KEY:
                request.state.is_service_request = True
            response = await call_next(request)
            return response