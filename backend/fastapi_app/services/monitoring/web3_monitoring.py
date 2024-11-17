from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from enum import Enum
from ...types.web3_types import Web3Network, Web3ActionType, TransactionStatus, TokenConfig
from ....redis_service.base import BaseRedis

class MetricPeriod(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

class Web3Metrics(BaseModel):
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    total_volume: Dict[str, float] = {}  # By token/SOL
    average_gas_used: float = 0
    transactions_by_type: Dict[str, int] = {}
    transactions_by_network: Dict[str, int] = {}
    active_wallets: int = 0
    error_types: Dict[str, int] = {}
    average_confirmation_time: float = 0
    
class Web3Monitoring(BaseRedis):
    def __init__(self):
        super().__init__()
        self.metrics_key = "web3_metrics"
        self.transaction_key = "web3_transactions"
        
    async def track_transaction(
        self, 
        network: Web3Network,
        task_id: str,
        action_type: Web3ActionType,
        wallet: str,
        amount: Optional[float] = None,
        token: Optional[TokenConfig] = None,
        gas_used: Optional[float] = None,
        error: Optional[str] = None,
    ):
        """Track a transaction for metrics"""
        try:
            metrics = await self.get_current_metrics()
            
            
            #Updating basic metrics
            metrics.total_transactions += 1
            if error:
                metrics.failed_transactions += 1
                metrics.error_types[error] = metrics.error_types.get(error, 0) + 1
            else:
                metrics.successful_transactions += 1
            
            #Update transaction type metrics
            metrics.transactions_by_type[action_type] = metrics.transactions_by_type.get(action_type, 0) + 1
            
            #Update network metrics
            metrics.transactions_by_network[network] = metrics.transactions_by_network.get(network, 0) + 1
            
            #Update volume metrics
            if amount:
                token_key = f"{token.mint if token else 'SOL'}"
                metrics.total_volume[token_key] = metrics.total_volume.get(token_key, 0) + amount
            
            #Update gas metrics
            if gas_used:
                current_avg = metrics.average_gas_used
                total_tx = metrics.total_transactions
                metrics.average_gas_used = ((current_avg * (total_tx - 1)) + gas_used) / total_tx
            
            await self.save_metrics(metrics)
            
            await self._store_transaction_data(
                task_id,
                network,
                action_type,
                wallet,
                amount,
                token,
                gas_used,
                error
            )
        except Exception as e:
            raise Exception(f"Failed to track transaction: {str(e)}")
        
    async def get_current_metrics(self) -> Web3Metrics:
        """Get the current metrics"""
        try:
            metrics_data = await self.get_data(self.metrics_key)
            return Web3Metrics(**(metrics_data or {}))
        except Exception:
            return Web3Metrics()

    async def save_metrics(self, metrics: Web3Metrics):
        """Save metrics to Redis"""
        try:
            await self.set_data(self.metrics_key, metrics.dict())
        except Exception as e:
            raise Exception(f"Failed to save metrics: {str(e)}")
            
    async def get_metrics_by_period(
        self,
        period: MetricPeriod,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get metrics for a specific time period"""
        if not start_time:
            start_time = datetime.utcnow() - self._get_period_delta(period)
        if not end_time:
            end_time = datetime.utcnow()
            
        transactions = await self._get_transactions_in_period(start_time, end_time)
        return self._calculate_period_metrics(transactions)
    
    async def _store_transaction_data(
        self,
        task_id: str,
        network: Web3Network,
        action_type: Web3ActionType,
        wallet: str,
        amount: Optional[float],
        token: Optional[str],
        gas_used: Optional[float],
        error: Optional[str]
    ):
        """Store transaction data for time-series analysis"""
        transaction_data = {
            "task_id": task_id,
            "network": network,
            "action_type": action_type,
            "wallet": wallet,
            "amount": amount,
            "token": token,
            "gas_used": gas_used,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.zadd(
            self.transaction_key,
            {str(task_id): datetime.utcnow().timestamp()}
        )
        await self.set_data(
            f"{self.transaction_key}{task_id}",
            transaction_data,
            expires=86400 * 30  # 30 days
        )
    
    async def _get_transactions_in_period(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get transactions within a time period"""
        transaction_ids = await self.zrangebyscore(
            self.transaction_key,
            min=start_time.timestamp(),
            max=end_time.timestamp()
        )
        
        transactions = []
        for tx_id in transaction_ids:
            tx_data = await self.get_data(f"{self.transaction_key}{tx_id}")
            if tx_data:
                transactions.append(tx_data)
                
        return transactions

    async def zrangebyscore(self, key: str, min: float, max: float) -> List[str]:
        """Get range of values from sorted set by score"""
        try:
            return [x.decode() for x in await self.redis.zrangebyscore(key, min, max)]
        except Exception as e:
            raise Exception(f"Failed to get range by score: {str(e)}")

    async def zadd(self, key: str, mapping: Dict[str, float]):
        """Add to sorted set with scores"""
        try:
            await self.redis.zadd(key, mapping)
        except Exception as e:
            raise Exception(f"Failed to add to sorted set: {str(e)}")
    
    def _calculate_period_metrics(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate metrics for a set of transactions"""
        metrics = {
            "total_transactions": len(transactions),
            "successful_transactions": 0,
            "failed_transactions": 0,
            "volume_by_token": {},
            "transactions_by_type": {},
            "transactions_by_network": {},
            "unique_wallets": set(),
            "error_types": {}
        }
        
        for tx in transactions:
            # Count successes/failures
            if tx.get("error"):
                metrics["failed_transactions"] += 1
                error_type = tx["error"]
                metrics["error_types"][error_type] = (
                    metrics["error_types"].get(error_type, 0) + 1
                )
            else:
                metrics["successful_transactions"] += 1
            
            # Track volume
            if tx.get("amount"):
                token_key = tx.get("token", "SOL")
                metrics["volume_by_token"][token_key] = (
                    metrics["volume_by_token"].get(token_key, 0) + tx["amount"]
                )
            
            # Track by type and network
            metrics["transactions_by_type"][tx["action_type"]] = (
                metrics["transactions_by_type"].get(tx["action_type"], 0) + 1
            )
            metrics["transactions_by_network"][tx["network"]] = (
                metrics["transactions_by_network"].get(tx["network"], 0) + 1
            )
            
            # Track unique wallets
            metrics["unique_wallets"].add(tx["wallet"])
        
        # Convert wallet set to count
        metrics["unique_wallets"] = len(metrics["unique_wallets"])
        
        return metrics
    
    def _get_period_delta(self, period: MetricPeriod) -> timedelta:
        """Get timedelta for a period"""
        deltas = {
            MetricPeriod.MINUTE: timedelta(minutes=1),
            MetricPeriod.HOUR: timedelta(hours=1),
            MetricPeriod.DAY: timedelta(days=1),
            MetricPeriod.WEEK: timedelta(weeks=1),
            MetricPeriod.MONTH: timedelta(days=30),
        }
        return deltas[period]
