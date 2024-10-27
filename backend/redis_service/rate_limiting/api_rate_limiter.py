from typing import Dict, Any, Optional
from datetime import datetime
from ..base import BaseRedis
from ..exceptions import RateLimitExceeded
from redis import RedisError

class APIRateLimiter(BaseRedis):
    """
    Manages API rate limiting based on user plans and endpoints
    """
    
    PLAN_LIMITS = {
        'free': {
            'default': {'calls': 100, 'window': 3600},
            'ai_process': {'calls': 50, 'window': 3600},
            'workflow_execution': {'calls': 20, 'window': 3600}
        },
        'premium': {
            'default': {'calls': 1000, 'window': 3600},
            'ai_process': {'calls': 500, 'window': 3600},
            'workflow_execution': {'calls': 200, 'window': 3600}
        },
        'enterprise': {
            'default': {'calls': 10000, 'window': 3600},
            'ai_process': {'calls': 5000, 'window': 3600},
            'workflow_execution': {'calls': 2000, 'window': 3600}
        }
    }
    
    def __init__(self):
        super().__init__()
        self.limit_prefix = "rate_limit:"
        
    async def check_rate_limit(
        self,
        user_id: str,
        action_type: str,
        plan_type: Optional[str] = None
    ) -> bool:
        """
        Check if user has exceeded their rate limit for specific action
        """
        try:
            # Get user's plan if not provided
            if not plan_type:
                plan_type = await self._get_user_plan(user_id)
            
            # Get limit configuration
            plan_config = self.PLAN_LIMITS.get(plan_type, self.PLAN_LIMITS['free'])
            limit_config = plan_config.get(action_type, plan_config['default'])
            
            # Check rate limit
            key = f"{self.limit_prefix}{user_id}:{action_type}"
            is_allowed = await self._check_and_update_limit(
                key,
                limit_config['calls'],
                limit_config['window']
            )
            
            if not is_allowed:
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {action_type}. "
                    f"Limit: {limit_config['calls']} calls per {limit_config['window']} seconds"
                )
            
            # Track usage
            await self._track_usage(user_id, action_type, plan_type)
            
            return True
            
        except RateLimitExceeded:
            raise
        except Exception as e:
            raise RedisError(f"Failed to check rate limit: {str(e)}")
            
    async def _check_and_update_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """
        Check and update rate limit counter
        """
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)
        
        return current <= limit
        
    async def _track_usage(
        self,
        user_id: str,
        action_type: str,
        plan_type: str
    ):
        """
        Track API usage for analytics
        """
        now = datetime.utcnow()
        day_key = f"usage:{now.strftime('%Y-%m-%d')}"
        
        # Track daily usage
        await self.redis.hincrby(day_key, f"{user_id}:{action_type}", 1)
        await self.redis.hincrby(day_key, f"plan:{plan_type}:{action_type}", 1)
        
    async def _get_user_plan(self, user_id: str) -> str:
        """
        Get user's current plan type
        """
        plan = await self.get_data(f"user:{user_id}:plan")
        return plan or 'free'