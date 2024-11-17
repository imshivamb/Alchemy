from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import Optional
from ...services.web3.web3_service import Web3Service
from ...types.web3_types import TransferRequest, Web3Response, Web3ActionType, Web3Network, MintRequest, BurnRequest, StakeRequest, UnstakeRequest
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
    
@router.get("/balance/{address}")
async def get_balance(
    address: str,
    network: Web3Network,
    token_mint: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get wallet or token balance
    """
    try:
        return await web3_service.get_balance(network, address, token_mint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/token/{token_mint}")
async def get_token_info(
    token_mint: str,
    network: Web3Network,
    current_user: dict = Depends(get_current_user)
):
    """Get token info"""
    try:
        return await web3_service.get_token_info(network, token_mint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/mint", response_model=Web3Response)
async def mint_tokens(
    request: MintRequest,
    workflow_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Mint tokens"""
    try:
        if not await web3_service.validate_address(request.destination):
            raise HTTPException(status_code=400, detail="Invalid destination address")
        
        task_id = await web3_service.create_task(
            workflow_id=workflow_id,
            action_type=Web3ActionType.MINT,
            network=request.network,
            params={
                "token_mint": request.token_mint,
                "destination": request.destination,
                "amount": request.amount,
                "private_key": request.private_key,
                "mint_authority": request.mint_authority
            },
            user_id=current_user["user_id"]
        )
        
        background_tasks.add_task(web3_service.process_task, task_id)
        
        return Web3Response(
            task_id=task_id,
            status="processing",
            message="Token minting initiated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/burn", response_model=Web3Response)
async def burn_tokens(
    request: BurnRequest,
    workflow_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Burn tokens"""
    try:
        task_id = await web3_service.create_task(
            workflow_id=workflow_id,
            action_type=Web3ActionType.BURN,
            network=request.network,
            params={
                "token_mint": request.token_mint,
                "amount": request.amount,
                "source": request.source,
                "private_key": request.private_key,
            },
            user_id=current_user["user_id"]
        )
        
        background_tasks.add_task(web3_service.process_task, task_id)
        
        return Web3Response(
            task_id=task_id,
            status="processing",
            message="Token burning initiated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/stake", response_model=Web3Response)
async def stake_sol(
    request: StakeRequest,
    workflow_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Stake SOL to a validator"""
    try:
        if not await web3_service.validate_address(request.validator):
            raise HTTPException(status_code=400, detail="Invalid validator address")
        
        task_id = await web3_service.create_task(
            workflow_id=workflow_id,
            action_type=Web3ActionType.STAKE,
            network=request.network,
            params={
                "amount": request.amount,
                "validator": request.validator,
                "private_key": request.private_key
            },
            user_id=current_user["user_id"]
        )
        background_tasks.add_task(web3_service.process_task, task_id)
        
        return Web3Response(
            task_id=task_id,
            status="processing",
            message="SOL staking initiated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/unstake", response_model=Web3Response)
async def unstake_sol(
    request: UnstakeRequest,
    workflow_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Unstake SOL from a validator"""
    try:
        task_id = await web3_service.create_task(
            workflow_id=workflow_id,
            action_type=Web3ActionType.UNSTAKE,
            network=request.network,
            params={
                "stake_account": request.stake_account,
                "private_key": request.private_key
            },
            user_id=current_user["user_id"]
        )
        background_tasks.add_task(web3_service.process_task, task_id)
        
        return Web3Response(
            task_id=task_id,
            status="processing",
            message="SOL unstaking initiated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stake/{stake_account}")
async def get_stake_info(
    stake_account: str,
    network: Web3Network,
    current_user: dict = Depends(get_current_user)
):
    """Get stake info"""
    try:
        return await web3_service.get_stake_info(network, stake_account)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get task status"""
    try:
        task = await web3_service.get_task_status(task_id)
        if task["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return task
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/tasks")
async def list_tasks(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    current_user: dict = Depends(get_current_user)
):
    """List tasks with optional filters"""
    try:
        return await web3_service.list_tasks(
            workflow_id=workflow_id,
            status=status,
            limit=limit,
            offset=offset,
            user_id=current_user["user_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/validate/{address}")
async def validate_address(address: str):
    """Validate Solana address format"""
    return {
        "valid": await web3_service.validate_address(address)
    }

@router.get("/networks")
async def list_networks():
    """List available networks and their status"""
    return [
        {
            "id": network.value,
            "name": network.name,
            "status": "active"
        }
        for network in Web3Network
    ]

@router.get("/validators/{network}")
async def list_validators(
    network: Web3Network,
    current_user: dict = Depends(get_current_user)
):
    """List active validators for a network"""
    try:
        return await web3_service.list_validators(network)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))