# API Rate Limiting & Throttling

## Overview

Obsidian AI Assistant implements robust rate limiting to protect backend resources, prevent abuse, and ensure fair
usage for all clients.

## Features

- **Global Rate Limits**: Configurable maximum requests per minute/hour per IP or API key
- **Per-Endpoint Limits**: Customizable limits for sensitive endpoints (e.g., /api/ask, /api/config)
- **Burst Protection**: Short-term burst limits to prevent sudden spikes
- **Response Headers**: Standard rate limit headers for client feedback
- **Error Handling**: HTTP 429 Too Many Requests with retry-after guidance

## Configuration

Rate limiting is configured via environment variables and config.yaml:

```yaml
# backend/config.yaml
rate_limit:
  enabled: true
  global_per_minute: 100
  global_per_hour: 1000
  endpoint_limits:
    /api/ask: 30/minute
    /api/config: 10/minute
  burst_limit: 10/second
  error_response: 429
```

Or via environment variables:

```bash
export RATE_LIMIT=100
export RATE_LIMIT_BURST=10
export RATE_LIMIT_ENABLED=true
```

## Response Headers

All rate-limited responses include standard headers:

- `X-RateLimit-Limit`: Maximum allowed requests
- `X-RateLimit-Remaining`: Requests left in current window
- `X-RateLimit-Reset`: Time (UTC epoch) when limit resets
- `Retry-After`: Seconds until next allowed request (on 429)

Example:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1697558400
Retry-After: 60
```

## Error Handling

When a client exceeds the limit:
- HTTP 429 Too Many Requests is returned
- JSON error body with details and retry guidance

Example:
```json
{
  "error": "Rate limit exceeded",
  "limit": 100,
  "remaining": 0,
  "retry_after": 60
}
```

## Best Practices

- **Handle 429 errors gracefully**: Implement exponential backoff and respect Retry-After
- **Monitor rate limit headers**: Adjust client request rates dynamically
- **Use API keys for higher limits**: Authenticated clients may receive higher quotas
- **Contact support for custom limits**: Enterprise users can request increased limits

## Testing

Rate limiting is validated by:
- Automated regression tests (see `test_rate_limiting.py`)
- Manual API testing with burst and sustained load
- Monitoring error rates and retry patterns

## Example Test (Pytest)

```python
def test_rate_limit_exceeded(client):
    for _ in range(101):
        response = client.get("/api/ask")
    assert response.status_code == 429
    assert "X-RateLimit-Remaining" in response.headers
    assert response.json()["error"] == "Rate limit exceeded"
```

## Related Documentation

- [Security Specification](SECURITY_SPECIFICATION.md)
- [Performance Monitoring](PERFORMANCE_MONITORING.md)
- [API Key Management](API_KEY_MANAGEMENT.md)
