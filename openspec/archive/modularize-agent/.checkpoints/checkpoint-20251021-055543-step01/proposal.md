# Proposal: Modularize AI Agent Architecture

## Why

## Impact

## Executive Summary

This proposal establishes a modular architecture for the Obsidian AI Agent, transforming the monolithic `agent/` directory into a well-organized, service-oriented collection of independent modules. This improves maintainability, testability, scalability, and enables easier feature development.

## Current State Analysis

**Problem**: The current `agent/` directory contains all backend functionality in a single directory:
- `agent.py` - Main FastAPI application (700+ lines)
- `modelmanager.py` - Model lifecycle management
- `embeddings.py` - Vector operations
- `indexing.py` - Document processing
- `caching.py` - Multi-level caching
- `security.py` - Authentication and encryption
- Multiple other utility modules

**Issues**:
- ❌ Monolithic entry point makes testing difficult
- ❌ Interdependencies make module isolation hard
- ❌ Difficult to enable/disable features
- ❌ Hard to understand module responsibilities
- ❌ Configuration scattered across modules
- ❌ No clear service lifecycle management

## Proposed Architecture

### New Directory Structure

```
agent/
├── __init__.py                    # Package initialization
├── app.py                         # FastAPI application factory
├── config.py                      # Centralized configuration
├── models/                        # AI Model Services
│   ├── __init__.py
│   ├── base.py                   # Base model interface
│   ├── gpt4all_provider.py        # GPT4All implementation
│   ├── llama_provider.py          # LLaMA-cpp implementation
│   └── router.py                  # Model routing logic
├── embeddings/                    # Vector/Embedding Services
│   ├── __init__.py
│   ├── base.py                   # Base embedding interface
│   ├── sentence_transformers.py  # Sentence transformer impl
│   └── manager.py                # Embedding lifecycle
├── vector_db/                     # Vector Database Services
│   ├── __init__.py
│   ├── base.py                   # Base vector DB interface
│   ├── chromadb_provider.py       # ChromaDB implementation
│   └── manager.py                # Vector DB lifecycle
├── indexing/                      # Document Indexing Services
│   ├── __init__.py
│   ├── base.py                   # Base indexer interface
│   ├── markdown_indexer.py        # Markdown processing
│   ├── pdf_indexer.py             # PDF processing
│   ├── web_indexer.py             # Web content indexing
│   └── manager.py                # Indexing coordination
├── cache/                         # Multi-level Caching
│   ├── __init__.py
│   ├── base.py                   # Cache interface
│   ├── memory_cache.py            # L1: In-memory cache
│   ├── disk_cache.py              # L2: Disk-based cache
│   ├── persistent_cache.py        # L3: Persistent cache
│   └── manager.py                # Cache lifecycle
├── voice/                         # Voice Processing Services
│   ├── __init__.py
│   ├── base.py                   # Base voice interface
│   ├── vosk_provider.py           # Vosk STT implementation
│   ├── whisper_provider.py        # Whisper STT implementation
│   └── manager.py                # Voice service lifecycle
├── security/                      # Security & Authentication
│   ├── __init__.py
│   ├── encryption.py              # Encryption utilities
│   ├── auth.py                    # Authentication logic
│   ├── rate_limiting.py           # Rate limiting
│   ├── input_validation.py        # Input validation
│   └── audit.py                   # Audit logging
├── api/                           # API Endpoints (organized by domain)
│   ├── __init__.py
│   ├── health.py                 # Health check endpoints
│   ├── config.py                 # Configuration endpoints
│   ├── ask.py                    # AI question endpoints
│   ├── search.py                 # Search endpoints
│   ├── indexing.py               # Indexing endpoints
│   ├── voice.py                  # Voice endpoints
│   └── enterprise.py             # Enterprise endpoints
├── enterprise/                    # Enterprise Features (optional)
│   ├── __init__.py
│   ├── auth.py                   # SSO/RBAC
│   ├── tenant.py                 # Multi-tenancy
│   ├── compliance.py             # GDPR/SOC2
│   └── admin.py                  # Admin dashboard
├── services/                      # Orchestration/Coordination
│   ├── __init__.py
│   ├── base.py                   # Base service interface
│   ├── orchestrator.py           # Service coordination
│   └── lifecycle.py              # Service lifecycle management
├── middleware/                    # HTTP Middleware
│   ├── __init__.py
│   ├── tracing.py                # Request tracing
│   ├── error_handling.py          # Error handling
│   └── monitoring.py             # Monitoring/metrics
├── utils/                         # Utilities
│   ├── __init__.py
│   ├── logging.py                # Logging setup
│   ├── errors.py                 # Custom exceptions
│   ├── types.py                  # Type definitions
│   └── helpers.py                # Helper functions
├── models/                        # (Storage: models/)
│   └── *.gguf                    # AI model files
├── cache/                         # (Storage: cache/)
│   └── *                         # Cache files
├── logs/                          # (Storage: logs/)
│   └── *.log                     # Application logs
└── vector_db/                     # (Storage: vector_db/)
    └── chroma*/                  # ChromaDB storage
```

### Key Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Dependency Injection**: Services receive dependencies, not create them
3. **Interface-Based Design**: Abstract base classes define contracts
4. **Lazy Loading**: Features loaded only when needed
5. **Configuration-Driven**: Feature toggles enable/disable modules
6. **Testability**: Each module independently testable
7. **Plugin Architecture**: Easy to add providers/implementations

### Core Components

#### 1. Application Factory (`app.py`)
```python
def create_app(config: Config) -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI()
    
    # Initialize services
    services = ServiceOrchestrator(config)
    app.state.services = services
    
    # Register endpoints
    app.include_router(health_router)
    app.include_router(config_router)
    app.include_router(ask_router, prefix="/api")
    # ... more routers
    
    return app
```

#### 2. Service Orchestrator (`services/orchestrator.py`)
```python
class ServiceOrchestrator:
    """Coordinates service initialization and lifecycle."""
    
    def __init__(self, config: Config):
        self.config = config
        self._services = {}
        self._initialize_services()
    
    def get_service(self, service_name: str) -> Service:
        """Get or initialize a service."""
        # Lazy loading with caching
        pass
    
    def shutdown(self):
        """Graceful shutdown of all services."""
        pass
```

#### 3. Provider Pattern (`models/base.py`)
```python
class BaseModelProvider(ABC):
    """Abstract base for model providers."""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    async def validate(self) -> bool:
        pass

class GPT4AllProvider(BaseModelProvider):
    """GPT4All implementation."""
    pass

class LlamaProvider(BaseModelProvider):
    """LLaMA-cpp implementation."""
    pass
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Create modular directory structure
- Implement Service Orchestrator
- Create base interfaces for all modules
- Migrate core services (models, embeddings, vector_db)
- Tests: 50+ new tests

### Phase 2: Services & APIs (Week 2-3)
- Migrate remaining services (voice, cache, security)
- Organize API endpoints by domain
- Implement dependency injection
- Tests: 40+ new tests

### Phase 3: Features & Polish (Week 3-4)
- Migrate enterprise features
- Add feature toggles/configuration
- Optimize performance
- Tests: 30+ new tests

### Phase 4: Documentation & Deployment (Week 4-5)
- Update all documentation
- Create migration guide
- Package as pip-installable module
- Create example plugins
- Tests: 20+ new tests

## Benefits

### Immediate Benefits
✅ **Maintainability**: Each module has clear responsibility and interface
✅ **Testability**: Independent testing of each module (50+ new tests per phase)
✅ **Clarity**: Codebase structure mirrors architecture
✅ **Onboarding**: New developers understand structure faster
✅ **Flexibility**: Easy to customize/extend features

### Long-Term Benefits
✅ **Scalability**: Support multiple deployment models
✅ **Extensibility**: Plugin system for custom implementations
✅ **Performance**: Lazy loading improves startup time
✅ **Enterprise**: Easier to implement enterprise features
✅ **Community**: Community can contribute provider implementations

## Testing Strategy

### Test Structure
```
tests/
├── agent/                          # Agent module tests
│   ├── test_app.py                # FastAPI app factory tests
│   ├── models/
│   │   ├── test_base.py           # Base interface tests
│   │   ├── test_gpt4all.py        # Provider tests
│   │   └── test_router.py         # Routing logic tests
│   ├── embeddings/                # Embedding service tests
│   ├── vector_db/                 # Vector DB service tests
│   ├── services/
│   │   └── test_orchestrator.py   # Orchestrator tests
│   └── api/                       # Endpoint tests
├── integration/                    # Integration tests
└── performance/                    # Performance tests
```

### Coverage Goals
- Unit Tests: 95%+ coverage per module
- Integration Tests: 100% API coverage
- Performance Tests: All Tier 1-5 operations
- Total: 150+ new tests across 4 phases

## Migration Path

### For Existing Deployments
1. Parallel deployment: New modular agent alongside existing
2. Gradual migration: Route traffic to new modular version
3. Fallback: Roll back to existing if issues
4. Full migration: Complete switch after validation

### Backward Compatibility
✅ API endpoints remain unchanged
✅ Configuration format compatible
✅ Plugin interface remains stable
✅ No breaking changes for users

## Success Criteria

- ✅ All existing tests pass with modular structure
- ✅ 150+ new tests for modular architecture
- ✅ Code coverage maintained at 88%+
- ✅ Performance impact: <5% on response times
- ✅ Documentation 100% complete
- ✅ Zero production issues during migration
- ✅ Plugin system operational

## Timeline

- **Phase 1 (Week 1-2)**: Foundation - 50 tests
- **Phase 2 (Week 2-3)**: Services & APIs - 40 tests  
- **Phase 3 (Week 3-4)**: Features - 30 tests
- **Phase 4 (Week 4-5)**: Documentation - 20 tests
- **Total**: 4-5 weeks, 150+ new tests

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Performance regression | Low | High | Tier 1-5 perf tests, benchmarking |
| Breaking changes | Low | High | Backward compat tests, migration guide |
| Incomplete migration | Medium | Medium | Phased approach, feature toggles |
| Learning curve | Medium | Low | Comprehensive documentation |

## Governance

This proposal follows OpenSpec governance:
- ✅ Capability declaration: Service-oriented modular architecture
- ✅ Change tracking: Via openspec/changes/modularize-agent/
- ✅ Test validation: 150+ new tests required
- ✅ Documentation: Comprehensive architecture guide
- ✅ Review process: Architecture review before Phase 1 implementation

## Next Steps

1. **Approval**: Architecture review and approval
2. **Design**: Detailed design for Phase 1 foundation
3. **Implementation**: Begin Phase 1 foundation work
4. **Testing**: Comprehensive test suite development
5. **Documentation**: Create architecture guides
6. **Review**: Phase reviews after each phase

---

**Proposal Status**: Ready for Review  
**Created**: October 21, 2025  
**Last Updated**: October 21, 2025  
**Stakeholders**: Architecture team, Backend team, QA team
