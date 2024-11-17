# tests/services/test_webhook_monitoring.py

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi_app.services.monitoring.webhook_monitoring import (
    WebhookMonitoring,
    WebhookMetricPeriod,
    WebhookMetrics
)

@pytest.fixture
async def monitoring():
    monitoring = WebhookMonitoring()
    yield monitoring
    # Clean up Redis after each test
    await monitoring.redis.flushdb()

@pytest.mark.asyncio
async def test_track_delivery(monitoring):
    # Arrange
    webhook_id = "test_webhook"
    delivery_id = "test_delivery"
    status_code = 200
    response_time = 150.0
    
    # Act
    await monitoring.track_delivery(
        webhook_id=webhook_id,
        delivery_id=delivery_id,
        status_code=status_code,
        response_time=response_time
    )
    
    # Assert
    metrics = await monitoring.get_current_metrics()
    assert metrics.total_deliveries == 1
    assert metrics.successful_deliveries == 1
    assert metrics.status_codes.get("2xx") == 1
    assert metrics.average_response_time == response_time

@pytest.mark.asyncio
async def test_track_failed_delivery(monitoring):
    # Arrange
    webhook_id = "test_webhook"
    delivery_id = "test_delivery"
    error = "timeout"
    
    # Act
    await monitoring.track_delivery(
        webhook_id=webhook_id,
        delivery_id=delivery_id,
        error=error
    )
    
    # Assert
    metrics = await monitoring.get_current_metrics()
    assert metrics.total_deliveries == 1
    assert metrics.failed_deliveries == 1
    assert metrics.error_types.get(error) == 1

@pytest.mark.asyncio
async def test_webhook_health(monitoring):
    # Arrange
    webhook_id = "test_webhook"
    
    # Add some test deliveries
    for i in range(10):
        await monitoring.track_delivery(
            webhook_id=webhook_id,
            delivery_id=f"delivery_{i}",
            status_code=200,
            response_time=100.0
        )
    
    # Add one failed delivery
    await monitoring.track_delivery(
        webhook_id=webhook_id,
        delivery_id="failed_delivery",
        error="timeout"
    )
    
    # Act
    health = await monitoring.get_webhook_health(webhook_id)
    
    # Assert
    assert health["health_score"] > 0
    assert "status" in health
    assert health["metrics"]["total_deliveries"] == 11
    assert health["metrics"]["failed_deliveries"] == 1

