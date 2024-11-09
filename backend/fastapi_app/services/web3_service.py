from redis_service.base import BaseRedis
from ..types.web3_types import Web3Network, Web3ActionType
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import base58
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts
from solana.rpc.commitment import Confirmed
from solana.token.async_client import AsyncToken
from solana.token.constants import TOKEN_PROGRAM_ID

class Web3Service(BaseRedis):
    def __init__(self):
        super().__init__()
        self.task_prefix = "web3_task:"
        self.clients = {
            Web3Network.MAINNET: AsyncClient("https://api.mainnet-beta.solana.com"),
            Web3Network.TESTNET: AsyncClient("https://api.testnet.solana.com"),
            Web3Network.DEVNET: AsyncClient("https://api.devnet.solana.com"),
        }
        
    async def create_task(
        self,
        workflow_id: str,
        action_type: Web3ActionType,
        network: Web3Network,
        params: Dict[str, Any],
        user_id: str
        ) -> str:
        """Create a new Web3 task"""
        task_id = str(uuid.uuid4())
        task_data = {
            "workflow_id": workflow_id,
            "action_type": action_type,
            "network": network,
            "params": params,
            "user_id": user_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "result": None,
            "error": None,
        }
        await self.set_data(
            f"{self.task_prefix}{task_id}",
            task_data,
            expires=86400
        )
        return task_id
    
    async def process_task(self, task_id: str) -> None:
        """Process a Web3 task"""
        try:
            task = await self.get_task_status(task_id)
            
            await self.update_task_progress(task_id, "processing")
            
            client = self.clients[task["network"]]
            
            result = await self._process_action(
                client,
                task["action_type"],
                task["params"]
            )
            
            await self.update_task_progress(task_id, status="completed", result=result)
        except Exception as e:
            await self.update_task_status(
                task_id,
                status="failed",
                error=str(e)
            )
            
    async def _process_action(
        self,
        client: AsyncClient,
        action_type: Web3ActionType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a Web3 action"""
        if action_type == Web3ActionType.TRANSFER:
            return await self._handle_transfer(client, params)
        elif action_type == Web3ActionType.BURN:
            return await self._handle_burn(client, params)
        elif action_type == Web3ActionType.MINT:
            return await self._handle_mint(client, params)
        elif action_type == Web3ActionType.STAKE:
            return await self._handle_stake(client, params)
        elif action_type == Web3ActionType.UNSTAKE:
            return await self._handle_unstake(client, params)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
        
    async def _handle_transfer(
        self, 
        client: AsyncClient,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a SOL transfer action"""
        try:
            if "token_mint" in params:
                
                token = AsyncToken(
                    conn=client,
                    pubkey=params["token_mint"],
                    program_id=TOKEN_PROGRAM_ID,
                    payer=Keypair.from_secret_key(base58.b58decode(params["private_key"]))
                )
                signature = await token.transfer(
                    source=params["from_token_account"],
                    dest=params["to_token_account"],
                    owner=params["owner"],
                    amount=params["amount"],
                )
            else:
                transfer_params = TransferParams(
                    from_pubkey=params["from_pubkey"],
                    to_pubkey=params["to_pubkey"],
                    lamports=params["amount"],
                )
                transaction = Transaction().add(
                    transfer(transfer_params)
                )
                signature = await client.send_transaction(
                    transaction,
                    Keypair.from_secret_key(
                        base58.b58decode(params["private_key"])
                    )
                )
            return {
                "signature": str(signature.value),
                "status": "success"
            }
        except Exception as e:
            raise Exception(f"Transfer failed: {str(e)}")
        
    async def _handle_mint(
        self,
        client: AsyncClient,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a mint action"""
        try:
            token = AsyncToken(
                conn=client,
                pubkey=params["token_mint"],
                program_id=TOKEN_PROGRAM_ID,
                payer=Keypair.from_secret_key(base58.b58decode(params["private_key"]))
            )
            signature = await token.mint_to(
                dest=params["destination"],
                mint_authority=params["mint_authority"],
                amount=params["amount"]
            )
            return {
                "signature": str(signature.value),
                "status": "success"
            }
        except Exception as e:
            raise Exception(f"Mint failed: {str(e)}")
        
    async def _handle_burn(
        self,
        client: AsyncClient,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a burn action"""
        try:
            token = AsyncToken(
                conn=client,
                pubkey=params["token_mint"],
                program_id=TOKEN_PROGRAM_ID,
                payer=Keypair.from_secret_key(base58.b58decode(params["private_key"]))
            )
            
            signature = await token.burn(
                source=params["source"],
                owner=params["owner"],
                amount=params["amount"]
            )
            return {
                "signature": str(signature.value),
                "status": "success"
            }
        except Exception as e:
            raise Exception(f"Burn failed: {str(e)}")
    
    # async def _handle_stake(
    #     self,
    #     client: AsyncClient,
    #     params: Dict[str, Any]
    # ) -> Dict[str, Any]:
    #     """Handle SOL staking"""
        
    #         # Implement staking logic using stake program
    #     # This would involve creating stake account, delegating to validator, etc.
    #     pass
    

    # async def _handle_unstake(self, client: AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Handle SOL unstaking"""
    #     try:
    #         # Implement unstaking logic
    #         # This would involve deactivating stake, withdrawing, etc.
    #         pass
    #     except Exception as e:
    #         raise Exception(f"Unstake failed: {str(e)}")
    
    async def get_token_info(self, network: Web3Network, token_mint: str) -> Dict[str, Any]:
        """Get token information"""
        try:
            client = self.clients[network]
            token = AsyncToken(
                conn=client,
                pubkey=token_mint,
                program_id=TOKEN_PROGRAM_ID,
                payer=None
            )
            
            mint_info = await token.get_mint_info()
            return {
                "decimals": mint_info.decimals,
                "supply": mint_info.supply,
                "freeze_authority": str(mint_info.freeze_authority) if mint_info.freeze_authority else None,
                "mint_authority": str(mint_info.mint_authority) if mint_info.mint_authority else None
            }
        except Exception as e:
            raise Exception(f"Failed to get token info: {str(e)}")
        
    # async def get_stake_info(self, network: Web3Network, stake_address: str) -> Dict[str, Any]:
    #     """Get stake account information"""
    #     try:
    #         client = self.clients[network]
    #         response = await client.get_stake_activation(stake_address)
    #         return {
    #             "state": response.value.state,
    #             "active": response.value.active,
    #             "inactive": response.value.inactive
    #         }
    #     except Exception as e:
    #         raise Exception(f"Failed to get stake info: {str(e)}")
    
    async def get_balance(self, network: Web3Network, address: str, token_mint: Optional[str] = None) -> Dict[str, Any]:
        """Get wallet or token account balance"""
        try:
            client = self.clients[network]
            if token_mint:
                token = AsyncToken(
                    conn=client,
                    pubkey=token_mint,
                    program_id=TOKEN_PROGRAM_ID,
                    payer=None
                )
                balance = await token.get_balance(address)
                decimals = await token.get_mint_info()
                
                return {
                    "balance": balance.value,
                    "decimals": decimals.decimals,
                    "token_mint": token_mint
                }
            else:
                response = await client.get_balance(address)
                return {
                    "balance": response.value,
                    "decimals": 9,
                    "token": "SOL"
                }
        except Exception as e:
            raise Exception(f"Failed to get balance: {str(e)}")
    async def monitor_transaction(
        self,
        network: Web3Network,
        signature: str
    ) -> Dict[str, Any]:
        """Monitor transaction status"""
        try:
            client = self.clients[network]
            response = await client.get_transaction(signature)
            
            if response.value is None:
                return {"status": "pending"}
                
            return {
                "status": "confirmed" if response.value.meta.err is None else "failed",
                "slot": response.value.slot,
                "error": str(response.value.meta.err) if response.value.meta.err else None
            }
            
        except Exception as e:
            raise Exception(f"Failed to monitor transaction: {str(e)}")

    async def validate_address(self, address: str) -> bool:
        """Validate Solana address format"""
        try:
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        except:
            return False
