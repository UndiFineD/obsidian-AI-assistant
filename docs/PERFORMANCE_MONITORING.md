# Performance Monitoring & Request Tracing

## Overview

The Obsidian AI Assistant backend includes comprehensive performance monitoring and request tracing capabilities designed to help identify bottlenecks, track slow queries, and maintain optimal system performance.

## Features

### 1. Request Tracing

Every request is tracked with:
- **Unique Request ID**: UUID generated for each request
- **Timing Information**: Start time, end time, duration in milliseconds
- **Endpoint Details**: HTTP method, path, status code
- **Client Information**: IP address, user agent
- **Success/Failure Tracking**: Error detection and counting

### 2. Slow Query Detection

The system automatically detects and logs slow requests based on configurable thresholds:

- **Slow Threshold**: 1000ms (1 second) - logged as WARNING
- **Very Slow Threshold**: 5000ms (5 seconds) - logged as CRITICAL

Slow requests are:
- Logged with detailed context
- Stored in a rolling buffer (last 100 slow requests)
- Available via REST API for analysis

### 3. Endpoint Statistics

Aggregated performance metrics per endpoint:

- **Total Requests**: Count of all requests to the endpoint
- **Average Duration**: Mean response time in milliseconds
- **Min/Max Duration**: Fastest and slowest request times
- **Error Rate**: Percentage of requests that resulted in errors
- **Slow Request Rate**: Percentage of requests exceeding slow threshold
- **Error Count**: Total number of failed requests
- **Slow Count**: Total number of slow requests

### 4. Performance Tiers

Requests are categorized into performance tiers with SLA targets:

| Tier | SLA Target | Description | Examples |
|------|-----------|-------------|----------|
| Tier 1 | <100ms | Critical fast paths | /health, /status, /api/config |
| Tier 2 | <500ms | Standard operations | Cached AI queries, simple searches |
| Tier 3 | <2000ms | AI operations | Uncached AI generation, semantic search |
| Tier 4 | <10000ms | Complex operations | Web analysis, document indexing |
| Tier 5 | <60000ms | Batch operations | Vault reindexing, model loading |

## REST API Endpoints

### GET /api/performance/tracing/summary

Returns overall performance summary with slow requests and endpoint statistics.

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-10-17T16:00:00Z",
  "summary": {
    "total_requests": 1542,
    "avg_duration_ms": 42.3,
    "slow_request_count": 12,
    "error_count": 3
  },
  "slow_requests": [
    {
      "request_id": "abc123",
      "method": "POST",
      "path": "/api/ask",
      "duration_ms": 3245.2,
      "status_code": 200,
      "severity": "SLOW",
      "threshold_exceeded_by_ms": 2245.2
    }
  ],
  "endpoint_stats": {
    "GET /health": {
      "total_requests": 500,
      "avg_duration_ms": 12.5,
      "min_duration_ms": 8.2,
      "max_duration_ms": 45.1,
      "error_count": 0,
      "error_rate": 0.0,
      "slow_count": 0,
      "slow_rate": 0.0
    }
  }
}
```

### GET /api/performance/tracing/slow-requests

Returns recent slow requests for analysis.

**Query Parameters:**
- `limit` (optional, default: 20): Maximum number of slow requests to return

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-10-17T16:00:00Z",
  "slow_threshold_ms": 1000,
  "very_slow_threshold_ms": 5000,
  "count": 12,
  "slow_requests": [
    {
      "request_id": "abc123",
      "method": "POST",
      "path": "/api/ask",
      "duration_ms": 3245.2,
      "status_code": 200,
      "client_ip": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "severity": "SLOW",
      "threshold_exceeded_by_ms": 2245.2
    }
  ]
}
```

### GET /api/performance/tracing/endpoint/{endpoint}

Returns performance statistics for a specific endpoint.

**Path Parameters:**
- `endpoint`: The endpoint path (e.g., "health", "api/ask")

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-10-17T16:00:00Z",
  "endpoint": "health",
  "statistics": {
    "GET /health": {
      "total_requests": 500,
      "avg_duration_ms": 12.5,
      "min_duration_ms": 8.2,
      "max_duration_ms": 45.1,
      "error_count": 0,
      "error_rate": 0.0,
      "slow_count": 0,
      "slow_rate": 0.0,
      "total_duration_ms": 6250.0
    }
  }
}
```

## Request Headers

All responses include tracing headers:

- **X-Request-ID**: Unique identifier for the request (UUID format)
- **X-Response-Time**: Request processing time in milliseconds

Example:
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 42.5ms
```

## Configuration

### Slow Query Thresholds

Configured in `backend/request_tracing.py`:

```python
class RequestTracer:
    def __init__(
        self,
        slow_threshold: int = 1000,  # 1 second
        very_slow_threshold: int = 5000,  # 5 seconds
        max_history: int = 1000,  # Keep last 1000 requests
        max_slow_requests: int = 100  # Keep last 100 slow requests
    ):
        ...
```

### Storage Limits

- **Request History**: Last 1000 requests kept in memory
- **Slow Requests**: Last 100 slow requests kept in memory
- **Endpoint Stats**: Unlimited (aggregated statistics per endpoint)

## Performance Testing

### Regression Tests

Run performance regression tests to ensure SLA compliance:

```powershell
python -m pytest tests/backend/test_performance_regression.py -v
```

Tests include:
- Tier 1-4 performance validation
- Concurrent request handling
- Memory leak detection
- Response time consistency
- Warmup effect validation

### Endpoint Tests

Test request tracing endpoints:

```powershell
python -m pytest tests/backend/test_request_tracing_endpoints.py -v
```

Tests include:
- Tracing summary endpoint
- Slow requests endpoint
- Per-endpoint statistics
- Request header validation
- Error handling
- URL encoding

## Logging

Slow requests are automatically logged with structured context:

```json
{
  "timestamp": "2025-10-17T16:00:00Z",
  "level": "WARNING",
  "logger": "request_tracing",
  "message": "SLOW REQUEST DETECTED: POST /api/ask took 3245.2ms (threshold: 1000ms)",
  "request_id": "abc123",
  "endpoint": "/api/ask",
  "duration_ms": 3245.2,
  "slow_threshold_ms": 1000,
  "severity": "SLOW",
  "category": "performance"
}
```

Very slow requests (>5000ms) are logged at CRITICAL level.

## Integration

### Middleware Stack

Request tracing is integrated via middleware in `backend/backend.py`:

```python
from .request_tracing import RequestTracingMiddleware

app.add_middleware(RequestTracingMiddleware)
```

The middleware automatically:
- Generates unique request IDs
- Tracks request start/end times
- Calculates duration
- Detects slow queries
- Adds tracing headers to responses
- Updates endpoint statistics

### Operation-Level Tracing

For fine-grained performance tracking within a request:

```python
from backend.request_tracing import trace_operation

async def complex_operation():
    with trace_operation("database_query"):
        result = await db.query()
    
    with trace_operation("ai_generation"):
        response = await ai_model.generate()
    
    return result, response
```

## Monitoring Best Practices

### 1. Regular Review

Monitor slow requests daily:
```bash
curl http://localhost:8000/api/performance/tracing/slow-requests?limit=50
```

### 2. Endpoint Analysis

Identify problematic endpoints:
```bash
curl http://localhost:8000/api/performance/tracing/summary
```

### 3. Performance Trends

Track performance over time by comparing endpoint statistics across deployments.

### 4. Alert Thresholds

Set up monitoring alerts for:
- Slow request rate > 5%
- Error rate > 1%
- Average duration exceeding tier SLA by 50%

### 5. Load Testing

Use performance regression tests in CI/CD:
```bash
pytest tests/backend/test_performance_regression.py --benchmark
```

## Troubleshooting

### High Slow Request Rate

1. Check endpoint statistics to identify problematic endpoints
2. Review slow request details for common patterns
3. Analyze request payloads and context
4. Consider caching, optimization, or scaling

### Missing Tracing Data

1. Verify RequestTracingMiddleware is enabled
2. Check logs for middleware initialization errors
3. Ensure requests include proper headers

### Performance Degradation

1. Review `/api/performance/metrics` for system resource usage
2. Check cache hit rates
3. Monitor database connection pool
4. Analyze concurrent request patterns

## Implementation Files

- **`backend/request_tracing.py`** (442 lines): Core tracing logic
  - `RequestTracer` class: Main tracing engine
  - `RequestTracingMiddleware`: ASGI middleware
  - `trace_operation()`: Context manager for operation timing
  - `get_request_tracer()`: Singleton accessor

- **`backend/backend.py`**: REST API endpoints
  - `/api/performance/tracing/summary`
  - `/api/performance/tracing/slow-requests`
  - `/api/performance/tracing/endpoint/{endpoint}`

- **Tests**:
  - `tests/backend/test_performance_regression.py` (16 tests)
  - `tests/backend/test_request_tracing_endpoints.py` (13 tests)

## Future Enhancements

Planned features for future releases:

1. **Distributed Tracing**: OpenTelemetry integration for multi-service tracing
2. **Custom Metrics**: User-defined performance metrics and thresholds
3. **Real-time Dashboards**: Web UI for live performance monitoring
4. **Automatic Scaling**: Trigger scaling based on performance metrics
5. **ML-Based Anomaly Detection**: Detect unusual performance patterns
6. **Historical Analysis**: Long-term performance trend storage and analysis
7. **Performance Profiling**: Detailed profiling of slow requests
8. **Custom Alerts**: Configurable alerting based on performance thresholds

## Related Documentation

- [Performance Requirements Specification](PERFORMANCE_REQUIREMENTS_SPECIFICATION.md)
- [System Architecture Specification](SYSTEM_ARCHITECTURE_SPECIFICATION.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Health Monitoring System](HEALTH_MONITORING.md)
