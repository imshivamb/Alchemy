from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from ...services.web3_service import Web3Service
from ...types.web3_types import TransferRequest, Web3Response, Web3ActionType
from ...core.auth import get_current_user

router = APIRouter()
web3_service = Web3Service()

@router.post("/transfer", response_model=Web3Response)
async def transfer(
    request: TransferRequest,
    workflow_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Intitate a transfer of SOL or a token"""
    try:
        if not await web3_service.validate_address(request.to_address):
            raise HTTPException(status_code=400, detail="Invalid recipient address")
        
        task_id = await web3_service.create_task(
            workflow_id=workflow_id,
            action_type=Web3ActionType.TRANSFER,
            network=request.network,
            params={
                "to_pubkey": request.to_address,
                "amount": request.amount,
                "token_mint": request.token_mint,
                "private_key": request.private_key
            },
            user_id=current_user["user_id"]
        )
        background_tasks.add_task(web3_service.process_task, task_id)
        
        return Web3Response(
            task_id=task_id,
            status="processing",
            message="Transaction initiated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

