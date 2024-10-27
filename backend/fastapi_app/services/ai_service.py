import aiohttp
import asyncio
import uuid
from typing import Dict, Any
import os
from datetime import datetime
from redis_service.base import BaseRedis

class AIService(BaseRedis):
    def __init__(self):
        super().__init__()
        self.task_prefix = "ai_task:"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    
    async def create_task(self, workflow_id: str, input_data: Dict[Any, Any], model: str) -> str:
        """Create a new AI processing task"""
        task_id = str(uuid.uuid4())
        task_data = {
            "workflow_id": workflow_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "input_data": input_data,
            "model": model,
            "result": None,
            "error": None
        }
        
        # Storing the task in Redis with a 24-hour expiration
        await self.set_data(
            f"{self.task_prefix}{task_id}",
            task_data,
            expires=86400
        )
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get Task status from Redis"""
        task_data = await self.get_data(f"{self.task_prefix}{task_id}")
        if not task_data:
            raise Exception(f"Task {task_id} not found")
        return task_data
    
    async def update_task_status(self, task_id: str, status: str, result: Dict = None, error: str = None):
        """Update task status in Redis"""
        task_data = await self.get_task_status(task_id)
        task_data.update({
            "status": status,
            "result": result,
            "error": error,
            "updated_at": datetime.utcnow().isoformat()
        })
        await self.set_data(f"{self.task_prefix}{task_id}", task_data)

    async def setup_subscribers(self):
        """Setup subscribers for AI tasks"""
        await self.subscribe('ai_tasks', self.handle_task_update)

    async def handle_task_update(self, data: dict):
        """Handle AI task updates"""
        task_id = data.get('task_id')
        if task_id:
            await self.update_task_progress(
                task_id,
                data.get('progress', 0),
                data.get('status', 'processing')
            )
    
    async def process_task(self, task_id: str):
        """Process the AI task with progress tracking and locking"""
        try:
            # Acquire lock for task processing
            if not await self.acquire_lock(f"{self.task_prefix}{task_id}"):
                raise Exception("Task is already being processed")

            # Update progress and status to 'starting'
            await self.update_task_progress(task_id, 0, 'starting')

            # Retrieve task data from Redis
            task_data = await self.get_task_status(task_id)
            
            # Step 1: Validate input
            await self.update_task_progress(task_id, 25, 'validating')
            # (Validation logic here, e.g., checking input format)

            # Step 2: Process with OpenAI API
            await self.update_task_progress(task_id, 50, 'processing')
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": task_data["model"],
                        "messages": [
                            {"role": "user", "content": str(task_data["input_data"])}
                        ]
                    }
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        # Step 3: Finalize and update with the result
                        await self.update_task_progress(task_id, 75, 'finalizing')
                        await self.update_task_status(task_id, status="completed", result=result)
                        await self.update_task_progress(task_id, 100, 'completed')
                    else:
                        raise Exception(f"OpenAI API Error: {result}")
        
        except Exception as e:
            # Update task with failure status and error message
            await self.update_task_status(task_id, status="failed", error=str(e))
            await self.update_task_progress(task_id, 0, 'failed')
            raise
        finally:
            # Release the lock for this task
            await self.release_lock(f"{self.task_prefix}{task_id}")
