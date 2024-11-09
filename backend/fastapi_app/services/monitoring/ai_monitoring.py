# services/monitoring/ai_monitoring.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel
from redis_service.base import BaseRedis

class AIMetrics(BaseModel):
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0
    requests_per_minute: float = 0
    token_usage: Dict[str, int] = {}
    model_usage: Dict[str, int] = {}
    error_types: Dict[str, int] = {}

class AIMonitoring(BaseRedis):
    def __init__(self):
        super().__init__()
        self.metrics_key = "ai_metrics:"
        
    async def track_request(
        self,
        task_id: str,
        model: str,
        start_time: datetime,
        status: str,
        tokens_used: Optional[int] = None,
        error: Optional[str] = None
    ):
        """Track an AI request for metrics"""
        try:
            metrics = await self.get_current_metrics()
            
            # Update basic metrics
            metrics.total_requests += 1
            if status == "completed":
                metrics.successful_requests += 1
            elif status == "failed":
                metrics.failed_requests += 1
                if error:
                    metrics.error_types[error] = metrics.error_types.get(error, 0) + 1
            
            # Update model usage
            metrics.model_usage[model] = metrics.model_usage.get(model, 0) + 1
            
            # Update token usage if available
            if tokens_used:
                metrics.token_usage[model] = metrics.token_usage.get(model, 0) + tokens_used
            
            # Calculate average response time
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_requests - 1) + response_time)
                / metrics.total_requests
            )
            
            # Update requests per minute
            await self._update_request_rate(metrics)
            
            # Save updated metrics
            await self.save_metrics(metrics)
            
        except Exception as e:
            print(f"Error tracking metrics: {str(e)}")
            
    async def get_current_metrics(self) -> AIMetrics:
        """Get current AI metrics"""
        try:
            metrics_data = await self.get_data(self.metrics_key)
            return AIMetrics(**metrics_data) if metrics_data else AIMetrics()
        except Exception:
            return AIMetrics()
            
    async def save_metrics(self, metrics: AIMetrics):
        """Save metrics to Redis"""
        await self.cache_data(
            self.metrics_key,
            metrics.dict()
        )
        
    async def _update_request_rate(self, metrics: AIMetrics):
        """Update requests per minute calculation"""
        current_time = datetime.utcnow()
        recent_requests = await self.sorted_range_by_score(
            "recent_ai_requests",
            min=int((current_time - timedelta(minutes=1)).timestamp()),
            max=int(current_time.timestamp())
        )
        
        metrics.requests_per_minute = len(recent_requests)
        
        # Add current request to recent requests
        await self.sorted_add(
            "recent_ai_requests",
            {str(current_time.timestamp()): current_time.timestamp()}
        )
        
        # Remove old requests
        await self.sorted_remove_by_score(
            "recent_ai_requests",
            min=0,
            max=int((current_time - timedelta(minutes=1)).timestamp())
        )