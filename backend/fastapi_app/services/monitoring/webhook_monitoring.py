
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum
from redis_service.base import BaseRedis

class WebhookMetricPeriod(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

class WebhookMetrics(BaseModel):
    total_webhooks: int = 0
    active_webhooks: int = 0
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    average_response_time: float = 0
    deliveries_per_minute: float = 0
    status_codes: Dict[str, int] = {}
    error_types: Dict[str, int] = {}
    retry_count: int = 0

class WebhookMonitoring(BaseRedis):
    def __init__(self):
        super().__init__()
        self.metrics_key = "webhook_metrics:"
        self.delivery_key = "webhook_delivery:"
        
    async def track_delivery(
        self,
        webhook_id: str,
        delivery_id: str,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        error: Optional[str] = None,
        retry_count: Optional[int] = None
    ):
        """Track a webhook delivery for metrics"""
        try:
            # Get current metrics
            metrics = await self.get_current_metrics()
            
            # Update basic metrics
            metrics.total_deliveries += 1
            
            if error:
                metrics.failed_deliveries += 1
                metrics.error_types[error] = metrics.error_types.get(error, 0) + 1
            else:
                metrics.successful_deliveries += 1
                
            if status_code:
                status_range = f"{status_code // 100}xx"
                metrics.status_codes[status_range] = (
                    metrics.status_codes.get(status_range, 0) + 1
                )
                
            if response_time:
                total_time = (
                    metrics.average_response_time * (metrics.total_deliveries - 1) +
                    response_time
                )
                metrics.average_response_time = total_time / metrics.total_deliveries
                
            if retry_count:
                metrics.retry_count += retry_count
                
            # Store metrics
            await self.save_metrics(metrics)
            
            # Store delivery data for time-series analysis
            await self._store_delivery_data(
                webhook_id,
                delivery_id,
                status_code,
                response_time,
                error,
                retry_count
            )
            
        except Exception as e:
            print(f"Error tracking webhook metrics: {str(e)}")
            
    async def get_current_metrics(self) -> WebhookMetrics:
        """Get current webhook metrics"""
        try:
            metrics_data = await self.get_data(self.metrics_key)
            return WebhookMetrics(**(metrics_data or {}))
        except Exception:
            return WebhookMetrics()
            
    async def get_metrics_by_period(
        self,
        period: WebhookMetricPeriod,
        webhook_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get metrics for a specific time period"""
        if not start_time:
            start_time = datetime.utcnow() - self._get_period_delta(period)
        if not end_time:
            end_time = datetime.utcnow()
            
        deliveries = await self._get_deliveries_in_period(
            start_time,
            end_time,
            webhook_id
        )
        return self._calculate_period_metrics(deliveries)
        
    async def get_webhook_health(self, webhook_id: str) -> Dict[str, Any]:
        """Get health metrics for a specific webhook"""
        try:
            # Get recent deliveries
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            deliveries = await self._get_deliveries_in_period(
                start_time,
                end_time,
                webhook_id
            )
            
            metrics = self._calculate_period_metrics(deliveries)
            
            # Calculate health score
            total = metrics["total_deliveries"]
            if total == 0:
                health_score = 100  # No deliveries = healthy
            else:
                success_rate = metrics["successful_deliveries"] / total * 100
                avg_response_time = metrics["average_response_time"]
                retry_rate = metrics["retry_count"] / total * 100
                
                # Weight factors
                health_score = (
                    success_rate * 0.6 +  # 60% weight on success rate
                    (100 - min(avg_response_time / 1000 * 10, 100)) * 0.2 +  # 20% weight on response time
                    (100 - retry_rate) * 0.2  # 20% weight on retry rate
                )
                
            return {
                "health_score": round(health_score, 2),
                "status": "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "unhealthy",
                "metrics": metrics
            }
            
        except Exception as e:
            print(f"Error calculating webhook health: {str(e)}")
            return {
                "health_score": 0,
                "status": "unknown",
                "error": str(e)
            }
            
    async def _store_delivery_data(
        self,
        webhook_id: str,
        delivery_id: str,
        status_code: Optional[int],
        response_time: Optional[float],
        error: Optional[str],
        retry_count: Optional[int]
    ):
        """Store delivery data for time-series analysis"""
        delivery_data = {
            "webhook_id": webhook_id,
            "delivery_id": delivery_id,
            "status_code": status_code,
            "response_time": response_time,
            "error": error,
            "retry_count": retry_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.zadd(
            f"{self.delivery_key}timeline",
            {delivery_id: datetime.utcnow().timestamp()}
        )
        await self.set_data(
            f"{self.delivery_key}{delivery_id}",
            delivery_data,
            expires=86400 * 30  # 30 days
        )
        
    async def _get_deliveries_in_period(
        self,
        start_time: datetime,
        end_time: datetime,
        webhook_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get deliveries within a time period"""
        delivery_ids = await self.zrangebyscore(
            f"{self.delivery_key}timeline",
            min=start_time.timestamp(),
            max=end_time.timestamp()
        )
        
        deliveries = []
        for d_id in delivery_ids:
            delivery_data = await self.get_data(f"{self.delivery_key}{d_id}")
            if delivery_data:
                if not webhook_id or delivery_data["webhook_id"] == webhook_id:
                    deliveries.append(delivery_data)
                    
        return deliveries
        
    def _calculate_period_metrics(
        self,
        deliveries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate metrics for a set of deliveries"""
        metrics = {
            "total_deliveries": len(deliveries),
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "average_response_time": 0,
            "status_codes": {},
            "error_types": {},
            "retry_count": 0
        }
        
        total_response_time = 0
        
        for delivery in deliveries:
            if delivery.get("error"):
                metrics["failed_deliveries"] += 1
                error_type = delivery["error"]
                metrics["error_types"][error_type] = (
                    metrics["error_types"].get(error_type, 0) + 1
                )
            else:
                metrics["successful_deliveries"] += 1
                
            if delivery.get("status_code"):
                status_range = f"{delivery['status_code'] // 100}xx"
                metrics["status_codes"][status_range] = (
                    metrics["status_codes"].get(status_range, 0) + 1
                )
                
            if delivery.get("response_time"):
                total_response_time += delivery["response_time"]
                
            if delivery.get("retry_count"):
                metrics["retry_count"] += delivery["retry_count"]
                
        if metrics["total_deliveries"] > 0:
            metrics["average_response_time"] = (
                total_response_time / metrics["total_deliveries"]
            )
            
        return metrics
        
    def _get_period_delta(self, period: WebhookMetricPeriod) -> timedelta:
        """Get timedelta for a period"""
        deltas = {
            WebhookMetricPeriod.HOUR: timedelta(hours=1),
            WebhookMetricPeriod.DAY: timedelta(days=1),
            WebhookMetricPeriod.WEEK: timedelta(weeks=1),
            WebhookMetricPeriod.MONTH: timedelta(days=30)
        }
        return deltas[period]