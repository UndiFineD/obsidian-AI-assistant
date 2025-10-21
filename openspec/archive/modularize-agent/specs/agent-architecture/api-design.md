# Specification: Modular API Design

## Overview

This specification defines the modular API endpoint organization for the agent after refactoring into a service-oriented architecture. It maintains 100% backward compatibility while organizing endpoints by domain.

---

## API Structure (MUST)

APIs MUST be organized into domain-specific modules:

```
agent/api/
├── __init__.py           # Router registration
├── health.py             # Health and status endpoints
├── config.py             # Configuration endpoints
├── ask.py                # Question/answer endpoints
├── search.py             # Vector search endpoints
├── indexing.py           # Document indexing endpoints
├── voice.py              # Voice/transcription endpoints
└── enterprise.py         # Enterprise features (optional)
```

**Requirements**:
- Each domain MUST be in separate module
- Each module MUST define FastAPI `APIRouter`
- All routers MUST be registered in `__init__.py`
- All endpoints MUST be type-hinted
- All endpoints MUST have docstrings

---

## Health Endpoints

### Module: `agent/api/health.py`

```python
# agent/api/health.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check(
    orchestrator: ServiceOrchestrator = Depends(get_orchestrator)
) -> HealthResponse:
    """Basic health check endpoint.
    
    Returns: Service status summary
    SLA: <100ms
    """
    return HealthResponse(
        status="healthy",
        services=orchestrator.get_health_status()
    )

@router.get("/status", response_model=DetailedStatusResponse)
async def detailed_status(
    orchestrator: ServiceOrchestrator = Depends(get_orchestrator)
) -> DetailedStatusResponse:
    """Detailed service status.
    
    Returns: Full system metrics and service details
    SLA: <100ms
    """
    return DetailedStatusResponse(
        status=orchestrator.get_health_status(),
        metrics=get_system_metrics(),
        uptime_seconds=get_uptime(),
        version=get_version()
    )

@router.get("/api/health/detailed")
async def detailed_health(
    orchestrator: ServiceOrchestrator = Depends(get_orchestrator)
) -> Dict:
    """Enhanced health check with metrics.
    
    Returns: Service health, system metrics, alerts
    SLA: <100ms
    """
    pass

@router.get("/api/health/metrics")
async def health_metrics(
    window_seconds: int = 300
) -> Dict:
    """Aggregated metrics over time window.
    
    Returns: Metrics history for analysis
    SLA: <100ms
    """
    pass
```

**Requirements**:
- ✅ <100ms SLA for all endpoints
- ✅ 100% backward compatible
- ✅ All metrics included
- ✅ Service status reported

### Backward Compatibility (MUST)

Original endpoints MUST continue working:
- ✅ `GET /health` → HealthResponse
- ✅ `GET /status` → DetailedStatusResponse

---

## Configuration Endpoints

### Module: `agent/api/config.py`

```python
# agent/api/config.py
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/config", tags=["config"])

@router.get("", response_model=ConfigResponse)
async def get_config() -> ConfigResponse:
    """Get current runtime configuration.
    
    Returns: Whitelisted config fields only
    SLA: <100ms
    """
    settings = get_settings()
    return ConfigResponse(
        api_port=settings.api_port,
        backend_url=settings.backend_url,
        gpu_enabled=settings.gpu,
        model_backend=settings.model_backend,
        cache_enabled=settings.cache_enabled
    )

@router.post("", response_model=ConfigResponse)
async def update_config(
    updates: ConfigUpdate
) -> ConfigResponse:
    """Update runtime configuration.
    
    Body: Configuration updates
    Returns: Updated configuration
    SLA: <500ms
    """
    # Only allow whitelisted keys
    allowed_keys = {"gpu", "cache_enabled", "chunk_size"}
    for key in updates.dict(exclude_none=True):
        if key not in allowed_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update {key}"
            )
    
    settings = update_settings(updates)
    return ConfigResponse(**settings.dict())

@router.post("/reload")
async def reload_config() -> Dict:
    """Reload configuration from file.
    
    Returns: Reload status
    SLA: <1s
    """
    reload_settings()
    return {"status": "reloaded"}
```

**Requirements**:
- ✅ Whitelist-based update security
- ✅ Configuration validation
- ✅ Runtime update support
- ✅ File reload capability

---

## Ask Endpoints

### Module: `agent/api/ask.py`

```python
# agent/api/ask.py
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["ask"])

class AskRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    context: Optional[str] = None
    model: Optional[str] = None
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    cache: bool = True

class AskResponse(BaseModel):
    answer: str
    source_documents: List[Document] = []
    model_used: str
    cached: bool
    processing_time_ms: float

@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest
) -> AskResponse:
    """Ask AI assistant a question.
    
    Body: Question with optional context
    Returns: AI-generated answer
    SLA: <2s (cached) or <5s (uncached)
    Backward Compatibility: MUST maintain exact response format
    """
    start_time = time.time()
    
    # Try cache first
    cache_key = f"ask:{hash(request.prompt)}"
    if request.cache:
        cached = await get_cache().get(cache_key)
        if cached:
            return AskResponse(**cached, cached=True)
    
    # Generate answer
    answer = await get_model_service().generate(
        prompt=request.prompt,
        context=request.context,
        temperature=request.temperature
    )
    
    response = AskResponse(
        answer=answer,
        model_used=request.model or "default",
        cached=False,
        processing_time_ms=(time.time() - start_time) * 1000
    )
    
    # Cache result
    if request.cache:
        await get_cache().set(cache_key, response.dict())
    
    return response

@router.post("/api/ask", response_model=AskResponse)
async def api_ask_question(request: AskRequest) -> AskResponse:
    """API variant of ask endpoint."""
    return await ask_question(request)
```

**Requirements**:
- ✅ <2s SLA (cached)
- ✅ <5s SLA (uncached)
- ✅ 100% backward compatible
- ✅ Exact response format maintained
- ✅ Source documents included

---

## Search Endpoints

### Module: `agent/api/search.py`

```python
# agent/api/search.py
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["search"])

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=50)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    document: str
    similarity_score: float
    source: str
    metadata: Dict[str, Any] = {}

@router.post("/search", response_model=List[SearchResult])
async def semantic_search(request: SearchRequest) -> List[SearchResult]:
    """Semantic similarity search.
    
    Body: Query and search parameters
    Returns: Matching documents ranked by similarity
    SLA: <2s
    """
    # Embed query
    embeddings = await get_embeddings().embed_text(request.query)
    
    # Search vector DB
    results = await get_vector_db().search(
        query_embedding=embeddings,
        top_k=request.top_k,
        similarity_threshold=request.similarity_threshold
    )
    
    return [SearchResult(**r.dict()) for r in results]
```

**Requirements**:
- ✅ <2s SLA
- ✅ Configurable top-k results
- ✅ Similarity threshold filtering
- ✅ Source document tracking

---

## Indexing Endpoints

### Module: `agent/api/indexing.py`

```python
# agent/api/indexing.py
from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/api", tags=["indexing"])

class ReindexResponse(BaseModel):
    status: str
    documents_indexed: int
    documents_removed: int
    processing_time_seconds: float
    timestamp: datetime

@router.post("/reindex", response_model=ReindexResponse)
@router.post("/scan_vault", response_model=ReindexResponse)
async def reindex_vault() -> ReindexResponse:
    """Reindex entire vault for search.
    
    Returns: Reindexing results and statistics
    SLA: <60s
    Background: Can be run as background task
    """
    start_time = time.time()
    
    result = await get_indexing().reindex_vault()
    
    return ReindexResponse(
        status="complete",
        documents_indexed=result.indexed,
        documents_removed=result.removed,
        processing_time_seconds=time.time() - start_time,
        timestamp=datetime.now()
    )

@router.post("/index_pdf")
async def index_pdf_file(file: UploadFile) -> Dict:
    """Index a PDF file.
    
    Body: PDF file upload
    Returns: Indexing result
    SLA: <10s
    """
    content = await file.read()
    
    result = await get_indexing().index_content(
        content=content,
        file_type="pdf",
        file_name=file.filename
    )
    
    return {"status": "indexed", "documents": len(result)}
```

**Requirements**:
- ✅ <60s SLA for full vault
- ✅ <10s SLA for single file
- ✅ Background task support
- ✅ Progress tracking

---

## Voice Endpoints

### Module: `agent/api/voice.py`

```python
# agent/api/voice.py
from fastapi import APIRouter, File

router = APIRouter(prefix="/api", tags=["voice"])

class TranscribeRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio")
    format: str = Field("wav", description="Audio format")

class TranscribeResponse(BaseModel):
    text: str
    confidence: float
    processing_time_ms: float

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest) -> TranscribeResponse:
    """Transcribe audio to text.
    
    Body: Base64 encoded audio
    Returns: Transcribed text
    SLA: <500ms
    """
    start_time = time.time()
    
    # Decode audio
    audio_bytes = base64.b64decode(request.audio_base64)
    
    # Validate
    if not await get_voice().validate_audio(audio_bytes):
        raise HTTPException(
            status_code=400,
            detail="Invalid audio format"
        )
    
    # Transcribe
    text = await get_voice().transcribe(
        audio_data=audio_bytes,
        format=request.format
    )
    
    return TranscribeResponse(
        text=text,
        confidence=0.95,  # From model
        processing_time_ms=(time.time() - start_time) * 1000
    )
```

**Requirements**:
- ✅ <500ms SLA
- ✅ Audio validation
- ✅ Format flexibility
- ✅ Confidence reporting

---

## Enterprise Endpoints

### Module: `agent/api/enterprise.py` (Optional)

```python
# agent/api/enterprise.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/enterprise", tags=["enterprise"])

@router.get("/status")
async def enterprise_status(
    auth: Auth = Depends(require_enterprise_auth)
) -> Dict:
    """Enterprise feature status.
    
    Returns: Enabled enterprise features
    Requires: Authentication
    """
    pass

@router.post("/auth/sso")
async def sso_login(request: SSORequest) -> Dict:
    """SSO authentication endpoint.
    
    Supports: Azure AD, Google, Okta
    Returns: JWT token
    """
    pass

@router.get("/users")
async def list_users(
    auth: Auth = Depends(require_admin_auth)
) -> List[UserInfo]:
    """List all users (admin only)."""
    pass

@router.get("/compliance/gdpr")
async def gdpr_status(
    auth: Auth = Depends(require_compliance_auth)
) -> Dict:
    """GDPR compliance status."""
    pass
```

**Requirements**:
- ✅ Enterprise authentication required
- ✅ Role-based access control
- ✅ Audit logging of all operations
- ✅ Optional (feature toggle controlled)

---

## Response Format Standards

### Standard Response Envelope (MUST)

All responses SHOULD follow consistent structure:

```python
class StandardResponse(BaseModel):
    status: str  # "success", "error", "partial"
    data: Any
    error: Optional[ErrorDetail] = None
    timestamp: datetime
    version: str  # API version

class ErrorResponse(BaseModel):
    status: str = "error"
    error: ErrorDetail
    timestamp: datetime
```

**Requirements**:
- ✅ Status field always present
- ✅ Timestamp tracking
- ✅ Version for tracking
- ✅ Consistent error format

---

## Backward Compatibility (MUST)

### Guaranteed Working Endpoints

These endpoints MUST continue working identically:

```
POST /ask
POST /api/ask
GET /health
GET /status
POST /reindex
POST /api/scan_vault
POST /api/search
POST /api/index_pdf
POST /transcribe
```

**Compatibility Verification**:
```python
# tests/agent/api/test_backward_compatibility.py
async def test_original_ask_endpoint_works():
    """Original /ask endpoint must work."""
    response = client.post("/ask", json={"prompt": "test"})
    assert response.status_code == 200
    assert "answer" in response.json()

async def test_original_health_endpoint_works():
    """Original /health endpoint must work."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

# Test all original endpoints...
```

---

## Error Handling Standards

### HTTP Status Codes (MUST)

```python
# Successful
200 - OK
201 - Created

# Client Errors
400 - Bad Request (invalid input)
401 - Unauthorized (authentication required)
403 - Forbidden (authorization required)
404 - Not Found
422 - Validation Error (Pydantic validation)

# Server Errors
500 - Internal Server Error
503 - Service Unavailable
```

**Requirements**:
- ✅ Appropriate status codes
- ✅ Descriptive error messages
- ✅ Error logging
- ✅ User-friendly descriptions

---

## Performance Requirements (MUST)

### SLA Tiers

| Endpoint Group | Target | Examples |
|----------------|--------|----------|
| Health | <100ms | /health, /status, /api/config |
| Ask (cached) | <500ms | /ask with recent query |
| Ask (uncached) | <2s | /ask with new query |
| Search | <2s | /api/search |
| Voice | <500ms | /transcribe |
| Indexing | <60s | /reindex (full vault) |

**Verification**:
```python
# tests/agent/api/test_performance.py
async def test_health_sla():
    """Health endpoint must respond <100ms."""
    start = time.time()
    response = client.get("/health")
    elapsed = (time.time() - start) * 1000
    assert elapsed < 100, f"SLA violated: {elapsed}ms"
```

---

## Success Criteria

- ✅ All endpoints implemented
- ✅ 100% backward compatible
- ✅ All SLA targets met
- ✅ All tests passing
- ✅ Error handling consistent
- ✅ Documentation complete
- ✅ Performance validated

---

**Specification Status**: Active  
**Version**: 1.0  
**Last Updated**: October 21, 2025
