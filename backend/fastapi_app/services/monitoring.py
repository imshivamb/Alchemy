from datetime import datetime, timedelta
from typing import Dict, List

class WebhookMonitoring:
    def __init__(self):
        self.metrics = {
            "total_received": 0,
            "total_success": 0,
            "total_failed": 0,
            "average_processing_time": 0,
            "webhooks_per_minute": 0
        }
        self.recent_webhooks = []
        
    def update_metrics(self, task: Dict):
        """Update monitoring metrics"""
        self.metrics["total_received"] += 1
        
        if task["status"] == "completed":
            self.metrics["total_success"] += 1
        elif task["status"] == "failed":
            self.metrics["total_failed"] += 1
            
        if "completed_at" in task:
            start_time = datetime.fromisoformat(task["created_at"])
            end_time = datetime.fromisoformat(task["completed_at"])
            processing_time = (end_time - start_time).total_seconds()
            
            #Calculate Processing Time
            current_avg = self.metrics["average_processing_time"]
            total_processed = self.metrics("total_success") + self.metrics["total_failed"]
            self.metrics["average_processing_time"] = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
            
        # Update rate metrics
        self.recent_webhooks.append(datetime.utcnow())
        self._update_rate_metrics()
        
    def _update_rate_metrics(self):
        """Update webhooks per minute calculation"""
        # Remove webhooks older than 1 minute
        cutoff_time = datetime.utcnow() - timedelta(minutes=1)
        self.recent_webhooks = [
            t for t in self.recent_webhooks if t > cutoff_time
        ]
        
        # Calculate current rate
        self.metrics["webhooks_per_minute"] = len(self.recent_webhooks)

    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return self.metrics