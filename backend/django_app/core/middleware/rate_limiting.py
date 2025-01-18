from django.http import HttpResponseTooManyRequests
from django.conf import settings
from redis_service.rate_limiting.api_rate_limiter import APIRateLimiter
import asyncio
import functools

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = APIRateLimiter()
        
    def __call__(self, request):
        # Skip rate limiting for excluded paths
        if self._should_skip_rate_limiting(request):
            return self.get_response(request)
            
        # Get user identifier
        user_id = self._get_user_identifier(request)
        
        # Get action type based on path
        action_type = self._get_action_type(request)
        
        try:
            # Run rate limit check in async context
            is_allowed = asyncio.run(self.rate_limiter.check_rate_limit(
                user_id=user_id,
                action_type=action_type,
                plan_type=self._get_user_plan(request)
            ))
            
            if not is_allowed:
                return HttpResponseTooManyRequests("Rate limit exceeded")
                
            return self.get_response(request)
            
        except Exception as e:
            # Log the error but allow request to proceed
            print(f"Rate limiting error: {str(e)}")
            return self.get_response(request)
            
    def _should_skip_rate_limiting(self, request):
        """Skip rate limiting for certain paths or methods"""
        EXCLUDED_PATHS = [
            '/admin/',
            '/auth/login/',
            '/auth/register/'
        ]
        return any(request.path.startswith(path) for path in EXCLUDED_PATHS)
        
    def _get_user_identifier(self, request):
        """Get user ID or IP address for rate limiting"""
        if request.user.is_authenticated:
            return str(request.user.id)
        return request.META.get('REMOTE_ADDR', 'anonymous')
        
    def _get_action_type(self, request):
        """Map request path to action type for rate limiting"""
        if request.path.startswith('/api/v1/ai/'):
            return 'ai_process'
        elif request.path.startswith('/workflows/'):
            return 'workflow_execution'
        return 'default'
        
    def _get_user_plan(self, request):
        """Get user's subscription plan"""
        if request.user.is_authenticated:
            # Add logic to get user's plan
            return getattr(request.user, 'plan_type', 'free')
        return 'free'