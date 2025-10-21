# API Reference

## Overview

The Obsidian AI Agent backend provides a comprehensive REST API for AI-powered note analysis, vector search, web
research, voice transcription, and enterprise features. The API is built with FastAPI and includes OpenAPI/Swagger
documentation.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses Bearer token authentication with role-based access control (RBAC):

- **user**: Basic access to AI features and search
- **admin**: Full access including system management and configuration

In test mode, authentication is bypassed for integration testing.

### Authentication Methods

#### Method 1: Bearer Token (Recommended)

**Format:**
```
Authorization: Bearer <token>
```

**Example:**
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  http://localhost:8000/api/ask
```

**Getting a Token:**
```bash
# Exchange credentials for token
curl -X POST "http://localhost:8000/api/auth/token" \
  -d "username=user&password=pass"

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIs...",
#   "token_type": "bearer",
#   "expires_in": 3600
# }
```

#### Method 2: API Key Authentication

**Format:**
```
X-API-Key: <api-key>
```

**Example:**
```bash
curl -H "X-API-Key: sk_test_4eC39HqLyjWDarht..." \
  http://localhost:8000/api/ask
```

**Enterprise Feature**: Generate API keys in admin dashboard

#### Method 3: OAuth2 SSO (Enterprise)

**Flow:**
```bash
# 1. Redirect user to SSO provider
curl -X POST "http://localhost:8000/api/enterprise/auth/sso" \
  -d '{"provider": "azure"}'

# 2. User authenticates at provider
# 3. Provider redirects to callback with auth code
# 4. Exchange code for token
curl -X POST "http://localhost:8000/api/enterprise/auth/callback" \
  -d '{"code": "auth_code", "state": "state_token"}'
```

### Role-Based Access Control (RBAC)

**User Role** (Default):
- Read-only access to search and AI features
- Cannot modify configuration or system settings

**Admin Role**:
- Full API access including configuration and reindexing
- User management capabilities (enterprise)
- System monitoring and optimization

**Example: Permission Denied**
```bash
# User role trying to access admin endpoint
curl -X POST "http://localhost:8000/api/reindex" \
  -H "Authorization: Bearer user_token"

# Response 403 Forbidden:
# {"detail": "Requires role: admin"}
```

### Token Management

**Token Lifespan:**
- Default expiration: 1 hour
- Enterprise JWT: Configurable via settings
- Refresh tokens: Available for long-lived sessions

**Refresh Token Flow:**
```bash
# Original token expired, get a new one
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Authorization: Bearer expired_token"
```

**Token Validation:**
```bash
# Check current token validity
curl -X GET "http://localhost:8000/api/auth/verify" \
  -H "Authorization: Bearer token_to_verify"

# Response:
# {"valid": true, "user": "user123", "expires_at": 1729094400}
```

### Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** for tokens: `export API_TOKEN=...`
3. **Rotate tokens regularly** (especially for long-running services)
4. **Use HTTPS** in production (Bearer tokens are plaintext)
5. **Implement token expiration** in applications
6. **Log authentication events** for security auditing

### Authentication Examples by Language

**Python:**
```python
import requests

headers = {"Authorization": "Bearer your_token"}
response = requests.get("http://localhost:8000/api/config", headers=headers)
```

**Node.js:**
```javascript
const response = await fetch("http://localhost:8000/api/config", {
  headers: {"Authorization": "Bearer your_token"}
});
```

**cURL:**
```bash
curl "http://localhost:8000/api/config" \
  -H "Authorization: Bearer your_token"
```

## Core Endpoints

### Health & Status

#### GET /health
Comprehensive health check with system information.

**Response:**
```json
{
  "status": "ok",
  "timestamp": 1729094400,
  "agent_url": "http://localhost:8000",
  "api_port": 8000,
  "vault_path": "./vault",
  "models_dir": "./agent/models",
  "cache_dir": "./agent/cache",
  "model_backend": "gpt4all",
  "embed_model": "all-MiniLM-L6-v2",
  "vector_db": "chromadb",
  "allow_network": false,
  "gpu": false
}
```

#### GET /status
Lightweight liveness probe.

**Response:**
```json
{
  "status": "ok"
}
```

#### GET /api/health
Alias for `/health` endpoint.

### Configuration Management

#### GET /api/config
Get current runtime configuration (whitelisted fields only).

**Response:**
```json
{
  "vault_path": "./vault",
  "chunk_size": 1000,
  "gpu": false,
  "agent/vector_db": "./agent/vector_db"
}
```

#### POST /api/config
Update runtime configuration.

**Request Body:**
```json
{
  "vault_path": "./new_vault",
  "chunk_size": 1500,
  "gpu": true
}
```

**Response:**
```json
{
  "ok": true,
  "settings": {
    "vault_path": "./new_vault",
    "chunk_size": 1500,
    "gpu": true
  }
}
```

#### POST /api/config/reload
Reload configuration from `agent/config.yaml`.

**Response:**
```json
{
  "ok": true,
  "settings": {
    "vault_path": "./vault",
    "chunk_size": 1000
  }
}
```

## AI & Search Endpoints

### AI Question Answering

#### POST /api/ask
Ask AI questions with context from indexed vault.

**Authentication:** Requires `user` role

**Request Body:**
```json
{
  "question": "What are the main themes in my notes?",
  "prefer_fast": true,
  "max_tokens": 256,
  "context_paths": ["/path/to/note1.md", "/path/to/note2.md"],
  "prompt": "Custom prompt template",
  "model_name": "llama-7b"
}
```

**Response:**
```json
{
  "answer": "Based on your notes, the main themes include...",
  "model_used": "llama-7b",
  "context_used": ["note1.md", "note2.md"],
  "processing_time": 1.23
}
```

#### POST /ask
Legacy alias for `/api/ask`.

### Vector Search

#### POST /api/search
Semantic search across indexed documents.

**Authentication:** Requires `user` role

**Request Body:**
```json
{
  "query": "machine learning concepts",
  "top_k": 5,
  "similarity_threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Machine learning is a subset of AI...",
      "metadata": {
        "source": "ml-notes.md",
        "chunk_id": "chunk_1"
      },
      "similarity": 0.85
    }
  ],
  "query_time": 0.12
}
```

### Document Indexing

#### POST /api/reindex
Rebuild vector database index for vault documents.

**Authentication:** Requires `admin` role

**Request Body:**
```json
{
  "vault_path": "./vault"
}
```

**Response:**
```json
{
  "status": "success",
  "indexed_files": 42,
  "processing_time": 15.67
}
```

#### POST /reindex
Legacy alias for `/api/reindex`.

#### POST /api/scan_vault
Scan vault for new or modified files.

**Authentication:** Requires `admin` role

**Response:**
```json
{
  "new_files": 5,
  "modified_files": 3,
  "deleted_files": 1,
  "scan_time": 0.45
}
```

#### POST /api/index_pdf
Index PDF files for semantic search.

**Authentication:** Requires `admin` role

**Request Body:**
```json
{
  "pdf_path": "/path/to/document.pdf"
}
```

**Response:**
```json
{
  "status": "indexed",
  "pages": 25,
  "chunks": 48
}
```

### Web Research

#### POST /api/web
Analyze web content and generate AI responses.

**Authentication:** Requires `user` role

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "question": "Summarize the main points"
}
```

**Response:**
```json
{
  "summary": "The article discusses...",
  "url": "https://example.com/article",
  "content_length": 5420,
  "processing_time": 3.21
}
```

#### POST /web
Legacy alias for `/api/web`.

### Voice Transcription

#### POST /transcribe
Speech-to-text transcription from base64 audio.

**Authentication:** Requires `user` role

**Request Body:**
```json
{
  "audio_data": "base64-encoded-audio-data",
  "format": "webm",
  "language": "en"
}
```

**Response:**
```json
{
  "transcription": "Hello, this is a test transcription",
  "language": "en",
  "confidence": 0.95,
  "processing_time": 2.1
}
```

#### POST /api/voice_transcribe
Voice transcription endpoint from voice router.

## Performance & Monitoring

### Performance Metrics

#### GET /api/performance/metrics
Get real-time performance metrics.

**Response:**
```json
{
  "cache": {
    "l1_hits": 1250,
    "l1_misses": 45,
    "l2_hits": 80,
    "l2_misses": 12
  },
  "pools": {
    "models": {
      "active": 2,
      "idle": 1,
      "max_size": 3
    },
    "vector_db": {
      "active": 1,
      "idle": 2,
      "max_size": 5
    }
  },
  "queue": {
    "pending": 0,
    "processing": 1,
    "completed": 156
  },
  "timestamp": 1729094400
}
```

#### GET /api/performance/cache/stats
Get detailed cache statistics.

**Response:**
```json
{
  "l1_cache": {
    "size": 128,
    "max_size": 256,
    "hit_rate": 0.92
  },
  "l2_cache": {
    "size": 512,
    "max_size": 1024,
    "hit_rate": 0.78
  }
}
```

#### POST /api/performance/cache/clear
Clear performance cache.

**Response:**
```json
{
  "status": "cleared",
  "l1_entries_removed": 128,
  "l2_entries_removed": 512
}
```

#### POST /api/performance/optimize
Trigger background optimization tasks.

**Response:**
```json
{
  "status": "optimization_started",
  "tasks": ["cache_cleanup", "pool_optimization", "index_maintenance"]
}
```

#### GET /api/performance/dashboard
Get performance dashboard data.

**Response:**
```json
{
  "system_health": "healthy",
  "uptime": 86400,
  "response_times": {
    "avg": 120,
    "p95": 250,
    "p99": 500
  },
  "throughput": {
    "requests_per_minute": 45,
    "peak_rpm": 120
  }
}
```

#### GET /api/performance/health
Get detailed performance health metrics.

**Response:**
```json
{
  "cpu_usage": 15.5,
  "memory_usage": 68.2,
  "disk_usage": 42.1,
  "network_io": {
    "bytes_sent": 1048576,
    "bytes_received": 2097152
  }
}
```

#### GET /api/performance/trends
Get performance trend data.

**Response:**
```json
{
  "response_times": [
    {"timestamp": 1729094400, "avg": 120},
    {"timestamp": 1729094460, "avg": 115}
  ],
  "throughput": [
    {"timestamp": 1729094400, "rpm": 45},
    {"timestamp": 1729094460, "rpm": 52}
  ]
}
```

## Enterprise Features

### Authentication & SSO

#### POST /api/enterprise/auth/sso
Initiate SSO authentication.

**Request Body:**
```json
{
  "provider": "azure",
  "redirect_uri": "https://app.example.com/callback"
}
```

**Response:**
```json
{
  "auth_url": "https://login.microsoftonline.com/...",
  "state": "random-state-token"
}
```

#### POST /api/enterprise/auth/callback
Handle SSO authentication callback.

**Request Body:**
```json
{
  "code": "auth-code",
  "state": "state-token"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "roles": ["user"]
  }
}
```

#### POST /api/enterprise/auth/logout
SSO logout.

**Response:**
```json
{
  "status": "logged_out",
  "logout_url": "https://login.microsoftonline.com/logout"
}
```

### Enterprise Status

#### GET /api/enterprise/status
Get enterprise feature status.

**Authentication:** Requires `admin` role (when available)

**Response:**
```json
{
  "enterprise_enabled": true,
  "features": ["sso", "rbac", "compliance", "multi_tenant"],
  "license": {
    "type": "enterprise",
    "expires": "2025-12-31"
  }
}
```

#### GET /api/enterprise/demo
Enterprise demo endpoint.

**Authentication:** Requires `admin` role

**Response:**
```json
{
  "demo_mode": true,
  "features_available": ["sso", "rbac"]
}
```

## OpenSpec Governance

### Change Management

#### GET /api/openspec/changes
List all OpenSpec changes.

**Response:**
```json
{
  "changes": [
    {
      "id": "change-001",
      "title": "Update API documentation",
      "status": "pending",
      "created": "2025-10-16T10:00:00Z"
    }
  ]
}
```

#### GET /api/openspec/changes/{change_id}
Get specific OpenSpec change details.

**Response:**
```json
{
  "id": "change-001",
  "title": "Update API documentation",
  "description": "Add new endpoints to API reference",
  "status": "pending",
  "files": ["docs/API_REFERENCE.md"],
  "created": "2025-10-16T10:00:00Z"
}
```

#### POST /api/openspec/changes/{change_id}/validate
Validate a specific OpenSpec change.

**Response:**
```json
{
  "valid": true,
  "warnings": [],
  "errors": []
}
```

#### POST /api/openspec/changes/{change_id}/apply
Apply a validated OpenSpec change.

**Response:**
```json
{
  "applied": true,
  "files_modified": ["docs/API_REFERENCE.md"],
  "timestamp": "2025-10-16T10:30:00Z"
}
```

#### POST /api/openspec/changes/{change_id}/archive
Archive a completed OpenSpec change.

**Response:**
```json
{
  "archived": true,
  "archive_path": "openspec/archive/change-001",
  "timestamp": "2025-10-16T10:45:00Z"
}
```

#### POST /api/openspec/validate-bulk
Validate multiple OpenSpec changes.

**Request Body:**
```json
{
  "change_ids": ["change-001", "change-002"]
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "change-001",
      "valid": true,
      "warnings": [],
      "errors": []
    },
    {
      "id": "change-002",
      "valid": false,
      "warnings": ["Missing description"],
      "errors": ["Invalid file path"]
    }
  ]
}
```

### Governance Metrics

#### GET /api/openspec/metrics
Get OpenSpec governance metrics.

**Response:**
```json
{
  "total_changes": 45,
  "pending_changes": 3,
  "applied_changes": 40,
  "archived_changes": 2,
  "avg_processing_time": 24.5
}
```

#### GET /api/openspec/dashboard
Get OpenSpec governance dashboard.

**Response:**
```json
{
  "overview": {
    "total_changes": 45,
    "recent_activity": 8
  },
  "status_breakdown": {
    "pending": 3,
    "in_review": 2,
    "applied": 40
  },
  "recent_changes": [
    {
      "id": "change-045",
      "title": "Update security specs",
      "status": "applied",
      "timestamp": "2025-10-16T09:00:00Z"
    }
  ]
}
```

## Security & Compliance

### Security Status

#### GET /api/security/status
Get security system status.

**Response:**
```json
{
  "security_enabled": true,
  "threat_level": "low",
  "active_protections": ["rate_limiting", "csrf", "input_validation"],
  "last_scan": "2025-10-16T08:00:00Z"
}
```

#### GET /api/security/events
Get security event log.

**Response:**
```json
{
  "events": [
    {
      "timestamp": "2025-10-16T10:00:00Z",
      "type": "rate_limit_triggered",
      "severity": "medium",
      "details": {
        "ip": "192.168.1.100",
        "endpoint": "/api/ask"
      }
    }
  ]
}
```

#### POST /api/security/clear-cache
Clear security cache.

**Response:**
```json
{
  "status": "cache_cleared",
  "entries_removed": 156
}
```

#### GET /api/security/compliance
Get compliance status.

**Response:**
```json
{
  "gdpr_compliant": true,
  "soc2_compliant": true,
  "last_audit": "2025-09-15T00:00:00Z",
  "next_audit": "2025-12-15T00:00:00Z"
}
```

#### POST /api/security/gdpr/deletion-request
Handle GDPR data deletion request.

**Request Body:**
```json
{
  "user_id": "user123",
  "data_types": ["search_history", "cached_responses"]
}
```

**Response:**
```json
{
  "request_id": "req-789",
  "status": "processed",
  "deleted_records": 45
}
```

#### GET /api/security/dashboard
Get security dashboard.

**Response:**
```json
{
  "threat_level": "low",
  "active_incidents": 0,
  "blocked_requests": 12,
  "security_score": 95
}
```

## Error Responses

All endpoints return standard HTTP status codes with JSON error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Missing or invalid authentication token"
}
```

### 403 Forbidden
```json
{
  "detail": "Requires role: admin"
}
```

### 404 Not Found
```json
{
  "detail": "Enterprise features not available"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

### Common Error Solutions

| Error | Cause | Solution | Example |
|-------|-------|----------|---------|
| 400 Bad Request | Invalid JSON syntax | Validate JSON with `jq` or JSON validator | `echo '{"bad}' \| jq '.'` shows syntax error |
| 401 Unauthorized | Missing token | Add `Authorization: Bearer <token>` header | `curl -H "Authorization: Bearer token123"` |
| 403 Forbidden | Insufficient permissions | Check user role requirements (admin vs user) | Need admin role for `/api/reindex` |
| 404 Not Found | Endpoint/resource not found | Verify endpoint path is correct | Typo: `/api/ask` not `/api/ask/` |
| 409 Conflict | Resource already exists | Use PUT to update instead of POST | Creating duplicate note |
| 422 Unprocessable Entity | Missing required fields | Check all required fields in request body | Missing "question" field |
| 429 Too Many Requests | Rate limit exceeded | Implement exponential backoff retry logic | Wait 60 seconds per `Retry-After` header |
| 500 Internal Server Error | Backend error | Check `/api/health/detailed` for service status | Model unavailable, disk full |
| 503 Service Unavailable | Backend overloaded/offline | Retry with backoff, check deployment status | All models busy, API down |

### Debugging Tips

**Enable Verbose Output:**
```bash
# See request headers and response
curl -v -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer token" \
  -d '{"question": "..."}'
```

**Check Health Status:**
```bash
# If you get errors, first check health
curl "http://localhost:8000/api/health/detailed" | jq '.services'
```

**Validate Request Body:**
```bash
# Use jq to validate JSON before sending
jq -n '{question: "test"}' | \
  curl -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer token" \
  -d @-
```

**Capture Full Error Response:**
```bash
# Save both stdout and stderr
curl -X POST "http://localhost:8000/api/ask" \
  -d '{"bad_field": "data"}' \
  2>&1 | tee error.log
```

## cURL Examples

### Complete cURL Reference (20+ Examples)

**1. Health Check**
```bash
curl http://localhost:8000/health
```

**2. Lightweight Status Check**
```bash
curl http://localhost:8000/status
```

**3. Ask Question (Basic)**
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics in my vault?"
  }'
```

**4. Ask Question (Advanced with Context)**
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Summarize machine learning concepts",
    "context_paths": ["/notes/ml.md", "/notes/ai.md"],
    "max_tokens": 512,
    "prefer_fast": false,
    "model_name": "llama-7b"
  }'
```

**5. Get Configuration**
```bash
curl "http://localhost:8000/api/config" \
  -H "Authorization: Bearer your-token"
```

**6. Update Configuration**
```bash
curl -X POST "http://localhost:8000/api/config" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "vault_path": "./my_vault",
    "chunk_size": 1500,
    "gpu": true
  }'
```

**7. Reload Configuration from File**
```bash
curl -X POST "http://localhost:8000/api/config/reload" \
  -H "Authorization: Bearer your-token"
```

**8. Semantic Search (Basic)**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "top_k": 5
  }'
```

**9. Semantic Search (Advanced)**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "neural networks",
    "top_k": 10,
    "similarity_threshold": 0.75
  }'
```

**10. Reindex Vault**
```bash
curl -X POST "http://localhost:8000/api/reindex" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "vault_path": "./vault"
  }'
```

**11. Scan Vault for Changes**
```bash
curl -X POST "http://localhost:8000/api/scan_vault" \
  -H "Authorization: Bearer your-token"
```

**12. Index PDF File**
```bash
curl -X POST "http://localhost:8000/api/index_pdf" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "/documents/research.pdf"
  }'
```

**13. Web Research (Basic)**
```bash
curl -X POST "http://localhost:8000/api/web" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "question": "What is the main topic?"
  }'
```

**14. Web Research (with Summary)**
```bash
curl -X POST "http://localhost:8000/api/web" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.example.com/story",
    "question": "Summarize the key findings"
  }' | jq '.summary'
```

**15. Voice Transcription**
```bash
curl -X POST "http://localhost:8000/api/voice_transcribe" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64-audio-string-here",
    "format": "webm",
    "language": "en"
  }'
```

**16. Get Performance Metrics**
```bash
curl "http://localhost:8000/api/performance/metrics"
```

**17. Get Cache Statistics**
```bash
curl "http://localhost:8000/api/performance/cache/stats"
```

**18. Clear Performance Cache**
```bash
curl -X POST "http://localhost:8000/api/performance/cache/clear"
```

**19. Trigger Optimization**
```bash
curl -X POST "http://localhost:8000/api/performance/optimize"
```

**20. Get Detailed Health Info**
```bash
curl "http://localhost:8000/api/health/detailed" | jq '.services'
```

**21. Get Security Status**
```bash
curl "http://localhost:8000/api/security/status" \
  -H "Authorization: Bearer your-token"
```

**22. View Security Events**
```bash
curl "http://localhost:8000/api/security/events" \
  -H "Authorization: Bearer your-token"
```

**23. Get Compliance Status**
```bash
curl "http://localhost:8000/api/security/compliance"
```

**24. Enterprise SSO Initiation**
```bash
curl -X POST "http://localhost:8000/api/enterprise/auth/sso" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "azure",
    "redirect_uri": "https://myapp.com/callback"
  }'
```

**25. Get Enterprise Status**
```bash
curl "http://localhost:8000/api/enterprise/status" \
  -H "Authorization: Bearer your-token"
```

### cURL Tips & Tricks

**Pretty-print JSON responses:**
```bash
curl http://localhost:8000/api/config | jq '.'
```

**Save response to file:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -d @request.json \
  -o response.json
```

**Include response headers:**
```bash
curl -i http://localhost:8000/health
```

**Follow redirects:**
```bash
curl -L http://localhost:8000/api/enterprise/auth/sso
```

**Show verbose output:**
```bash
curl -v http://localhost:8000/health
```

**Time the request:**
```bash
curl -w "\nTotal time: %{time_total}s\n" http://localhost:8000/health
```

## Rate Limiting & Throttling

Obsidian AI Agent implements robust rate limiting to protect backend resources, prevent abuse, and ensure fair usage for all clients.

### Configuration

Rate limiting is configured via environment variables and config.yaml:

```yaml
# agent/config.yaml
rate_limit:
  enabled: true
  global_per_minute: 100
  global_per_hour: 1000
  endpoint_limits:
    /api/ask: 30/minute
    /api/config: 10/minute
  burst_limit: 10/second
```

Or via environment variables:

```bash
export RATE_LIMIT=100
export RATE_LIMIT_BURST=10
export RATE_LIMIT_ENABLED=true
```

### Rate Limit Headers

All rate-limited responses include standard headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1729094460
Retry-After: 60
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum allowed requests |
| `X-RateLimit-Remaining` | Requests left in current window |
| `X-RateLimit-Reset` | Time (UTC epoch) when limit resets |
| `Retry-After` | Seconds until next allowed request (on 429) |

### Error Handling

When a client exceeds the limit, HTTP 429 Too Many Requests is returned:

```json
{
  "error": "Rate limit exceeded",
  "limit": 100,
  "remaining": 0,
  "retry_after": 60
}
```

**Best Practices:**
- Handle 429 errors with exponential backoff
- Monitor rate limit headers to adjust request rates dynamically
- Use API keys for higher limits (authenticated clients get increased quotas)
- Contact support for custom limits (enterprise users)

## Pagination

Many list endpoints support pagination for handling large result sets efficiently.

### Pagination Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Current page number (starts at 1) |
| `per_page` | integer | 10 | Number of results per page (max 100) |
| `sort_by` | string | `created` | Field to sort by |
| `order` | string | `desc` | Sort order (`asc` or `desc`) |

### Paginated Endpoints

Endpoints that support pagination:
- `GET /api/security/events` - Security event log
- `GET /api/openspec/changes` - OpenSpec changes list
- `GET /api/health/alerts` - Active alerts

### Pagination Example Request

```bash
curl "http://localhost:8000/api/security/events?page=2&per_page=20&sort_by=timestamp&order=desc" \
  -H "Authorization: Bearer your-token"
```

### Pagination Response Example

```json
{
  "data": [
    {
      "timestamp": "2025-10-16T10:30:00Z",
      "type": "successful_auth",
      "severity": "low"
    },
    {
      "timestamp": "2025-10-16T10:15:00Z",
      "type": "api_call",
      "severity": "low"
    }
  ],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total_results": 156,
    "total_pages": 8,
    "has_next": true,
    "has_previous": true,
    "next_page": 3,
    "previous_page": 1
  }
}
```

### Pagination Best Practices

**1. Efficient Iteration**
```bash
# Iterate through all pages
for page in {1..8}; do
  curl "http://localhost:8000/api/security/events?page=$page&per_page=50"
done
```

**2. Handle Last Page**
```bash
# Stop when has_next is false
page=1
while true; do
  response=$(curl -s "http://localhost:8000/api/security/events?page=$page")
  echo "$response" | jq '.data'
  
  has_next=$(echo "$response" | jq '.pagination.has_next')
  if [ "$has_next" = "false" ]; then
    break
  fi
  
  page=$((page + 1))
done
```

**3. Optimize Page Size**
- Use larger `per_page` values (50-100) for faster iteration
- Trade-off: Larger pages = fewer requests but larger payloads
- API enforces maximum of 100 results per page

**4. Sorting Optimization**
```bash
# Most recent events first
curl "http://localhost:8000/api/security/events?sort_by=timestamp&order=desc&per_page=50"

# Oldest events first
curl "http://localhost:8000/api/security/events?sort_by=timestamp&order=asc&per_page=50"
```

## Health Monitoring

The health monitoring system provides comprehensive observability into the backend.

### Health Endpoints

| Endpoint | Purpose | Target SLA |
|----------|---------|-----------|
| `GET /api/health/detailed` | Enhanced health with service status, metrics | <2s |
| `GET /api/health/metrics` | Aggregated metrics over time windows | <500ms |
| `GET /api/health/alerts` | Active and resolved alerts | <100ms |
| `POST /api/health/alerts/{id}/acknowledge` | Acknowledge alert awareness | <100ms |

### Health Response Example

```json
{
  "overall_status": "healthy",
  "timestamp": "2025-10-17T05:59:01.671Z",
  "uptime_seconds": 12345.67,
  "services": {
    "model_manager": {"status": "healthy", "response_time_ms": 23.4},
    "embeddings": {"status": "healthy", "response_time_ms": 15.2},
    "cache": {"status": "healthy", "response_time_ms": 8.1}
  },
  "system_metrics": {
    "cpu_percent": 45.2,
    "memory_percent": 62.3,
    "disk_usage_percent": 73.1
  },
  "active_alerts": 0
}
```

### Alert Thresholds

| Metric | Warning | Error | Critical |
|--------|---------|-------|----------|
| CPU (%) | 70 | 85 | 95 |
| Memory (%) | 75 | 90 | 95 |
| Disk (%) | 80 | 90 | 95 |

**For complete health monitoring documentation, see** `agent/health_monitoring.py` **source code or use** `/docs` **for interactive reference.**

- **Allowed Origins**: Configurable via `cors_allowed_origins` setting
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Authorization, Content-Type, X-CSRF-Token
- **Credentials**: Supported for authenticated requests

## Interactive Documentation

The API provides interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Real-World Use Cases

### Use Case 1: Research Paper Summarization

**Scenario**: Quickly summarize and extract key findings from research papers

**Workflow**:
```bash
# 1. Index the PDF
curl -X POST "http://localhost:8000/api/index_pdf" \
  -H "Authorization: Bearer token" \
  -d '{"pdf_path": "/papers/ai-research.pdf"}'

# 2. Search for specific concepts
curl -X POST "http://localhost:8000/api/search" \
  -H "Authorization: Bearer token" \
  -d '{
    "query": "neural network architecture",
    "top_k": 3
  }'

# 3. Ask for synthesis
curl -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer token" \
  -d '{
    "question": "What are the main contributions of this paper?",
    "context_paths": ["/papers/ai-research.pdf"]
  }'
```

**Expected Result**: Structured summary with key findings, methodology, and conclusions

### Use Case 2: Content Aggregation & Analysis

**Scenario**: Analyze multiple web articles on a topic and synthesize findings

**Workflow**:
```bash
# 1. Analyze first article
curl -X POST "http://localhost:8000/api/web" \
  -H "Authorization: Bearer token" \
  -d '{
    "url": "https://news.example.com/ai-trends",
    "question": "What are the top AI trends?"
  }'

# 2. Analyze second article
curl -X POST "http://localhost:8000/api/web" \
  -H "Authorization: Bearer token" \
  -d '{
    "url": "https://blog.example.com/ml-predictions",
    "question": "What ML advancements are predicted?"
  }'

# 3. Synthesize from indexed notes
curl -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer token" \
  -d '{
    "question": "Compare and contrast the trends from both articles"
  }'
```

**Expected Result**: Comparative analysis with synthesis of information

### Use Case 3: Voice-to-Note Workflow

**Scenario**: Record voice notes and have them indexed for later search

**Workflow**:
```bash
# 1. Convert speech to text
curl -X POST "http://localhost:8000/api/voice_transcribe" \
  -H "Authorization: Bearer token" \
  -d '{
    "audio_data": "base64-encoded-audio",
    "format": "webm",
    "language": "en"
  }'

# 2. Reindex vault to include new notes
curl -X POST "http://localhost:8000/api/reindex" \
  -H "Authorization: Bearer token"

# 3. Search voice notes
curl -X POST "http://localhost:8000/api/search" \
  -H "Authorization: Bearer token" \
  -d '{"query": "meeting discussion points"}'
```

**Expected Result**: Voice notes indexed and searchable alongside typed notes

### Use Case 4: Performance Monitoring & Optimization

**Scenario**: Monitor system performance and trigger optimizations

**Workflow**:
```bash
# 1. Check current metrics
curl "http://localhost:8000/api/performance/metrics" | jq '.cache'

# 2. If cache hit rate is low, check detailed health
curl "http://localhost:8000/api/health/detailed" | jq '.services'

# 3. Trigger optimization if needed
curl -X POST "http://localhost:8000/api/performance/optimize"

# 4. Verify improvement
curl "http://localhost:8000/api/performance/metrics" | jq '.cache'
```

**Expected Result**: System optimized with improved cache hit rates and response times

### Use Case 5: Enterprise Multi-Tenant Setup

**Scenario**: Set up SSO authentication and track compliance

**Workflow**:
```bash
# 1. Check enterprise status
curl "http://localhost:8000/api/enterprise/status"

# 2. Initiate SSO for team member
curl -X POST "http://localhost:8000/api/enterprise/auth/sso" \
  -d '{
    "provider": "azure",
    "redirect_uri": "https://company.example.com/callback"
  }'

# 3. Verify compliance status
curl "http://localhost:8000/api/security/compliance"
```

**Expected Result**: Team members authenticated via SSO with compliance tracking

## SDK Examples

### Python
```python
import requests

# Basic request
response = requests.post(
    "http://localhost:8000/api/ask",
    headers={"Authorization": "Bearer your-token"},
    json={"question": "What is machine learning?"}
)
print(response.json())
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/ask', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: 'What is machine learning?'
  })
});
const data = await response.json();
console.log(data);
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'
```

## Performance Considerations

- **Response Times**: Target <100ms for health, <500ms for cached operations, <2s for AI generation
- **Caching**: Multi-level caching (L1 memory, L2 disk, L3 persistent, L4 vector DB)
- **Connection Pooling**: Managed pools for models and database connections
- **Background Processing**: Async task queue for heavy operations

## Deployment Notes

- **Health Checks**: Use `/status` for kubernetes liveness, `/health` for readiness
- **Configuration**: Environment variables override `agent/config.yaml`
- **Scaling**: Horizontal scaling supported with shared cache (Redis recommended)
- **Monitoring**: Comprehensive metrics available via `/api/performance/*` endpoints

