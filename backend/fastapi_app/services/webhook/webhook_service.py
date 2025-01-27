from typing import Dict, Any, Optional, Tuple, Union, List
import uuid
from datetime import datetime, timedelta
import httpx
import json
import hmac
import hashlib
import asyncio
import os
import logging
from redis_service.base import BaseRedis
from ..monitoring import WebhookMonitoring
from ...types.webhook_types import WebhookConfig, WebhookSecret, RetryStrategy, WebhookStatus, WebhookMethod

class WebhookService(BaseRedis):
    def __init__(self):
        super().__init__()
        self.webhook_prefix = "webhook:"
        self.delivery_prefix = "webhook_delivery:"
        
    async def register_webhook(
        self,
        name: str,
        config: WebhookConfig,
        workflow_id: str,
        webhook_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Register a newwebhook"""
        webhook_id = f"wh-{datetime.utcnow().timestamp()}"
        secret = WebhookSecret(
            key=self._generate_secret(),
            header_name="X-Webhook-Signature",
            hash_algorithm="sha256"
        )
        
        webhook_data = {
            "id": webhook_id,
            "name": name,
            "config": {
                **config.dict(),
                "url": str(config.url)
            },
            "secret": secret.dict(),
            "workflow_id": workflow_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": WebhookStatus.ACTIVE,
            "last_triggered": None,
            "total_deliveries": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
        }
        
        await self.set_data(
            f"{self.webhook_prefix}{webhook_id}",
            webhook_data
        )
        
        return webhook_data

    async def trigger_webhook(
        self,
        webhook_id: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Trigger a webhook"""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook with id {webhook_id} not found")
        
        delivery_id = f"whd_{datetime.utcnow().timestamp()}"
        
        delivery_data = {
            "id": delivery_id,
            "webhook_id": webhook_id,
            "payload": payload,
            "status": WebhookStatus.PENDING,
            "headers": headers or {},
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0,
            "next_retry": None,
            "response": None,
            "error": None,
        }
        
        await self.set_data(
            f"{self.delivery_prefix}{delivery_id}",
            delivery_data,
            expires=86400
        )
        
        asyncio.create_task(self.process_delivery(delivery_id))
        
        return delivery_id

    async def _process_delivery(self, delivery_id: str):
        """Process a webhook delivery"""
        try:
            delivery = await self.get_delivery(delivery_id)
            webhook = await self.get_webhook(delivery["webhook_id"])
            config = WebhookConfig(**webhook["config"])
            
            delivery["attempts"] += 1
            await self._update_delivery(delivery_id, ("attempts", delivery["attempts"]))
            
            headers = {
                **config.headers,
                **delivery["headers"],
                "Content-Type": "application/json",
                webhook["secret"]["header_name"]: self._generate_signature(
                    webhook["secret"]["key"],
                    json.dumps(delivery["payload"])
                )
            }
            
            async with httpx.AsyncClient(verify=config.verify_ssl) as client:
                response = await client.request(
                    method=config.method,
                    url=str(config.url),
                    headers=headers,
                    json=delivery["payload"],
                    timeout=config.timeout
                )
                
                if response.is_success:
                    await self._handle_success(delivery_id, webhook["id"], response)
                else:
                    await self._handle_failure(
                        delivery_id,
                        webhook["id"],
                        f"HTTP {response.status_code}: {response.text}",
                        config.retry_strategy
                    )
                    
        except Exception as e:
            await self._handle_failure(
                delivery_id,
                delivery["webhook_id"],
                str(e),
                config.retry_strategy
            )
            
    async def _handle_success(
        self,
        delivery_id: str,
        webhook_id: str,
        response: httpx.Response
    ):
        """Handle a successful delivery"""
        update_data = {
            "status": WebhookStatus.SUCCESS,
            "completed_at": datetime.utcnow().isoformat(),
            "response": {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }
        }
        
        await self._update_delivery(delivery_id, update_data)
        await self._update_webhook_stats(webhook_id, success=True)
        
    async def _handle_failure(
        self,
        delivery_id: str,
        webhook_id: str,
        error: str,
        retry_strategy: RetryStrategy
    ):
        """Handle a failed delivery"""
        delivery = await self.get_delivery(delivery_id)
        
        if delivery["attempts"] >= retry_strategy.max_retries:
            update_data = {
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "error": error
            }
            await self._update_webhook_stats(webhook_id, success=False)
        else:
            next_retry = self._calculate_next_retry(
                delivery["attempts"],
                retry_strategy
            )
            update_data = {
                "status": "pending",
                "error": error,
                "next_retry": next_retry.isoformat()
            }
            
            # Schedule retry
            retry_delay = (next_retry - datetime.utcnow()).total_seconds()
            asyncio.create_task(self._schedule_retry(delivery_id, retry_delay))
            
        await self._update_delivery(delivery_id, update_data)
            
    async def list_webhooks(
        self,
        user_id: str,
        workflow_id: Optional[str] = None,
        status: Optional[WebhookStatus] = None,
        page: int = 1,
        per_page: int = 50
    ) -> List[Dict[str, Any]]:
        """List webhooks with optional filtering by workflow_id and status.
        
        Args:
            user_id: ID of the user requesting webhooks
            workflow_id: Optional workflow ID to filter webhooks
            status: Optional webhook status to filter by
            page: Page number for pagination (default: 1)
            per_page: Number of webhooks per page (default: 50)
            
        Returns:
            List of webhook data dictionaries
        """
        pattern = f"{self.webhook_prefix}*"
        webhooks = []
        
        async for key in self.redis.scan_iter(match=pattern):
            webhook_data = await self.get_data(key)
            
            if not webhook_data or webhook_data.get("user_id") != user_id:
                continue
                
            # Apply filters if provided
            if workflow_id and webhook_data.get("workflow_id") != workflow_id:
                continue
                
            if status and webhook_data.get("status") != status:
                continue
                
            webhooks.append(webhook_data)
        
        # Sort webhooks by created_at descending
        webhooks.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return webhooks[start_idx:end_idx]
    def _generate_signature(
        self, 
        secret: str,
        payload: str
    ) -> str:
        """Generate a signature for a payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
    def _generate_secret(self) -> str:
        """Generate a webhook secret"""
        return hashlib.sha256(os.urandom(32)).hexdigest()
    
    def _calculate_next_retry(
        self,
        attempts: int,
        retry_strategy: RetryStrategy
    ) -> datetime:
        """Calculate next retry time using exponential backoff"""
        interval = min(
            retry_strategy.initial_interval * (retry_strategy.multiplier ** (attempts - 1)),
            retry_strategy.max_interval
        )
        return datetime.utcnow() + timedelta(seconds=interval)

    async def _schedule_retry(self, delivery_id: str, delay: float):
        """Schedule a retry after delay"""
        await asyncio.sleep(delay)
        asyncio.create_task(self._process_delivery(delivery_id))

    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook data by ID"""
        return await self.get_data(f"{self.webhook_prefix}{webhook_id}")

    async def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery data by ID"""
        return await self.get_data(f"{self.delivery_prefix}{delivery_id}")

    async def _update_delivery(self, delivery_id: str, update: Union[Dict[str, Any], Tuple[str, Any]]):
        """Update delivery data"""
        if isinstance(update, tuple):
            key, value = update
            update_dict = {key: value}
        else:
            update_dict = update
            
        delivery = await self.get_delivery(delivery_id)
        if delivery:
            delivery.update(update_dict)
            await self.set_data(f"{self.delivery_prefix}{delivery_id}", delivery)

    async def _update_webhook_stats(self, webhook_id: str, success: bool):
        """Update webhook delivery statistics"""
        webhook = await self.get_webhook(webhook_id)
        if webhook:
            webhook["total_deliveries"] += 1
            if success:
                webhook["successful_deliveries"] += 1
            else:
                webhook["failed_deliveries"] += 1
            webhook["last_triggered"] = datetime.utcnow().isoformat()
            await self.set_data(f"{self.webhook_prefix}{webhook_id}", webhook)
            
    async def list_deliveries(
        self,
        webhook_id: str,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List webhook deliveries with pagination and filtering"""
        pattern = f"{self.delivery_prefix}*"
        deliveries = []
        
        async for key in self.redis.scan_iter(match=pattern):
            delivery_data = await self.get_data(key)
            if delivery_data and delivery_data.get("webhook_id") == webhook_id:
                # Apply status filter if provided
                if status and delivery_data.get("status") != status:
                    continue
                deliveries.append(delivery_data)
        
        # Sort by created_at descending
        deliveries.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        paginated_deliveries = deliveries[offset:offset + limit]
        
        # Add duration for each delivery
        for delivery in paginated_deliveries:
            if delivery.get("completed_at"):
                start_time = datetime.fromisoformat(delivery["created_at"])
                end_time = datetime.fromisoformat(delivery["completed_at"])
                delivery["duration"] = (end_time - start_time).total_seconds() * 1000  # Convert to ms
        
        return paginated_deliveries

    async def get_webhook_health(self, webhook_id: str) -> Dict[str, Any]:
        """Get webhook health metrics including response times and status codes"""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook with id {webhook_id} not found")

        # Get recent deliveries for metrics
        recent_deliveries = await self._get_recent_deliveries(webhook_id)
        
        # Calculate response times
        response_times = []
        status_codes = {}
        error_types = {}
        retry_count = 0
        
        for delivery in recent_deliveries:
            # Track response times
            if delivery.get("completed_at"):
                start_time = datetime.fromisoformat(delivery["created_at"])
                end_time = datetime.fromisoformat(delivery["completed_at"])
                duration = (end_time - start_time).total_seconds() * 1000  # Convert to ms
                response_times.append({
                    "timestamp": delivery["created_at"],
                    "duration": duration
                })
            
            # Track status codes
            if delivery.get("response", {}).get("status_code"):
                status_code = str(delivery["response"]["status_code"])
                status_codes[status_code] = status_codes.get(status_code, 0) + 1
            
            # Track error types
            if delivery.get("error"):
                error_type = delivery["error"].split(":")[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Track retries
            if delivery.get("attempts", 0) > 1:
                retry_count += 1

        # Calculate health score (0-100)
        success_rate = (webhook["successful_deliveries"] / webhook["total_deliveries"] * 100) if webhook["total_deliveries"] > 0 else 0
        avg_response_time = sum(rt["duration"] for rt in response_times) / len(response_times) if response_times else 0
        
        # Determine health status
        health_status = "healthy"
        if success_rate < 90:
            health_status = "degraded"
        if success_rate < 70:
            health_status = "unhealthy"
        if webhook["total_deliveries"] == 0:
            health_status = "unknown"

        return {
            "health_score": success_rate,
            "status": health_status,
            "metrics": {
                "total_deliveries": webhook["total_deliveries"],
                "successful_deliveries": webhook["successful_deliveries"],
                "failed_deliveries": webhook["failed_deliveries"],
                "average_response_time": avg_response_time,
                "status_codes": status_codes,
                "error_types": error_types,
                "retry_count": retry_count
            },
            "response_times": response_times
        }

    async def _get_recent_deliveries(self, webhook_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent deliveries for a webhook"""
        # TODO: need to implement this based on the storage strategy
        # This is a placeholder that returns an empty list
        pattern = f"{self.delivery_prefix}*"
        deliveries = []
        
        async for key in self.redis.scan_iter(match=pattern):
            delivery_data = await self.get_data(key)
            if delivery_data and delivery_data.get("webhook_id") == webhook_id:
                deliveries.append(delivery_data)
        
        # Sort by created_at and limit
        deliveries.sort(key=lambda x: x["created_at"], reverse=True)
        return deliveries[:limit]
    
    async def delete_webhook(self, webhook_id: str) -> None:
        """Delete a webhook and its associated deliveries"""
        # First check if webhook exists
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook with id {webhook_id} not found")

        # Delete webhook data
        await self.redis.delete(f"{self.webhook_prefix}{webhook_id}")

        # Delete associated deliveries
        pattern = f"{self.delivery_prefix}*"
        async for key in self.redis.scan_iter(match=pattern):
            delivery_data = await self.get_data(key)
            if delivery_data and delivery_data.get("webhook_id") == webhook_id:
                await self.redis.delete(key)

        # Return None on successful deletion
        return None