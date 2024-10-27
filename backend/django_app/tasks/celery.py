from celery import Celery
from celery.signals import task_success, task_failure, task_retry
from django.conf import settings
from typing import Dict, Any
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery('zapnium')

app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks(lambda:settings.INSTALLED_APPS)

class TaskPriority:
    HIGH = 'high'
    NORMAL = 'normal'
    LOW = 'low'
    
class QueueNames:
    AI_TASKS = 'ai_tasks'
    WEBHOOK_TASKS = 'webhook_tasks'
    WORKFLOW_TASKS = 'workflow_tasks'
    DEFAULT = 'default'
    
#Celery Configuration
app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone= settings.TIME_ZONE,
    task_queues={
        QueueNames.AI_TASKS: {'routing_key': 'ai.#'},
        QueueNames.WEBHOOK_TASKS: {'routing_key': 'webhook.#'},
        QueueNames.WORKFLOW_TASKS: {'routing_key': 'workflow.#'},
        QueueNames.DEFAULT: {'routing_key': 'default'}
    },
    task_routes ={
        'tasks.ai.*': {'queue': QueueNames.AI_TASKS},
        'tasks.webhook.*': {'queue': QueueNames.WEBHOOK_TASKS},
        'tasks.workflow.*': {'queue': QueueNames.WORKFLOW_TASKS},
    },
    task_default_queue=QueueNames.DEFAULT,
    task_default_exchange='zapnium',
    task_default_routing_key='default',
    
    #Retry Settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Rate limiting
    task_annotations={
        'tasks.ai.*': {'rate_limit': '10/m'},
        'tasks.webhook.*': {'rate_limit': '30/m'}
    }
)

class TaskProcessor:
    def __init__(self):
        self.celery = app
        self.redis_client = None
        
    def get_queue_for_tasks(self, task_type: str) -> str:
        """Determine appropriate queue for task type"""
        queue_mapping = {
            'ai-process': QueueNames.AI_TASKS,
            'webhook': QueueNames.WEBHOOK_TASKS,
            'workflow': QueueNames.WORKFLOW_TASKS
        }
        return queue_mapping.get(task_type, QueueNames.DEFAULT)
    
    def get_priority_for_tasks(self, task_data: Dict[str, Any]) -> int:
        """Determine task priority based on user plan and task type"""
        priority_mapping = {
            'enterprise': {
                'ai_process': 9,
                'webhook': 8,
                'workflow': 7
            },
            'premium': {
                'ai_process': 6,
                'webhook': 5,
                'workflow': 4
            },
            'basic': {
                'ai_process': 4,
                'webhook': 3,
                'workflow': 2
            },
            'free': {
                'ai_process': 3,
                'webhook': 2,
                'workflow': 1
            }
        }
        
        user_plan = task_data.get('user_plan', 'free')
        task_type = task_data.get('task_type', 'workflow')
        return priority_mapping.get(user_plan, {}).get(task_type, 0)
    
    async def process_task(self,task_type: str, task_data: Dict[str, Any], retry_policy: Dict[str, Any] = None) -> str:
        """
        Process a task with proper queueing and monitoring
        """
        try:

            queue = self.get_queue_for_tasks(task_type)
            priority = self.get_priority_for_tasks(task_data)
        
            # Default retry policy
            default_retry_policy = {
                'max_retries': 3,
                'interval_start': 60,
                'interval_step': 60,
                'interval_max': 300
            }
            
            retry_policy = {**default_retry_policy, **(retry_policy or {})}
            
            #Send Task to celery
            task = self.celery.send_task(
                f"task:{task_type}",
                args=[task_data],
                kwargs={'retry_policy': retry_policy},
                queue=queue,
                priority=priority,
                retry=True,
                retry_policy=retry_policy
            )
            # Store task metadata in Redis
            await self._store_task_metadata(task.id, task_type, task_data)
            
            return task.id
        
        except Exception as e:
            logger.error(f"Failed to process task: {str(e)}", exc_info=True)
            raise
        
    async def _store_task_metadata(
        self,
        task_id: str,
        task_type: str,
        task_data: Dict[str, Any]
    ):
        """Store task metadata in Redis"""
        metadata = {
            'task_id': task_id,
            'task_type': task_type,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'user_id': task_data.get('user_id'),
            'workflow_id': task_data.get('workflow_id')
        }
        
        await self.redis_client.set_data(
            f'task:metadata:{task_id}',
            metadata,
            expires=86400  # 24 hours
        )