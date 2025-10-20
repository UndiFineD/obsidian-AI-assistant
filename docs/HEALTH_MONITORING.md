# Health Monitoring System Documentation

## Overview

The health monitoring system provides comprehensive observability into the Obsidian AI Assistant backend, including
service health checks, system metrics collection, alert management, and performance tracking.

## Architecture

### Components

1. **HealthMonitor** (`backend/health_monitoring.py`)
   - Central monitoring coordinator
   - Service health check orchestration
   - System metrics aggregation
   - Alert threshold management
   - Historical data retention

1. **Health API Endpoints** (`backend/backend.py`)
   - `/api/health/detailed` - Enhanced health with service status
   - `/api/health/metrics` - Aggregated metrics over time windows
   - `/api/health/alerts` - Active and resolved alerts
   - `/api/health/alerts/{id}/acknowledge` - Alert acknowledgement

1. **Alert System**
   - Threshold-based alerting (CPU, memory, disk, response time)
   - Severity levels: INFO, WARNING, ERROR, CRITICAL
   - Alert lifecycle: creation → acknowledgement → resolution
   - Automatic resolution on service recovery

## API Reference

### GET /api/health/detailed

Enhanced health check with comprehensive service status.

**Response:**
```json
{
    "overall_status": "healthy|degraded|unhealthy|unknown",
    "timestamp": "2025-10-17T05:59:01.671Z",
    "uptime_seconds": 12345.67,
    "services": {
        "model_manager": {
            "status": "healthy",
            "response_time_ms": 23.4,
            "message": "Service responding normally",
            "last_check": "2025-10-17T05:59:01.671Z",
            "consecutive_failures": 0
        },
        "embeddings": {...},
        "cache": {...}
    },
    "system_metrics": {
        "cpu_percent": 45.2,
        "memory_percent": 62.3,
        "memory_available_mb": 4096.0,
        "disk_usage_percent": 73.1,
        "network_connections": 15,
        "process_count": 157
    },
    "active_alerts": 2,
    "total_alerts": 5
}
```

**Performance SLA:**
- Target: <2000ms
- Tier: 3 (AI generation, document search)
- Caching: Not cached (live metrics)

### GET /api/health/metrics

Aggregated metrics over a time window.

**Parameters:**
- `window_minutes` (optional, default=5): Time window for aggregation

**Response:**
```json
{
    "current_metrics": {
        "cpu_percent": 48.5,
        "memory_percent": 65.2,
        ...
    },
    "aggregated": {
        "window_minutes": 5,
        "data_points": 23,
        "cpu_avg": 47.3,
        "cpu_max": 52.1,
        "memory_avg": 64.8,
        "memory_max": 68.2,
        "disk_avg": 72.9,
        "connections_avg": 14.2
    }
}
```

**Performance SLA:**
- Target: <500ms
- Tier: 2 (cached operations)
- Caching: 30-second TTL on aggregated data

### GET /api/health/alerts

Retrieve active and resolved alerts.

**Parameters:**
- `include_resolved` (optional, default=false): Include resolved alerts

**Response:**
```json
{
    "alerts": [
        {
            "alert_id": "cpu_usage",
            "severity": "warning",
            "service_name": "CPU",
            "message": "CPU usage is 72.3%",
            "current_value": 72.3,
            "threshold_value": 70.0,
            "timestamp": "2025-10-17T05:59:01.671Z",
            "acknowledged": false,
            "resolved": false
        }
    ],
    "summary": {
        "active": 2,
        "total": 5
    }
}
```

**Performance SLA:**
- Target: <100ms
- Tier: 1 (health checks, status)
- Caching: In-memory alert state

### POST /api/health/alerts/{alert_id}/acknowledge

Acknowledge an alert to indicate awareness.

**Parameters:**
- `alert_id` (path): ID of the alert to acknowledge

**Response:**
```json
{
    "success": true,
    "alert_id": "cpu_usage"
}
```

**Error Response:**
```json
{
    "error": {
        "category": "NOT_FOUND",
        "code": "ALERT_NOT_FOUND",
        "message": "Alert cpu_usage_999 not found",
        "context": {"alert_id": "cpu_usage_999"},
        "suggestion": "Check alert ID or list available alerts with GET /api/health/alerts",
        "documentation_url": "/docs#health-monitoring"
    }
}
```

## Alert Thresholds

### Default Thresholds

| Metric | Warning | Error | Critical |
|--------|---------|-------|----------|
| CPU (%) | 70 | 85 | 95 |
| Memory (%) | 75 | 90 | 95 |
| Disk (%) | 80 | 90 | 95 |
| Response Time (ms) | 1000 | 3000 | 5000 |

### Threshold Configuration

Thresholds are initialized in `HealthMonitor._initialize_thresholds()` and can be customized:

```python
from backend.health_monitoring import get_health_monitor

monitor = get_health_monitor()
monitor.alert_thresholds["cpu"]["warning"] = 60.0  # Lower threshold
monitor.alert_thresholds["memory"]["critical"] = 98.0  # Higher threshold
```

## Service Health Checks

### Monitored Services

1. **model_manager**: AI model loading and inference
2. **embeddings**: Vector embedding generation
3. **cache**: Caching layer responsiveness
4. **vector_db**: Vector database operations (future)

### Health Check Logic

Services are checked by running a test function with timeout:

```python
async def check_model_manager():
    """Check if model manager is responsive"""
    global model_manager
    if model_manager is None:
        raise Exception("Model manager not initialized")
    # Additional health checks can be added here

await monitor.check_service_health(
    "model_manager",
    check_model_manager,
    timeout_seconds=5.0
)
```

### Status Levels

- **HEALTHY**: Service responding normally, response time < threshold
- **DEGRADED**: Service responding but slow (response time > warning threshold)
- **UNHEALTHY**: Service not responding or errors
- **UNKNOWN**: Service not yet checked or status indeterminate

### Consecutive Failures

Services track consecutive failures to determine alert severity:
- 1 failure → WARNING
- 2 failures → ERROR  
- 3+ failures → CRITICAL

Recovery resets failure counter to 0.

## System Metrics

### Collected Metrics

| Metric | Description | Source |
|--------|-------------|--------|
| cpu_percent | CPU usage (%) | psutil.cpu_percent() |
| memory_percent | Memory usage (%) | psutil.virtual_memory().percent |
| memory_available_mb | Available memory (MB) | psutil.virtual_memory().available |
| disk_usage_percent | Disk usage (%) | psutil.disk_usage('/').percent |
| network_connections | Active connections | len(psutil.net_connections()) |
| process_count | Running processes | len(psutil.pids()) |
| uptime_seconds | Monitor uptime | time.time() - start_time |

### Metrics History

- Historical metrics stored in `HealthMonitor.metrics_history`
- Maximum 1000 data points retained (FIFO)
- Timestamp for each metric collection
- Used for time-series aggregation and trending

### Metrics Aggregation

Metrics are aggregated over configurable time windows:

```python
summary = monitor.get_metrics_summary(window_minutes=10)
# Returns: cpu_avg, cpu_max, memory_avg, memory_max, disk_avg, connections_avg
```

Aggregation includes:
- Average (mean) values
- Maximum values
- Data point count
- Time window specification

## Alert Lifecycle

### 1. Alert Generation

Alerts are generated when:
- Service health checks fail (consecutive failures ≥ threshold)
- System metrics exceed thresholds (CPU, memory, disk)
- Response times exceed thresholds

```python
alert = Alert(
    alert_id="service_name_health",
    severity=AlertSeverity.WARNING,
    service_name="service_name",
    message="Service health check failed",
    current_value=3.0,  # consecutive failures
    threshold_value=3.0
)
monitor.active_alerts[alert_id] = alert
```

### 2. Alert Acknowledgement

Operators acknowledge alerts to indicate awareness:

```python
success = monitor.acknowledge_alert("cpu_usage")
# Alert.acknowledged = True
```

Acknowledgement does not resolve the alert - it only marks it as seen.

### 3. Alert Resolution

Alerts are automatically resolved when:
- Service recovers (health check succeeds)
- Metrics fall below warning threshold

```python
# Automatic resolution
if service.status == ServiceStatus.HEALTHY:
    if alert_id in monitor.active_alerts:
        monitor.active_alerts[alert_id].resolved = True
```

Resolved alerts are excluded from default alert listings but available with `include_resolved=true`.

## Integration Patterns

### Health Check Registration

Register custom health checks for new services:

```python
from backend.health_monitoring import get_health_monitor

monitor = get_health_monitor()

async def check_custom_service():
    """Custom service health check"""
    # Perform service-specific checks
    # Raise exception on failure
    pass

# Run health check
result = await monitor.check_service_health(
    "custom_service",
    check_custom_service,
    timeout_seconds=3.0
)
```

### Custom Alert Thresholds

Override default thresholds for specific environments:

```python
# Development: Higher thresholds (more tolerant)
if os.getenv("ENVIRONMENT") == "development":
    monitor.alert_thresholds["cpu"]["critical"] = 98.0
    monitor.alert_thresholds["memory"]["critical"] = 98.0

# Production: Lower thresholds (more strict)
elif os.getenv("ENVIRONMENT") == "production":
    monitor.alert_thresholds["cpu"]["warning"] = 60.0
    monitor.alert_thresholds["memory"]["warning"] = 70.0
```

### Monitoring Dashboard Integration

Health monitoring data can be consumed by external dashboards:

```python
import httpx

async def fetch_health_data():
    async with httpx.AsyncClient() as client:
        # Get detailed health status
        health = await client.get("http://localhost:8000/api/health/detailed")
        
        # Get metrics aggregated over 15 minutes
        metrics = await client.get("http://localhost:8000/api/health/metrics?window_minutes=15")
        
        # Get active alerts
        alerts = await client.get("http://localhost:8000/api/health/alerts")
        
        return {
            "health": health.json(),
            "metrics": metrics.json(),
            "alerts": alerts.json()
        }
```

## Performance Optimization

### Caching Strategy

- **Health checks**: Not cached (live status required)
- **System metrics**: Cached for 10 seconds (balance freshness/performance)
- **Aggregated metrics**: Cached for 30 seconds (computationally expensive)
- **Alert lists**: In-memory (instant access)

### Resource Management

Health monitoring is designed to have minimal overhead:

1. **Async Operations**: All health checks are async to avoid blocking
2. **Timeout Protection**: All checks have configurable timeouts
3. **History Limits**: Metrics history capped at 1000 entries
4. **Lazy Initialization**: Monitor created on first access

### SLA Compliance

| Endpoint | Target | Tier | Caching |
|----------|--------|------|---------|
| /api/health/detailed | <2s | 3 | None |
| /api/health/metrics | <500ms | 2 | 30s |
| /api/health/alerts | <100ms | 1 | Memory |
| /api/health/alerts/{id}/acknowledge | <100ms | 1 | None |

## Testing

### Unit Tests

Comprehensive unit tests in `tests/backend/test_health_monitoring.py`:
- Service health check success/failure/timeout
- Consecutive failure tracking
- System metrics collection
- Alert threshold triggers
- Alert lifecycle (creation/acknowledgement/resolution)
- Metrics aggregation accuracy

**Test Count**: 24 tests
**Coverage**: 100% of health_monitoring.py

### Integration Tests

Integration tests in `tests/integration/test_health_endpoints.py`:
- API endpoint responses
- Error handling
- Concurrent requests
- Alert lifecycle workflows
- Metrics validation

**Test Count**: 17 tests (when fixed)
**Coverage**: All health endpoints

### Running Tests

```bash
# Run health monitoring tests only
pytest tests/backend/test_health_monitoring.py -v

# Run integration tests
pytest tests/integration/test_health_endpoints.py -v

# Run all tests
pytest tests/ -v

# With coverage
pytest --cov=backend.health_monitoring --cov-report=html tests/backend/test_health_monitoring.py
```

## Troubleshooting

### High CPU Alerts

**Symptom**: Continuous CPU usage alerts

**Causes**:
- Model inference load
- Indexing operations
- Memory pressure causing thrashing

**Resolution**:
1. Check active requests: `GET /api/health/detailed`
2. Review metrics history: `GET /api/health/metrics?window_minutes=30`
3. Scale horizontally (add instances) or vertically (more CPU)
4. Adjust thresholds if alerts are false positives

### Service Health Check Failures

**Symptom**: `ServiceStatus.UNHEALTHY` for critical services

**Causes**:
- Service not initialized (cold start)
- Dependency failures (vector DB, cache)
- Resource exhaustion
- Network issues

**Resolution**:
1. Check service logs for error details
2. Verify dependencies are available
3. Restart backend if initialization failed
4. Check system resources (memory, disk space)

### Memory Pressure

**Symptom**: Memory usage exceeding 90%

**Causes**:
- Large model loading
- Metrics history accumulation
- Cache growth
- Memory leaks

**Resolution**:
1. Clear cache: `POST /api/performance/cache/clear`
2. Review metrics history size (max 1000 entries)
3. Monitor for memory leaks with profiling tools
4. Consider model optimization or reduced batch sizes

### Alert Storm

**Symptom**: Many alerts triggered simultaneously

**Causes**:
- System-wide issue (disk full, network down)
- Cascading failures
- Threshold misconfiguration

**Resolution**:
1. Check system-level issues first (disk, network, resources)
2. Acknowledge non-critical alerts to reduce noise
3. Review threshold configuration
4. Address root cause before individual service issues

## Best Practices

### 1. Regular Health Monitoring

- Check `/api/health/detailed` regularly (every 30-60 seconds)
- Monitor trends in `/api/health/metrics` for early warning signs
- Set up automated alerting based on alert API

### 2. Alert Management

- Acknowledge alerts promptly to track operator awareness
- Document resolution steps for common alerts
- Review resolved alerts to identify patterns

### 3. Threshold Tuning

- Start with default thresholds
- Adjust based on baseline performance (use metrics history)
- Different thresholds for dev/staging/production
- Document threshold changes and rationale

### 4. Performance Optimization

- Use metrics aggregation for dashboards (reduces API calls)
- Cache dashboard data client-side (30-60 second refresh)
- Monitor health endpoint performance itself
- Scale monitoring infrastructure with backend

### 5. Integration

- Integrate with external monitoring (Prometheus, Grafana, Datadog)
- Export metrics to time-series databases
- Set up alerting pipelines (PagerDuty, Slack, email)
- Create runbooks for common alert scenarios

## Future Enhancements

### Planned Features

1. **Prometheus Integration**: Metrics export in Prometheus format
2. **Custom Health Checks**: Plugin system for service-specific checks
3. **Predictive Alerts**: Machine learning for anomaly detection
4. **Distributed Tracing**: Request flow visualization
5. **Auto-Remediation**: Automatic recovery actions for common issues

### API Extensions

- `POST /api/health/checks/register`: Register custom health checks
- `GET /api/health/history`: Historical health data export
- `GET /api/health/recommendations`: AI-powered optimization suggestions
- `POST /api/health/simulate`: Simulate alert scenarios for testing

## References

- Source Code: `backend/health_monitoring.py`
- API Endpoints: `backend/backend.py` (lines 731-859)
- Unit Tests: `tests/backend/test_health_monitoring.py`
- Integration Tests: `tests/integration/test_health_endpoints.py`
- Dependencies: psutil, pydantic, FastAPI
