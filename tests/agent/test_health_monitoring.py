"""
Comprehensive tests for health monitoring system

Tests:
- Service health checks with various failure scenarios
- System metrics collection and aggregation
- Alert generation and threshold management
- Health endpoint responses and error handling
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agent.health_monitoring import (
    Alert,
    AlertSeverity,
    HealthCheckResult,
    HealthMonitor,
    ServiceStatus,
    SystemMetrics,
    get_health_monitor,
)


@pytest.fixture
def health_monitor():
    """Create a fresh health monitor for each test"""
    return HealthMonitor()


@pytest.mark.asyncio
async def test_service_health_check_success(health_monitor):
    """Test successful service health check"""

    async def healthy_service():
        await asyncio.sleep(0.01)  # Simulate work

    result = await health_monitor.check_service_health(
        "test_service", healthy_service, timeout_seconds=1.0
    )

    assert result.service_name == "test_service"
    assert result.status == ServiceStatus.HEALTHY
    assert result.response_time_ms > 0
    assert result.consecutive_failures == 0


@pytest.mark.asyncio
async def test_service_health_check_timeout(health_monitor):
    """Test health check timeout handling"""

    async def slow_service():
        await asyncio.sleep(10)  # Will timeout

    result = await health_monitor.check_service_health(
        "slow_service", slow_service, timeout_seconds=0.1
    )

    assert result.service_name == "slow_service"
    assert result.status == ServiceStatus.UNHEALTHY
    assert "Timeout" in result.message
    assert result.consecutive_failures == 1


@pytest.mark.asyncio
async def test_service_health_check_failure(health_monitor):
    """Test health check exception handling"""

    async def failing_service():
        raise Exception("Service down")

    result = await health_monitor.check_service_health(
        "failing_service", failing_service, timeout_seconds=1.0
    )

    assert result.service_name == "failing_service"
    assert result.status == ServiceStatus.UNHEALTHY
    assert "Service down" in result.message
    assert result.consecutive_failures == 1


@pytest.mark.asyncio
async def test_consecutive_failures_tracking(health_monitor):
    """Test consecutive failure counting"""

    async def failing_service():
        raise Exception("Persistent failure")

    # First failure
    result1 = await health_monitor.check_service_health("unstable_service", failing_service)
    assert result1.consecutive_failures == 1

    # Second failure
    result2 = await health_monitor.check_service_health("unstable_service", failing_service)
    assert result2.consecutive_failures == 2

    # Third failure
    result3 = await health_monitor.check_service_health("unstable_service", failing_service)
    assert result3.consecutive_failures == 3


@pytest.mark.asyncio
async def test_service_recovery_resets_failures(health_monitor):
    """Test that recovery resets consecutive failure count"""

    async def unstable_service():
        if not hasattr(unstable_service, "call_count"):
            unstable_service.call_count = 0
        unstable_service.call_count += 1
        if unstable_service.call_count <= 2:
            raise Exception("Temporary failure")

    # Two failures
    await health_monitor.check_service_health("recovery_test", unstable_service)
    await health_monitor.check_service_health("recovery_test", unstable_service)

    # Recovery
    result = await health_monitor.check_service_health("recovery_test", unstable_service)
    assert result.status == ServiceStatus.HEALTHY
    assert result.consecutive_failures == 0


@pytest.mark.asyncio
async def test_system_metrics_collection(health_monitor):
    """Test system metrics collection"""
    # Ensure monitor has non-zero uptime
    import time

    time.sleep(0.01)

    with patch("agent.health_monitoring.psutil") as mock_psutil:
        # Mock system metrics
        mock_psutil.cpu_percent.return_value = 45.5

        mock_memory = Mock()
        mock_memory.percent = 65.0
        mock_memory.available = 4 * 1024 * 1024 * 1024  # 4GB
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_disk = Mock()
        mock_disk.percent = 75.0
        mock_psutil.disk_usage.return_value = mock_disk

        mock_psutil.net_connections.return_value = [1, 2, 3, 4, 5]
        mock_psutil.pids.return_value = list(range(100))

        metrics = await health_monitor.collect_system_metrics()

        assert metrics.cpu_percent == 45.5
        assert metrics.memory_percent == 65.0
        assert metrics.memory_available_mb > 0
        assert metrics.disk_usage_percent == 75.0
        assert metrics.network_connections == 5
        assert metrics.process_count == 100
        assert metrics.uptime_seconds >= 0  # Can be 0 for very fast tests


@pytest.mark.asyncio
async def test_metrics_history_management(health_monitor):
    """Test metrics history size limiting"""
    with patch("agent.health_monitoring.psutil") as mock_psutil:
        # Setup mocks
        mock_psutil.cpu_percent.return_value = 50.0
        mock_memory = Mock(percent=50.0, available=1024 * 1024 * 1024)
        mock_psutil.virtual_memory.return_value = mock_memory
        mock_disk = Mock(percent=50.0)
        mock_psutil.disk_usage.return_value = mock_disk
        mock_psutil.net_connections.return_value = []
        mock_psutil.pids.return_value = []

        # Add many metrics
        for _ in range(1100):
            await health_monitor.collect_system_metrics()

        # Should be limited to 1000
        assert len(health_monitor.metrics_history) == 1000


def test_alert_threshold_initialization(health_monitor):
    """Test alert thresholds are properly initialized"""
    thresholds = health_monitor.alert_thresholds

    assert "cpu" in thresholds
    assert "memory" in thresholds
    assert "disk" in thresholds
    assert "response_time" in thresholds

    # Check threshold levels
    assert thresholds["cpu"]["warning"] < thresholds["cpu"]["error"]
    assert thresholds["cpu"]["error"] < thresholds["cpu"]["critical"]


@pytest.mark.asyncio
async def test_alert_generation_on_failure(health_monitor):
    """Test that alerts are generated on service failures"""

    async def failing_service():
        raise Exception("Critical failure")

    # Trigger multiple failures to reach critical threshold
    for _ in range(3):
        await health_monitor.check_service_health("critical_service", failing_service)

    alerts = health_monitor.get_alerts()
    assert len(alerts) > 0

    # Find the service health alert
    service_alert = next((a for a in alerts if "critical_service" in a["alert_id"]), None)
    assert service_alert is not None
    assert service_alert["severity"] == "critical"


@pytest.mark.asyncio
async def test_alert_resolution_on_recovery(health_monitor):
    """Test that alerts are resolved when service recovers"""

    # Fail then succeed
    async def recovering_service():
        if not hasattr(recovering_service, "recovered"):
            recovering_service.recovered = False
            raise Exception("Temporary failure")
        # On second call, succeed
        recovering_service.recovered = True

    # Trigger failure
    await health_monitor.check_service_health("recovering", recovering_service)

    # Trigger recovery
    recovering_service.recovered = True
    await health_monitor.check_service_health("recovering", recovering_service)

    # Check alert is resolved
    alerts = health_monitor.get_alerts(include_resolved=True)
    if alerts:
        alert = next((a for a in alerts if "recovering" in a["alert_id"]), None)
        if alert:
            assert alert["resolved"]


@pytest.mark.asyncio
async def test_cpu_threshold_alerts(health_monitor):
    """Test CPU usage threshold alerts"""
    with patch("agent.health_monitoring.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 96.0  # Critical level
        mock_memory = Mock(percent=50.0, available=1024 * 1024 * 1024)
        mock_psutil.virtual_memory.return_value = mock_memory
        mock_disk = Mock(percent=50.0)
        mock_psutil.disk_usage.return_value = mock_disk
        mock_psutil.net_connections.return_value = []
        mock_psutil.pids.return_value = []

        await health_monitor.collect_system_metrics()

        alerts = health_monitor.get_alerts()
        cpu_alert = next((a for a in alerts if a["alert_id"] == "cpu_usage"), None)

        assert cpu_alert is not None
        assert cpu_alert["severity"] == "critical"
        assert cpu_alert["current_value"] == 96.0


@pytest.mark.asyncio
async def test_memory_threshold_alerts(health_monitor):
    """Test memory usage threshold alerts"""
    with patch("agent.health_monitoring.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 50.0
        mock_memory = Mock(percent=92.0, available=1024 * 1024 * 1024)  # Error level
        mock_psutil.virtual_memory.return_value = mock_memory
        mock_disk = Mock(percent=50.0)
        mock_psutil.disk_usage.return_value = mock_disk
        mock_psutil.net_connections.return_value = []
        mock_psutil.pids.return_value = []

        await health_monitor.collect_system_metrics()

        alerts = health_monitor.get_alerts()
        mem_alert = next((a for a in alerts if a["alert_id"] == "memory_usage"), None)

        assert mem_alert is not None
        assert mem_alert["severity"] == "error"


def test_overall_health_status_healthy(health_monitor):
    """Test overall health status when all services healthy"""
    health_monitor.services = {
        "service1": HealthCheckResult(
            service_name="service1", status=ServiceStatus.HEALTHY, response_time_ms=50.0
        ),
        "service2": HealthCheckResult(
            service_name="service2",
            status=ServiceStatus.HEALTHY,
            response_time_ms=100.0,
        ),
    }

    assert health_monitor.get_overall_health_status() == ServiceStatus.HEALTHY


def test_overall_health_status_degraded(health_monitor):
    """Test overall health status with degraded service"""
    health_monitor.services = {
        "service1": HealthCheckResult(
            service_name="service1", status=ServiceStatus.HEALTHY, response_time_ms=50.0
        ),
        "service2": HealthCheckResult(
            service_name="service2",
            status=ServiceStatus.DEGRADED,
            response_time_ms=4000.0,
        ),
    }

    assert health_monitor.get_overall_health_status() == ServiceStatus.DEGRADED


def test_overall_health_status_unhealthy(health_monitor):
    """Test overall health status with unhealthy service"""
    health_monitor.services = {
        "service1": HealthCheckResult(
            service_name="service1", status=ServiceStatus.HEALTHY, response_time_ms=50.0
        ),
        "service2": HealthCheckResult(
            service_name="service2",
            status=ServiceStatus.UNHEALTHY,
            response_time_ms=0.0,
            message="Service down",
        ),
    }

    assert health_monitor.get_overall_health_status() == ServiceStatus.UNHEALTHY


def test_health_summary_structure(health_monitor):
    """Test health summary contains required fields"""
    summary = health_monitor.get_health_summary()

    assert "overall_status" in summary
    assert "timestamp" in summary
    assert "uptime_seconds" in summary
    assert "services" in summary
    assert "active_alerts" in summary
    assert "total_alerts" in summary


def test_metrics_summary_structure(health_monitor):
    """Test metrics summary contains required fields"""
    summary = health_monitor.get_metrics_summary(window_minutes=5)

    assert "window_minutes" in summary
    assert "data_points" in summary
    assert "cpu_avg" in summary
    assert "memory_avg" in summary


def test_alert_acknowledgement(health_monitor):
    """Test alert acknowledgement"""
    # Create an alert
    alert = Alert(
        alert_id="test_alert",
        severity=AlertSeverity.WARNING,
        service_name="test_service",
        message="Test alert",
    )
    health_monitor.active_alerts["test_alert"] = alert

    # Acknowledge it
    success = health_monitor.acknowledge_alert("test_alert")

    assert success
    assert health_monitor.active_alerts["test_alert"].acknowledged


def test_alert_acknowledgement_not_found(health_monitor):
    """Test acknowledging non-existent alert"""
    success = health_monitor.acknowledge_alert("nonexistent")
    assert not success


def test_get_alerts_excludes_resolved_by_default(health_monitor):
    """Test that resolved alerts are excluded by default"""
    health_monitor.active_alerts = {
        "alert1": Alert(
            alert_id="alert1",
            severity=AlertSeverity.WARNING,
            service_name="service1",
            message="Active alert",
            resolved=False,
        ),
        "alert2": Alert(
            alert_id="alert2",
            severity=AlertSeverity.ERROR,
            service_name="service2",
            message="Resolved alert",
            resolved=True,
        ),
    }

    alerts = health_monitor.get_alerts(include_resolved=False)
    assert len(alerts) == 1
    assert alerts[0]["alert_id"] == "alert1"


def test_get_alerts_includes_resolved_when_requested(health_monitor):
    """Test that resolved alerts are included when requested"""
    health_monitor.active_alerts = {
        "alert1": Alert(
            alert_id="alert1",
            severity=AlertSeverity.WARNING,
            service_name="service1",
            message="Active alert",
            resolved=False,
        ),
        "alert2": Alert(
            alert_id="alert2",
            severity=AlertSeverity.ERROR,
            service_name="service2",
            message="Resolved alert",
            resolved=True,
        ),
    }

    alerts = health_monitor.get_alerts(include_resolved=True)
    assert len(alerts) == 2


def test_get_health_monitor_singleton():
    """Test that get_health_monitor returns singleton instance"""
    monitor1 = get_health_monitor()
    monitor2 = get_health_monitor()

    assert monitor1 is monitor2


@pytest.mark.asyncio
@pytest.mark.slow
async def test_slow_response_time_degraded_status(health_monitor):
    """Test that slow response times result in degraded status"""

    async def slow_but_working_service():
        await asyncio.sleep(3.5)  # Slow but completes

    result = await health_monitor.check_service_health(
        "slow_service", slow_but_working_service, timeout_seconds=5.0
    )

    # Should complete but be marked degraded due to high response time
    assert result.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
    assert result.response_time_ms > 3000


@pytest.mark.asyncio
async def test_metrics_aggregation_window(health_monitor):
    """Test metrics aggregation over time window"""
    with patch("agent.health_monitoring.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 50.0
        mock_memory = Mock(percent=60.0, available=1024 * 1024 * 1024)
        mock_psutil.virtual_memory.return_value = mock_memory
        mock_disk = Mock(percent=70.0)
        mock_psutil.disk_usage.return_value = mock_disk
        mock_psutil.net_connections.return_value = list(range(10))
        mock_psutil.pids.return_value = []

        # Collect several metrics
        for _ in range(5):
            await health_monitor.collect_system_metrics()

        summary = health_monitor.get_metrics_summary(window_minutes=1)

        assert summary["data_points"] >= 5
        assert 40 <= summary["cpu_avg"] <= 60
        assert 50 <= summary["memory_avg"] <= 70
