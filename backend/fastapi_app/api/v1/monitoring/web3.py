from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
from fastapi_app.services.monitoring.web3_monitoring import Web3Monitoring, MetricPeriod
from fastapi_app.core import require_admin, get_current_user


router = APIRouter()
monitoring = Web3Monitoring()

@router.get("/metrics/current")
async def get_current_metrics(
    current_user: dict = Depends(require_admin)
):
    """Get current Web3 metrics"""
    try:
        return await monitoring.get_current_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/period")
async def get_metrics_by_period(
    period: MetricPeriod,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: dict = Depends(require_admin)
):
    """Get metrics for a specific time period"""
    try:
        return await monitoring.get_metrics_by_period(
            period,
            start_time,
            end_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/wallet/{wallet}")
async def get_wallet_metrics(
    wallet: str,
    period: MetricPeriod = MetricPeriod.DAY,
    current_user: dict = Depends(get_current_user)
):
    """Get metrics for a specific wallet"""
    try:
        # Ensure user can only access their own wallet metrics
        if wallet != current_user.get("wallet"):
            raise HTTPException(
                status_code=403,
                detail="Can only access metrics for your own wallet"
            )
            
        return await monitoring.get_wallet_metrics(wallet, period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/gas")
async def get_gas_metrics(
    period: MetricPeriod = MetricPeriod.DAY,
    current_user: dict = Depends(require_admin)
):
    """Get gas usage metrics"""
    try:
        return await monitoring.get_gas_metrics(period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/errors")
async def get_error_metrics(
    period: MetricPeriod = MetricPeriod.DAY,
    current_user: dict = Depends(require_admin)
):
    """Get error metrics"""
    try:
        return await monitoring.get_error_metrics(period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
