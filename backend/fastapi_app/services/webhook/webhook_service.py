from typing import Dict, Any, Optional, Tuple, Union
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
from ..webhook_monitoring import WebhookMonitoring
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
            "config": config.dict(),
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
        
        await self.get_data(
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
