# Specification: Modular Service-Oriented Agent Architecture

## Capability Declaration

This specification governs the implementation of a **modular, service-oriented architecture** for the Obsidian AI Agent. The capability establishes requirements for:

- ✅ Service module organization and structure
- ✅ Dependency injection and service lifecycle
- ✅ Provider pattern for pluggable implementations
- ✅ Feature toggles and optional services
- ✅ API endpoint organization
- ✅ Backward compatibility guarantees
- ✅ Testing requirements (150+ new tests)
- ✅ Performance SLAs (Tier 1-5 compliance)

---

## Governance Keywords

This specification uses OpenSpec governance language:

- **MUST**: Mandatory requirement, must be implemented
- **SHOULD**: Strong recommendation, implement unless justified
- **MAY**: Optional enhancement, nice to have
- **MUST NOT**: Prohibition, never do this
- **CAPABILITY GOVERNS**: This specification defines the capability
- **REQUIREMENT**: Implementation requirement

---

## Architecture Requirements

### Module Organization (MUST)

The agent MUST be organized into the following modules:

```
agent/
├── models/                    # AI Model Services
├── embeddings/               # Vector/Embedding Services
├── vector_db/               # Vector Database Services
├── indexing/                # Document Indexing Services
├── cache/                   # Multi-level Caching
├── voice/                   # Voice Processing Services
├── security/                # Security & Authentication
├── api/                     # API Endpoints (by domain)
├── enterprise/              # Enterprise Features (optional)
├── services/                # Orchestration/Coordination
├── middleware/              # HTTP Middleware
└── utils/                   # Utilities
```

**Requirement**: Each module MUST have:
- `__init__.py` with module exports
- `base.py` with abstract interfaces (except utils)
- Concrete implementations
- Unit tests with 95%+ coverage

### Service Interface Pattern (MUST)

Each service module MUST implement the provider pattern:

```python
# base.py
class BaseServiceProvider(ABC):
    """Abstract base for service implementations."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def validate(self) -> bool:
        """Validate service is operational."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Graceful shutdown."""
        pass
```

**Requirement**: All services MUST:
- Inherit from appropriate base class
- Implement initialization protocol
- Implement validation protocol
- Implement shutdown protocol
- Use async/await throughout

### Dependency Injection (MUST)

The application MUST use dependency injection for all service dependencies:

```python
# ServiceOrchestrator coordinates all services
class ServiceOrchestrator:
    def __init__(self, config: Config):
        # Initialize services with dependencies
        pass
    
    def get_service(self, name: str) -> Service:
        # Lazy loading with caching
        pass
```

**Requirement**: 
- Services MUST NOT create their own dependencies
- All dependencies MUST be injected via constructor
- ServiceOrchestrator MUST coordinate initialization
- Lifecycle MUST be managed centrally

### Configuration Management (MUST)

Configuration MUST be centralized in `config.py`:

```python
class Config:
    """Centralized configuration."""
    
    # Model configuration
    model_backend: str = "gpt4all"
    model_path: str = "agent/models/..."
    
    # Service toggles
    enable_voice: bool = True
    enable_enterprise: bool = False
    
    # Feature flags
    cache_enabled: bool = True
    vector_db_enabled: bool = True
```

**Requirement**:
- Configuration MUST be centralized
- Services MUST be optional via toggles
- Environment variables MUST override config file
- Configuration MUST be validated on startup

### API Endpoint Organization (MUST)

API endpoints MUST be organized by domain in `api/` module:

```
api/
├── health.py          # GET /health, /status
├── config.py          # GET/POST /api/config
├── ask.py             # POST /ask, /api/ask
├── search.py          # POST /api/search
├── indexing.py        # POST /reindex, /api/scan_vault
├── voice.py           # POST /transcribe
└── enterprise.py      # Enterprise endpoints
```

**Requirement**:
- Each domain MUST have own router module
- Routers MUST be imported in `__init__.py`
- Endpoints MUST be registered via `app.include_router()`
- All endpoints MUST be type-hinted
- All endpoints MUST have tests

### Backward Compatibility (MUST)

The modular architecture MUST maintain 100% backward compatibility:

```python
# Existing API endpoints MUST continue to work:
POST /ask                    # Original endpoint
POST /api/ask                # API variant
GET /health                  # Original health check
GET /status                  # Status with details
```

**Requirement**:
- All existing API endpoints MUST work unchanged
- Configuration format MUST be compatible
- Database schema MUST NOT change
- Cache format MUST NOT change
- No breaking changes for users

---

## Testing Requirements (MUST)

### Test Coverage (MUST)

Each phase MUST include comprehensive tests:

| Phase | Module Tests | Integration Tests | Performance Tests | Total |
|-------|--------------|-------------------|-------------------|-------|
| Phase 1 | 50 | - | - | 50 |
| Phase 2 | 40 | 12 | - | 40 |
| Phase 3 | 30 | - | - | 30 |
| Phase 4 | - | - | 20 | 20 |
| **Total** | **120** | **12** | **20** | **150+** |

**Requirement**:
- Unit tests: 95%+ coverage per module
- Integration tests: 100% API coverage
- Performance tests: All Tier 1-5 operations
- All tests MUST pass before phase completion

### Performance Requirements (MUST)

The modular architecture MUST meet SLA targets:

| Tier | Target | Operations |
|------|--------|-----------|
| Tier 1 | <100ms | Health checks, status, config, cache lookup |
| Tier 2 | <500ms | Cached ask, simple search, voice transcription |
| Tier 3 | <2s | AI generation, document search, embeddings |
| Tier 4 | <10s | Web analysis, large document indexing |
| Tier 5 | <60s | Vault reindex, model loading |

**Requirement**:
- Performance impact MUST be <5% vs existing
- All Tier 1-5 operations MUST pass SLA tests
- Lazy loading MUST NOT degrade performance
- Startup time MUST NOT increase >10%

### Security Testing (MUST)

Security tests MUST cover:

- ✅ Authentication and authorization
- ✅ Input validation and sanitization
- ✅ Encryption/decryption operations
- ✅ Rate limiting and abuse prevention
- ✅ Audit logging and compliance
- ✅ Dependency vulnerability scanning

**Requirement**: Security tests MUST pass with zero critical vulnerabilities.

---

## Feature Toggle Specification

### Toggle Categories (MUST)

Services MUST support feature toggles:

```yaml
features:
  # Core services (MUST be always available)
  core:
    models: true
    embeddings: true
    vector_db: true
  
  # Optional services
  voice:
    enabled: true
    provider: "vosk"  # or "whisper"
  
  indexing:
    enabled: true
    providers: ["markdown", "pdf", "web"]
  
  enterprise:
    enabled: false
    sso: false
    multi_tenant: false
    compliance: false
```

**Requirement**:
- Feature toggles MUST enable/disable services
- Services MUST not initialize if disabled
- Configuration MUST validate available providers
- Tests MUST cover all toggle combinations

---

## Implementation Phases

### Phase 1: Foundation (MUST)

Phase 1 MUST establish the modular foundation:

- ✅ Directory structure created
- ✅ ServiceOrchestrator implemented
- ✅ Core services modularized (models, embeddings, vector_db)
- ✅ 50+ unit tests
- ✅ Code coverage 88%+
- ✅ Architecture review passed

### Phase 2: Services & APIs (MUST)

Phase 2 MUST migrate remaining services:

- ✅ All services migrated to modules
- ✅ API endpoints organized by domain
- ✅ Middleware integrated
- ✅ 40+ unit + integration tests
- ✅ Code coverage 90%+
- ✅ API tests 100% pass

### Phase 3: Features & Polish (MUST)

Phase 3 MUST implement feature toggles:

- ✅ Enterprise features optional
- ✅ Feature toggles working
- ✅ Performance validated
- ✅ 30+ unit tests
- ✅ Code coverage 92%+
- ✅ <5% performance impact

### Phase 4: Documentation (MUST)

Phase 4 MUST complete deployment:

- ✅ Documentation 100% complete
- ✅ Migration utilities created
- ✅ Deployment tested
- ✅ 20+ performance + deployment tests
- ✅ Code coverage 88%+ maintained
- ✅ Production ready

---

## Validation & Governance

### OpenSpec Compliance (CAPABILITY GOVERNS)

This specification GOVERNS:

1. **Module Structure**: Must follow directory layout
2. **Service Interfaces**: Must implement base classes
3. **Dependency Injection**: Must use ServiceOrchestrator
4. **Testing**: Must achieve 150+ tests
5. **Performance**: Must meet SLA targets
6. **Backward Compatibility**: Must maintain 100% API compatibility
7. **Documentation**: Must be 100% complete

### Compliance Validation (MUST)

Compliance MUST be validated through:

```python
# conftest.py compliance tests
def test_module_structure():
    """Verify modular structure exists."""
    assert Path("agent/models").exists()
    assert Path("agent/embeddings").exists()
    assert Path("agent/services").exists()
    # ... all modules

def test_service_interfaces():
    """Verify all services implement interfaces."""
    assert hasattr(ModelService, 'validate')
    assert hasattr(EmbeddingService, 'validate')
    # ... all services

def test_backward_compatibility():
    """Verify all original endpoints work."""
    response = client.post("/ask", json={"prompt": "test"})
    assert response.status_code in [200, 422, 500]
    # ... all endpoints
```

**Requirement**: Compliance tests MUST pass 100%.

---

## Success Criteria

### Functional Success (MUST)

- ✅ Modular structure complete and working
- ✅ All services migrated to modules
- ✅ Feature toggles operational
- ✅ All existing endpoints working
- ✅ Zero production issues

### Quality Success (MUST)

- ✅ 150+ new tests written
- ✅ All tests passing (100% success rate)
- ✅ Code coverage 88%+ maintained
- ✅ All Tier 1-5 SLAs met
- ✅ Zero security vulnerabilities

### Documentation Success (MUST)

- ✅ Architecture guide complete
- ✅ Module reference guide complete
- ✅ Plugin developer guide complete
- ✅ Migration guide complete
- ✅ Examples for all modules

### Deployment Success (MUST)

- ✅ Deployment tested (multiple scenarios)
- ✅ Migration utilities working
- ✅ Rollback procedures tested
- ✅ Production checklist complete
- ✅ Team trained and ready

---

## References

- **Architecture Proposal**: `proposal.md` in same change directory
- **Implementation Tasks**: `tasks.md` in same change directory
- **Test Coverage**: 150+ new tests across 4 phases
- **Performance SLAs**: docs/PERFORMANCE_REQUIREMENTS_SPECIFICATION.md
- **OpenSpec Governance**: openspec/specs/project-documentation.md

---

**Specification Status**: Active  
**Version**: 1.0  
**Last Updated**: October 21, 2025  
**Approval Status**: Pending Architecture Review
