# backend/shared/monitoring/application_monitor.py

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .metrics_collector import MetricsCollector, MetricType

class ApplicationMonitor:
    """
    Monitor application-specific metrics
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        
    async def track_request(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_id: Optional[str] = None
    ):
        """
        Track API request metrics
        """
        tags = {
            "endpoint": endpoint,
            "method": method,
            "status": str(status_code),
        }
        if user_id:
            tags["user_id"] = user_id
            
        # Track request count
        await self.metrics_collector.collect_metric(
            "app.request.count",
            1,
            MetricType.COUNTER,
            tags
        )
        
        # Track response time
        await self.metrics_collector.collect_metric(
            "app.request.response_time",
            response_time,
            MetricType.HISTOGRAM,
            tags
        )
        
    async def track_workflow_execution(
        self,
        workflow_id: str,
        execution_time: float,
        status: str,
        user_id: Optional[str] = None
    ):
        """
        Track workflow execution metrics
        """
        tags = {
            "workflow_id": workflow_id,
            "status": status
        }
        if user_id:
            tags["user_id"] = user_id
            
        # Track execution count
        await self.metrics_collector.collect_metric(
            "workflow.execution.count",
            1,
            MetricType.COUNTER,
            tags
        )
        
        # Track execution time
        await self.metrics_collector.collect_metric(
            "workflow.execution.time",
            execution_time,
            MetricType.HISTOGRAM,
            tags
        )
        
    async def track_error(
        self,
        error_type: str,
        service: str,
        severity: str,
        user_id: Optional[str] = None
    ):
        """
        Track error metrics
        """
        tags = {
            "error_type": error_type,
            "service": service,
            "severity": severity
        }
        if user_id:
            tags["user_id"] = user_id
            
        await self.metrics_collector.collect_metric(
            "app.error.count",
            1,
            MetricType.COUNTER,
            tags
        )