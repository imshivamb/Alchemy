from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from ..services.webhook_service import WebhookService
from typing import Dict, Any

router = APIRouter()
webhook_service = WebhookService()

@router.post("/{webhook_id}")
async def handle_webhook(
    webhook_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Handle incoming webhooks and trigger workflows
    """
    try:
        #Get request details
        headers = dict(request.headers)
        body = await request.body()
        
        #Process webhook asynchronously
        task_id = await webhook_service.create_task(webhook_id, headers, body)
        
        #Add to background tasks
        background_tasks.add_task(webhook_service.process_webhook, task_id)
        
        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Webhook received and processing started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/status/{task_id}")
async def get_webhook_status(task_id: str):
    """
    Get webhook processing status
    """
    try:
        status = await webhook_service.get_task_status(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/{task_id}/retry")
async def retry_webhook(task_id: str, background_tasks: BackgroundTasks):
    """Retry a failed webhook task"""
    try:
        await webhook_service.retry_failed_task(task_id)
        return {
            "message": "Webhook retry initiated",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
