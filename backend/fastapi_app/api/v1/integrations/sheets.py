from  fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from fastapi_app.services.integrations.sheets.sheet_service import SheetsService
from services.integrations.sheets.types import (
    SpreadsheetCreate,
    RangeData,
    ValueInputOption,
    ValueRenderOption
)
from core.auth import get_current_user

router = APIRouter(prefix="/sheets", tags=["Google-Sheets"])
sheets_service = SheetsService()

@router.post("/spreadsheets")
async def create_spreadsheet(spreadsheet: SpreadsheetCreate, current_user: dict = Depends(get_current_user)):
    """Create a new Spreadsheet"""
    try:
        result = await sheets_service.create_spreadsheet(
            user_id=current_user['user_id'],
            spreadsheet=spreadsheet
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/spreadsheets/{spreadsheet_id}/values/{range}")
async def get_values(
    spreadsheet_id: str,
    range: str,
    render_option: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE,
    current_user: dict = Depends(get_current_user)
):
    """Get values from a spreadsheet range"""
    try:
        values = await sheets_service.get_values(
            user_id=current_user["user_id"],
            spreadsheet_id=spreadsheet_id,
            range=range,
            render_option=render_option
        )
        return {"values": values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
@router.put("/spreadsheets/{spreadsheet_id}/values")
async def update_values(
    spreadsheet_id: str,
    range_data: RangeData,
    input_option: ValueInputOption = ValueInputOption.USER_ENTERED,
    current_user: dict = Depends(get_current_user)
):
    """Update values in a spreadsheet range"""
    try:
        result = await sheets_service.update_values(
            user_id=current_user["user_id"],
            spreadsheet_id=spreadsheet_id,
            range_data=range_data,
            input_option=input_option
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/spreadsheets/{spreadsheet_id}/values:append")
async def append_values(
    spreadsheet_id: str,
    range_data: RangeData,
    input_option: ValueInputOption = ValueInputOption.USER_ENTERED,
    current_user: dict = Depends(get_current_user)
):
    """Append values to a spreadsheet"""
    try:
        result = await sheets_service.append_values(
            user_id=current_user["user_id"],
            spreadsheet_id=spreadsheet_id,
            range_data=range_data,
            input_option=input_option
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spreadsheets/{spreadsheet_id}/values/{range}:clear")
async def clear_values(
    spreadsheet_id: str,
    range: str,
    current_user: dict = Depends(get_current_user)
):
    """Clear values in a spreadsheet range"""
    try:
        result = await sheets_service.clear_values(
            user_id=current_user["user_id"],
            spreadsheet_id=spreadsheet_id,
            range=range
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spreadsheets/{spreadsheet_id}")
async def get_spreadsheet_metadata(
    spreadsheet_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get spreadsheet metadata"""
    try:
        result = await sheets_service.get_spreadsheet_metadata(
            user_id=current_user["user_id"],
            spreadsheet_id=spreadsheet_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spreadsheets/{spreadsheet_id}:batchUpdate")
async def batch_update(
    spreadsheet_id: str,
    requests: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """Perform batch updates on a spreadsheet"""
    try:
        result = await sheets_service.batch_update(
            user_id=current_user["user_id"],
            spreadsheet_id=spreadsheet_id,
            requests=requests
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))