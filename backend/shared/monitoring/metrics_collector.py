# backend/shared/monitoring/metrics_collector.py

from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
import asyncio
import json
from redis_service.base import BaseRedis
from dataclasses import dataclass
from enum import Enum

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricValue:
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str]

class MetricsCollector(BaseRedis):
    """
    Collect and manage system metrics
    """
    
    def __init__(self):
        super().__init__()
        self.metrics_prefix = "metrics:"
        self.aggregation_intervals = [
            300,    # 5 minutes
            3600,   # 1 hour
            86400,  # 1 day
        ]
        
    async def collect_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType,
        tags: Dict[str, str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Collect metric with proper storage and aggregation
        """
        timestamp = timestamp or datetime.utcnow()
        tags = tags or {}
        
        # Store raw metric
        await self._store_metric(name, value, metric_type, tags, timestamp)
        
        # Aggregate metrics
        await self._aggregate_metric(name, value, metric_type, tags, timestamp)
        
        # Publish metric event
        await self._publish_metric(name, value, metric_type, tags, timestamp)
        
    async def get_metrics(
        self,
        name: str,
        start_time: datetime,
        end_time: datetime,
        interval: int = 300,
        tags: Dict[str, str] = None
    ) -> List[MetricValue]:
        """
        Get metrics for specified time range
        """
        # Find appropriate aggregation level
        agg_interval = self._get_aggregation_interval(start_time, end_time)
        
        # Get metrics from storage
        metrics = await self._get_aggregated_metrics(
            name, start_time, end_time, agg_interval, tags
        )
        
        return metrics
        
    async def _store_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType,
        tags: Dict[str, str],
        timestamp: datetime
    ):
        """
        Store raw metric
        """
        metric_key = self._get_metric_key(name, tags)
        metric_data = {
            'value': value,
            'type': metric_type.value,
            'tags': tags,
            'timestamp': timestamp.isoformat()
        }
        
        # Store in time series
        await self.redis.zadd(
            f"{self.metrics_prefix}raw:{metric_key}",
            {json.dumps(metric_data): timestamp.timestamp()}
        )
        
        # Expire raw data after 24 hours
        await self.redis.expire(
            f"{self.metrics_prefix}raw:{metric_key}",
            86400
        )
        
    async def _aggregate_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType,
        tags: Dict[str, str],
        timestamp: datetime
    ):
        """
        Aggregate metrics for different time intervals
        """
        metric_key = self._get_metric_key(name, tags)
        
        for interval in self.aggregation_intervals:
            bucket_timestamp = self._get_bucket_timestamp(timestamp, interval)
            
            # Update aggregations based on metric type
            if metric_type == MetricType.COUNTER:
                await self._aggregate_counter(
                    metric_key, value, bucket_timestamp, interval
                )
            elif metric_type == MetricType.GAUGE:
                await self._aggregate_gauge(
                    metric_key, value, bucket_timestamp, interval
                )
            elif metric_type == MetricType.HISTOGRAM:
                await self._aggregate_histogram(
                    metric_key, value, bucket_timestamp, interval
                )
                
    async def _aggregate_counter(
        self,
        metric_key: str,
        value: Union[int, float],
        bucket_timestamp: datetime,
        interval: int
    ):
        """
        Aggregate counter metrics
        """
        key = f"{self.metrics_prefix}agg:{interval}:{metric_key}"
        await self.redis.hincrby(
            key,
            bucket_timestamp.timestamp(),
            int(value)
        )
        
    async def _aggregate_gauge(
        self,
        metric_key: str,
        value: Union[int, float],
        bucket_timestamp: datetime,
        interval: int
    ):
        """
        Aggregate gauge metrics
        """
        key = f"{self.metrics_prefix}agg:{interval}:{metric_key}"
        await self.redis.hset(
            key,
            bucket_timestamp.timestamp(),
            value
        )
        
    async def _aggregate_histogram(
        self,
        metric_key: str,
        value: Union[int, float],
        bucket_timestamp: datetime,
        interval: int
    ):
        """
        Aggregate histogram metrics
        """
        key = f"{self.metrics_prefix}agg:{interval}:{metric_key}"
        # Update histogram buckets
        for bucket in self._get_histogram_buckets():
            if value <= bucket:
                await self.redis.hincrby(
                    f"{key}:bucket:{bucket}",
                    bucket_timestamp.timestamp(),
                    1
                )
                break
                
    def _get_bucket_timestamp(
        self,
        timestamp: datetime,
        interval: int
    ) -> datetime:
        """
        Get normalized timestamp for the interval
        """
        return datetime.fromtimestamp(
            (timestamp.timestamp() // interval) * interval
        )
        
    def _get_metric_key(self, name: str, tags: Dict[str, str]) -> str:
        """
        Generate metric key from name and tags
        """
        tag_string = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}:{tag_string}" if tag_string else name
        
    def _get_histogram_buckets(self) -> List[float]:
        """
        Get histogram buckets
        """
        return [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10]
        
    def _get_aggregation_interval(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> int:
        """
        Determine the best aggregation interval based on time range
        """
        time_range = (end_time - start_time).total_seconds()
        
        if time_range <= 3600:  # 1 hour
            return 300  # 5 minute aggregation
        elif time_range <= 86400:  # 1 day
            return 3600  # 1 hour aggregation
        else:
            return 86400  # 1 day aggregation
            
    async def _get_aggregated_metrics(
        self,
        name: str,
        start_time: datetime,
        end_time: datetime,
        interval: int,
        tags: Dict[str, str] = None
    ) -> List[MetricValue]:
        """
        Retrieve aggregated metrics for time range
        """
        metric_key = self._get_metric_key(name, tags)
        key = f"{self.metrics_prefix}agg:{interval}:{metric_key}"
        
        # Get all metrics in time range
        metrics = []
        current_time = start_time
        
        while current_time <= end_time:
            bucket_timestamp = self._get_bucket_timestamp(current_time, interval)
            value = await self.redis.hget(key, str(bucket_timestamp.timestamp()))
            
            if value is not None:
                metrics.append(
                    MetricValue(
                        value=float(value),
                        timestamp=bucket_timestamp,
                        tags=tags or {}
                    )
                )
                
            current_time += timedelta(seconds=interval)
            
        return metrics