from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class Web3Network(Enum):
    MAINNET = "solana-mainnet"
    TESTNET = "solana-testnet"
    DEVNET = "solana-devnet"
    
class Web3ActionType(str,Enum):
    TRANSFER = "transfer"
    MINT = "mint"
    BURN = "burn"
    STAKE = "stake"
    UNSTAKE = "unstake"
    
class TransferRequest(BaseModel):
    network: Web3Network
    to_address: str
    amount: float
    token_mint: Optional[str] = None
    private_key: str = Field(..., exclude=True )
    
class Web3Response(BaseModel):
    task_id: str
    status: str
    message: str
    

