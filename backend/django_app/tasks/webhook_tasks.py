

from .base import BaseTask
from celery import shared_task
from fastapi_app.services import webhook_service
from typing import Dict, Any
import httpx
import hmac
import hashlib
from django.conf import settings

@shared_task(
    bind=True,
    base=BaseTask,
    name='tasks.webhook_process',
    queue='webhook_tasks',
    rate_limit='30/m'
)
async def process_webhook(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process webhook requests"""
    try:
        webhook_id = task_data.get('webhook_id')
        payload = task_data.get('payload')
        target_url = task_data.get('target_url')
        
        # Sign the payload
        signature = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Send webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
            target_url,
            json=payload,
            headers={
                'X-Webhook-Signature': signature,
                'Content-Type': 'application/json'
            },
            timeout=30.0
            )
            
        return {
            'status': 'success',
            'webhook_id': webhook_id,
            'response_status': response.status_code,
            'response_body': response.json()
        }
        
    except httpx.TimeoutException as exc:
        self.retry(exc=exc, countdown=300, max_retries=3)
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)

@shared_task(
    bind=True,
    base=BaseTask,
    name='tasks.webhook_retry',
    queue='webhook_tasks'
)
def retry_failed_webhook(self, webhook_id: str) -> Dict[str, Any]:
    """Retry failed webhooks"""
    try:
        # Fetch failed webhook details and retry
        webhook_data = webhook_service.fetch_webhook_data(webhook_id)
        return process_webhook.delay(webhook_data)
    except Exception as exc:
        self.retry(exc=exc, countdown=300, max_retries=2)