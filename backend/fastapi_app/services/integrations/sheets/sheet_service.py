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
        try:
            service = await self.get_client(user_id)
            
            request = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueRenderOption=render_option
            )
            response = request.execute()
            
            return response.get('values', [])
        except HttpError as error:
            raise Exception(f"Failed to get values: {error}")
    
    async def update_values(
        self,
        user_id: str,
        spreadsheet_id: str,
        range_data: RangeData,
        input_option: ValueInputOption = ValueInputOption.USER_ENTERED
    ) -> Dict[str, Any]:
        """Update values in spreadsheet"""
        try:
            service = await self.get_client(user_id)
            
            body = {
                'values': range_data.values
            }
            
            request = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_data.range,
                valueInputOption=input_option,
                body=body
            )
            response = request.execute()
            
            return {
                'updated_cells': response['updatedCells'],
                'updated_rows': response['updatedRows'],
                'updated_columns': response['updatedColumns'],
                'updated_range': response['updatedRange']
            }
            
        except HttpError as error:
            raise Exception(f"Failed to update values: {error}")
    
    async def append_values(
        self,
        user_id: str,
        spreadsheet_id: str,
        range_data: RangeData,
        input_option: ValueInputOption = ValueInputOption.USER_ENTERED
    ) -> Dict[str, Any]:
        """Append values to spreadsheet"""
        try:
            service = await self.get_client(user_id)
            
            body = {
                'values': range_data.values
            }
            
            request = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_data.range,
                valueInputOption=input_option,
                body=body
            )
            response = request.execute()
            
            return {
                'updates': {
                    'spreadsheet_id': response['spreadsheetId'],
                    'updated_range': response['updates']['updatedRange'],
                    'updated_rows': response['updates']['updatedRows'],
                    'updated_columns': response['updates']['updatedColumns'],
                }
            }
            
        except HttpError as error:
            raise Exception(f"Failed to append values: {error}")
    
    async def clear_values(
        self,
        user_id: str,
        spreadsheet_id: str,
        range: str
    ) -> Dict[str, Any]:
        """Clear values in spreadsheet"""
        try:
            service = await self.get_client(user_id)
            
            request = service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range,
                body={}
            )
            response = request.execute()
            
            return {
                'cleared_range': response['clearedRange']
            }
            
        except HttpError as error:
            raise Exception(f"Failed to clear values: {error}")

    async def get_spreadsheet_metadata(
        self,
        user_id: str,
        spreadsheet_id: str
    ) -> Dict[str, Any]:
        """Get spreadsheet metadata"""
        try:
            service = await self.get_client(user_id)
            
            request = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            )
            response = request.execute()
            
            return {
                'spreadsheet_id': response['spreadsheetId'],
                'title': response['properties']['title'],
                'locale': response['properties']['locale'],
                'time_zone': response['properties']['timeZone'],
                'sheets': [
                    {
                        'sheet_id': sheet['properties']['sheetId'],
                        'title': sheet['properties']['title'],
                        'index': sheet['properties']['index'],
                        'sheet_type': sheet['properties']['sheetType'],
                        'grid_properties': sheet['properties'].get('gridProperties', {})
                    }
                    for sheet in response['sheets']
                ]
            }
            
        except HttpError as error:
            raise Exception(f"Failed to get metadata: {error}")

    async def batch_update(
        self,
        user_id: str,
        spreadsheet_id: str,
        requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform batch updates on spreadsheet"""
        try:
            service = await self.get_client(user_id)
            
            body = {
                'requests': requests
            }
            
            request = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            )
            response = request.execute()
            
            return response
            
        except HttpError as error:
            raise Exception(f"Failed to perform batch update: {error}")
    
