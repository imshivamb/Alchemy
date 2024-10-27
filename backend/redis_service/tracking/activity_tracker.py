from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..base import BaseRedis
from ..exceptions import RedisServiceError
import json

class ActivityTracker(BaseRedis):
    """
    Tracks and manages real-time system activities with metrics
    """
    def __init__(self):
        super().__init__()
        self.activity_prefix = "activity:"
        self.metrics_prefix = "metrics:"
        
    async def track_activity(self, activity_type: str, user_id: str, data: Dict[str, Any], context: Optional[Dict] = None):
        """
        Track user or system activity with context
        """
        try:
            activity ={
                'type': activity_type,
                'user_id': user_id,
                'data': data,
                'context': context or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            #Store in recent activity
            await self.push_to_queue(
                f"{self.activity_prefix}recent", activity, max_len=1000
            )
            
            #Store user specific activity
            await self.push_to_queue(f"{self.activity_prefix}user:{user_id}",
                activity,
                max_len=100)
            
            #Update Metrics
            await self._update_metrics(activity_type, user_id)
            
            # Publish activity event
            await self.publish('activity_events', activity)
            
        except Exception as e:
            raise RedisServiceError(f"Failed to track activity: {str(e)}")
        
    async def get_user_activities(self, user_id: str,limit: int = 20,
        activity_type: Optional[str] = None) -> List[Dict]:
        """
        Get user-specific activities with optional filtering
        """
        try:
            activities = await self.redis.lrange(
                f"{self.activity_prefix}user:{user_id}", 0, limit - 1
            )
            parsed_activities = [json.loads(activity) for activity in activities]
            
            if activity_type:
                return [
                    activity for activity in parsed_activities
                    if activity['type'] == activity_type
                ]
                
            return parsed_activities
        
        except Exception as e:
            raise RedisServiceError(f"Failed to get user activities: {str(e)}")
        
    async def _update_metrics(self, activity_type: str, user_id: str):
        """
        Update activity metrics with time-based aggregation
        """
        now = datetime.utcnow()
        
        # Update daily metrics
        day_key = f"{self.metrics_prefix}daily:{now.strftime('%Y-%m-%d')}"
        await self.redis.hincrby(day_key, activity_type, 1)
        await self.redis.hincrby(day_key, f"user:{user_id}", 1)
        
        # Update hourly metrics
        hour_key = f"{self.metrics_prefix}hourly:{now.strftime('%Y-%m-%d:%H')}"
        await self.redis.hincrby(hour_key, activity_type, 1)
        
        # Cleanup old metrics (keep last 30 days)
        await self._cleanup_old_metrics()
        
    async def _cleanup_old_metrics(self):
        """
        Clean up metrics older than 30 days
        """
        cutoff = datetime.utcnow() - timedelta(days=30)
        pattern = f"{self.metrics_prefix}daily:{cutoff.strftime('%Y-%m-%d')}*"
        old_keys = await self.redis.keys(pattern)
        if old_keys:
            await self.redis.delete(*old_keys)