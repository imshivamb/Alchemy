from ...types.ai_types import AIRequest, AIBatchRequest, AIResponse, AIModelInfo, OutputFormat, AIModelType, PreprocessorType, AIConfig
from ...services.ai.ai_service import AIService
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from typing import List, Dict, Any, Optional
from ...core.auth import get_current_user

router = APIRouter()
ai_service = AIService()

@router.post("/process", response_model=AIResponse)
async def process_with_ai(
    request: AIRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
    ):
    """Process data with AI
    Requires authentication token in header:
    Authorization: Bearer <token>
    """
    try:
        config =  AIConfig(
            model=request.model,
            temprature=request.temperature,
            max_tokens=request.max_tokens,
            output_format=request.output_format,
            system_message=request.system_message,
            prompt=request.input_data.get("prompt", ""),
            preprocessors=request.preprocessors,
            fallback_behavior=request.fallback_behavior
        )
        task_id = await ai_service.create_task(
            workflow_id=request.workflow_id,
            config=config,
            user_id=current_user['user_id']
        )
        
        background_tasks.add_task(
            ai_service.process_task, task_id
        )
        
        return AIResponse(
            task_id=task_id,
            status="processing",
            message="AI Processing Started"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/batch", response_model=List[AIResponse])
async def process_batch(
    request: AIBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Process a batch of AI requests"""
    try:
        responses = []
        for ai_request in request.requests:
            response = await process_with_ai(
                request=ai_request,
                background_tasks=background_tasks, 
                current_user=current_user
                )
            responses.append(response)
            if request.sequential:
                await ai_service.wait_for_completion(response.task_id)
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=List[AIModelInfo])
async def list_models(
    current_user: dict = Depends(get_current_user)
):
    """
    Get available AI models and their configurations
    """
    try:
        return await ai_service.get_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/estimate")
async def estimate_cost(
    config: AIConfig,
    prompt: str,
    current_user: dict = Depends(get_current_user)
):
    """Estimate the cost of an AI request"""
    try:
        return await ai_service.estimate_cost(config, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of an AI task"""
    try:
        task = await ai_service.get_task_status(task_id)
        if task["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this task")
        
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/tasks")
async def list_tasks(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    current_user: dict = Depends(get_current_user)
):
    """
    List AI tasks with optional filtering
    """
    try:
        return await ai_service.list_tasks(
            user_id=current_user["user_id"],
            workflow_id=workflow_id,
            status=status,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel an ongoing AI task
    """
    try:
        task = await ai_service.get_task_status(task_id)
        if task["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to cancel this task"
            )
        
        await ai_service.cancel_task(task_id)
        return {"message": "Task cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/retry")
async def retry_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Retry a failed AI task
    """
    try:
        task = await ai_service.get_task_status(task_id)
        if task["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to retry this task"
            )
        
        if task["status"] != "failed":
            raise HTTPException(
                status_code=400,
                detail="Only failed tasks can be retried"
            )
        
        background_tasks.add_task(ai_service.retry_task, task_id)
        return {"message": "Task retry initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    


