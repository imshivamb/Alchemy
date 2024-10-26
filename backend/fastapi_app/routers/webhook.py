from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from ..services.webhook_service import WebhookService
from typing import Dict, Any
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_webhook_service() -> WebhookService:
    """Dependency to get an instance of WebhookService"""
    return WebhookService()

@router.post("/{webhook_id}")
async def handle_webhook(
    webhook_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Handle incoming webhooks and trigger workflows
    """
    try:
        # Get request details
        headers = dict(request.headers)
        body = await request.body()

        # Create a webhook processing task in Redis
        task_id = await webhook_service.create_task(webhook_id, headers, body)

        # Add webhook processing to background tasks
        background_tasks.add_task(webhook_service.process_webhook, task_id)

        # Log received webhook
        logger.info(f"Webhook received: task_id={task_id}, webhook_id={webhook_id}")

        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Webhook received and processing started"
        }

    except Exception as e:
        logger.error(f"Failed to handle webhook {webhook_id}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process webhook")

@router.get("/status/{task_id}")
async def get_webhook_status(
    task_id: str,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Get the processing status of a webhook task
    """
    try:
        # Fetch task status from the service
        status = await webhook_service.get_task_status(task_id)

        # Log status retrieval
        logger.info(f"Fetched status for task_id={task_id}: {status['status']}")

        return status

    except Exception as e:
        logger.warning(f"Task {task_id} not found: {e}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")

@router.post("/{task_id}/retry")
async def retry_webhook(
    task_id: str,
    background_tasks: BackgroundTasks,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """Retry a failed webhook task"""
    try:
        # Check if task is eligible for retry and reset its status
        await webhook_service.retry_failed_task(task_id)

        # Add the retry task to background processing
        background_tasks.add_task(webhook_service.process_webhook, task_id)

        # Log retry initiation
        logger.info(f"Retry initiated for task_id={task_id}")

        return {
            "message": "Webhook retry initiated",
            "task_id": task_id
        }

    except ValueError as e:
        # Handle specific error if the task is not in a failed state
        logger.warning(f"Retry failed for task_id={task_id}: {e}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        # Handle any other processing error
        logger.error(f"Error retrying task {task_id}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retry webhook")
