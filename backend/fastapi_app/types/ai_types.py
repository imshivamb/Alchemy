from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class AIModelType(str, Enum):
    GPT_40_MINI = 'gpt-40-mini'
    GPT_4 = 'gpt-4'
    GPT_35 = 'gpt-3.5-turbo'
    CUSTOM = 'custom'

class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"

class PreprocessorType(str, Enum):
    SUMMARIZE = 'summarize'
    TRANSLATE = 'translate'
    EXTRACT = 'extract'
    FORMAT = 'format'
    
class AIConfig(BaseModel):
    model: AIModelType
    prompt: str
    system_message: Optional[str] = None
    temprature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=150, gt=0)
    preprocessors: List[Dict[str, Any]] = []
    output_format: OutputFormat = OutputFormat.TEXT
    fallback_behavior: Optional[Dict[str, Any]] = None
    
# class AIResponse(BaseModel):
#     task_id: str
#     status: str
#     result: Optional[Dict[str, Any]] = None
#     error: Optional[str] = None
#     created_at: datetime
#     completed_at: Optional[datetime] = None
#     usage: Optional[Dict[str, Any]] = None
    
    

    