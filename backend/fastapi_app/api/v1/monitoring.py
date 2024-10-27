from fastapi import APIRouter, Query, HTTPException, Depends
from ...services.monitoring import WebhookMonitoring
from datetime import datetime, timedelta
from shared.monitoring.metrics_collector import MetricsCollector
from shared.monitoring.system_monitor import SystemMonitor
from shared.monitoring.application_monitor import ApplicationMonitor
from ...core.auth import get_current_user

router = APIRouter()
monitoring = WebhookMonitoring()
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor()
app_monitor = ApplicationMonitor()

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
    
@router.get("/metrics/system")
async def get_system_metrics(
    start_time: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(hours=1)),
    end_time: datetime = Query(default_factory=lambda: datetime.utcnow()),
    interval: int = Query(default=300),
    current_user: dict = Depends(get_current_user)
):
    """
    Get system metrics for the specified time range
    """
    try:
        metrics = {}
        
        if not current_user.get('is_staff'):
            raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
        
        # CPU metrics
        metrics['cpu'] = await metrics_collector.get_metrics(
            "system.cpu.utilization",
            start_time,
            end_time,
            interval
        )
        
        # Memory metrics
        metrics['memory'] = await metrics_collector.get_metrics(
            "system.memory.usage",
            start_time,
            end_time,
            interval
        )
        
        # Disk metrics
        metrics['disk'] = await metrics_collector.get_metrics(
            "system.disk.usage",
            start_time,
            end_time,
            interval
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch system metrics: {str(e)}"
        )

@router.get("/metrics/application")
async def get_application_metrics(
    start_time: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(hours=1)),
    end_time: datetime = Query(default_factory=lambda: datetime.utcnow()),
    interval: int = Query(default=300)
):
    """
    Get application metrics for the specified time range
    """
    try:
        metrics = {}
        
        # Request metrics
        metrics['requests'] = {
            'count': await metrics_collector.get_metrics(
                "app.request.count",
                start_time,
                end_time,
                interval
            ),
            'response_time': await metrics_collector.get_metrics(
                "app.request.response_time",
                start_time,
                end_time,
                interval
            )
        }
        
        # Workflow metrics
        metrics['workflows'] = {
            'count': await metrics_collector.get_metrics(
                "workflow.execution.count",
                start_time,
                end_time,
                interval
            ),
            'execution_time': await metrics_collector.get_metrics(
                "workflow.execution.time",
                start_time,
                end_time,
                interval
            )
        }
        
        # Error metrics
        metrics['errors'] = await metrics_collector.get_metrics(
            "app.error.count",
            start_time,
            end_time,
            interval
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch application metrics: {str(e)}"
        )