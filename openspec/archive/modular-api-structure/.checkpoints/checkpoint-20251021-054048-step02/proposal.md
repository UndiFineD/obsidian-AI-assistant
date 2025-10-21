# OpenSpec Change Proposal: Modular API Structure in agent/api/

## Executive Summary

This proposal addresses the current monolithic API structure where all endpoints are
defined directly in `agent/backend.py`. The change establishes a modular, domain-driven
API architecture where endpoints are organized into separate modules within `agent/api/`
directory, improving maintainability, testability, and scalability.

**Change ID**: modular-api-structure  
**Status**: Ready for Review  
**Impact Level**: Medium-High  
**Complexity**: Medium  
**Scope**: API organization and endpoint consolidation

---

## Problem Statement

### Current State

All API endpoints are currently implemented in a single file:
- `agent/backend.py` (~1,700+ lines)
- Contains all endpoint decorators (@app.post, @app.get)
- Mixes concerns: health, config, ask, search, indexing, voice, auth, enterprise
- Difficult to find specific endpoints
- Hard to test individual domains
- Tight coupling between domains

### Issues

1. **Maintainability**: Single large file hard to navigate and modify
2. **Testability**: No clean way to test endpoint groups independently
3. **Organization**: No clear structure for endpoint domains
4. **Scalability**: Adding new endpoints clutters the main file
5. **Team Collaboration**: Multiple developers can't work on different domains
6. **Onboarding**: New developers struggle to understand endpoint organization
7. **Code Review**: Large file makes reviewing endpoint changes difficult

---

## Proposed Solution

### New API Directory Structure

Organize endpoints into domain-specific modules:

```
agent/
├── api/                           # NEW: Modular API (MUST)
│   ├── __init__.py               # Exports and router registration
│   ├── base.py                   # Base router and common utilities
│   ├── health.py                 # Health, status, metrics endpoints
│   ├── config.py                 # Configuration endpoints
│   ├── auth.py                   # Authentication endpoints
│   ├── ask.py                    # Question/answer endpoints
│   ├── search.py                 # Vector search endpoints
│   ├── indexing.py               # Document indexing endpoints
│   ├── voice.py                  # Voice transcription endpoints
│   ├── cache.py                  # Cache management endpoints
│   ├── logs.py                   # Logging endpoints
│   ├── security.py               # Security endpoints
│   └── enterprise.py             # Enterprise features (optional)
├── backend.py                     # REFACTORED: Application factory
├── app.py                         # Application initialization
└── ... (other modules)
```

### Key Features

#### 1. Domain-Based Organization (MUST)

Each endpoint domain has dedicated module:
- **health.py**: GET `/health`, `/status`, `/api/health/*`
- **config.py**: GET/POST `/api/config`
- **ask.py**: POST `/ask`, `/api/ask`
- **search.py**: POST `/api/search`
- **indexing.py**: POST `/reindex`, `/api/scan_vault`, `/api/index_pdf`
- **voice.py**: POST `/transcribe`
- **auth.py**: POST `/api/auth/*`, authentication endpoints
- **cache.py**: POST `/api/cache/*`, cache management
- **logs.py**: GET/POST `/api/logs/*`
- **security.py**: POST `/api/security/*`
- **enterprise.py**: `/api/enterprise/*` (optional)

#### 2. Consistent Module Structure (MUST)

Each API module MUST follow pattern:

```python
# agent/api/health.py
from fastapi import APIRouter, Depends
from agent.services import ServiceOrchestrator

router = APIRouter(
    prefix="/api",
    tags=["health"],
    dependencies=[]
)

@router.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    pass

@router.get("/status")
async def detailed_status() -> StatusResponse:
    """Detailed status."""
    pass

# Export for registration
__all__ = ["router"]
```

#### 3. Application Factory Pattern (MUST)

Main application initialization in `app.py`:

```python
# agent/app.py
from fastapi import FastAPI
from agent.api import register_routers

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Obsidian AI Agent",
        version="2.0"
    )
    
    # Register all API routers
    register_routers(app)
    
    # Add middleware
    add_middleware(app)
    
    return app

app = create_app()
```

#### 4. Router Registration (MUST)

Centralized router registration in `agent/api/__init__.py`:

```python
# agent/api/__init__.py
from fastapi import FastAPI
from . import health, config, auth, ask, search, indexing, voice
from . import cache, logs, security, enterprise

def register_routers(app: FastAPI) -> None:
    """Register all API routers."""
    # Core routers (always registered)
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
    
    # Optional enterprise routers
    if get_settings().enterprise_enabled:
        app.include_router(enterprise.router)

__all__ = ["register_routers"]
```

#### 5. Backward Compatibility (MUST)

All original endpoints continue working:
- ✅ `/health` → health.py
- ✅ `/api/health` → health.py
- ✅ `/api/config` → config.py
- ✅ `/ask` → ask.py
- ✅ `/api/ask` → ask.py
- ✅ `/api/search` → search.py
- ✅ `/reindex` → indexing.py
- ✅ `/transcribe` → voice.py

---

## Benefits

### 1. **Improved Maintainability**
- Clear endpoint organization
- Easy to locate endpoints
- Focused change impact
- Reduced cognitive load

### 2. **Better Testability**
- Test each domain independently
- Isolated mock services
- Focused unit tests
- Domain-specific fixtures

### 3. **Scalability**
- Easy to add new endpoint domains
- No file size constraints
- Parallel development possible
- Feature teams can own domains

### 4. **Code Quality**
- Smaller files easier to review
- Clear responsibility boundaries
- Better SOLID principles
- Reduced complexity per file

### 5. **Team Productivity**
- Parallel development on different domains
- Fewer merge conflicts
- Clear code ownership
- Faster onboarding

### 6. **Enterprise Support**
- Optional enterprise module
- Clean feature toggle
- No pollution of core API
- Easy to distribute separately

---

## Implementation Plan

### Phase 1: Preparation (2-3 hours)

**Tasks**:
1. Create `agent/api/` directory structure
2. Create base router utilities
3. Design module interfaces
4. Plan endpoint groupings
5. Update imports structure

### Phase 2: Migration (4-6 hours)

**Tasks**:
1. Extract health endpoints → `health.py`
2. Extract config endpoints → `config.py`
3. Extract auth endpoints → `auth.py`
4. Extract ask endpoints → `ask.py`
5. Extract search endpoints → `search.py`
6. Extract indexing endpoints → `indexing.py`
7. Extract voice endpoints → `voice.py`
8. Extract cache endpoints → `cache.py`
9. Extract logs endpoints → `logs.py`
10. Extract security endpoints → `security.py`
11. Extract enterprise endpoints → `enterprise.py`

### Phase 3: Integration (2-3 hours)

**Tasks**:
1. Create router registration system
2. Create application factory
3. Update `backend.py` to use new structure
4. Update imports and dependencies
5. Verify all endpoints accessible

### Phase 4: Verification (2-3 hours)

**Tasks**:
1. Run full endpoint test suite
2. Verify backward compatibility
3. Test endpoint discovery
4. Performance validation
5. API documentation generation

### Phase 5: Documentation (1-2 hours)

**Tasks**:
1. Create API module guide
2. Update architecture documentation
3. Create contribution guide for API
4. Update developer setup guide
5. Create endpoint reference

---

## Files to Change

### New Files (11 files)
- `agent/api/__init__.py` - Router registration
- `agent/api/base.py` - Base router utilities
- `agent/api/health.py` - Health/status endpoints
- `agent/api/config.py` - Configuration endpoints
- `agent/api/auth.py` - Authentication endpoints
- `agent/api/ask.py` - Question/answer endpoints
- `agent/api/search.py` - Search endpoints
- `agent/api/indexing.py` - Indexing endpoints
- `agent/api/voice.py` - Voice endpoints
- `agent/api/cache.py` - Cache endpoints
- `agent/api/enterprise.py` - Enterprise endpoints (optional)

### Modified Files (3-5 files)
- `agent/backend.py` - Remove endpoints, import routers
- `agent/app.py` - Create application factory
- Test files - Update imports
- Documentation files

---

## Success Criteria

### Functional Success (MUST)
- ✅ All endpoints migrated to modules
- ✅ All endpoints work identically
- ✅ No endpoints missing
- ✅ Backward compatibility 100%
- ✅ Application starts correctly

### Quality Success (MUST)
- ✅ All tests passing (100%)
- ✅ No performance degradation
- ✅ Code coverage maintained
- ✅ No new warnings/errors
- ✅ API docs generate correctly

### Organization Success (MUST)
- ✅ Clear module structure
- ✅ Logical endpoint grouping
- ✅ Easy to find endpoints
- ✅ Easy to add new endpoints
- ✅ Easy to test domains

### Documentation Success (MUST)
- ✅ API guide complete
- ✅ Module structure documented
- ✅ Contribution guide created
- ✅ Examples provided
- ✅ Team trained

---

## Risk Assessment

### Risk: Migration Errors
**Likelihood**: Low  
**Impact**: Medium  
**Mitigation**:
- Incremental migration (one domain at a time)
- Comprehensive testing after each migration
- Backward compatibility verification

### Risk: Performance Impact
**Likelihood**: Very Low  
**Impact**: Low  
**Mitigation**:
- Router registration is minimal overhead
- Performance tests validate no degradation
- Same code, just organized differently

### Risk: Circular Dependencies
**Likelihood**: Low  
**Impact**: Medium  
**Mitigation**:
- Use dependency injection
- Avoid circular imports
- Central imports management

### Risk: Team Confusion
**Likelihood**: Low  
**Impact**: Low  
**Mitigation**:
- Clear documentation
- Team training/walkthrough
- Contributing guide

---

## Timeline

| Phase | Duration | Effort | Tasks |
|-------|----------|--------|-------|
| Phase 1 | 2-3h | 2h | Preparation |
| Phase 2 | 4-6h | 5h | Migration |
| Phase 3 | 2-3h | 2h | Integration |
| Phase 4 | 2-3h | 2h | Verification |
| Phase 5 | 1-2h | 1h | Documentation |
| **Total** | **11-17h** | **12h** | **5 phases** |

---

## Future Enhancements (MAY)

- MAY: Auto-generated API documentation
- MAY: OpenAPI schema per domain
- MAY: Endpoint versioning (v1, v2)
- MAY: API rate limiting per domain
- MAY: Domain-specific middleware
- MAY: OpenTelemetry tracing per endpoint

---

## Related Changes

This change works well with:
- **modularize-agent**: Complements service-oriented architecture
- **reorganize-models-directory**: Independent improvement
- Both improve code organization and maintainability

---

**Proposal Status**: Ready for Review  
**Created**: October 21, 2025  
**Version**: 1.0
