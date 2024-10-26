import aioredis
from typing import Optional, Any, Callable
import json
from datetime import datetime
import asyncio
import uuid

class BaseRedis:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self._subscribers = {}
        
    # Basic Redis Operations
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
        
    #Caching
    async def set_cache(self, key: str, value: Any, expires: int = 3600):
        """Cache data with expiration"""
        cache_data = {
            'data': value,
            'cached_at': datetime.utcnow().isoformat(),
        }
        await self.set_data(f"cache:{key}", cache_data, expires)
        
    async def get_cached_data(self, key: str) -> Optional[Any]:
        """GEt Cached Data"""
        data = await self.get_data(f"cache:{key}")
        return data['data'] if data else None
    
    #Rate Limiting
    async def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """Check rate limit for a key"""
        current = await self.redis.incr(f"ratelimit: {key}")
        if current == 1:
            await self.redis.expire(f"ratelimit: {key}", window)
        return current <= limit
    
    #PubSub Operations
    async def publish(self, channel: str, message: Any) -> None:
        """Publish message to channel"""
        await self.redis.publish(channel, json.dumps(message))
        
    async def subscribe(self, channel: str, callback: Callable):
        """Subscribe to channel with callback"""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)
        
        async def listener():
            await self.pubsub.subscribe(channel)
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = json.loads(message['data'])
                    for cb in self._subscribers[channel]:
                        await cb(data)
                await asyncio.sleep(0.01)
                
        asyncio.create_task(listener())
        
    # Queue Operations
    async def push_to_queue(self, queue_name: str, item: Any):
        """Push item to queue"""
        await self.redis.lpush(queue_name, json.dumps(item))
        
    async def pop_from_queue(self, queue_name: str) -> Optional[Any]:
        """Pop item from queue"""
        data = await self.redis.rpop(f"queue:{queue_name}")
        return json.loads(data) if data else None
    
    #Task status management
    async def update_task_progress(self, task_id: str, progress: int, status: str = "processing"):
        """Update task progress"""
        task_data = {
            'progress': progress,
            'status': status,
            'updated_at': datetime.utcnow().isoformat(),
        }
        await self.set_data(f"task_progress:{task_id}", task_data)
        await self.publish('task_updates', {
                'task_id': task_id,
                **task_data
            })
        
    # Distributed Locking
    async def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        """Acquire distributed lock"""
        lock_id = str(uuid.uuid4())
        acquired = await self.redis.set(
            f"lock:{lock_name}",
            lock_id,
            ex=timeout,
            nx=True
        )
        return bool(acquired)

    async def release_lock(self, lock_name: str):
        """Release distributed lock"""
        await self.redis.delete(f"lock:{lock_name}")