# backend/redis_service/cache/workflow_cache.py

from typing import Dict, Any, Optional
from datetime import datetime
from ..base import BaseRedis
from ..exceptions import CacheError

class WorkflowCache(BaseRedis):
    """
    Manages workflow result caching with versioning
    """
    
    def __init__(self):
        super().__init__()
        self.cache_prefix = "workflow:cache:"
        self.version_prefix = "workflow:version:"
        
    async def cache_result(
        self,
        workflow_id: str,
        result: Dict[str, Any],
        expires: int = 3600
    ):
        """
        Cache workflow execution result with version tracking
        """
        try:
            # Increment version
            version = await self.redis.incr(f"{self.version_prefix}{workflow_id}")
            
            cache_data = {
                'result': result,
                'version': version,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            # Cache the result
            await self.set_data(
                f"{self.cache_prefix}{workflow_id}",
                cache_data,
                expires=expires
            )
            
            # Publish cache update event
            await self.publish('cache_events', {
                'type': 'workflow_cached',
                'workflow_id': workflow_id,
                'version': version
            })
            
        except Exception as e:
            raise CacheError(f"Failed to cache workflow result: {str(e)}")
            
    async def get_cached_result(
        self,
        workflow_id: str,
        check_version: bool = True
    ) -> Optional[Dict]:
        """
        Get cached workflow result with optional version checking
        """
        try:
            cached = await self.get_data(f"{self.cache_prefix}{workflow_id}")
            if not cached:
                return None
                
            if check_version:
                current_version = await self.redis.get(
                    f"{self.version_prefix}{workflow_id}"
                )
                if int(current_version) > cached['version']:
                    return None
                    
            return cached['result']
            
        except Exception as e:
            raise CacheError(f"Failed to get cached result: {str(e)}")
            
    async def invalidate_cache(self, workflow_id: str):
        """
        Invalidate cached workflow result
        """
        try:
            await self.delete_data(f"{self.cache_prefix}{workflow_id}")
            await self.redis.incr(f"{self.version_prefix}{workflow_id}")
            
            # Publish cache invalidation event
            await self.publish('cache_events', {
                'type': 'cache_invalidated',
                'workflow_id': workflow_id
            })
            
        except Exception as e:
            raise CacheError(f"Failed to invalidate cache: {str(e)}")