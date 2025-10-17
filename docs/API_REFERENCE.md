# API Reference

## Overview

The Obsidian AI Assistant backend provides a comprehensive REST API for AI-powered note analysis, vector search, web
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

## Core Endpoints

### Health & Status

#### GET /health
Comprehensive health check with system information.

**Response:**
```json
{
  "status": "ok",
  "timestamp": 1729094400,
  "backend_url": "http://localhost:8000",
  "api_port": 8000,
  "vault_path": "./vault",
  "models_dir": "./backend/models",
  "cache_dir": "./backend/cache",
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
  "backend/vector_db": "./backend/vector_db"
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
Reload configuration from `backend/config.yaml`.

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

## Rate Limiting

API endpoints are protected by rate limiting:

- **Default**: 100 requests per minute per IP
- **AI endpoints**: 20 requests per minute per user
- **Admin endpoints**: 50 requests per minute per admin user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1729094460
```

## CORS Policy

The API supports CORS for web applications:

- **Allowed Origins**: Configurable via `cors_allowed_origins` setting
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Authorization, Content-Type, X-CSRF-Token
- **Credentials**: Supported for authenticated requests

## Interactive Documentation

The API provides interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

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
- **Configuration**: Environment variables override `backend/config.yaml`
- **Scaling**: Horizontal scaling supported with shared cache (Redis recommended)
- **Monitoring**: Comprehensive metrics available via `/api/performance/*` endpoints
