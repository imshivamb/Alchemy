from redis_service.base import BaseRedis
from fastapi_app.types.oauth_types import OAuthToken, OAuthProvider
from typing import Optional
from datetime import datetime
from fastapi_app.services.oauth.google import GoogleOAuth

class TokenManager(BaseRedis):
    def __init__(self):
        super().__init__()
        self.token_prefix = "oauth_token:"
        
    async def store_token(self, user_id: str, token: OAuthToken, provider: OAuthProvider):
        """Store OAuth Token"""
        key = f"{self.token_prefix}{provider}:{user_id}"
        await self.set_data(key, token.dict())

    async def get_valid_token(
        self,
        user_id: str,
        provider: OAuthProvider
    ) -> Optional[OAuthToken]:
        """Get valid OAuth token, refresh if needed"""
        key = f"{self.token_prefix}{provider}:{user_id}"
        token_data = await self.get_data(key)
        
        if not token_data:
            return None
            
        token = OAuthToken(**token_data)
        
        # Check if token needs refresh
        if datetime.utcnow() >= token.expires_at:
            if provider == OAuthProvider.GOOGLE:
                oauth = GoogleOAuth()
                new_token = await oauth.refresh_token(token.refresh_token)
                if new_token:
                    await self.store_token(user_id, provider, new_token)
                    return new_token
            return None
            
        return token