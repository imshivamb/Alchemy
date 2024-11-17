
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict
from datetime import datetime
from fastapi_app.services.monitoring.webhook_monitoring import (
    WebhookMonitoring,
    WebhookMetricPeriod
)
from ....core.auth import get_current_user, require_admin

router = APIRouter()
monitoring = WebhookMonitoring()

@router.get("/metrics/current")
async def get_current_metrics(
    current_user: dict = Depends(require_admin)
):
    """Get current webhook metrics"""
    try:
        return await monitoring.get_current_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/period")
async def get_metrics_by_period(
    period: WebhookMetricPeriod,
    webhook_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: dict = Depends(require_admin)
):
    """Get metrics for a specific time period"""
    try:
        metrics = await monitoring.get_metrics_by_period(
            period,
            webhook_id,
            start_time,
            end_time
        )
        return {
            "period": period,
            "start_time": start_time or (datetime.utcnow() - monitoring._get_period_delta(period)),
            "end_time": end_time or datetime.utcnow(),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/{webhook_id}/health")
async def get_webhook_health(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get health metrics for a specific webhook"""
    try:
        return await monitoring.get_webhook_health(webhook_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/{webhook_id}/metrics")
async def get_webhook_metrics(
    webhook_id: str,
    period: WebhookMetricPeriod = WebhookMetricPeriod.DAY,
    current_user: dict = Depends(get_current_user)
):
    """Get metrics for a specific webhook"""
    try:
        return await monitoring.get_metrics_by_period(
            period,
            webhook_id=webhook_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))