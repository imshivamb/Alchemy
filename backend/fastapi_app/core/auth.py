from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
from django.conf import settings

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and return user info
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
# Optional: Get current user dependency
async def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """
    Get current user from token
    """
    return token_data