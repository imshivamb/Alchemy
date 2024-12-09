from typing import Dict, Any, List, Optional, Union
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ...oauth.token_manager import TokenManager
from fastapi_app.types.oauth_types import OAuthProvider
from google.oauth2.credentials import Credentials
from django.conf import settings
from .types import (
    ValueInputOption,
    ValueRenderOption,
    RangeData,
    SpreadsheetCreate
)

class SheetsService:
    def __init__(self):
        self.token_manager = TokenManager()
        
    async def get_client(self, user_id: str) -> build:
        """Get Authenticated Google Sheets Client"""
        token = await self.token_manager.get_valid_token(
            user_id,
            OAuthProvider.GOOGLE
        )
        
        if not token:
            raise ValueError("No valid token found")
        return build(
            'sheets',
            'v4',
            credentials=Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
        )
        
    async def create_spreadsheet(
        self,
        user_id: str,
        spreadsheet: SpreadsheetCreate
    ) -> Dict[str, Any]:
        """Create a new spreadsheet"""
        try:
            service = await self.get_client(user_id)
            
            sheet_properties = [
                {
                    'properties': {
                        'title': sheet.title,
                        'sheetType': sheet.sheet_type,
                        'gridProperties': {
                            'rowCount': sheet.row_count,
                            'columnCount': sheet.column_count
                        }
                    }
                }
                for sheet in spreadsheet.sheets
            ]
            
            spreadsheet_body = {
                'properties': {
                    'title': spreadsheet.title
                },
                'sheets': sheet_properties
            }
            
            request = service.spreadsheets().create(body=spreadsheet_body)
            response = request.execute()
            
            return {
                    'spreadsheet_id': response['spreadsheetId'],
                    'title': response['properties']['title'],
                    'sheets': [
                        {
                            'sheet_id': sheet['properties']['sheetId'],
                            'title': sheet['properties']['title']
                        }
                        for sheet in response['sheets']
                    ],
                    'spreadsheet_url': response['spreadsheetUrl']
                }
        except Exception as e:
            raise Exception(f"Failed to create spreadsheet: {e}")
        
    async def get_values(self,
                         user_id: str,
                         spreadsheet_id: str,
                         range: str,
                         render_option: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE) -> List[List[Any]]:
        """Read values from spreadsheet"""
        
        
    
