"""
Comprehensive Health Monitoring System

This module provides:
- Service status tracking with dependency checks
- Performance metrics collection and aggregation
- Alert thresholds and notification triggers
- Health check endpoints for monitoring dashboards
- System observability and diagnostic capabilities
"""

import asyncio
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil
from pydantic import BaseModel, Field


class ServiceStatus(str, Enum):
    """Service health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthCheckResult(BaseModel):
    """Result of a health check operation"""
    service_name: str
    status: ServiceStatus
    response_time_ms: float
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0


class SystemMetrics(BaseModel):
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    network_connections: int
    process_count: int
    uptime_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    """Health monitoring alert"""
    alert_id: str
    severity: AlertSeverity
    service_name: str
    message: str
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False


class HealthMonitor:
    """
    Comprehensive health monitoring system
    
    Features:
    - Real-time service health checks
    - Performance metrics collection
    - Alert management with thresholds
    - Dependency tracking and cascade detection
    """
    
    def __init__(self):
        self.services: Dict[str, HealthCheckResult] = {}
        self.metrics_history: List[SystemMetrics] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.start_time = time.time()
        self.check_intervals: Dict[str, int] = {}  # Service: interval in seconds
        self.alert_thresholds = self._initialize_thresholds()
        
    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize default alert thresholds"""
        return {
            "cpu": {
                "warning": 70.0,
                "error": 85.0,
                "critical": 95.0
            },
            "memory": {
                "warning": 75.0,
                "error": 90.0,
                "critical": 95.0
            },
            "disk": {
                "warning": 80.0,
                "error": 90.0,
                "critical": 95.0
            },
            "response_time": {
                "warning": 1000.0,  # ms
                "error": 3000.0,
                "critical": 5000.0
            }
        }
    
    async def check_service_health(
        self,
        service_name: str,
        check_function: callable,
        timeout_seconds: float = 5.0
    ) -> HealthCheckResult:
        """
        Check health of a specific service
        
        Args:
            service_name: Name of the service to check
            check_function: Async function that performs the health check
            timeout_seconds: Maximum time to wait for response
            
        Returns:
            HealthCheckResult with status and timing information
        """
        start_time = time.time()
        
        try:
            # Run health check with timeout
            await asyncio.wait_for(
                check_function(),
                timeout=timeout_seconds
            )
            
            response_time = (time.time() - start_time) * 1000
            status = ServiceStatus.HEALTHY
            message = "Service responding normally"
            
            # Check response time thresholds
            if response_time > self.alert_thresholds["response_time"]["error"]:
                status = ServiceStatus.DEGRADED
                message = f"High response time: {response_time:.2f}ms"
            
            result = HealthCheckResult(
                service_name=service_name,
                status=status,
                response_time_ms=response_time,
                message=message,
                consecutive_failures=0
            )
            
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Timeout after {timeout_seconds}s",
                consecutive_failures=self.services.get(service_name, HealthCheckResult(
                    service_name=service_name,
                    status=ServiceStatus.UNKNOWN,
                    response_time_ms=0
                )).consecutive_failures + 1
            )
            
        except Exception as e:
            result = HealthCheckResult(
                service_name=service_name,
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Health check failed: {str(e)}",
                consecutive_failures=self.services.get(service_name, HealthCheckResult(
                    service_name=service_name,
                    status=ServiceStatus.UNKNOWN,
                    response_time_ms=0
                )).consecutive_failures + 1
            )
        
        # Update service status
        self.services[service_name] = result
        
        # Generate alerts if needed
        await self._check_alerts(result)
        
        return result
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """
        Collect current system performance metrics
        
        Returns:
            SystemMetrics with current system state
        """
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            
            # Get network connections
            connections = len(psutil.net_connections())
            
            # Get process count
            process_count = len(psutil.pids())
            
            # Calculate uptime
            uptime = time.time() - self.start_time
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_connections=connections,
                process_count=process_count,
                uptime_seconds=uptime
            )
            
            # Store in history (keep last 1000 entries)
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)
            
            # Check metrics against thresholds
            await self._check_metrics_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            # Return empty metrics on error
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                network_connections=0,
                process_count=0,
                uptime_seconds=0.0
            )
    
    async def _check_alerts(self, result: HealthCheckResult):
        """Check if health check result should trigger alerts"""
        alert_id = f"{result.service_name}_health"
        
        if result.status == ServiceStatus.UNHEALTHY:
            if result.consecutive_failures >= 3:
                severity = AlertSeverity.CRITICAL
            elif result.consecutive_failures >= 2:
                severity = AlertSeverity.ERROR
            else:
                severity = AlertSeverity.WARNING
            
            alert = Alert(
                alert_id=alert_id,
                severity=severity,
                service_name=result.service_name,
                message=result.message or "Service health check failed",
                current_value=float(result.consecutive_failures),
                threshold_value=3.0
            )
            self.active_alerts[alert_id] = alert
            
        elif result.status == ServiceStatus.HEALTHY:
            # Resolve alert if service is now healthy
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].resolved = True
    
    async def _check_metrics_alerts(self, metrics: SystemMetrics):
        """Check system metrics against thresholds"""
        # Check CPU usage
        await self._check_threshold_alert(
            "cpu_usage",
            "CPU",
            metrics.cpu_percent,
            self.alert_thresholds["cpu"]
        )
        
        # Check memory usage
        await self._check_threshold_alert(
            "memory_usage",
            "Memory",
            metrics.memory_percent,
            self.alert_thresholds["memory"]
        )
        
        # Check disk usage
        await self._check_threshold_alert(
            "disk_usage",
            "Disk",
            metrics.disk_usage_percent,
            self.alert_thresholds["disk"]
        )
    
    async def _check_threshold_alert(
        self,
        alert_id: str,
        resource_name: str,
        current_value: float,
        thresholds: Dict[str, float]
    ):
        """Check a metric value against thresholds and create/resolve alerts"""
        if current_value >= thresholds["critical"]:
            severity = AlertSeverity.CRITICAL
        elif current_value >= thresholds["error"]:
            severity = AlertSeverity.ERROR
        elif current_value >= thresholds["warning"]:
            severity = AlertSeverity.WARNING
        else:
            # Below warning threshold, resolve any existing alert
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].resolved = True
            return
        
        # Create or update alert
        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            service_name=resource_name,
            message=f"{resource_name} usage is {current_value:.1f}%",
            current_value=current_value,
            threshold_value=thresholds[severity.value]
        )
        self.active_alerts[alert_id] = alert
    
    def get_overall_health_status(self) -> ServiceStatus:
        """
        Calculate overall system health status
        
        Returns:
            Worst status among all monitored services
        """
        if not self.services:
            return ServiceStatus.UNKNOWN
        
        statuses = [service.status for service in self.services.values()]
        
        if ServiceStatus.UNHEALTHY in statuses:
            return ServiceStatus.UNHEALTHY
        elif ServiceStatus.DEGRADED in statuses:
            return ServiceStatus.DEGRADED
        elif ServiceStatus.HEALTHY in statuses:
            return ServiceStatus.HEALTHY
        else:
            return ServiceStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive health summary
        
        Returns:
            Dictionary with overall health status and details
        """
        overall_status = self.get_overall_health_status()
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "services": {
                name: {
                    "status": service.status.value,
                    "response_time_ms": service.response_time_ms,
                    "message": service.message,
                    "last_check": service.timestamp.isoformat() if service.timestamp else None,
                    "consecutive_failures": service.consecutive_failures
                }
                for name, service in self.services.items()
            },
            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
            "total_alerts": len(self.active_alerts)
        }
    
    def get_metrics_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """
        Get aggregated metrics summary for a time window
        
        Args:
            window_minutes: Time window in minutes for aggregation
            
        Returns:
            Dictionary with aggregated metrics
        """
        if not self.metrics_history:
            return {
                "window_minutes": window_minutes,
                "data_points": 0,
                "cpu_avg": 0.0,
                "memory_avg": 0.0,
                "disk_avg": 0.0
            }
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            recent_metrics = self.metrics_history[-10:]  # Use last 10 if no recent data
        
        return {
            "window_minutes": window_minutes,
            "data_points": len(recent_metrics),
            "cpu_avg": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "cpu_max": max(m.cpu_percent for m in recent_metrics),
            "memory_avg": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            "memory_max": max(m.memory_percent for m in recent_metrics),
            "disk_avg": sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics),
            "connections_avg": sum(m.network_connections for m in recent_metrics) / len(recent_metrics)
        }
    
    def get_alerts(self, include_resolved: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of alerts
        
        Args:
            include_resolved: Whether to include resolved alerts
            
        Returns:
            List of alert dictionaries
        """
        alerts = list(self.active_alerts.values())
        
        if not include_resolved:
            alerts = [a for a in alerts if not a.resolved]
        
        return [
            {
                "alert_id": a.alert_id,
                "severity": a.severity.value,
                "service_name": a.service_name,
                "message": a.message,
                "current_value": a.current_value,
                "threshold_value": a.threshold_value,
                "timestamp": a.timestamp.isoformat(),
                "acknowledged": a.acknowledged,
                "resolved": a.resolved
            }
            for a in sorted(alerts, key=lambda x: x.timestamp, reverse=True)
        ]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: ID of the alert to acknowledge
            
        Returns:
            True if alert was acknowledged, False if not found
        """
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            return True
        return False


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get or create the global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor
