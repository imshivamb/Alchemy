from redis_service.base import BaseRedis
from ...types.web3_types import Web3Network, Web3ActionType, TransactionStatus
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import base58
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey as PublicKey

from solana.rpc.types import TokenAccountOpts, TxOpts
from solana.rpc.commitment import Confirmed
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
# from solana.stake.program import StakeProgram
# from solana.stake.state import StakeState, Authorized, Lockup
from .constants import RPC_ENDPOINTS, DEFAULT_COMMITMENT, MAX_RETRIES, RETRY_DELAY, TRANSACTION_TIMEOUT, MINIMUM_SOL_BALANCE

class Web3Service(BaseRedis):
    def __init__(self):
        super().__init__()
        self.task_prefix = "web3_task:"
        self.clients = {
            network: AsyncClient(endpoint)
            for network, endpoint in RPC_ENDPOINTS.items()
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
        task_id = f"web3_{datetime.utcnow().timestamp()}"
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
            
            await self.update_task_progress(task_id, TransactionStatus.PROCESSING)
            
            client = self.clients[task["network"]]
            
            result = await self._process_action(
                client,
                task["action_type"],
                task["params"]
            )
            
            await self.update_task_progress(task_id, status=TransactionStatus.COMPLETED, result=result)
        except Exception as e:
            await self.update_task_status(
                task_id,
                status=TransactionStatus.FAILED,
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
    
    # async def _handle_stake(self, client: AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Handle SOL staking to a validator"""
    #     try:
    #         payer = Keypair.from_secret_key(
    #             base58.b58decode(params["private_key"])
    #         )
            
    #         stake_account = Keypair.generate()
            
    #         rent = await client.get_minimum_balance_for_rent_exemption(
    #             StakeState.get_size()
    #         )
            
    #         #Create stake account transaction
    #         create_stake_tx = Transaction().add(
    #             StakeProgram.create_account({
    #                 'from_pubkey': payer.public_key,
    #                 'stake_pubkey': stake_account.public_key,
    #                 'authorized': Authorized(
    #                     staker=payer.public_key,
    #                     withdrawer=payer.public_key,
    #                 ),
    #                 'lockup': Lockup(
    #                     unix_timestamp=0,
    #                     epoch=0,
    #                     custodian=payer.public_key,
    #                 ),
    #                 'lamports': params["amount"] + rent
    #             })
    #         )
    #         create_signature = await client.send_transaction(
    #             create_stake_tx,
    #             payer,
    #             stake_account,
    #             opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    #         )
            
    #         delegate_tx = Transaction().add(
    #             StakeProgram.delegate_stake(
    #                 stake_pubkey=stake_account.public_key,
    #                 authorized_pubkey=payer.public_key,
    #                 vote_pubkey=params["validator"]
    #             )
    #         )
            
    #         delegate_signature = await client.send_transaction(
    #             delegate_tx,
    #             payer,
    #             opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    #         )
            
    #         return {
    #             "status": "success",
    #             "stake_account": str(stake_account.public_key),
    #             "create_signature": str(create_signature.value),
    #             "delegate_signature": str(delegate_signature.value),
    #             "amount": params["amount"],
    #             "validator": params["validator"]
    #         }
    #     except Exception as e:
    #         raise Exception(f"Staking failed: {str(e)}")
        
    # async def _handle_unstake(self, client: AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
    #     """Handle SOL unstaking"""
    #     try:
    #         payer = Keypair.from_secret_key(
    #             base58.b58decode(params["private_key"])
    #         )
            
    #         deactivate_tx = Transaction().add(
    #             StakeProgram.deactivate_stake(
    #                 stake_pubkey=params["stake_account"],
    #                 authorized_pubkey=payer.public_key
    #             )
    #         )
            
    #         deactivate_signature = await client.send_transaction(
    #             deactivate_tx,
    #             payer,
    #             opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    #         )
            
    #         stake_info = await self.get_stake_info(
    #             params["network"],
    #             params["stake_account"]
    #         )
            
    #         return {
    #             "status": "deactivating",
    #             "signature": str(deactivate_signature.value),
    #             "stake_account": params["stake_account"],
    #             "current_epoch": stake_info["epoch"],
    #             "estimated_cooldown_epochs": 2,
    #             "message": "Stake account deactivated. Funds will be available after cooldown period."
    #         }
    #     except Exception as e:
    #         raise Exception(f"Unstaking failed: {str(e)}")
        
    # async def withdraw_unstaked(
    #     self,
    #     network: Web3Network,
    #     stake_account: str,
    #     recipient: str,
    #     private_key: str
    # ) -> Dict[str, Any]:
    #     """
    #     Withdraw deactivated stake to recipient address
    #     """
    #     try:
    #         client = self.clients[network]
    #         payer = Keypair.from_secret_key(base58.b58decode(private_key))
            
    #         # Check stake account status
    #         stake_info = await self.get_stake_info(network, stake_account)
    #         if stake_info["state"] != "inactive":
    #             raise Exception("Stake account is not ready for withdrawal")
                
    #         # Create withdraw transaction
    #         withdraw_tx = Transaction().add(
    #             StakeProgram.withdraw(
    #                 stake_pubkey=stake_account,
    #                 authorized_pubkey=payer.public_key,
    #                 to_pubkey=recipient,
    #                 lamports=stake_info["inactive"]
    #             )
    #         )
            
    #         # Sign and send withdrawal transaction
    #         signature = await client.send_transaction(
    #             withdraw_tx,
    #             payer,
    #             opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    #         )
            
    #         return {
    #             "status": "success",
    #             "signature": str(signature.value),
    #             "amount": stake_info["inactive"],
    #             "recipient": recipient
    #         }
            
    #     except Exception as e:
    #         raise Exception(f"Withdrawal failed: {str(e)}")
    
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
        
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and details"""
        task_data = await self.get_data(f"{self.task_prefix}{task_id}")
        if not task_data:
            raise ValueError(f"Task {task_id} not found")
        return task_data

    async def get_stake_info(self, network: Web3Network, stake_account: str) -> Dict[str, Any]:
        """Get stake account information"""
        try:
            client = self.clients[network]
            response = await client.get_stake_activation(stake_account)
            
            stake_data = {
                "state": response.value.state,
                "active": response.value.active,
                "inactive": response.value.inactive,
                "epoch": response.value.epoch
            }
            
            # Get additional stake account info
            account_info = await client.get_account_info(stake_account)
            if account_info.value:
                stake_data.update({
                    "lamports": account_info.value.lamports,
                    "owner": str(account_info.value.owner),
                    "executable": account_info.value.executable,
                    "rent_epoch": account_info.value.rent_epoch
                })
                
            return stake_data
        except Exception as e:
            raise Exception(f"Failed to get stake info: {str(e)}")
    
    async def list_validators(
        self,
        network: Web3Network,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get list of active validators with their details"""
        try:
            client = self.clients[network]
            
            # Get vote accounts
            response = await client.get_vote_accounts()
            
            validators = []
            for validator in response.value.current:
                validators.append({
                    "pubkey": str(validator.vote_pubkey),
                    "node_pubkey": str(validator.node_pubkey),
                    "activated_stake": validator.activated_stake,
                    "commission": validator.commission,
                    "last_vote": validator.last_vote,
                    "root_slot": validator.root_slot,
                    "credits": validator.epoch_credits[-1][1] if validator.epoch_credits else 0,
                    "epoch_vote_account": True
                })
                
            # Sort by activated stake descending
            validators.sort(key=lambda x: x["activated_stake"], reverse=True)
            
            # Apply pagination
            return validators[offset:offset + limit]
            
        except Exception as e:
            raise Exception(f"Failed to get validators: {str(e)}")

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Dict[str, Any] = None,
        error: str = None
    ) -> None:
        """Update task status in Redis"""
        task_data = await self.get_task_status(task_id)
        task_data.update({
            "status": status,
            "result": result,
            "error": error,
            "updated_at": datetime.utcnow().isoformat()
        })
        await self.set_data(f"{self.task_prefix}{task_id}", task_data)