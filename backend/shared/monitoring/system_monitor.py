# backend/shared/monitoring/system_monitor.py

from typing import Dict, Any, List
import psutil
import asyncio
from datetime import datetime
from .metrics_collector import MetricsCollector, MetricType

class SystemMonitor:
    """
    Monitor system resources and performance
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.collection_interval = 60  # 1 minute
        
    async def start_monitoring(self):
        """
        Start system monitoring
        """
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self.collection_interval)
                
    async def _collect_system_metrics(self):
        """
        Collect various system metrics
        """
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        await self.metrics_collector.collect_metric(
            "system.cpu.utilization",
            cpu_percent,
            MetricType.GAUGE,
            {"unit": "percent"}
        )
        
        # Memory metrics
        memory = psutil.virtual_memory()
        await self.metrics_collector.collect_metric(
            "system.memory.usage",
            memory.percent,
            MetricType.GAUGE,
            {"unit": "percent"}
        )
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        await self.metrics_collector.collect_metric(
            "system.disk.usage",
            disk.percent,
            MetricType.GAUGE,
            {"unit": "percent"}
        )
        
        # Network metrics
        net_io = psutil.net_io_counters()
        await self.metrics_collector.collect_metric(
            "system.network.bytes_sent",
            net_io.bytes_sent,
            MetricType.COUNTER,
            {"unit": "bytes"}
        )
        await self.metrics_collector.collect_metric(
            "system.network.bytes_recv",
            net_io.bytes_recv,
            MetricType.COUNTER,
            {"unit": "bytes"}
        )