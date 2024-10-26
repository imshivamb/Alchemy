import aioredis
from typing import Optional, Any
import json

class BaseRedis:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)
        
    async def set_data(self, key: str, value: Any, expires: Optional[int] = None):
        """Store data in Redis"""
        await self.redis.set(key, json.dumps(value), ex=expires)
        
    async def get_data(self, key: str) -> Optional[Any]:
        """Retrieve data from Redis"""
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def delete_data(self, key: str):
        """Delete data from Redis"""
        await self.redis.delete(key)
        