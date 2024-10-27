from celery import Task
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseTask(Task):
    """Base task class with error handling and retries"""
    
    abstract = True
    
    def apply_async(self, *args, **kwargs):
        """Override to add custom logic before task execution"""
        return super().apply_async(*args, **kwargs)
        
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(
            f"Task {task_id} failed: {str(exc)}",
            exc_info=True,
            extra={
                'task_id': task_id,
                'args': args,
                'kwargs': kwargs
            }
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        logger.warning(
            f"Task {task_id} being retried: {str(exc)}",
            extra={
                'task_id': task_id,
                'args': args,
                'kwargs': kwargs
            }
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)
        
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(
            f"Task {task_id} completed successfully",
            extra={
                'task_id': task_id,
                'result': retval
            }
        )
        super().on_success(retval, task_id, args, kwargs)