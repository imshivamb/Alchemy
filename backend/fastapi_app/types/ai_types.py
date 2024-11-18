from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class AIModelType(str, Enum):
    GPT_40_MINI = 'gpt-40-mini'
    GPT_4 = 'gpt-4'
    GPT_35_TURBO = 'gpt-3.5-turbo'
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
    
class AIRequest(BaseModel):
    workflow_id: str
    input_data: Dict[Any, Any]
    model: AIModelType = Field(default=AIModelType.GPT_35_TURBO)
    max_tokens: int = Field(default=150, gt=0, le=8192)
    temperature: float = Field(default=0.7, ge=0, le=1)
    preprocessors: Optional[List[Dict[str, Any]]] = None
    output_format: OutputFormat = Field(default=OutputFormat.TEXT)
    system_message: Optional[str] = None
    fallback_behavior: Optional[Dict[str, Any]] = None
    
class AIBatchRequest(BaseModel):
    requests: List[AIRequest]
    sequential: bool = Field(default=True)
    
class AIResponse(BaseModel):
    task_id: str
    status: str
    message: str
    
class AIModelInfo(BaseModel):
    id: str
    name: str
    max_tokens: int
    supports_functions: bool
    cost_per_token: float
    recommended_uses: List[str]
    

    