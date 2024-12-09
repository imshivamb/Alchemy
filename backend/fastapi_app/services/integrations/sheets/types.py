from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union

class SheetsActionType(str, Enum):
    READ = "read"
    WRITE = "write"
    APPEND = "append"
    CLEAR = "clear"
    CREATE = "create"
    
class ValueInputOption(str, Enum):
    RAW = "raw"
    USER_ENTERED = "user_entered"
    
class ValueRenderOption(str, Enum):
    FORMATTED_VALUE = "formatted_value"
    UNFORMATTED_VALUE = "unformatted_value"
    FORMULA = "formula"
    
class RangeData(BaseModel):
    range: str
    values: List[List[Any]]
    
class SheetProperties(BaseModel):
    title: str
    sheet_type: str = "GRID"
    row_count: int = 1000
    column_count: int = 26

class SpreadsheetCreate(BaseModel):
    title: str
    sheets: List[SheetProperties]
