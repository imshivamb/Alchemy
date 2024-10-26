from typing import Dict, Any
import uuid
from datetime import datetime
import httpx
import json
import hmac
import hashlib
from ...redis.base import BaseRedis
import logging

class WebhookService(BaseRedis):
    def __init__(self):
        super().__init__()
        self.webhook_prefix = "webhook_task:"
        logging.basicConfig(level=logging.INFO)

    async def create_task(self, webhook_id: str, headers: Dict, body: bytes) -> str:
        """Create a new webhook processing task in Redis with a 24-hour TTL."""
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
        await self.set_data(f"{self.webhook_prefix}{task_id}", task_data, expires=86400)
        logging.info(f"Task {task_id} created with status 'pending'")
        return task_id

    def verify_signature(self, secret: str, body: bytes, signature: str) -> bool:
        """Verify webhook signature to ensure authenticity."""
        expected_signature = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        is_valid = hmac.compare_digest(expected_signature, signature)
        if not is_valid:
            logging.warning("Webhook signature verification failed.")
        return is_valid

    async def process_webhook(self, task_id: str):
        """Process the webhook task asynchronously."""
        task = await self.get_task_status(task_id)
        await self.mark_task_processing(task_id)

        try:
            webhook_data = await self.fetch_webhook_data(task["webhook_id"])
            
            if not self.is_signature_valid(task, webhook_data):
                raise ValueError("Invalid webhook signature")

            if webhook_data["webhook_type"] == "trigger":
                await self.trigger_workflow(webhook_data, task["body"])
            else:
                await self.send_webhook(webhook_data, task["body"])

            await self.mark_task_completed(task_id)
        except Exception as e:
            await self.mark_task_failed(task_id, str(e))
            logging.error(f"Error processing task {task_id}: {e}")

    async def fetch_webhook_data(self, webhook_id: str) -> Dict[str, Any]:
        """Fetch webhook details from the Django API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8000/api/v1/webhooks/{webhook_id}")
            response.raise_for_status()
            return response.json()

    def is_signature_valid(self, task: Dict, webhook_data: Dict) -> bool:
        """Check if the signature in the headers matches the computed signature."""
        signature = task["headers"].get("X-Webhook-Signature")
        if signature:
            return self.verify_signature(webhook_data["secret_key"], task["body"].encode(), signature)
        return True  # No signature to validate

    async def trigger_workflow(self, webhook_data: Dict, body: str):
        """Trigger a workflow based on webhook data."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/workflows/trigger",
                json={
                    "workflow_id": webhook_data["workflow_id"],
                    "trigger_data": json.loads(body),
                    "trigger_type": "webhook"
                }
            )
            response.raise_for_status()

    async def send_webhook(self, webhook_data: Dict, body: str):
        """Send an outgoing webhook to the specified target URL."""
        signature = hmac.new(
            webhook_data["secret_key"].encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            **webhook_data.get("headers", {}),
            "X-Webhook-Signature": signature,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_data["target_url"],
                headers=headers,
                json=json.loads(body)
            )
            if response.status_code not in [200, 201, 202]:
                raise Exception(f"Webhook delivery failed with status {response.status_code}: {response.text}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Retrieve the current status of a webhook processing task from Redis."""
        task = await self.get_data(f"{self.webhook_prefix}{task_id}")
        if not task:
            raise ValueError(f"Task {task_id} not found")
        return task

    async def mark_task_processing(self, task_id: str):
        """Update the task status to 'processing'."""
        await self.update_task_status(task_id, status="processing")
        logging.info(f"Task {task_id} marked as processing")

    async def mark_task_completed(self, task_id: str):
        """Update the task status to 'completed'."""
        await self.update_task_status(task_id, status="completed")
        logging.info(f"Task {task_id} completed successfully")

    async def mark_task_failed(self, task_id: str, error: str):
        """Update the task status to 'failed' with an error message."""
        await self.update_task_status(task_id, status="failed", error=error)
        logging.error(f"Task {task_id} failed with error: {error}")

    async def update_task_status(self, task_id: str, status: str, result: Dict = None, error: str = None):
        """Update the task status in Redis."""
        task_data = await self.get_task_status(task_id)
        task_data.update({
            "status": status,
            "result": result,
            "error": error,
            "updated_at": datetime.utcnow().isoformat()
        })
        await self.set_data(f"{self.webhook_prefix}{task_id}", task_data)

    async def retry_failed_task(self, task_id: str):
        """Retry a failed webhook task."""
        task = await self.get_task_status(task_id)
        if task["status"] != "failed":
            raise ValueError("Only failed tasks can be retried")
        
        await self.mark_task_processing(task_id)
        await self.process_webhook(task_id)
