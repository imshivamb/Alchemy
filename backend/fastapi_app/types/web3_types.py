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
    
class MintRequest(BaseModel):
    network: Web3Network
    token_mint: str
    destination: str
    amount: float
    private_key: str = Field(..., exclude=True)
    mint_authority: Optional[str] = None
    
class BurnRequest(BaseModel):
    network: Web3Network
    token_mint: str
    amount: float
    source: str
    private_key: str = Field(..., exclude=True)
    mint_authority: Optional[str] = None
    
class StakeRequest(BaseModel):
    network: Web3Network
    validator: str
    amount: float
    private_key: str = Field(..., exclude=True)
    
class UnstakeRequest(BaseModel):
    network: Web3Network
    stake_account: str
    private_key: str = Field(..., exclude=True)
    
class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TokenConfig(BaseModel):
    mint: str
    decimals: int

class GasConfig(BaseModel):
    priority_fee: Optional[int] = None
    max_fee: Optional[int] = None

class Web3Config(BaseModel):
    network: Web3Network
    action_type: Web3ActionType
    amount: Optional[str]
    recipient: Optional[str]
    token: Optional[TokenConfig]
    contract_address: Optional[str]
    function_name: Optional[str]
    parameters: Optional[Dict[str, Any]]
    gas_config: Optional[GasConfig]