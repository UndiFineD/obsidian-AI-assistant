# OpenSpec Change: Modular API Structure in agent/api/

## Executive Summary

**Change ID**: modular-api-structure  
**Status**: Ready for Review  
**Scope**: Reorganize API endpoints from monolithic to modular domain-driven architecture  
**Impact**: Medium-High (11 new files, 1 refactored)  
**Effort**: 11-17 hours  
**Timeline**: 5 phases  

---

## What's Changing

### Current State
All endpoints in one file:
```
agent/backend.py (1,700+ lines)
├── Health endpoints (GET /health, /status, /api/health/*)
├── Config endpoints (GET/POST /api/config)
├── Auth endpoints (POST /api/auth/*)
├── Ask endpoints (POST /ask, /api/ask)
├── Search endpoints (POST /api/search)
├── Indexing endpoints (POST /reindex, /api/index_pdf)
├── Voice endpoints (POST /transcribe)
├── Cache endpoints (POST /api/cache/*)
├── Logs endpoints (GET/POST /api/logs/*)
├── Security endpoints (POST /api/security/*)
└── Enterprise endpoints (POST /api/enterprise/*)
```

### After Migration
Modular domain-driven organization:
```
agent/api/
├── __init__.py               # Router registration
├── base.py                   # Base utilities
├── health.py                 # Health/status endpoints
├── config.py                 # Configuration endpoints
├── auth.py                   # Authentication endpoints
├── ask.py                    # Question/answer endpoints
├── search.py                 # Search endpoints
├── indexing.py               # Indexing endpoints
├── voice.py                  # Voice endpoints
├── cache.py                  # Cache management
├── logs.py                   # Logging endpoints
├── security.py               # Security endpoints
└── enterprise.py             # Enterprise features (optional)

agent/backend.py (REFACTORED)
├── Remove endpoints
├── Import routers
├── Keep service logic
```

---

## Why This Change?

### Problems Solved
1. ✅ **Maintainability**: Large single file hard to navigate
2. ✅ **Testability**: No clean way to test endpoint groups
3. ✅ **Scalability**: Adding endpoints clutters main file
4. ✅ **Team Collaboration**: Multiple developers can't work on different domains
5. ✅ **Code Quality**: Smaller files easier to review
6. ✅ **Onboarding**: New developers struggle with organization

### Benefits
- Cleaner, more organized codebase
- Each domain in dedicated module
- Easier to find and modify endpoints
- Parallel development possible
- Better for code reviews
- Supports enterprise features as optional module

---

## Implementation Timeline

| Phase | Duration | Tasks | Activities |
|-------|----------|-------|-----------|
| Phase 1 | 2-3h | 5 | Create directories, design patterns |
| Phase 2 | 4-6h | 11 | Extract and migrate endpoints |
| Phase 3 | 2-3h | 5 | Create routers, integrate app |
| Phase 4 | 2-3h | 5 | Test, verify compatibility |
| Phase 5 | 1-2h | 5 | Documentation, training |
| **Total** | **11-17h** | **31** | **Complete refactoring** |

---

## File Structure Overview

### Files to Create (11 files)
- `agent/api/__init__.py` - Router registration
- `agent/api/base.py` - Base utilities
- `agent/api/health.py` - Health/status endpoints
- `agent/api/config.py` - Configuration endpoints
- `agent/api/auth.py` - Authentication endpoints
- `agent/api/ask.py` - Question/answer endpoints
- `agent/api/search.py` - Search endpoints
- `agent/api/indexing.py` - Indexing endpoints
- `agent/api/voice.py` - Voice endpoints
- `agent/api/cache.py` - Cache management
- `agent/api/enterprise.py` - Enterprise features (optional)

### Files to Refactor (3-5 files)
- `agent/backend.py` - Remove endpoints, import routers
- `agent/app.py` - Create application factory
- Test files - Update imports

---

## Endpoint Organization

### Health Module (7 endpoints)
```
GET  /health                          Basic health check
GET  /status                          Detailed status
GET  /api/health                      API health check
GET  /api/health/detailed             Enhanced health
GET  /api/health/metrics              Time-window metrics
GET  /api/health/alerts               Active alerts
POST /api/health/alerts/{id}/ack      Acknowledge alert
```

### Config Module (3 endpoints)
```
GET  /api/config                      Get configuration
POST /api/config                      Update configuration
POST /api/config/reload               Reload config from file
```

### Auth Module (3+ endpoints)
```
POST /api/auth/token                  Get JWT token
GET  /api/auth/verify                 Verify token
POST /api/auth/api_key/rotate         Rotate API key
```

### Ask Module (2 endpoints)
```
POST /ask                             Original ask endpoint
POST /api/ask                         API ask endpoint
```

### Search Module (1 endpoint)
```
POST /api/search                      Vector similarity search
```

### Indexing Module (3 endpoints)
```
POST /reindex                         Full vault reindex
POST /api/scan_vault                  Alias for reindex
POST /api/index_pdf                   Index PDF file
```

### Voice Module (2 endpoints)
```
POST /transcribe                      Audio transcription
POST /api/voice_transcribe            API voice endpoint
```

### Cache Module (2+ endpoints)
```
POST /api/cache/clear                 Clear cache
POST /api/cache/*                     Other cache endpoints
```

### Logs Module (2+ endpoints)
```
GET  /api/logs/*                      Get logs
POST /api/logs/*                      Log management
```

### Security Module (2+ endpoints)
```
POST /api/security/*                  Security operations
```

### Enterprise Module (5+ endpoints - OPTIONAL)
```
GET  /api/enterprise/status           Feature status
POST /api/enterprise/auth/sso         SSO authentication
GET  /api/enterprise/users            User management
POST /api/enterprise/tenants          Tenant management
GET  /api/enterprise/compliance/*     Compliance reporting
```

---

## Key Design Patterns

### Module Structure (MUST)
```python
# Each module follows this pattern
from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["domain"]
)

@router.get("/endpoint")
async def endpoint():
    pass

__all__ = ["router"]
```

### Router Registration (MUST)
```python
# Central registration in __init__.py
from . import health, config, auth, ask, search, indexing, voice

def register_routers(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(config.router)
    # ... register all routers
```

### Application Factory (MUST)
```python
# app.py creates and configures app
from agent.api import register_routers

def create_app() -> FastAPI:
    app = FastAPI()
    register_routers(app)
    return app

app = create_app()
```

---

## Backward Compatibility

✅ **100% Backward Compatible**
- All original endpoints continue working
- Same response formats
- Same status codes
- Same error handling
- No breaking changes

---

## Quality Commitments

- ✅ **100% Test Pass Rate** - All tests must pass
- ✅ **95%+ Code Coverage** - Coverage maintained
- ✅ **<5% Performance Variance** - No degradation
- ✅ **Zero Breaking Changes** - Full compatibility
- ✅ **Complete Documentation** - All guides updated

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Missed endpoints | Low | Medium | Comprehensive migration checklist |
| Circular imports | Low | Medium | Use DI, avoid circular deps |
| Performance impact | Very Low | Low | Router registration minimal overhead |
| Team confusion | Low | Low | Clear documentation and training |

---

## Success Metrics

| Metric | Target | How Validated |
|--------|--------|--------------|
| Endpoints migrated | 100% | All in modules |
| Backward compatibility | 100% | Tests pass |
| Code coverage | 95%+ | Coverage reports |
| Response time variance | <5% | Performance tests |
| Documentation | 100% | All guides written |

---

## Team Review Checklist

### Before Approval
- [ ] Change scope understood
- [ ] Module organization makes sense
- [ ] Router pattern is clear
- [ ] Performance impact acceptable
- [ ] Backward compatibility guaranteed
- [ ] Timeline realistic
- [ ] Risk mitigations adequate

### After Approval
- [ ] Assigned to developer
- [ ] Feature branch created
- [ ] Phases executed sequentially
- [ ] Tests pass at each phase
- [ ] Documentation updated
- [ ] Team trained on new structure

---

## Next Steps

1. **This Week**: Review and provide feedback
2. **Next Week (if approved)**:
   - Create feature branch
   - Execute Phase 1-5
   - Test continuously
   - Merge to main
3. **After Merge**:
   - Deploy to staging
   - Monitor for issues
   - Train team

---

**Status**: Ready for Review  
**Version**: 1.0  
**Created**: October 21, 2025  
**OpenSpec Governance**: ✅ Compliant
