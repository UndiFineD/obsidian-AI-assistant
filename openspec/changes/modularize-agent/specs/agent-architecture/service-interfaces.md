# Specification: Service Interfaces & Dependency Injection

## Overview

This specification defines the service interface contracts that all agent modules MUST implement. It establishes the foundation for modular, pluggable services with proper lifecycle management.

---

## Base Service Interface

### ServiceProvider (MUST)

All services MUST inherit from `ServiceProvider`:

```python
# agent/services/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from enum import Enum

class ServiceStatus(Enum):
    """Service operational status."""
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    SHUTTING_DOWN = "shutting_down"

class ServiceProvider(ABC):
    """Base class for all service providers."""
    
    name: str  # Service identifier
    version: str  # Service version
    
    @property
    @abstractmethod
    def status(self) -> ServiceStatus:
        """Current service status."""
        pass
    
    @property
    @abstractmethod
    def is_ready(self) -> bool:
        """Whether service is ready for requests."""
        pass
    
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
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Return service metrics."""
        pass
```

**Requirements**:
- MUST implement all abstract methods
- MUST maintain `status` property
- MUST be async-ready
- MUST provide metrics for monitoring

---

## Core Module Interfaces

### ModelService (MUST)

```python
# agent/models/base.py
from agent.services.base import ServiceProvider

class ModelService(ServiceProvider):
    """Base class for AI model services."""
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate text response."""
        pass
    
    @abstractmethod
    async def stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream text response."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return model capabilities."""
        pass
```

**Implementations Required**:
- ✅ GPT4AllModelService
- ✅ LlamaModelService
- ✅ ModelRouter (selects best model)

### EmbeddingService (MUST)

```python
# agent/embeddings/base.py
class EmbeddingService(ServiceProvider):
    """Base class for embedding services."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Return embedding dimension."""
        pass
```

**Implementations Required**:
- ✅ SentenceTransformersEmbedding
- ✅ EmbeddingManager (caching + pooling)

### VectorDBService (MUST)

```python
# agent/vector_db/base.py
class VectorDBService(ServiceProvider):
    """Base class for vector database services."""
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents to vector DB."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[SearchResult]:
        """Search vector database."""
        pass
    
    @abstractmethod
    async def delete_documents(self, doc_ids: List[str]) -> int:
        """Delete documents from DB."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all documents."""
        pass
```

**Implementations Required**:
- ✅ ChromaDBVectorService
- ✅ VectorDBManager (connections, caching)

### IndexingService (MUST)

```python
# agent/indexing/base.py
class IndexingService(ServiceProvider):
    """Base class for document indexing."""
    
    @abstractmethod
    async def index_file(
        self,
        file_path: str,
        content: Optional[str] = None
    ) -> List[Document]:
        """Index a single file."""
        pass
    
    @abstractmethod
    async def index_batch(
        self,
        file_paths: List[str]
    ) -> int:
        """Index multiple files."""
        pass
    
    @abstractmethod
    async def reindex_vault(self) -> IndexingResult:
        """Reindex entire vault."""
        pass
```

**Implementations Required**:
- ✅ MarkdownIndexer
- ✅ PDFIndexer
- ✅ WebIndexer
- ✅ IndexingManager (orchestration)

### CacheService (MUST)

```python
# agent/cache/base.py
class CacheService(ServiceProvider):
    """Base class for caching."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass
```

**Implementations Required**:
- ✅ L1MemoryCache (in-process)
- ✅ L2DiskCache (persistent)
- ✅ L3PersistentCache (database)
- ✅ CacheManager (multi-level coordination)

### VoiceService (MUST)

```python
# agent/voice/base.py
class VoiceService(ServiceProvider):
    """Base class for voice processing."""
    
    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        format: str = "wav"
    ) -> str:
        """Transcribe audio to text."""
        pass
    
    @abstractmethod
    async def validate_audio(self, audio_data: bytes) -> bool:
        """Validate audio format."""
        pass
```

**Implementations Required**:
- ✅ VoskVoiceService
- ✅ WhisperVoiceService
- ✅ VoiceManager (selection + pooling)

---

## Service Orchestrator (MUST)

### ServiceOrchestrator Class

```python
# agent/services/orchestrator.py
class ServiceOrchestrator:
    """Central orchestrator for all services."""
    
    def __init__(self, config: Config):
        """Initialize orchestrator."""
        self.config = config
        self._services: Dict[str, ServiceProvider] = {}
        self._initialized = False
    
    async def initialize_all(self) -> None:
        """Initialize all enabled services."""
        # Must respect feature toggles
        if self.config.features.models.enabled:
            await self._initialize_model_service()
        
        if self.config.features.embeddings.enabled:
            await self._initialize_embedding_service()
        
        # ... other services
        
        self._initialized = True
    
    def get_service(
        self,
        service_name: str,
        service_class: Type[T]
    ) -> T:
        """Get service instance with validation."""
        if service_name not in self._services:
            raise ServiceNotFoundError(f"Service {service_name} not initialized")
        
        service = self._services[service_name]
        if not isinstance(service, service_class):
            raise ServiceTypeError(...)
        
        if not service.is_ready:
            raise ServiceNotReadyError(...)
        
        return service
    
    async def shutdown_all(self) -> None:
        """Graceful shutdown of all services."""
        for service in reversed(list(self._services.values())):
            await service.shutdown()
        
        self._initialized = False
    
    def get_health_status(self) -> Dict[str, ServiceStatus]:
        """Get status of all services."""
        return {
            name: service.status
            for name, service in self._services.items()
        }
```

**Requirements**:
- MUST respect feature toggles
- MUST initialize in dependency order
- MUST shutdown in reverse order
- MUST validate service types
- MUST provide health status

---

## Dependency Injection Pattern

### Injection Container (MUST)

```python
# agent/services/container.py
class DIContainer:
    """Dependency injection container."""
    
    def __init__(self, config: Config):
        self.config = config
        self._singletons: Dict[str, Any] = {}
    
    def register_singleton(
        self,
        name: str,
        factory: Callable[..., Any]
    ) -> None:
        """Register singleton service factory."""
        self._singletons[name] = None  # Lazy initialize
        self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """Get service with lazy initialization."""
        if self._singletons[name] is None:
            factory = self._factories[name]
            self._singletons[name] = factory(self)
        
        return self._singletons[name]
```

**Requirements**:
- MUST use lazy initialization
- MUST support singletons
- MUST manage lifecycle
- MUST allow factory functions

---

## Lifecycle Management

### Lifecycle Hooks (MUST)

All services MUST support:

```python
# Initialization
async with ServiceManager(config) as manager:
    # All services initialized here
    model_service = manager.get("models")
    # Use services
    pass  # Automatic cleanup on exit
```

**Sequence**:

1. **Configuration** → Load and validate config
2. **Instantiation** → Create service instances
3. **Initialization** → Call `initialize()` on each
4. **Validation** → Call `validate()` on each
5. **Ready** → Services available for use
6. **Shutdown** → Call `shutdown()` in reverse order

**Requirements**:
- MUST initialize in dependency order
- MUST validate before ready
- MUST shutdown gracefully
- MUST handle exceptions during lifecycle

---

## Service Registry (MUST)

```python
# agent/services/registry.py
class ServiceRegistry:
    """Central registry of all services."""
    
    _services: Dict[str, Type[ServiceProvider]] = {}
    
    @classmethod
    def register(
        cls,
        name: str,
        service_class: Type[ServiceProvider]
    ) -> None:
        """Register service implementation."""
        cls._services[name] = service_class
    
    @classmethod
    def get_service_class(cls, name: str) -> Type[ServiceProvider]:
        """Get service implementation by name."""
        if name not in cls._services:
            raise ServiceNotRegisteredError(f"Service {name} not registered")
        return cls._services[name]
```

**Built-in Registrations**:
```python
# Must register all core services
ServiceRegistry.register("models", ModelRouter)
ServiceRegistry.register("embeddings", EmbeddingManager)
ServiceRegistry.register("vector_db", VectorDBManager)
ServiceRegistry.register("indexing", IndexingManager)
ServiceRegistry.register("cache", CacheManager)
ServiceRegistry.register("voice", VoiceManager)
```

---

## Error Handling (MUST)

### Service Exceptions

```python
# agent/services/exceptions.py
class ServiceError(Exception):
    """Base service exception."""
    pass

class ServiceNotFoundError(ServiceError):
    """Service not registered."""
    pass

class ServiceNotReadyError(ServiceError):
    """Service not ready for requests."""
    pass

class ServiceTypeError(ServiceError):
    """Service type mismatch."""
    pass

class ServiceInitializationError(ServiceError):
    """Service initialization failed."""
    pass
```

**Requirements**:
- MUST raise appropriate exceptions
- MUST include context information
- MUST allow graceful error handling

---

## Testing Requirements (MUST)

### Interface Tests

Each service interface MUST have tests:

```python
# tests/agent/services/test_base.py
class TestServiceProvider:
    """Test ServiceProvider interface."""
    
    async def test_service_initialization(self):
        """Service must initialize."""
        service = MockService(config)
        await service.initialize()
        assert service.is_ready
    
    async def test_service_validation(self):
        """Service must validate."""
        service = MockService(config)
        assert await service.validate()
    
    async def test_service_shutdown(self):
        """Service must shutdown."""
        service = MockService(config)
        await service.initialize()
        await service.shutdown()
        assert not service.is_ready
```

**Coverage Requirements**:
- ✅ Initialization tests (all services)
- ✅ Validation tests (all services)
- ✅ Shutdown tests (all services)
- ✅ Exception handling tests
- ✅ Lifecycle tests

---

## Configuration Schema

```yaml
# agent/config.yaml
services:
  models:
    enabled: true
    provider: "gpt4all"  # or "llama"
    
  embeddings:
    enabled: true
    provider: "sentence_transformers"
    model: "all-MiniLM-L6-v2"
  
  vector_db:
    enabled: true
    provider: "chromadb"
    persist: true
  
  voice:
    enabled: false
    provider: "vosk"  # or "whisper"
  
  indexing:
    enabled: true
    providers: ["markdown", "pdf", "web"]

di:
  singleton_ttl: 3600  # Cache service instances
  lazy_init: true      # Initialize on first use
```

---

## Success Criteria

- ✅ All services implement ServiceProvider
- ✅ ServiceOrchestrator properly orchestrates
- ✅ Dependency injection working correctly
- ✅ Lifecycle management tested
- ✅ Feature toggles controlling services
- ✅ 100% backward compatibility maintained
- ✅ Zero production service issues

---

**Specification Status**: Active  
**Version**: 1.0  
**Last Updated**: October 21, 2025
