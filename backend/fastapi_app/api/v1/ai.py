from fastapi import BackgroundTasks, APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from ...services.ai_service import AIService
from ...core.auth import get_current_user

router = APIRouter()
ai_service = AIService()

class AIRequest(BaseModel):
    workflow_id: str
    input_data: Dict[Any, Any]
    model: str = 'gpt-40-mini'
    max_tokens: int = 150
    
@router.post("/process")
async def process_with_ai(request: AIRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Process data with AI models
    
    Requires authentication token in header:
    Authorization: Bearer <token>
    """
    try:
        user_id = current_user.get('user_id')
        
        task_id = await ai_service.create_task(
            workflow_id=request.workflow_id,
            input_data=request.input_data,
            model=request.model,
            user_id=user_id 
        
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
async def get_task_status(task_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get AI processing task status
    """
    try:
        task = await ai_service.get_task_status(task_id)
        if task['user_id'] != current_user.get('user_id'):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this task"
            )
        return task
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))