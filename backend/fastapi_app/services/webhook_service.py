from typing import Dict, Any
import uuid
from datetime import datetime
import httpx
import json
import hmac
import hashlib
from ...redis.base import BaseRedis

class WebhookService(BaseRedis):
    def __init__(self):
        super().__init__()
        self.webhook_prefix = "webhook_task:"
    
    async def create_task(self, webhook_id: str, headers: Dict, body: bytes) -> str:
        """Create a new webhook processing task in Redis"""
        task_id = str(uuid.uuid4())
        task_data = {
            "webhook_id": webhook_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "headers": headers,
            "body": body.decode(),
            "result": None,
            "error": None
        }
        
        #Store in Redis with 24 hours TTL
        await self.set_data(f"{self.webhook_prefix}{task_id}", task_data, expires=86400)
        return task_id
    
    def verify_signature(self, secret: str, body: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        expected = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    async def process_webhook(self, task_id: str):
        """Process the webhook task asynchronously"""
        task = await self.get_task_status(task_id)
        task["status"] = "processing"
        await self.update_task_status(task_id, status="processing")
        
        try:
            # Get webhook details from Django database
            async with httpx.AsyncClient() as client:
                webhook_response = await client.get(
                    f"http://localhost:8000/api/v1/webhooks/{task['webhook_id']}"
                )
                webhook_data = webhook_response.json()
                
            #Verify webhook signature
            signature = task["headers"].get("X-Webhook-Signature")
            if signature and not self.verify_signature(
                webhook_data["secret_key"],
                task["body"].encode(),
                signature
            ):
                raise Exception("Invalid webhook signature")
            
             # Process based on webhook type
            if webhook_data["webhook_type"] == "trigger":
                 await self.trigger_workflow(webhook_data, task["body"])
            else:
                 # Send webhook (outgoing)
                await self.send_webhook(webhook_data, task["body"])
                
             # Update task status as completed
            await self.update_task_status(task_id, status="completed")
        except Exception as e:
            # Update task status as failed
            await self.update_task_status(task_id, status="failed", error=str(e))
            
    async def trigger_workflow(self, webhook_data: Dict, body: str):
        """Trigger a workflow based on webhook data"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/workflows/trigger",
                json={
                    "workflow_id": webhook_data["workflow_id"],
                    "trigger_data": json.loads(body),
                    "trigger_type": "webhook"
                }
            )
            if response.status_code != 200:
                raise Exception(f"Failed to trigger workflow: {response.text}")
    
    async def send_webhook(self, webhook_data: Dict, body: str):
        """Send an outgoing webhook"""
        async with httpx.AsyncClient() as client:
            # GEnerate Signature
            signature = hmac.new(webhook_data["secret_key"].encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Prepare headers
            headers = {
                **webhook_data.get("headers", {}),
                "X-Webhook-Signature": signature,
                "Content-Type": "application/json"
            }
            
            #Send Request
            response = await client.post(
                webhook_data["target_url"],
                headers=headers,
                json=json.loads(body)
            )
            if response.status_code not in [200, 201, 202]:
                raise Exception(f"Failed to send webhook: {response.text}")
            
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a webhook processing task in Redis"""
        task = await self.get_data(f"{self.webhook_prefix}{task_id}")
        if not task:
            raise Exception(f"Task {task_id} not found")
        return task
    
    async def update_task_status(self, task_id: str, status: str, result: Dict = None, error: str = None):
        """Update webhook task status in Redis"""
        task_data = await self.get_task_status(task_id)
        task_data.update({
            "status": status,
            "result": result,
            "error": error,
            "updated_at": datetime.utcnow().isoformat()
        })
        await self.set_data(f"{self.webhook_prefix}{task_id}", task_data)
        
    async def retry_failed_task(self, task_id: str):
        """Retry a failed webhook task"""
        task = await self.get_task_status(task_id)
        if task["status"] != "failed":
            raise Exception("Only failed tasks can be retried")

        # Reset task status
        await self.update_task_status(task_id, status="pending", error=None)

        # Process task again
        await self.process_webhook(task_id)