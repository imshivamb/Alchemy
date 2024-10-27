# backend/redis_service/queue/task_queue_manager.py

from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import json
import asyncio
from ..base import BaseRedis
from ..exceptions import TaskQueueError

class TaskQueueManager(BaseRedis):
    """
    Manages prioritized task queues with monitoring and error handling
    """
    
    QUEUE_PRIORITIES = {
        'high': 'queue:high_priority',
        'normal': 'queue:normal_priority',
        'low': 'queue:low_priority'
    }

    async def enqueue_task(
        self,
        queue_type: str,
        task_data: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> str:
        """
        Add task to specific priority queue
        """
        if queue_type not in self.QUEUE_PRIORITIES:
            raise TaskQueueError(
                f"Invalid queue type. Must be one of {list(self.QUEUE_PRIORITIES.keys())}"
            )

        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'data': task_data,
            'status': 'queued',
            'queue_type': queue_type,
            'created_at': datetime.utcnow().isoformat(),
            'timeout': timeout
        }

        try:
            # Add to priority queue
            await self.push_to_queue(
                self.QUEUE_PRIORITIES[queue_type],
                task
            )

            # Set task metadata
            await self.set_data(
                f"task:{task_id}",
                task,
                expires=timeout
            )

            # Publish event for monitoring
            await self.publish('task_events', {
                'event': 'task_queued',
                'task_id': task_id,
                'queue': queue_type,
                'timestamp': datetime.utcnow().isoformat()
            })

            return task_id

        except Exception as e:
            raise TaskQueueError(f"Failed to enqueue task: {str(e)}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get current status of a task
        """
        task = await self.get_data(f"task:{task_id}")
        if not task:
            raise TaskQueueError(f"Task {task_id} not found")
        return task

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """
        Update task status with result or error
        """
        task = await self.get_task_status(task_id)
        task.update({
            'status': status,
            'result': result,
            'error': error,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        await self.set_data(f"task:{task_id}", task)
        await self.publish('task_events', {
            'event': 'task_updated',
            'task_id': task_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def process_queues(self):
        """
        Process tasks from queues based on priority
        """
        while True:
            try:
                task = await self._get_next_task()
                if task:
                    await self._process_task(task)
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing task: {str(e)}")
            await asyncio.sleep(0.1)

    async def _get_next_task(self) -> Optional[Dict]:
        """
        Get next task respecting priority
        """
        for priority in self.QUEUE_PRIORITIES.values():
            task = await self.pop_from_queue(priority)
            if task:
                return task
        return None

    async def _process_task(self, task: Dict):
        """
        Process a single task
        """
        task_id = task['id']
        try:
            await self.update_task_status(task_id, 'processing')
            
            # Process based on task type
            result = await self._execute_task(task)
            await self.update_task_status(task_id, 'completed', result=result)
            
        except Exception as e:
            await self.update_task_status(task_id, 'failed', error=str(e))
            raise TaskQueueError(f"Task processing failed: {str(e)}")

    async def _execute_task(self, task: Dict) -> Dict:
        """
        Execute task based on type
        Override this method in specific implementations
        """
        raise NotImplementedError("Task execution must be implemented")