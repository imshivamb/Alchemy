# backend/redis_service/exceptions.py

class RedisServiceError(Exception):
    """Base exception for Redis service"""
    pass

class TaskQueueError(RedisServiceError):
    """Raised when there's an error with task queue operations"""
    pass

class StateError(RedisServiceError):
    """Raised when there's an error with state management"""
    pass

class RateLimitExceeded(RedisServiceError):
    """Raised when rate limit is exceeded"""
    pass

class CacheError(RedisServiceError):
    """Raised when there's an error with caching operations"""
    pass