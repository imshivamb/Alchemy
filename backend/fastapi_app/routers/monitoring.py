from fastapi import APIRouter
from ..services.monitoring import WebhookMonitoring
from datetime import datetime

router = APIRouter()
monitoring = WebhookMonitoring()

@router.get("/metrics")
async def get_webhook_metrics():
    """
    Get webhook processing metrics
    """
    return monitoring.get_metrics()

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }