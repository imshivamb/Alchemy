from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.conf import settings
from fastapi_app.types.oauth_types import OAuthToken

class GoogleOAuth:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
    async def create_auth_url(self) -> str:
        """Create the authorization URL for Google OAuth."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url
    
    async def get_tokens(self, code: str) -> OAuthToken:
        """Exchange the authorization code for tokens."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return OAuthToken(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_type="Bearer",
            expires_at=datetime.utcnow() + timedelta(seconds=credentials.expiry.timestamp() - datetime.utcnow().timestamp()),
            scope=self.scopes
        )
        
    async def refresh_token(self, refresh_token: str) -> Optional[OAuthToken]:
        """Refresh access token"""
        try:
            credentials = Credentials(
                None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )

            credentials.refresh(Request())

            return OAuthToken(
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_type="Bearer",
                expires_at=datetime.utcnow() + timedelta(seconds=credentials.expiry.timestamp() - datetime.utcnow().timestamp()),
                scope=self.scopes
            )
        except RefreshError:
            return None

