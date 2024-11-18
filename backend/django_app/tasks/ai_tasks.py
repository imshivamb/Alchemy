
from .base import BaseTask
from celery import shared_task
from fastapi_app.services.ai import ai_service
from typing import Dict, Any

@shared_task(
    bind=True,
    base=BaseTask,
    name='tasks.ai_process',
    queue='ai_tasks',
    rate_limit='10/m'
)
def process_ai_request(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process AI request"""
    try:
        # AI processing logic here
        result = ai_service.process_task(task_data)
        return result
    except Exception as exc:
        # Handle specific exceptions and retry if needed
        self.retry(exc=exc, countdown=60, max_retries=3)