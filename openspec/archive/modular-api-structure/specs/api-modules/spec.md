# Specification: Modular API Structure in agent/api/

## Capability Declaration

This specification governs the reorganization of API endpoints from a monolithic
structure in `agent/backend.py` to a modular, domain-driven architecture within
`agent/api/` directory. It establishes requirements for:

- ✅ API module organization and structure
- ✅ Router creation and registration
- ✅ Endpoint organization by domain
- ✅ Backward compatibility maintenance
- ✅ Application factory pattern
- ✅ Testing requirements

---

## Governance Keywords

- **MUST**: Mandatory requirement
- **SHOULD**: Strong recommendation
- **MAY**: Optional enhancement
- **REQUIREMENT**: Implementation requirement
- **CAPABILITY GOVERNS**: Scope declaration

---

## Directory Structure (MUST)

### API Module Organization

The `agent/api/` directory MUST contain domain-specific modules:

```
agent/api/
├── __init__.py              # Router registration (MUST)
├── base.py                  # Base utilities (MUST)
├── health.py                # Health/status endpoints (MUST)
├── config.py                # Configuration endpoints (MUST)
├── auth.py                  # Authentication endpoints (MUST)
├── ask.py                   # Question/answer endpoints (MUST)
├── search.py                # Search endpoints (MUST)
├── indexing.py              # Indexing endpoints (MUST)
├── voice.py                 # Voice endpoints (MUST)
├── cache.py                 # Cache endpoints (MUST)
├── logs.py                  # Logging endpoints (MUST)
├── security.py              # Security endpoints (MUST)
└── enterprise.py            # Enterprise features (MAY)
```

**Requirements**:
- MUST have dedicated subdirectory in agent/
- MUST contain one module per endpoint domain
- MUST include `__init__.py` and `base.py`
- SHOULD include enterprise module (optional)

---

## Module Structure (MUST)

### Standard Module Pattern

Each API module MUST follow this structure:

```python
# agent/api/health.py
from fastapi import APIRouter, Depends
from typing import List

# Import services and dependencies
from agent.services import get_orchestrator
from agent.models import HealthResponse

# Create router with metadata
router = APIRouter(
    prefix="/api",
    tags=["health"],
    dependencies=[]
)

# Define endpoints
@router.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint.
    
    Returns: Service status
    SLA: <100ms
    """
    pass

@router.get("/status")
async def detailed_status() -> DetailedStatusResponse:
    """Detailed status endpoint.
    
    Returns: Full system status
    SLA: <100ms
    """
    pass

# Export router
__all__ = ["router"]
```

**Requirements**:
- MUST define APIRouter with appropriate prefix
- MUST tag endpoints with domain
- MUST include all related endpoints
- MUST export router as `__all__`
- MUST have consistent docstrings

---

## Router Registration (MUST)

### Central Registration in __init__.py

The `agent/api/__init__.py` MUST handle router registration:

```python
# agent/api/__init__.py
from fastapi import FastAPI
from agent.settings import get_settings

# Import all routers
from . import health, config, auth, ask, search, indexing, voice
from . import cache, logs, security

# Conditionally import optional routers
try:
    from . import enterprise
    ENTERPRISE_AVAILABLE = True
except ImportError:
    ENTERPRISE_AVAILABLE = False

def register_routers(app: FastAPI) -> None:
    """Register all API routers.
    
    Args:
        app: FastAPI application instance
    """
    # Register core routers (always available)
    app.include_router(health.router)
    app.include_router(config.router)
    app.include_router(auth.router)
    app.include_router(ask.router)
    app.include_router(search.router)
    app.include_router(indexing.router)
    app.include_router(voice.router)
    app.include_router(cache.router)
    app.include_router(logs.router)
    app.include_router(security.router)
    
    # Register optional enterprise routers
    if get_settings().enterprise_enabled and ENTERPRISE_AVAILABLE:
        app.include_router(enterprise.router)

__all__ = ["register_routers"]
```

**Requirements**:
- MUST import all core routers
- MUST handle optional routers safely
- MUST use feature toggles for enterprise
- MUST be called from application factory

---

## Endpoint Organization (MUST)

### Domain-Based Organization

Endpoints MUST be organized by business domain:

#### Health Module (MUST)
- Endpoints: GET `/health`, `/status`, `/api/health/*`
- Responsibility: System health, metrics, alerts
- Prefix: `/api`
- SLA: <100ms

#### Config Module (MUST)
- Endpoints: GET/POST `/api/config`, `/api/config/reload`
- Responsibility: Configuration management
- Prefix: `/api`
- SLA: <500ms

#### Auth Module (MUST)
- Endpoints: POST `/api/auth/*`, authentication
- Responsibility: JWT tokens, API keys, verification
- Prefix: `/api`
- SLA: <500ms

#### Ask Module (MUST)
- Endpoints: POST `/ask`, `/api/ask`
- Responsibility: Question answering with models
- Prefix: (no prefix for `/ask`, `/api` for `/api/ask`)
- SLA: <2s (cached), <5s (uncached)

#### Search Module (MUST)
- Endpoints: POST `/api/search`
- Responsibility: Vector similarity search
- Prefix: `/api`
- SLA: <2s

#### Indexing Module (MUST)
- Endpoints: POST `/reindex`, `/api/scan_vault`, `/api/index_pdf`
- Responsibility: Document indexing and vault scanning
- Prefix: (varies)
- SLA: <60s

#### Voice Module (MUST)
- Endpoints: POST `/transcribe`
- Responsibility: Audio transcription
- Prefix: (no `/api` prefix)
- SLA: <500ms

#### Cache Module (MUST)
- Endpoints: POST `/api/cache/*`
- Responsibility: Cache management and optimization
- Prefix: `/api`
- SLA: <100ms

#### Logs Module (MUST)
- Endpoints: GET/POST `/api/logs/*`
- Responsibility: Logging management
- Prefix: `/api`
- SLA: <500ms

#### Security Module (MUST)
- Endpoints: POST `/api/security/*`
- Responsibility: Security operations
- Prefix: `/api`
- SLA: <500ms

#### Enterprise Module (MAY)
- Endpoints: `/api/enterprise/*`
- Responsibility: Enterprise features (optional)
- Prefix: `/api`
- Status: Optional, feature-toggled

---

## Application Factory (MUST)

### Factory Pattern Implementation

Application initialization MUST use factory pattern in `agent/app.py`:

```python
# agent/app.py
from fastapi import FastAPI
from fastapi.middleware import Middleware
from agent.api import register_routers
from agent.middleware import setup_middleware
from agent.settings import get_settings

def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()
    
    # Create application
    app = FastAPI(
        title="Obsidian AI Agent",
        description="AI-powered note assistant",
        version="2.0",
        openapi_url="/api/openapi.json" if settings.debug else None
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Register API routers
    register_routers(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    return app

# Create and export app instance
app = create_app()
```

**Requirements**:
- MUST create FastAPI instance
- MUST call register_routers()
- MUST setup middleware
- MUST setup exception handlers
- MUST export app instance

---

## Backward Compatibility (MUST)

### API Compatibility Guarantees

All original endpoints MUST work identically:

| Original Path | Module | Status |
|---------------|--------|--------|
| `/health` | health.py | ✅ MUST work |
| `/api/health` | health.py | ✅ MUST work |
| `/status` | health.py | ✅ MUST work |
| `/ask` | ask.py | ✅ MUST work |
| `/api/ask` | ask.py | ✅ MUST work |
| `/api/config` | config.py | ✅ MUST work |
| `/api/search` | search.py | ✅ MUST work |
| `/reindex` | indexing.py | ✅ MUST work |
| `/api/scan_vault` | indexing.py | ✅ MUST work |
| `/transcribe` | voice.py | ✅ MUST work |

**Requirements**:
- ✅ All paths must work identically
- ✅ Same response formats
- ✅ Same status codes
- ✅ Same error handling

---

## Testing Requirements (MUST)

### Module-Level Tests

Each module MUST have comprehensive tests:

```python
# tests/agent/api/test_health.py
from fastapi.testclient import TestClient
from agent.app import app

client = TestClient(app)

def test_health_endpoint():
    """Health endpoint must return 200."""
    response = client.get("/health")
    assert response.status_code == 200

def test_api_health_endpoint():
    """API health endpoint must return 200."""
    response = client.get("/api/health")
    assert response.status_code == 200

def test_status_endpoint():
    """Status endpoint must return detailed info."""
    response = client.get("/status")
    assert response.status_code == 200
    assert "status" in response.json()
```

**Coverage Requirements**:
- ✅ Endpoint existence tests
- ✅ Response format tests
- ✅ Error condition tests
- ✅ Authentication tests
- ✅ 95%+ coverage per module

### Integration Tests

Router registration MUST be tested:

```python
def test_all_routers_registered():
    """All routers must be registered."""
    # Test that all domains accessible
    assert client.get("/health").status_code == 200
    assert client.post("/api/config").status_code in [200, 422]
    # ... test all domains
```

### Performance Tests

Response times MUST meet SLAs:

```python
def test_health_sla():
    """Health endpoint must be <100ms."""
    start = time.time()
    response = client.get("/health")
    elapsed = (time.time() - start) * 1000
    assert elapsed < 100
```

---

## Base Router Utilities (MUST)

### Common Patterns in base.py

Base utilities MUST provide:

```python
# agent/api/base.py
from fastapi import APIRouter, Request
from typing import Callable

# Common response models
class StandardResponse(BaseModel):
    """Standard API response envelope."""
    status: str
    data: Any
    timestamp: datetime

# Common error handlers
async def common_exception_handler(request: Request, exc: Exception):
    """Common exception handling."""
    return StandardResponse(
        status="error",
        data=None,
        timestamp=datetime.now()
    )

# Common dependencies
async def get_current_user(request: Request) -> User:
    """Get current authenticated user."""
    pass

__all__ = [
    "StandardResponse",
    "common_exception_handler",
    "get_current_user"
]
```

**Requirements**:
- MUST provide common response models
- MUST provide common error handlers
- MUST provide common dependencies
- MUST be reused across modules

---

## Migration Path (MUST)

### Incremental Migration

Migration MUST be incremental:

1. **Phase 1**: Create directory and base utilities
2. **Phase 2**: Migrate endpoints module by module
3. **Phase 3**: Integrate routers into app factory
4. **Phase 4**: Verify backward compatibility
5. **Phase 5**: Remove old endpoint code from backend.py

**Requirements**:
- MUST maintain working state during migration
- MUST verify each phase
- MUST test continuously
- MUST not introduce breaking changes

---

## Success Criteria

### Functional Success (MUST)
- ✅ All endpoints in modules
- ✅ Endpoints work identically
- ✅ No missing endpoints
- ✅ 100% backward compatibility
- ✅ App starts correctly

### Quality Success (MUST)
- ✅ All tests passing (100%)
- ✅ No performance degradation
- ✅ Coverage maintained (95%+)
- ✅ No new warnings/errors
- ✅ API docs complete

### Organization Success (MUST)
- ✅ Clear module structure
- ✅ Logical endpoint grouping
- ✅ Easy to find endpoints
- ✅ Easy to add endpoints
- ✅ Easy to test domains

---

**Specification Status**: Active  
**Version**: 1.0  
**Last Updated**: October 21, 2025
