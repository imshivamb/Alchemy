from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from ...types.webhook_types import *
from fastapi_app.services.webhook.webhook_service import WebhookService
from ...core.auth import get_current_user
from fastapi import HTTPException, Request
import httpx

router = APIRouter()
webhook_service = WebhookService()

class WebhookCreateRequest(BaseModel):
    name: str
    config: WebhookConfig
    workflow_id: str
    webhook_id: str

class WebhookResponse(BaseModel):
    id: str
    name: str
    config: WebhookConfig
    status: WebhookStatus
    created_at: datetime
    secret: WebhookSecret
    workflow_id: str
    user_id: str
    last_triggered: Optional[datetime]
    total_deliveries: int
    successful_deliveries: int 
    failed_deliveries: int

class WebhookDeliveryResponse(BaseModel):
    id: str
    webhook_id: str
    payload: Dict[str, Any]
    status: str
    headers: Dict[str, str]
    created_at: datetime
    completed_at: Optional[datetime]
    attempts: int
    next_retry: Optional[datetime]
    response: Optional[Dict[str, Any]]
    error: Optional[str]

@router.post("/webhooks", response_model=WebhookResponse, status_code=201)
async def create_webhook(
    request: WebhookCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new webhook"""
    try:
        webhook = await webhook_service.register_webhook(
            webhook_id=request.webhook_id,
            name=request.name,
            config=request.config,
            workflow_id=request.workflow_id,
            user_id=current_user["user_id"]
        )
        return webhook
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    workflow_id: Optional[str] = None,
    status: Optional[WebhookStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """List webhooks"""
    try:
        return await webhook_service.list_webhooks(
            user_id=current_user["user_id"],
            workflow_id=workflow_id,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get webhook details"""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        return webhook
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/{webhook_id}/trigger", response_model=Dict[str, str])
async def trigger_webhook(
    webhook_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    payload: Dict[str, Any] = Body(...)
):
    """Manually trigger a webhook"""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        delivery_id = await webhook_service.trigger_webhook(
            webhook_id=webhook_id,
            payload=payload
        )
        return {
            "delivery_id": delivery_id,
            "status": "processing",
            "message": "Webhook triggered successfully"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/{webhook_id}/deliveries", response_model=List[WebhookDeliveryResponse])
async def list_deliveries(
    webhook_id: str,
    status: Optional[str] = None,
    limit: int = Query(default=10, le=100, gt=0),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List webhook deliveries"""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        return await webhook_service.list_deliveries(
            webhook_id=webhook_id,
            status=status,
            limit=limit,
            offset=offset
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deliveries/{delivery_id}", response_model=WebhookDeliveryResponse)
async def get_delivery(
    delivery_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get delivery details"""
    try:
        delivery = await webhook_service.get_delivery(delivery_id)
        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery not found")
            
        webhook = await webhook_service.get_webhook(delivery["webhook_id"])
        if not webhook:
            raise HTTPException(status_code=404, detail="Associated webhook not found")
        
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        return delivery
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deliveries/{delivery_id}/retry", response_model=Dict[str, str])
async def retry_delivery(
    delivery_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Retry a failed delivery"""
    try:
        delivery = await webhook_service.get_delivery(delivery_id)
        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery not found")
            
        webhook = await webhook_service.get_webhook(delivery["webhook_id"])
        if not webhook:
            raise HTTPException(status_code=404, detail="Associated webhook not found")
        
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        if delivery["status"] != "failed":
            raise HTTPException(
                status_code=400,
                detail="Only failed deliveries can be retried"
            )
            
        await webhook_service.retry_delivery(delivery_id)
        return {
            "message": "Delivery retry initiated",
            "delivery_id": delivery_id
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.put("/webhooks/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    config: WebhookConfig,
    current_user: dict = Depends(get_current_user)
):
    """Update webhook configuration"""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        updated_webhook = await webhook_service.update_webhook(
            webhook_id=webhook_id,
            config=config
        )
        return updated_webhook
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete webhook"""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        await webhook_service.delete_webhook(webhook_id)
        return {"message": "Webhook deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/webhooks/{webhook_id}/verify")
async def verify_signature(
    webhook_id: str,
    payload: str,
    signature: str,
    current_user: dict = Depends(get_current_user)
):
    """Verify webhook signature"""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        is_valid = await webhook_service.verify_signature(
            webhook["secret"]["key"],
            payload,
            signature
        )
        return {"valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/{webhook_id}/health")
async def get_webhook_health(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get webhook health metrics"""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if webhook["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        return await webhook_service.get_webhook_health(webhook_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/webhooks/test-proxy")
async def test_webhook_proxy(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Proxy webhook test requests through backend"""
    try:
        data = await request.json()
        
        # Validate input
        if not data.get("target_url"):
            raise HTTPException(400, "Missing target_url")
            
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=data.get("method", "POST"),
                url=data["target_url"],
                headers=data.get("headers", {}),
                json=data.get("payload", {})
            )
            
            return {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }
            
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Proxy error: {str(e)}")