from fastapi import BackgroundTasks, APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from ...services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

class AIRequest(BaseModel):
    workflow_id: str
    input_data: Dict[Any, Any]
    model: str = 'gpt-40-mini'
    max_tokens: int = 150
    
@router.post("/process")
async def process_with_ai(request: AIRequest, background_tasks: BackgroundTasks):
    """
    Process data with AI models
    """
    try:
        task_id = await ai_service.create_task(
            workflow_id=request.workflow_id,
            input_data=request.input_data,
            model=request.model,
        
        )
        #Add to background tasks
        background_tasks.add_task(
            ai_service.process_task,
            task_id=task_id
        )
        return {
             "task_id": task_id,
             "status": "Processing",
             "message": "AI model is processing the data"
             
         }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get AI processing task status
    """
    try:
        status = await ai_service.get_task_status(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))