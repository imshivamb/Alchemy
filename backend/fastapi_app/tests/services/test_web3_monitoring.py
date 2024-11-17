import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from ...services.monitoring.web3_monitoring import (
    Web3Monitoring,
    MetricPeriod,
    Web3Metrics
)
from types.web3_types import Web3Network, Web3ActionType

@pytest.fixture
def monitoring():
    return Web3Monitoring()

@pytest.mark.asyncio
async def test_track_transaction(monitoring):
    # Arrange
    task_id = "test_task"
    network = Web3Network.DEVNET
    action_type = Web3ActionType.TRANSFER
    wallet = "test_wallet"
    amount = 1.0
    
    # Act
    await monitoring.track_transaction(
        task_id=task_id,
        network=network,
        action_type=action_type,
        wallet=wallet,
        amount=amount
    )
    
    # Assert
    metrics = await monitoring.get_current_metrics()
    assert metrics.total_transactions == 1
    assert metrics.successful_transactions == 1
    assert metrics.total_volume.get('SOL') == 1.0

@pytest.mark.asyncio
async def test_track_failed_transaction(monitoring):
    # Arrange
    task_id = "test_task"
    network = Web3Network.DEVNET
    action_type = Web3ActionType.TRANSFER
    wallet = "test_wallet"
    error = "insufficient_funds"
    
    # Act
    await monitoring.track_transaction(
        task_id=task_id,
        network=network,
        action_type=action_type,
        wallet=wallet,
        error=error
    )
    
    # Assert
    metrics = await monitoring.get_current_metrics()
    assert metrics.total_transactions == 1
    assert metrics.failed_transactions == 1
    assert metrics.error_types.get(error) == 1

@pytest.mark.asyncio
async def test_get_metrics_by_period(monitoring):
    # Arrange
    current_time = datetime.utcnow()
    
    # Add some test transactions
    for i in range(5):
        await monitoring.track_transaction(
            task_id=f"task_{i}",
            network=Web3Network.DEVNET,
            action_type=Web3ActionType.TRANSFER,
            wallet=f"wallet_{i}",
            amount=1.0
        )
    
    # Act
    metrics = await monitoring.get_metrics_by_period(
        period=MetricPeriod.HOUR,
        start_time=current_time - timedelta(hours=1),
        end_time=current_time
    )
    
    # Assert
    assert metrics["total_transactions"] == 5
    assert metrics["successful_transactions"] == 5
    assert metrics["unique_wallets"] == 5
    assert metrics["volume_by_token"]["SOL"] == 5.0

@pytest.mark.asyncio
async def test_metrics_expiry(monitoring):
    # Arrange
    task_id = "test_task"
    old_time = datetime.utcnow() - timedelta(days=31)
    
    # Act
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = old_time
        await monitoring.track_transaction(
            task_id=task_id,
            network=Web3Network.DEVNET,
            action_type=Web3ActionType.TRANSFER,
            wallet="test_wallet",
            amount=1.0
        )
    
    # Assert
    current_metrics = await monitoring.get_metrics_by_period(
        period=MetricPeriod.MONTH
    )
    assert current_metrics["total_transactions"] == 0