# 📋 Obsidian AI Assistant - Technical Specification

## 📌 Document Overview

- **Version**: 1.0.0
- **Last Updated**: October 6, 2025
- **Author**: Keimpe de Jong
- **Project**: Obsidian AI Assistant
- **Repository**: obsidian-AI-assistant

---

## 🎯 Project Mission

Offline-first AI assistant for Obsidian with comprehensive backend services, semantic search, and voice input support.

---


[// --- BEGIN MERGED SPECIFICATIONS ---]

# 📋 COMPREHENSIVE TECHNICAL SPECIFICATION

## **🏗️ System Architecture**

### Core Components

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Obsidian      │    │   FastAPI       │    │   Local LLM     │
│   Plugin        │◄──►│   Backend       │◄──►│   Models        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   ChromaDB      │
                    │   Vector Store  │
                    │                 │
                    └─────────────────┘
```

# 📋 SPECIFICATION SUMMARY

[Content from SPECIFICATION_SUMMARY.md]

# 📋 FEATURE SPECIFICATION: ADD UNIT TESTS

[Content from spec.md]

# 📋 FEATURE SPECIFICATION: ADD UNIT TESTS (FIXED)

[Content from spec-fixed.md]

[// --- END MERGED SPECIFICATIONS ---]

## 🔧 Backend API Documentation

### FastAPI Architecture Overview

The Obsidian AI Assistant backend is built on FastAPI, providing a modern, high-performance Python web framework with automatic API documentation, request validation, and type safety. The API follows RESTful principles with comprehensive error handling and standardized response formats.

#### Core Architecture Features

...

### Core Components

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Obsidian      │    │   FastAPI       │    │   Local LLM     │
│   Plugin        │◄──►│   Backend       │◄──►│   Models        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   ChromaDB      │
                    │   Vector Store  │
                    │                 │
                    └─────────────────┘
```

### Module Structure

```text
backend/
├── backend.py          # FastAPI application & endpoints
├── settings.py         # Centralized configuration
├── embeddings.py       # Vector operations & ChromaDB
├── indexing.py         # Document processing 
├── llm_router.py       # Model routing logic
├── modelmanager.py     # Model management
├── caching.py          # TTL-based caching system
├── security.py         # Encryption & auth
├── voice.py            # Speech recognition
└── utils.py            # Shared utilities

plugin/
├── main.ts             # Core plugin logic
├── manifest.json       # Plugin metadata
├── styles.css          # UI styling
├── config.template.json # Configuration template
├── analyticsPane.ts    # Analytics dashboard
├── taskQueue.ts        # Task management
├── taskQueueView.ts    # Queue UI
├── voice.ts            # Voice processing
└── voiceInput.ts       # Voice input handling
```

---

## 🔧 Backend API Documentation

### FastAPI Architecture Overview

The Obsidian AI Assistant backend is built on FastAPI, providing a modern, high-performance Python web framework with automatic API documentation, request validation, and type safety. The API follows RESTful principles with comprehensive error handling and standardized response formats.

#### Core Architecture Features

- **Automatic Documentation**: OpenAPI/Swagger UI at `/docs` and ReDoc at `/redoc`
- **Type Safety**: Pydantic models for request/response validation
- **Async Operations**: Full asynchronous support for concurrent requests
- **CORS Enabled**: Cross-origin requests supported for web integration
- **Service Injection**: Dependency injection for database and model management
- **Caching Layer**: Integrated response caching for performance optimization

### Server Configuration

#### Base Configuration

- **Protocol**: HTTP/HTTPS
- **Default Host**: `127.0.0.1` (localhost)
- **Default Port**: `8000` (configurable via `API_PORT` environment variable)
- **Framework**: FastAPI 0.104+
- **Base URL**: `http://127.0.0.1:8000`
- **Documentation URL**: `http://127.0.0.1:8000/docs`

#### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Accept requests from any origin
    allow_credentials=True,        # Support cookies and auth headers
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all request headers
)
```

#### Server Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PORT` | 8000 | Server port |
| `BACKEND_URL` | `http://127.0.0.1:8000` | Full backend URL |
| `ALLOW_NETWORK` | false | Enable network-based features |
| `GPU` | true | Enable GPU acceleration |
| `MODEL_BACKEND` | `llama_cpp` | AI model backend type |
| `VAULT_PATH` | `vault` | Default vault directory |
| `CACHE_DIR` | `cache` | Cache storage directory |

---

## 📡 API Endpoint Reference

### Health & Monitoring Endpoints

#### GET /health

**Purpose**: Comprehensive health check with complete system information

**Authentication**: None required

**Response Schema**:

```typescript
interface HealthResponse {
    status: "ok" | "degraded" | "error";
    timestamp: number;                    // Unix timestamp
    backend_url: string;                  // Configured backend URL
    api_port: number;                     // Active API port
    vault_path: string;                   // Vault directory path
    models_dir: string;                   // Models directory path
    cache_dir: string;                    // Cache directory path
    model_backend: string;                // Active model backend
    embed_model: string;                  // Embedding model name
    vector_db: string;                    // Vector database type
    allow_network: boolean;               // Network features enabled
    gpu: boolean;                         // GPU acceleration status
    services?: {                          // Optional service status
        model_manager: "ready" | "loading" | "error";
        embeddings: "ready" | "error";
        cache: "ready" | "error";
        vault_indexer: "ready" | "error";
    };
}
```

**Example Response**:

```json
{
    "status": "ok",
    "timestamp": 1728123456,
    "backend_url": "http://127.0.0.1:8000",
    "api_port": 8000,
    "vault_path": "vault",
    "models_dir": "models",
    "cache_dir": "cache",
    "model_backend": "llama_cpp",
    "embed_model": "sentence-transformers/all-MiniLM-L6-v2",
    "vector_db": "chroma",
    "allow_network": false,
    "gpu": true,
    "services": {
        "model_manager": "ready",
        "embeddings": "ready",
        "cache": "ready",
        "vault_indexer": "ready"
    }
}
```

**Status Codes**:

- `200 OK`: System healthy and operational
- `503 Service Unavailable`: System degraded or services unavailable

#### GET /status

**Purpose**: Lightweight liveness probe for container orchestration

**Authentication**: None required

**Response Schema**:

```typescript
interface StatusResponse {
    status: "ok";
}
```

**Example Response**:

```json
{
    "status": "ok"
}
```

**Status Codes**:

- `200 OK`: Service is alive and responding
- `503 Service Unavailable`: Service is not ready

#### GET /api/health

**Purpose**: API-versioned health endpoint (alias for `/health`)

**Note**: Provides identical functionality to `/health` with API prefix for consistency

---

### Configuration Management

#### GET /api/config

**Purpose**: Retrieve current runtime configuration (filtered for security)

**Authentication**: None required

**Query Parameters**: None

**Response Schema**:

```typescript
interface ConfigResponse {
    // Core Settings
    allow_network: boolean;
    model_backend: string;
    model_path: string;
    embed_model: string;
    vector_db: string;
    api_port: number;
    gpu: boolean;
    
    // Directory Paths
    cache_dir: string;
    vault_path: string;
    models_dir: string;
    
    // Processing Parameters
    top_k: number;
    chunk_size: number;
    chunk_overlap: number;
    similarity_threshold: number;
    continuous_mode: boolean;
    
    // Voice Settings (if available)
    vosk_model_path?: string;
}
```

**Example Response**:

```json
{
    "allow_network": true,
    "model_backend": "llama_cpp",
    "model_path": "models/llama-7b.gguf",
    "embed_model": "sentence-transformers/all-MiniLM-L6-v2",
    "vector_db": "chroma",
    "api_port": 8000,
    "gpu": false,
    "cache_dir": "cache",
    "vault_path": "test_vault",
    "models_dir": "models",
    "top_k": 10,
    "chunk_size": 2000,
    "chunk_overlap": 200,
    "similarity_threshold": 0.75,
    "continuous_mode": false,
    "vosk_model_path": "models/vosk-model-small-en-us-0.15"
}
```

**Status Codes**:

- `200 OK`: Configuration retrieved successfully

**Security Note**: Only whitelisted configuration fields are returned. Sensitive settings like API keys are excluded.

#### POST /api/config

**Purpose**: Update runtime configuration settings

**Authentication**: None required (consider implementing authentication for production)

**Request Schema**:

```typescript
interface ConfigUpdateRequest {
    // Optional fields - only provided fields will be updated
    allow_network?: boolean;
    model_backend?: string;
    model_path?: string;
    embed_model?: string;
    vector_db?: string;
    gpu?: boolean;
    cache_dir?: string;
    vault_path?: string;
    models_dir?: string;
    top_k?: number;
    chunk_size?: number;
    chunk_overlap?: number;
    similarity_threshold?: number;
    continuous_mode?: boolean;
    vosk_model_path?: string;
}
```

**Request Example**:

```json
{
    "vault_path": "new_vault",
    "chunk_size": 1000,
    "gpu": false,
    "similarity_threshold": 0.8
}
```

**Response Schema**:

```typescript
interface ConfigUpdateResponse {
    ok: boolean;
    settings: ConfigResponse;    // Updated configuration
    message?: string;           // Optional status message
}
```

**Example Response**:

```json
{
    "ok": true,
    "settings": {
        "allow_network": true,
        "model_backend": "llama_cpp",
        "vault_path": "new_vault",
        "chunk_size": 1000,
        "gpu": false,
        "similarity_threshold": 0.8
    }
}
```

**Status Codes**:

- `200 OK`: Configuration updated successfully
- `400 Bad Request`: Invalid configuration parameters
- `500 Internal Server Error`: Failed to persist configuration

**Validation Rules**:

- `top_k`: Integer between 1 and 100
- `chunk_size`: Integer between 100 and 10000
- `chunk_overlap`: Integer between 0 and chunk_size/2
- `similarity_threshold`: Float between 0.0 and 1.0
- Path fields: Must be valid directory/file paths

#### POST /api/config/reload

**Purpose**: Reload configuration from `backend/config.yaml` file

**Authentication**: None required

**Request Body**: Empty

**Response Schema**:

```typescript
interface ConfigReloadResponse {
    ok: boolean;
    settings: ConfigResponse;    // Reloaded configuration
    message?: string;           // Status message
}
```

**Example Response**:

```json
{
    "ok": true,
    "settings": {
        "allow_network": false,
        "model_backend": "llama_cpp",
        "vault_path": "vault",
        "chunk_size": 800
    },
    "message": "Configuration reloaded from config.yaml"
}
```

**Status Codes**:

- `200 OK`: Configuration reloaded successfully
- `500 Internal Server Error`: Failed to reload configuration file

---

### AI Operations

#### POST /ask & POST /api/ask

**Purpose**: Primary AI question processing and response generation

**Authentication**: None required

**Request Schema**:

```typescript
interface AskRequest {
    question: string;                     // Required: User question/prompt
    prefer_fast?: boolean;                // Optional: Prefer speed over quality (default: true)
    max_tokens?: number;                  // Optional: Maximum response tokens (default: 256)
    context_paths?: string[];             // Optional: Specific vault files for context
    prompt?: string;                      // Optional: Custom system prompt
    model_name?: string;                  // Optional: Specific model to use (default: configured model)
}
```

**Request Examples**:

Basic question:

```json
{
    "question": "What is the capital of France?"
}
```

Advanced question with context:

```json
{
    "question": "Summarize the key points from my project notes",
    "prefer_fast": false,
    "max_tokens": 512,
    "context_paths": ["projects/current-project.md", "meetings/latest-standup.md"],
    "prompt": "You are an expert project manager. Analyze the provided notes and create a concise summary."
}
```

**Response Schema**:

```typescript
interface AskResponse {
    answer: string;                       // AI-generated response
    cached: boolean;                      // Whether response came from cache
    model_used: string;                   // Model that generated the response
    processing_time?: number;             // Generation time in seconds
    context_used?: string[];              // Files used for context
    tokens_used?: number;                 // Number of tokens consumed
    metadata?: {
        confidence?: number;              // Response confidence score (0-1)
        sources?: string[];               // Source files referenced
        model_backend?: string;           // Backend engine used
    };
}
```

**Example Responses**:

Successful cached response:

```json
{
    "answer": "Paris is the capital of France.",
    "cached": true,
    "model_used": "llama-7b",
    "processing_time": 0.012,
    "tokens_used": 8,
    "metadata": {
        "confidence": 0.98,
        "model_backend": "llama_cpp"
    }
}
```

Generated response with context:

```json
{
    "answer": "Based on your project notes, here are the key points:\n\n1. **Sprint Progress**: Currently 75% complete with the authentication module\n2. **Blockers**: Waiting for API keys from external service provider\n3. **Next Steps**: Focus on UI components while resolving the API integration\n4. **Timeline**: On track for delivery by end of next week",
    "cached": false,
    "model_used": "llama-13b",
    "processing_time": 2.456,
    "context_used": ["projects/current-project.md", "meetings/latest-standup.md"],
    "tokens_used": 142,
    "metadata": {
        "confidence": 0.92,
        "sources": ["current-project.md", "latest-standup.md"],
        "model_backend": "llama_cpp"
    }
}
```

**Status Codes**:

- `200 OK`: Question processed successfully
- `422 Unprocessable Entity`: Invalid request format or missing required fields
- `500 Internal Server Error`: AI model error, service unavailable, or processing failure
- `503 Service Unavailable`: Models not loaded or backend services unavailable

**Error Response Schema**:

```typescript
interface ErrorResponse {
    error: string;                        // Error type/category
    message: string;                      // Human-readable error message
    details?: {
        field?: string;                   // Field that caused validation error
        type?: string;                    // Error type (e.g., "missing", "invalid")
        input_value?: any;                // Value that caused the error
    };
}
```

**Error Examples**:

Validation error:

```json
{
    "error": "ValidationError",
    "message": "Field 'question' is required",
    "details": {
        "field": "question",
        "type": "missing",
        "input_value": null
    }
}
```

Model error:

```json
{
    "error": "ModelError",
    "message": "No model available for inference",
    "details": {
        "type": "service_unavailable",
        "model_backend": "llama_cpp"
    }
}
```

**Caching Behavior**:

- Questions are cached based on exact text match
- Cache TTL is configurable (default: 1 hour)
- Context paths and custom prompts affect cache key
- Cached responses return immediately with `cached: true`

**Performance Considerations**:

- Use `prefer_fast: true` for real-time interactions
- Set `max_tokens` appropriately to control response length and processing time
- Limit `context_paths` to relevant files to reduce processing overhead
- Consider caching for frequently asked questions

---

### Document Management & Indexing

#### POST /reindex & POST /api/reindex

**Purpose**: Rebuild the vector database index for vault documents

**Authentication**: None required

**Request Schema**:

```typescript
interface ReindexRequest {
    vault_path?: string;          // Optional: Vault directory path (default: configured vault_path)
}
```

**Request Examples**:

Default vault reindex:

```json
{
    "vault_path": "./vault"
}
```

**Response Schema**:

```typescript
interface ReindexResponse {
    status: "success" | "partial" | "failed";
    files_processed: number;              // Number of files successfully processed
    chunks_indexed: number;               // Total chunks created and indexed
    processing_time: number;              // Total processing time in seconds
    files_failed?: string[];              // Files that failed to process
    errors?: string[];                    // Detailed error messages
    statistics?: {
        markdown_files: number;
        pdf_files: number;
        text_files: number;
        other_files: number;
        avg_chunk_size: number;
        total_size_mb: number;
    };
}
```

**Example Response**:

```json
{
    "status": "success",
    "files_processed": 25,
    "chunks_indexed": 150,
    "processing_time": 5.67,
    "statistics": {
        "markdown_files": 20,
        "pdf_files": 3,
        "text_files": 2,
        "other_files": 0,
        "avg_chunk_size": 1200,
        "total_size_mb": 2.4
    }
}
```

**Status Codes**:

- `200 OK`: Reindexing completed successfully or with partial success
- `400 Bad Request`: Invalid vault path or configuration
- `500 Internal Server Error`: Indexing service failure

#### POST /web & POST /api/web

**Purpose**: Index web content and generate AI responses

**Authentication**: None required

**Requirements**: `allow_network` must be enabled in configuration

**Request Schema**:

```typescript
interface WebRequest {
    url: string;                         // Required: Valid HTTP/HTTPS URL
    question?: string;                   // Optional: Question about the web content
}
```

**Request Examples**:

Basic web content indexing:

```json
{
    "url": "https://example.com/article"
}
```

Web content with question:

```json
{
    "url": "https://docs.python.org/3/library/json.html",
    "question": "How do I parse JSON in Python?"
}
```

**Response Schema**:

```typescript
interface WebResponse {
    answer: string;                      // AI-generated response about the content
    url_processed: string;               // URL that was processed
    content_indexed: boolean;            // Whether content was successfully indexed
    processing_time?: number;            // Processing time in seconds
    metadata?: {
        title?: string;                  // Page title
        content_length?: number;         // Content length in characters
        chunks_created?: number;         // Number of chunks indexed
        content_type?: string;           // MIME type of the content
    };
}
```

**Example Responses**:

Successful web indexing:

```json
{
    "answer": "This page discusses Python's json module, which provides methods to parse JSON data using json.loads() for strings and json.load() for files.",
    "url_processed": "https://docs.python.org/3/library/json.html",
    "content_indexed": true,
    "processing_time": 3.21,
    "metadata": {
        "title": "json — JSON encoder and decoder — Python 3.12.0 documentation",
        "content_length": 15420,
        "chunks_created": 12,
        "content_type": "text/html"
    }
}
```

**Status Codes**:

- `200 OK`: Web content processed successfully
- `400 Bad Request`: Invalid URL format or network features disabled
- `403 Forbidden`: Network access not allowed in configuration
- `404 Not Found`: URL not accessible or content not found
- `500 Internal Server Error`: Processing or indexing failure

**Error Handling**:

- Invalid URLs return 400 with error details
- Network timeouts return 500 with timeout information
- Restricted content types are logged but may return partial results

#### POST /api/scan_vault

**Purpose**: Scan vault directory and index new/modified files

**Authentication**: None required

**Query Parameters**:

- `vault_path` (string, optional): Directory path to scan (default: configured vault_path)

**Response Schema**:

```typescript
interface ScanVaultResponse {
    indexed_files: string[];             // List of files that were indexed
    total_files: number;                 // Total number of files found
    skipped_files: string[];             // Files that were skipped (unchanged)
    processing_time: number;             // Scan and indexing time in seconds
    statistics?: {
        new_files: number;
        modified_files: number;
        unchanged_files: number;
        error_files: number;
    };
}
```

**Example Response**:

```json
{
    "indexed_files": ["notes/project.md", "docs/api.md", "meeting-notes.pdf"],
    "total_files": 15,
    "skipped_files": ["old-notes.md", "archived/2022.md"],
    "processing_time": 2.34,
    "statistics": {
        "new_files": 2,
        "modified_files": 1,
        "unchanged_files": 12,
        "error_files": 0
    }
}
```

**Status Codes**:

- `200 OK`: Vault scan completed successfully
- `400 Bad Request`: Invalid vault path
- `500 Internal Server Error`: Scanning or indexing failure

#### POST /api/index_pdf

**Purpose**: Index a specific PDF file for semantic search

**Authentication**: None required

**Query Parameters**:

- `pdf_path` (string, required): Path to the PDF file to index

**Response Schema**:

```typescript
interface IndexPdfResponse {
    chunks_indexed: number;              // Number of chunks created from PDF
    file_processed: string;              // Path of the processed PDF file
    status: "success" | "failed";       // Processing status
    processing_time?: number;            // Processing time in seconds
    metadata?: {
        pages: number;                   // Number of pages processed
        file_size_mb: number;            // File size in megabytes
        text_extracted: number;          // Characters extracted
    };
    errors?: string[];                   // Any processing errors
}
```

**Example Response**:

```json
{
    "chunks_indexed": 15,
    "file_processed": "documents/research-paper.pdf",
    "status": "success",
    "processing_time": 4.12,
    "metadata": {
        "pages": 23,
        "file_size_mb": 1.8,
        "text_extracted": 45230
    }
}
```

**Status Codes**:

- `200 OK`: PDF indexed successfully
- `400 Bad Request`: Invalid file path or unsupported PDF format
- `404 Not Found`: PDF file not found
- `500 Internal Server Error`: PDF processing or indexing failure



### Search Operations

#### POST /api/search

**Purpose**: Perform semantic similarity search across indexed documents

**Authentication**: None required

**Query Parameters**:

- `query` (string, required): Search query text
- `top_k` (int, optional): Maximum number of results (default: 5, max: 100)

**Response Schema**:

```typescript
interface SearchResponse {
    results: SearchResult[];
    query: string;                       // Echo of the search query
    total_results: number;               // Number of results returned
    processing_time?: number;            // Search time in seconds
}

interface SearchResult {
    content: string;                     // Matching text content
    score: number;                       // Similarity score (0-1)
    source: string;                      // Source file path
    chunk_id: string;                    // Unique chunk identifier
    metadata?: {
        file_type?: string;              // File type (md, pdf, txt)
        chunk_index?: number;            // Position within source file
        created_at?: string;             // Index creation timestamp
    };
}
```

**Example Request**:

```http
POST /api/search?query=machine%20learning&top_k=3
```

**Example Response**:

```json
{
    "results": [
        {
            "content": "Machine learning algorithms can be supervised or unsupervised...",
            "score": 0.95,
            "source": "notes/ai-concepts.md",
            "chunk_id": "chunk_123",
            "metadata": {
                "file_type": "md",
                "chunk_index": 2,
                "created_at": "2024-10-06T10:30:00Z"
            }
        },
        {
            "content": "Deep learning is a subset of machine learning that uses neural networks...",
            "score": 0.87,
            "source": "research/deep-learning.pdf",
            "chunk_id": "chunk_456",
            "metadata": {
                "file_type": "pdf",
                "chunk_index": 5,
                "created_at": "2024-10-06T09:15:00Z"
            }
        }
    ],
    "query": "machine learning",
    "total_results": 2,
    "processing_time": 0.045
}
```

**Status Codes**:

- `200 OK`: Search completed successfully (even if no results found)
- `400 Bad Request`: Missing or invalid query parameter
- `500 Internal Server Error`: Search service failure or index unavailable

---

### Voice & Audio Processing

#### POST /transcribe

**Purpose**: Convert audio data to text using speech recognition

**Authentication**: None required

**Request Schema**:

```typescript
interface TranscribeRequest {
    audio_data: string;                  // Base64-encoded audio data
    format?: string;                     // Audio format (default: "webm")
    language?: string;                   // Language code (default: "en")
    mode?: "offline" | "online";         // Processing mode (default: "offline")
}
```

**Request Example**:

```json
{
    "audio_data": "UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
    "format": "wav",
    "language": "en",
    "mode": "offline"
}
```

**Response Schema**:

```typescript
interface TranscribeResponse {
    transcription: string;               // Transcribed text
    confidence?: number;                 // Confidence score (0-1)
    processing_time?: number;            // Processing time in seconds
    language?: string;                   // Detected/used language
    status: "success" | "partial" | "failed";
    metadata?: {
        audio_duration?: number;         // Audio length in seconds
        model_used?: string;             // Speech recognition model
        sample_rate?: number;            // Audio sample rate
    };
}
```

**Example Response**:

```json
{
    "transcription": "Hello, can you help me understand machine learning concepts?",
    "confidence": 0.95,
    "processing_time": 1.23,
    "language": "en",
    "status": "success",
    "metadata": {
        "audio_duration": 3.5,
        "model_used": "vosk-model-small-en-us-0.15",
        "sample_rate": 16000
    }
}
```

**Status Codes**:

- `200 OK`: Transcription completed successfully
- `400 Bad Request`: Invalid audio data or unsupported format
- `415 Unsupported Media Type`: Audio format not supported
- `500 Internal Server Error`: Transcription service failure

**Supported Audio Formats**:

- WAV (recommended)
- WebM
- MP3 (converted to WAV internally)
- OGG

**Voice Processing Pipeline**:

1. Base64 decode audio data
2. Format validation and conversion
3. Speech recognition using Vosk or configured engine
4. Post-processing and confidence scoring
5. Response formatting and return

---

## 📊 Data Models

### Pydantic Request Models

The FastAPI backend uses Pydantic models for request validation, providing automatic type checking, data validation, and API documentation generation.

#### AskRequest

```python
class AskRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    question: str                                    # Required: User question or prompt
    prefer_fast: bool = True                        # Prefer speed over quality
    max_tokens: int = 256                           # Maximum response tokens
    context_paths: Optional[List[str]] = None       # Specific vault files for context
    prompt: Optional[str] = None                    # Custom system prompt
    model_name: Optional[str] = "llama-7b"         # Model selection override
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        if len(v) > 10000:
            raise ValueError('Question too long (max 10,000 characters)')
        return v.strip()
```

#### ReindexRequest

```python
class ReindexRequest(BaseModel):
    vault_path: str = "./vault"                     # Directory path to reindex
    
    @field_validator('vault_path')
    @classmethod
    def validate_vault_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Vault path cannot be empty')
        return v.strip()
```

#### WebRequest

```python
class WebRequest(BaseModel):
    url: str                                        # Required: HTTP/HTTPS URL
    question: Optional[str] = None                  # Optional question about content
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()
```

#### TranscribeRequest

```python
class TranscribeRequest(BaseModel):
    audio_data: str                                 # Base64 encoded audio data
    format: str = "webm"                           # Audio format
    language: str = "en"                           # Language code (ISO 639-1)
    mode: Optional[str] = "offline"                # Processing mode
    
    @field_validator('audio_data')
    @classmethod
    def validate_audio_data(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Audio data cannot be empty')
        return v
```

### Response Models & Error Handling

#### StandardResponse

```python
class StandardResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    request_id: Optional[str] = None
```

#### ErrorResponse

```python
class ErrorResponse(BaseModel):
    error: str                                      # Error category/type
    message: str                                    # Human-readable error message
    details: Optional[Dict[str, Any]] = None       # Additional error context
    timestamp: int = Field(default_factory=lambda: int(time.time()))
```

#### AskResponse

```python
class AskResponse(StandardResponse):
    answer: str                                     # AI-generated response
    cached: bool = False                           # Whether from cache
    model_used: str                                # Model that generated response
    processing_time: Optional[float] = None        # Processing time in seconds
    tokens_used: Optional[int] = None              # Token consumption
    metadata: Optional[Dict[str, Any]] = None      # Additional metadata
```

### OpenAPI Documentation

#### Automatic API Documentation

FastAPI automatically generates OpenAPI 3.0 specifications accessible at:

- **Interactive API Docs (Swagger UI)**: `GET /docs`
- **Alternative Docs (ReDoc)**: `GET /redoc`  
- **OpenAPI JSON Schema**: `GET /openapi.json`

#### Authentication & Rate Limiting

**Current Status**: No authentication required (localhost development)

**Production Recommendations**: Implement JWT authentication and rate limiting for production deployments.

---

## ⚙️ Configuration System

### Configuration Precedence

1. **Environment Variables** (highest priority)
2. **backend/config.yaml** (medium priority)
3. **Code Defaults** (lowest priority)

### Settings Model

```python
class Settings(BaseModel):
    # Core server
    backend_url: str = "http://127.0.0.1:8000"
    api_port: int = 8000
    allow_network: bool = False
    continuous_mode: bool = False
    
    # Paths
    project_root: str = str(Path(__file__).resolve().parents[1])
    vault_path: str = "vault"
    models_dir: str = "models"
    cache_dir: str = "cache"
    
    # LLM Settings
    model_backend: str = "llama_cpp"
    model_path: str = "models/llama-7b.gguf"
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_db: str = "chroma"
    gpu: bool = True
    
    # Processing Parameters
    top_k: int = 10
    chunk_size: int = 800
    chunk_overlap: int = 200
    similarity_threshold: float = 0.75
    
    # Voice Settings
    vosk_model_path: str = "models/vosk-model-small-en-us-0.15"
```

### Environment Variables

```bash
# Core Settings
API_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
ALLOW_NETWORK=false

# Paths
VAULT_PATH=./vault
MODELS_DIR=./models
CACHE_DIR=./cache

# LLM Configuration
MODEL_BACKEND=llama_cpp
MODEL_PATH=models/llama-7b.gguf
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
GPU=true

# Processing
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
TOP_K=10
SIMILARITY_THRESHOLD=0.75

# Voice
VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15
```

---

## 🧪 Testing Standards

### Coverage Requirements

- **Target**: 70%+ overall coverage
- **Critical Modules**: 90%+ (settings, caching, security)
- **API Endpoints**: 65%+ coverage
- **Integration Tests**: End-to-end scenarios

### Test Architecture

```text
tests/
├── backend/                     # Backend module tests
│   ├── test_backend.py         # FastAPI endpoints & integration
│   ├── test_backend_simple.py  # Simple tests avoiding PyTorch conflicts
│   ├── test_caching.py         # Cache management 
│   ├── test_settings.py        # Settings management
│   ├── test_llm_router.py      # Model routing logic
│   ├── test_embeddings.py      # Vector operations
│   ├── test_indexing.py        # Document processing
│   ├── test_security.py        # Encryption/decryption
│   └── test_voice.py           # Voice transcription
├── conftest.py                  # Shared test configuration
├── test_final.py               # End-to-end integration tests
└── simple_backend.py           # Mock backend for testing
```

### PyTorch Conflict Resolution

```python
# Module-level mocking strategy
@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
```

### Test Categories

#### Unit Tests

**Scope**: Individual functions and classes in isolation

**Requirements**:

- **Coverage**: 80%+ for critical modules (settings, security, caching)
- **Isolation**: Mock external dependencies
- **Speed**: < 100ms per test
- **Frameworks**: pytest, unittest.mock, pytest-asyncio

**Test Patterns**:

```python
# Example unit test structure
@pytest.mark.asyncio
async def test_embedding_generation():
    with patch('backend.embeddings.SentenceTransformer'):
        embedder = EmbeddingManager()
        result = await embedder.generate_embedding("test text")
        assert len(result) == 384
        assert isinstance(result, list)
```

#### Integration Tests

**Scope**: Component interactions and API workflows

**Requirements**:

- **Coverage**: 70%+ for API endpoints
- **Database**: Test with actual ChromaDB instance
- **Network**: Mock external HTTP calls
- **Performance**: < 5s per test scenario

**Test Scenarios**:

```python
# Example integration test
@pytest.mark.integration
async def test_full_question_workflow(test_client):
    # Index test document
    response = await test_client.post("/reindex", json={"vault_path": "test_vault"})
    assert response.status_code == 200
    
    # Ask question
    response = await test_client.post("/ask", json={"question": "What is AI?"})
    assert response.status_code == 200
    assert "answer" in response.json()
```

#### Performance Tests

**Scope**: System performance under various loads

**Requirements**:

- **Response Time**: API endpoints < SLA targets
- **Throughput**: Handle concurrent requests
- **Memory**: Monitor resource usage
- **Tools**: locust, pytest-benchmark, memory-profiler

**Benchmarks**:

```python
# Performance test example
@pytest.mark.benchmark
def test_embedding_performance(benchmark):
    embedder = EmbeddingManager()
    result = benchmark(embedder.generate_embedding, "test text")
    assert benchmark.stats.avg < 0.5  # 500ms max
```

**Load Testing Targets**:

- **Concurrent Users**: 10 simultaneous requests
- **Response Times**:
  - Health endpoints: < 100ms
  - Search operations: < 1000ms
  - AI generation: < 30s
- **Memory Usage**: < 2GB under normal load

#### Security Tests

**Scope**: Vulnerability assessment and security controls

**Requirements**:

- **Input Validation**: Test injection attacks
- **Authentication**: Verify access controls
- **Encryption**: Test data protection
- **Tools**: bandit, safety, custom security tests

**Security Test Categories**:

```python
# Security test examples
@pytest.mark.security
def test_sql_injection_prevention():
    malicious_input = "'; DROP TABLE users; --"
    with pytest.raises(ValidationError):
        validate_search_query(malicious_input)

@pytest.mark.security
def test_encryption_decryption():
    secret_key = SecurityManager.generate_key()
    encrypted = SecurityManager.encrypt("sensitive data", secret_key)
    decrypted = SecurityManager.decrypt(encrypted, secret_key)
    assert decrypted == "sensitive data"
```

**Security Checklist**:

- [ ] Input sanitization for all API endpoints
- [ ] Fernet encryption for sensitive cache data
- [ ] File path traversal prevention
- [ ] Memory leak detection in long-running processes
- [ ] Dependency vulnerability scanning

### Acceptance Criteria

#### Functional Requirements

**API Endpoints**:

- All endpoints return proper HTTP status codes
- Request/response models validate correctly
- Error handling provides meaningful messages
- Documentation matches actual behavior

**Core Features**:

- Document indexing processes all supported formats
- Semantic search returns relevant results
- Voice transcription accuracy > 90%
- Configuration changes apply without restart

#### Performance Requirements

**Response Time SLA**:

- Health endpoints: < 100ms (99th percentile)
- Configuration endpoints: < 200ms (95th percentile)
- Search operations: < 1000ms (90th percentile)
- AI generation: Variable based on model size

**Resource Utilization**:

- Memory usage < 4GB under normal load
- CPU usage < 80% during peak operations
- Disk I/O < 100MB/s for indexing operations
- Cache hit ratio > 70% for repeated queries

#### Quality Gates

**Code Quality**:

- Linting: 0 critical issues (flake8, black, mypy)
- Security: 0 high/critical vulnerabilities (bandit, safety)
- Coverage: Minimum thresholds per component
- Documentation: All public APIs documented

**Test Quality**:

- All tests must pass in CI/CD pipeline
- No flaky tests (< 1% failure rate)
- Test execution time < 10 minutes total
- Performance regression detection

### Test Frameworks and Tools

#### Core Testing Stack

```bash
# Testing dependencies
pytest>=7.4.0                    # Test framework
pytest-asyncio>=0.21.0          # Async test support
pytest-cov>=4.1.0               # Coverage reporting
pytest-benchmark>=4.0.0         # Performance testing
pytest-mock>=3.11.0             # Enhanced mocking
httpx>=0.24.0                    # HTTP testing client
```

#### Development Tools

```bash
# Code quality tools
black>=23.7.0                    # Code formatting
flake8>=6.0.0                    # Linting
mypy>=1.5.0                      # Type checking
bandit>=1.7.5                    # Security scanning
safety>=2.3.0                    # Dependency scanning
```

#### Performance Testing

```bash
# Load testing tools
locust>=2.15.0                   # Load testing framework
memory-profiler>=0.61.0          # Memory usage profiling
py-spy>=0.3.14                   # CPU profiling
```

### CI/CD Integration

#### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 backend/ tests/
        black --check backend/ tests/
        mypy backend/
    
    - name: Run security scan
      run: |
        bandit -r backend/
        safety check
    
    - name: Run unit tests
      run: |
        pytest tests/ --cov=backend --cov-report=xml --cov-fail-under=70
    
    - name: Run integration tests
      run: |
        pytest tests/ -m integration
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, backend/]
```

#### Quality Metrics Dashboard

**Coverage Reports**:

- HTML reports generated in `htmlcov/`
- XML reports for CI/CD integration
- Line-by-line coverage analysis
- Branch coverage tracking

**Performance Metrics**:

- Benchmark results stored in `benchmarks/`
- Performance regression detection
- Memory usage profiling reports
- Load testing summaries

### Test Execution

```bash
# Full test suite with coverage
pytest --cov=backend --cov-report=term-missing --cov-report=html

# Individual module tests
pytest tests/backend/test_backend_simple.py -v

# Coverage target validation
pytest --cov=backend --cov-fail-under=70

# Performance tests only
pytest -m benchmark --benchmark-only

# Security tests only
pytest -m security

# Integration tests with clean database
pytest -m integration --reset-db

# Parallel test execution
pytest -n auto --dist=loadscope

# Test with specific Python version
tox -e py310,py311,py312
```

### Continuous Quality Assurance

#### Automated Quality Checks

**Daily Builds**:

- Full test suite execution
- Performance regression testing
- Security vulnerability scanning
- Dependency update checks

**Pull Request Gates**:

- All tests must pass
- Coverage threshold maintained
- No security vulnerabilities introduced
- Code style compliance verified

**Release Criteria**:

- 100% test passage rate
- Performance benchmarks met
- Security scan clean
- Documentation updated

---

## 🔒 Security Standards & Protocols

### Security Architecture Overview

The Obsidian AI Assistant implements a defense-in-depth security model with local-first processing, configurable network isolation, and comprehensive data protection mechanisms.

#### Security Principles

- **Privacy by Design**: User data remains local unless explicitly configured otherwise
- **Minimal Attack Surface**: Network features disabled by default
- **Defense in Depth**: Multiple security layers and fail-safe mechanisms
- **Secure Defaults**: Most secure configuration out-of-the-box
- **Transparency**: Clear security implications for all configuration options

### Data Protection & Privacy

#### Data Classification

| Data Type | Sensitivity Level | Storage Location | Protection Measures |
|-----------|------------------|------------------|-------------------|
| User Notes/Vault | **Critical** | Local filesystem | Filesystem permissions, optional encryption |
| AI Responses | **High** | Local cache | TTL-based cleanup, optional encryption |
| Configuration | **Medium** | Local config files | File permissions, secrets in env vars |
| Embeddings | **Medium** | Vector database | Local ChromaDB, optional encryption |
| Logs | **Low** | Local log files | Log rotation, sensitive data filtering |

#### Encryption Standards

**Cache Encryption (Optional)**:

```python
from cryptography.fernet import Fernet
import os

# Generate and store encryption key
def generate_cache_key():
    key = Fernet.generate_key()
    os.environ['CACHE_ENCRYPTION_KEY'] = key.decode()
    return key

# Encrypt sensitive cache data
def encrypt_cache_data(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())

# Decrypt cache data
def decrypt_cache_data(encrypted_data: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
```

**File System Security**:

- Vault files: Standard OS file permissions (600/700)
- Config files: Restricted access (600)
- Cache directory: User-only access (700)
- Log files: User-only read/write (600)

#### Data Retention & Cleanup

```python
class SecureDataManager:
    def __init__(self, retention_policy: dict):
        self.retention_policy = retention_policy
    
    async def cleanup_expired_data(self):
        """Remove data based on retention policy"""
        # Cache cleanup
        await self.cleanup_cache_older_than(
            self.retention_policy.get('cache_ttl', 86400)  # 24 hours
        )
        
        # Log rotation
        await self.rotate_logs_older_than(
            self.retention_policy.get('log_retention', 604800)  # 7 days
        )
        
        # Temporary files
        await self.cleanup_temp_files()
    
    async def secure_delete(self, file_path: str):
        """Securely overwrite file before deletion"""
        if os.path.exists(file_path):
            # Overwrite with random data multiple times
            file_size = os.path.getsize(file_path)
            with open(file_path, 'r+b') as f:
                for _ in range(3):  # DoD 5220.22-M standard
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            os.remove(file_path)
```

### Network Security

#### Network Access Control

```python
class NetworkSecurityPolicy:
    def __init__(self, allow_network: bool = False):
        self.allow_network = allow_network
        self.allowed_domains = []
        self.blocked_ips = []
    
    def validate_url_access(self, url: str) -> bool:
        """Validate if URL access is allowed"""
        if not self.allow_network:
            raise SecurityException("Network access disabled")
        
        # Parse URL and check against whitelist
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check against allowed domains
        if self.allowed_domains and domain not in self.allowed_domains:
            raise SecurityException(f"Domain {domain} not in allowlist")
        
        # Check against blocked IPs
        try:
            ip = socket.gethostbyname(domain)
            if ip in self.blocked_ips:
                raise SecurityException(f"IP {ip} is blocked")
        except socket.gaierror:
            pass
        
        return True
```

#### HTTPS and Certificate Validation

```python
import ssl
import certifi

def create_secure_ssl_context():
    """Create SSL context with secure defaults"""
    context = ssl.create_default_context(cafile=certifi.where())
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context

# Apply to HTTP requests
async def secure_http_request(url: str, **kwargs):
    ssl_context = create_secure_ssl_context()
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl_context=ssl_context)
    ) as session:
        async with session.get(url, **kwargs) as response:
            return await response.json()
```

### Authentication & Authorization

#### API Authentication Framework

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

class AuthenticationManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.token_expire_minutes = 60
    
    def create_access_token(self, data: dict) -> str:
        """Generate JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise AuthenticationException("Invalid token")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
```

#### Role-Based Access Control (RBAC)

```python
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class Permission(Enum):
    READ_CONFIG = "read_config"
    WRITE_CONFIG = "write_config"
    ASK_QUESTIONS = "ask_questions"
    MANAGE_VAULT = "manage_vault"
    VIEW_LOGS = "view_logs"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ_CONFIG,
        Permission.WRITE_CONFIG,
        Permission.ASK_QUESTIONS,
        Permission.MANAGE_VAULT,
        Permission.VIEW_LOGS
    ],
    UserRole.USER: [
        Permission.READ_CONFIG,
        Permission.ASK_QUESTIONS,
        Permission.MANAGE_VAULT
    ],
    UserRole.READONLY: [
        Permission.READ_CONFIG,
        Permission.ASK_QUESTIONS
    ]
}

def require_permission(permission: Permission):
    """Decorator to enforce permissions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user from context
            user_role = get_current_user_role()
            if permission not in ROLE_PERMISSIONS.get(user_role, []):
                raise AuthorizationException(f"Permission {permission} required")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### Input Validation & Sanitization

#### Comprehensive Input Validation

```python
import re
from typing import Any, Dict, List
import bleach
from pydantic import validator

class SecurityValidator:
    # Regex patterns for validation
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9._/-]+$')
    EMAIL_PATTERN = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
    
    @staticmethod
    def sanitize_html(content: str) -> str:
        """Strip potentially dangerous HTML"""
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        return bleach.clean(content, tags=allowed_tags, strip=True)
    
    @staticmethod
    def validate_file_path(path: str) -> str:
        """Validate file path for directory traversal attacks"""
        if '..' in path or path.startswith('/'):
            raise ValueError("Invalid file path")
        
        normalized = os.path.normpath(path)
        if not SecurityValidator.SAFE_PATH_PATTERN.match(normalized):
            raise ValueError("Path contains invalid characters")
        
        return normalized
    
    @staticmethod
    def validate_sql_injection(query: str) -> str:
        """Basic SQL injection protection"""
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC', 'UNION']
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Potentially dangerous keyword: {keyword}")
        
        return query

# Apply to Pydantic models
class SecureAskRequest(BaseModel):
    question: str
    
    @validator('question')
    def validate_question_security(cls, v):
        if len(v) > 10000:
            raise ValueError("Question too long")
        
        # Basic XSS protection
        sanitized = SecurityValidator.sanitize_html(v)
        
        # SQL injection check
        SecurityValidator.validate_sql_injection(v)
        
        return sanitized
```

### Security Monitoring & Logging

#### Security Event Logging

```python
import logging
from datetime import datetime
from enum import Enum

class SecurityEventType(Enum):
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CONFIG_CHANGE = "config_change"
    SUSPICIOUS_INPUT = "suspicious_input"
    RATE_LIMIT_HIT = "rate_limit_hit"
    FILE_ACCESS = "file_access"

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Create security-specific log handler
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_security_event(self, 
                          event_type: SecurityEventType, 
                          details: Dict[str, Any],
                          client_ip: str = None,
                          user_id: str = None):
        """Log security-relevant events"""
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type.value,
            'client_ip': client_ip,
            'user_id': user_id,
            'details': details
        }
        
        self.logger.info(f"SECURITY_EVENT: {event_data}")
        
        # Alert on critical events
        if event_type in [SecurityEventType.UNAUTHORIZED_ACCESS, 
                         SecurityEventType.SUSPICIOUS_INPUT]:
            self.send_security_alert(event_data)
    
    def send_security_alert(self, event_data: Dict[str, Any]):
        """Send immediate alerts for critical security events"""
        # Implementation depends on alerting system
        # Could be email, Slack, webhook, etc.
        pass
```

### Threat Modeling & Risk Assessment

#### STRIDE Threat Model

| Threat Category | Risk Level | Mitigation Strategies |
|----------------|------------|---------------------|
| **Spoofing** | Medium | JWT authentication, API key validation |
| **Tampering** | Low | File integrity checks, input validation |
| **Repudiation** | Low | Comprehensive audit logging |
| **Information Disclosure** | High | Local processing, encryption at rest |
| **Denial of Service** | Medium | Rate limiting, resource monitoring |
| **Elevation of Privilege** | Low | RBAC, principle of least privilege |

#### Security Risk Assessment

```python
class SecurityRiskAssessment:
    def __init__(self):
        self.risk_factors = {
            'network_enabled': {'weight': 0.8, 'impact': 'High'},
            'external_models': {'weight': 0.6, 'impact': 'Medium'},
            'file_processing': {'weight': 0.4, 'impact': 'Medium'},
            'cache_encryption_disabled': {'weight': 0.3, 'impact': 'Low'},
            'verbose_logging': {'weight': 0.2, 'impact': 'Low'}
        }
    
    def calculate_risk_score(self, config: Dict[str, Any]) -> float:
        """Calculate overall security risk score"""
        total_risk = 0.0
        active_risks = []
        
        if config.get('allow_network', False):
            total_risk += self.risk_factors['network_enabled']['weight']
            active_risks.append('network_enabled')
        
        if not config.get('cache_encryption', False):
            total_risk += self.risk_factors['cache_encryption_disabled']['weight']
            active_risks.append('cache_encryption_disabled')
        
        return {
            'risk_score': min(total_risk, 1.0),
            'risk_level': self.get_risk_level(total_risk),
            'active_risks': active_risks,
            'recommendations': self.get_recommendations(active_risks)
        }
    
    def get_risk_level(self, score: float) -> str:
        if score >= 0.7: return "High"
        elif score >= 0.4: return "Medium"
        else: return "Low"
```

---

## 📈 Performance Standards & Optimization

### Performance Architecture

The system is designed for optimal performance across different deployment scenarios, from resource-constrained development environments to high-performance production servers.

#### Performance Design Principles

- **Asynchronous Processing**: Non-blocking I/O for all external operations
- **Intelligent Caching**: Multi-level caching with smart invalidation
- **Resource Optimization**: Dynamic resource allocation based on system capabilities
- **Lazy Loading**: On-demand initialization of expensive components
- **Batch Processing**: Efficient handling of multiple operations

### Performance Benchmarks & Targets

#### Response Time Service Level Agreements (SLAs)

| Endpoint Category | Target (P95) | Target (P99) | Timeout | Notes |
|------------------|--------------|--------------|---------|-------|
| Health Checks | 50ms | 100ms | 5s | Critical for monitoring |
| Configuration | 100ms | 200ms | 10s | Cached responses |
| Search Operations | 500ms | 1000ms | 30s | Depends on index size |
| AI Generation (Fast) | 2s | 5s | 60s | Small models |
| AI Generation (Quality) | 10s | 30s | 300s | Large models |
| File Indexing | 1s/MB | 3s/MB | 600s | Depends on content type |
| Voice Transcription | 0.5x realtime | 1x realtime | 120s | Audio duration ratio |

#### Throughput Requirements

```python
class PerformanceTargets:
    # Requests per second (RPS) targets
    HEALTH_ENDPOINT_RPS = 100      # High frequency monitoring
    CONFIG_ENDPOINT_RPS = 20       # Administrative operations
    ASK_ENDPOINT_RPS = 5           # AI generation bottleneck
    SEARCH_ENDPOINT_RPS = 30       # Vector search operations
    
    # Concurrent request limits
    MAX_CONCURRENT_AI_REQUESTS = 3     # GPU/CPU resource limit
    MAX_CONCURRENT_INDEXING = 2        # I/O intensive operations
    MAX_CONCURRENT_SEARCH = 10         # Memory-bound operations
    
    # Resource utilization targets
    CPU_UTILIZATION_TARGET = 0.8      # 80% max sustained
    MEMORY_UTILIZATION_TARGET = 0.9    # 90% max sustained
    GPU_UTILIZATION_TARGET = 0.95      # 95% max (GPU bound)
```

#### Memory Usage Optimization

```python
import psutil
import torch
from typing import Dict, Any

class MemoryManager:
    def __init__(self):
        self.memory_threshold = 0.85  # 85% memory usage threshold
        self.cleanup_callbacks = []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        system_memory = psutil.virtual_memory()
        
        stats = {
            'system_total_gb': system_memory.total / (1024**3),
            'system_available_gb': system_memory.available / (1024**3),
            'system_usage_percent': system_memory.percent,
            'process_memory_gb': process.memory_info().rss / (1024**3),
            'gpu_memory_gb': self.get_gpu_memory() if torch.cuda.is_available() else 0
        }
        
        return stats
    
    def get_gpu_memory(self) -> float:
        """Get GPU memory usage in GB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / (1024**3)
        return 0.0
    
    def check_memory_pressure(self) -> bool:
        """Check if system is under memory pressure"""
        stats = self.get_memory_stats()
        return stats['system_usage_percent'] > (self.memory_threshold * 100)
    
    def optimize_memory_usage(self):
        """Trigger memory optimization routines"""
        if self.check_memory_pressure():
            # Clear model caches
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Trigger garbage collection
            import gc
            gc.collect()
            
            # Execute registered cleanup callbacks
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    logging.warning(f"Memory cleanup callback failed: {e}")
```

### Caching Strategy & Optimization

#### Multi-Level Caching Architecture

```python
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import hashlib
import json

class MultiLevelCache:
    def __init__(self):
        # L1: In-memory cache (fastest)
        self.memory_cache: Dict[str, Any] = {}
        self.memory_ttl: Dict[str, datetime] = {}
        
        # L2: Disk cache (persistent)
        self.disk_cache_dir = "cache/responses"
        
        # L3: Vector embeddings cache
        self.embedding_cache_dir = "cache/embeddings"
        
        # Cache configuration
        self.max_memory_entries = 1000
        self.default_ttl_minutes = 60
        
    async def get(self, key: str, cache_level: str = "auto") -> Optional[Any]:
        """Get cached value with automatic cache level selection"""
        cache_key = self._generate_cache_key(key)
        
        # Try L1 cache first (memory)
        if cache_level in ["auto", "memory"]:
            if cache_key in self.memory_cache:
                if self._is_valid_ttl(cache_key):
                    return self.memory_cache[cache_key]
                else:
                    # Expired - remove from memory
                    del self.memory_cache[cache_key]
                    del self.memory_ttl[cache_key]
        
        # Try L2 cache (disk)
        if cache_level in ["auto", "disk"]:
            disk_value = await self._get_from_disk_cache(cache_key)
            if disk_value:
                # Promote to L1 cache
                await self.set(key, disk_value, cache_level="memory")
                return disk_value
        
        return None
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl_minutes: int = None,
                  cache_level: str = "auto"):
        """Set cached value with configurable cache level"""
        cache_key = self._generate_cache_key(key)
        ttl = ttl_minutes or self.default_ttl_minutes
        
        if cache_level in ["auto", "memory"]:
            # L1 cache (memory)
            self._ensure_memory_capacity()
            self.memory_cache[cache_key] = value
            self.memory_ttl[cache_key] = datetime.now() + timedelta(minutes=ttl)
        
        if cache_level in ["auto", "disk"]:
            # L2 cache (disk)
            await self._set_disk_cache(cache_key, value, ttl)
    
    def _generate_cache_key(self, key: str) -> str:
        """Generate consistent cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _is_valid_ttl(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        return (cache_key in self.memory_ttl and 
                self.memory_ttl[cache_key] > datetime.now())
    
    def _ensure_memory_capacity(self):
        """Ensure memory cache doesn't exceed capacity"""
        if len(self.memory_cache) >= self.max_memory_entries:
            # Remove oldest entries (LRU eviction)
            oldest_keys = sorted(
                self.memory_ttl.keys(),
                key=lambda k: self.memory_ttl[k]
            )[:100]  # Remove 100 oldest entries
            
            for key in oldest_keys:
                del self.memory_cache[key]
                del self.memory_ttl[key]
```

#### Performance Monitoring & Profiling

```python
import time
import functools
from contextlib import asynccontextmanager
from typing import Dict, List

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.counters: Dict[str, int] = {}
    
    def timing_decorator(self, operation_name: str):
        """Decorator to measure function execution time"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self.record_timing(operation_name, execution_time)
            return wrapper
        return decorator
    
    @asynccontextmanager
    async def measure_operation(self, operation_name: str):
        """Context manager for measuring operation performance"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self.record_timing(operation_name, execution_time)
    
    def record_timing(self, operation: str, duration: float):
        """Record timing metric"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append(duration)
        
        # Keep only last 1000 measurements to prevent memory leak
        if len(self.metrics[operation]) > 1000:
            self.metrics[operation] = self.metrics[operation][-1000:]
    
    def get_performance_stats(self, operation: str = None) -> Dict[str, Any]:
        """Get performance statistics"""
        if operation:
            if operation not in self.metrics:
                return {"error": f"No metrics for operation: {operation}"}
            
            timings = self.metrics[operation]
            return {
                "operation": operation,
                "count": len(timings),
                "avg_ms": sum(timings) / len(timings) * 1000,
                "min_ms": min(timings) * 1000,
                "max_ms": max(timings) * 1000,
                "p95_ms": self._percentile(timings, 0.95) * 1000,
                "p99_ms": self._percentile(timings, 0.99) * 1000
            }
        else:
            return {op: self.get_performance_stats(op) for op in self.metrics.keys()}
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

# Usage examples
@perf_monitor.timing_decorator("ai_generation")
async def generate_ai_response(question: str) -> str:
    # AI generation logic
    pass

async def process_vault_indexing():
    async with perf_monitor.measure_operation("vault_indexing"):
        # Indexing logic
        pass
```

### Resource Optimization Strategies

#### Dynamic Resource Allocation

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

class ResourceManager:
    def __init__(self):
        self.cpu_count = os.cpu_count()
        self.gpu_available = torch.cuda.is_available()
        self.thread_pool: Optional[ThreadPoolExecutor] = None
        self.semaphores = {
            'ai_generation': asyncio.Semaphore(2),
            'file_processing': asyncio.Semaphore(4),
            'network_requests': asyncio.Semaphore(10)
        }
    
    def get_optimal_worker_count(self, task_type: str) -> int:
        """Calculate optimal worker count based on task type and resources"""
        base_workers = self.cpu_count
        
        if task_type == "cpu_intensive":
            return max(1, base_workers - 1)  # Leave one core for system
        elif task_type == "io_intensive":
            return base_workers * 2  # I/O bound tasks can use more workers
        elif task_type == "gpu_accelerated" and self.gpu_available:
            return min(2, base_workers // 2)  # GPU tasks need less CPU workers
        else:
            return max(1, base_workers // 2)
    
    async def execute_with_semaphore(self, 
                                   task_type: str, 
                                   coroutine):
        """Execute coroutine with appropriate semaphore control"""
        semaphore = self.semaphores.get(task_type)
        if semaphore:
            async with semaphore:
                return await coroutine
        else:
            return await coroutine
    
    def get_thread_pool(self, task_type: str) -> ThreadPoolExecutor:
        """Get thread pool executor optimized for task type"""
        if not self.thread_pool:
            max_workers = self.get_optimal_worker_count(task_type)
            self.thread_pool = ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix=f"aiassist-{task_type}"
            )
        return self.thread_pool
```

### Compliance & Audit Requirements

#### Compliance Framework

| Regulation | Applicability | Key Requirements | Implementation Status |
|------------|---------------|------------------|---------------------|
| **GDPR** | EU users | Data minimization, consent, right to erasure | ✅ Local processing |
| **CCPA** | California users | Data transparency, deletion rights | ✅ No external data sharing |
| **SOC 2** | Enterprise deployments | Security controls, access management | 🔄 Partial (logging) |
| **ISO 27001** | Security certification | Information security management | 🔄 Framework ready |
| **HIPAA** | Healthcare data | Data encryption, access controls | ❌ Requires additional controls |

#### Audit Logging Framework

```python
import json
from datetime import datetime
from enum import Enum

class AuditEventType(Enum):
    CONFIG_CHANGE = "config_change"
    USER_LOGIN = "user_login"
    DATA_ACCESS = "data_access"
    AI_GENERATION = "ai_generation"
    FILE_OPERATION = "file_operation"
    SYSTEM_EVENT = "system_event"

class ComplianceAuditor:
    def __init__(self, audit_log_path: str = "logs/audit.jsonl"):
        self.audit_log_path = audit_log_path
        self.required_fields = [
            'timestamp', 'event_type', 'user_id', 
            'resource', 'action', 'outcome'
        ]
    
    def log_audit_event(self, 
                       event_type: AuditEventType,
                       user_id: str,
                       resource: str,
                       action: str,
                       outcome: str,
                       additional_data: Dict[str, Any] = None):
        """Log compliance audit event"""
        audit_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type.value,
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'outcome': outcome,
            'session_id': self._get_session_id(),
            'client_ip': self._get_client_ip(),
            'additional_data': additional_data or {}
        }
        
        # Write to audit log
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(audit_record) + '\n')
    
    def generate_compliance_report(self, 
                                 start_date: datetime,
                                 end_date: datetime) -> Dict[str, Any]:
        """Generate compliance audit report"""
        events = []
        
        with open(self.audit_log_path, 'r') as f:
            for line in f:
                event = json.loads(line.strip())
                event_time = datetime.fromisoformat(event['timestamp'])
                
                if start_date <= event_time <= end_date:
                    events.append(event)
        
        return {
            'report_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': len(events),
            'events_by_type': self._count_events_by_type(events),
            'events_by_user': self._count_events_by_user(events),
            'security_events': self._filter_security_events(events)
        }
```

---

## 🚀 Deployment & Operations Guide

### Deployment Architecture Overview

The Obsidian AI Assistant supports multiple deployment scenarios from local development to production environments. The architecture is designed for flexibility, scalability, and maintainability across different infrastructure patterns.

#### Deployment Patterns

- **Local Development**: Single-machine setup with minimal dependencies
- **Standalone Server**: Dedicated server deployment with enhanced security
- **Containerized Deployment**: Docker-based deployment with orchestration
- **Cloud Deployment**: Scalable cloud infrastructure with managed services
- **Enterprise Deployment**: High-availability setup with monitoring and backup

### System Requirements

#### Minimum Requirements (Development)

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **CPU** | 2 cores, 2.0 GHz | Intel/AMD x64 or ARM64 |
| **Memory** | 4GB RAM | 8GB+ recommended for larger models |
| **Storage** | 5GB free space | SSD recommended for performance |
| **Python** | 3.10+ | 3.11+ recommended |
| **OS** | Windows 10+, Ubuntu 20.04+, macOS 10.15+ | 64-bit required |
| **Network** | Internet connection | For model downloads and updates |

#### Recommended Production Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **CPU** | 8+ cores, 3.0+ GHz | More cores improve concurrent performance |
| **Memory** | 16GB+ RAM | 32GB+ for large-scale deployments |
| **Storage** | 50GB+ SSD | Fast I/O critical for model loading |
| **GPU** | CUDA 11.8+ compatible | Optional but significantly improves performance |
| **Network** | Gigabit connection | For high-throughput scenarios |

### Installation & Setup

#### Automated Installation

**Windows PowerShell**:

```powershell
# Run as Administrator (optional, for system-wide installation)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Download and run setup script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/UndiFineD/obsidian-AI-assistant/main/setup.ps1" -OutFile "setup.ps1"
.\setup.ps1 -InstallType Production -EnableGPU $true

# Verify installation
python -m backend.backend --version
```

**Linux/macOS Bash**:

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/UndiFineD/obsidian-AI-assistant/main/setup.sh | bash -s -- --install-type=production --enable-gpu

# Verify installation
python -m backend.backend --version

# Set up systemd service (Linux)
sudo cp deployment/obsidian-ai-assistant.service /etc/systemd/system/
sudo systemctl enable obsidian-ai-assistant
sudo systemctl start obsidian-ai-assistant
```

#### Manual Installation

##### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

##### Step 2: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install GPU support (optional)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

##### Step 3: Download Models

```bash
# Download recommended models
python -m backend.modelmanager download --model llama-7b-chat
python -m backend.modelmanager download --embedding sentence-transformers/all-MiniLM-L6-v2
python -m backend.modelmanager download --voice vosk-model-small-en-us-0.15

# Verify model installation
python -m backend.modelmanager list
```

### Environment Configuration

#### Production Environment Variables

Create a `.env` file in the project root:

```bash
# Core Configuration
BACKEND_URL=http://127.0.0.1:8000
API_PORT=8000
ALLOW_NETWORK=false
CONTINUOUS_MODE=false

# Paths (relative to project root)
VAULT_PATH=vault
MODELS_DIR=models
CACHE_DIR=cache

# AI/ML Configuration
MODEL_BACKEND=llama_cpp
MODEL_PATH=models/llama-7b.gguf
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB=chroma
GPU=true

# Performance Tuning
TOP_K=10
CHUNK_SIZE=800
CHUNK_OVERLAP=200
SIMILARITY_THRESHOLD=0.75

# Voice Processing
VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15

# Security (Production)
CACHE_ENCRYPTION=true
CACHE_ENCRYPTION_KEY=your-generated-key-here
LOG_LEVEL=INFO
ENABLE_METRICS=true

# External Services (Optional)
HUGGINGFACE_TOKEN=your-hf-token-here
OPENAI_API_KEY=your-openai-key-here
```

#### Configuration File (backend/config.yaml)

```yaml
# Production configuration template
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  reload: false
  log_level: info

security:
  allow_network: false
  cache_encryption: true
  max_request_size: 10485760  # 10MB
  rate_limiting:
    enabled: true
    requests_per_minute: 60
    burst_size: 10

performance:
  model_backend: llama_cpp
  gpu_acceleration: true
  max_concurrent_requests: 10
  request_timeout: 300
  cache_ttl: 3600

monitoring:
  metrics_enabled: true
  health_check_interval: 30
  log_retention_days: 30
  performance_monitoring: true

backup:
  enabled: true
  interval: daily
  retention_count: 7
  backup_paths:
    - vault
    - cache/embeddings
    - logs
```

### Container Deployment

#### Dockerfile

```dockerfile
# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Set build arguments
ARG ENABLE_GPU=false
ARG MODEL_VARIANT=small

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements*.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Install GPU dependencies conditionally
RUN if [ "$ENABLE_GPU" = "true" ]; then \
    pip install --no-cache-dir --user torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu118; \
    fi

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash aiassist

# Set up application directory
WORKDIR /app
COPY --from=builder /root/.local /home/aiassist/.local
COPY --chown=aiassist:aiassist . .

# Create necessary directories
RUN mkdir -p logs cache models vault && \
    chown -R aiassist:aiassist logs cache models vault

# Switch to non-root user
USER aiassist
ENV PATH=/home/aiassist/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  ai-assistant:
    build:
      context: .
      args:
        ENABLE_GPU: "true"
        MODEL_VARIANT: "medium"
    ports:
      - "8000:8000"
    environment:
      - BACKEND_URL=http://localhost:8000
      - GPU=true
      - LOG_LEVEL=INFO
    volumes:
      - ./vault:/app/vault:ro
      - ./models:/app/models
      - ./cache:/app/cache
      - ./logs:/app/logs
      - ./backend/config.yaml:/app/backend/config.yaml:ro
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # Optional: Monitoring stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  grafana-data:
```

### Cloud Deployment

#### AWS Deployment (EC2 + ECS)

**CloudFormation Template**:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Obsidian AI Assistant Infrastructure'

Parameters:
  InstanceType:
    Type: String
    Default: t3.large
    AllowedValues: [t3.medium, t3.large, t3.xlarge, m5.large, m5.xlarge]
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: AIAssistant-VPC

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: AIAssistant-PublicSubnet

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for AI Assistant
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8000
          ToPort: 8000
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyPairName
      SecurityGroupIds:
        - !Ref SecurityGroup
      SubnetId: !Ref PublicSubnet
      ImageId: ami-0c02fb55956c7d316  # Amazon Linux 2023
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y docker python3 python3-pip git
          systemctl start docker
          systemctl enable docker
          
          # Install Docker Compose
          curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
          chmod +x /usr/local/bin/docker-compose
          
          # Clone repository
          cd /home/ec2-user
          git clone https://github.com/UndiFineD/obsidian-AI-assistant.git
          cd obsidian-AI-assistant
          
          # Set up environment
          cp .env.example .env
          
          # Start services
          docker-compose up -d
      Tags:
        - Key: Name
          Value: AIAssistant-Server

Outputs:
  PublicIP:
    Description: Public IP of the AI Assistant server
    Value: !GetAtt EC2Instance.PublicIp
    Export:
      Name: AIAssistant-PublicIP
```

#### Kubernetes Deployment

**Deployment YAML**:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-assistant

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-assistant-config
  namespace: ai-assistant
data:
  config.yaml: |
    server:
      host: 0.0.0.0
      port: 8000
      workers: 4
    performance:
      gpu_acceleration: false
      max_concurrent_requests: 20
    security:
      allow_network: false
      rate_limiting:
        enabled: true
        requests_per_minute: 100

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ai-assistant-storage
  namespace: ai-assistant
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: gp2

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-assistant
  namespace: ai-assistant
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-assistant
  template:
    metadata:
      labels:
        app: ai-assistant
    spec:
      containers:
      - name: ai-assistant
        image: obsidian-ai-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: GPU
          value: "false"
        - name: LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: config
          mountPath: /app/backend/config.yaml
          subPath: config.yaml
        - name: storage
          mountPath: /app/cache
        - name: storage
          mountPath: /app/models
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /status
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
      volumes:
      - name: config
        configMap:
          name: ai-assistant-config
      - name: storage
        persistentVolumeClaim:
          claimName: ai-assistant-storage

---
apiVersion: v1
kind: Service
metadata:
  name: ai-assistant-service
  namespace: ai-assistant
spec:
  selector:
    app: ai-assistant
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-assistant-ingress
  namespace: ai-assistant
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - ai-assistant.yourdomain.com
    secretName: ai-assistant-tls
  rules:
  - host: ai-assistant.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-assistant-service
            port:
              number: 80
```

### Monitoring & Observability

#### Prometheus Metrics Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'ai-assistant'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'system-metrics'
    static_configs:
      - targets: ['localhost:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Application Metrics

```python
# backend/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import psutil

# Metrics definitions
request_count = Counter(
    'ai_assistant_requests_total',
    'Total number of requests',
    ['endpoint', 'method', 'status_code']
)

request_duration = Histogram(
    'ai_assistant_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint', 'method']
)

active_connections = Gauge(
    'ai_assistant_active_connections',
    'Number of active connections'
)

model_loading_time = Histogram(
    'ai_assistant_model_loading_seconds',
    'Model loading time in seconds',
    ['model_name']
)

cache_hit_rate = Gauge(
    'ai_assistant_cache_hit_rate',
    'Cache hit rate percentage'
)

system_memory_usage = Gauge(
    'ai_assistant_memory_usage_bytes',
    'Memory usage in bytes'
)

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.used)
        
        # GPU metrics if available
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated()
            gpu_memory_usage.set(gpu_memory)
    
    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record request metrics"""
        request_count.labels(
            endpoint=endpoint,
            method=method,
            status_code=status_code
        ).inc()
        
        request_duration.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)

# FastAPI metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    metrics_collector.record_request(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=duration
    )
    
    return response

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    metrics_collector.collect_system_metrics()
    return Response(generate_latest(), media_type="text/plain")
```

#### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Obsidian AI Assistant Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_assistant_requests_total[5m])",
            "legendFormat": "{{endpoint}} {{method}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(ai_assistant_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(ai_assistant_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "ai_assistant_memory_usage_bytes / 1024 / 1024 / 1024",
            "legendFormat": "Memory Usage (GB)"
          }
        ]
      },
      {
        "title": "Cache Performance",
        "type": "singlestat",
        "targets": [
          {
            "expr": "ai_assistant_cache_hit_rate",
            "legendFormat": "Cache Hit Rate %"
          }
        ]
      }
    ]
  }
}
```

### Backup & Recovery

#### Automated Backup System

```python
# operations/backup.py
import os
import shutil
import tarfile
import boto3
from datetime import datetime, timedelta
from pathlib import Path
import logging

class BackupManager:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path(config.get('backup_dir', 'backups'))
        self.retention_days = config.get('retention_days', 30)
        
        # AWS S3 configuration (optional)
        if config.get('s3_enabled'):
            self.s3_client = boto3.client('s3')
            self.s3_bucket = config['s3_bucket']
    
    def create_backup(self, backup_type: str = 'full') -> str:
        """Create system backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"ai_assistant_{backup_type}_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_filename
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                if backup_type in ['full', 'data']:
                    # Backup vault data
                    if Path('vault').exists():
                        tar.add('vault', arcname='vault')
                    
                    # Backup vector database
                    if Path('vector_db').exists():
                        tar.add('vector_db', arcname='vector_db')
                    
                    # Backup cache (embeddings only)
                    cache_embeddings = Path('cache/embeddings')
                    if cache_embeddings.exists():
                        tar.add(cache_embeddings, arcname='cache/embeddings')
                
                if backup_type in ['full', 'config']:
                    # Backup configuration
                    if Path('backend/config.yaml').exists():
                        tar.add('backend/config.yaml', arcname='config.yaml')
                    
                    if Path('.env').exists():
                        tar.add('.env', arcname='.env')
                
                if backup_type in ['full', 'logs']:
                    # Backup logs
                    if Path('logs').exists():
                        tar.add('logs', arcname='logs')
            
            self.logger.info(f"Backup created: {backup_path}")
            
            # Upload to S3 if configured
            if hasattr(self, 's3_client'):
                self.upload_to_s3(backup_path, backup_filename)
            
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise
    
    def restore_backup(self, backup_path: str, restore_type: str = 'full'):
        """Restore from backup"""
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        try:
            # Create restoration directory
            restore_dir = Path('restore_temp')
            restore_dir.mkdir(exist_ok=True)
            
            # Extract backup
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(restore_dir)
            
            # Restore components based on type
            if restore_type in ['full', 'data']:
                self._restore_data(restore_dir)
            
            if restore_type in ['full', 'config']:
                self._restore_config(restore_dir)
            
            if restore_type in ['full', 'logs']:
                self._restore_logs(restore_dir)
            
            # Cleanup
            shutil.rmtree(restore_dir)
            
            self.logger.info(f"Restoration completed from: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Restoration failed: {e}")
            raise
    
    def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for backup_file in self.backup_dir.glob('*.tar.gz'):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                self.logger.info(f"Removed old backup: {backup_file}")
    
    def _restore_data(self, restore_dir: Path):
        """Restore data components"""
        # Restore vault
        vault_backup = restore_dir / 'vault'
        if vault_backup.exists():
            if Path('vault').exists():
                shutil.rmtree('vault')
            shutil.copytree(vault_backup, 'vault')
        
        # Restore vector database
        vector_db_backup = restore_dir / 'vector_db'
        if vector_db_backup.exists():
            if Path('vector_db').exists():
                shutil.rmtree('vector_db')
            shutil.copytree(vector_db_backup, 'vector_db')
        
        # Restore embeddings cache
        embeddings_backup = restore_dir / 'cache' / 'embeddings'
        if embeddings_backup.exists():
            embeddings_dir = Path('cache/embeddings')
            embeddings_dir.mkdir(parents=True, exist_ok=True)
            if embeddings_dir.exists():
                shutil.rmtree(embeddings_dir)
            shutil.copytree(embeddings_backup, embeddings_dir)

# Backup scheduler
import schedule
import threading
import time

class BackupScheduler:
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.running = False
    
    def start_scheduler(self):
        """Start backup scheduler in background thread"""
        schedule.every().day.at("02:00").do(
            self.backup_manager.create_backup, 'full'
        )
        schedule.every(6).hours.do(
            self.backup_manager.create_backup, 'data'
        )
        schedule.every().week.do(
            self.backup_manager.cleanup_old_backups
        )
        
        self.running = True
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
    
    def _run_scheduler(self):
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
```

### Troubleshooting Guide

#### Common Issues & Solutions

##### Issue: Model Loading Failures

```bash
# Symptoms
Error: "Failed to load model: llama-7b.gguf"

# Diagnosis
python -m backend.modelmanager verify --model llama-7b.gguf

# Solutions
1. Check model file exists and has correct permissions:
   ls -la models/llama-7b.gguf

2. Verify model file integrity:
   python -m backend.modelmanager checksum --model llama-7b.gguf

3. Re-download model:
   python -m backend.modelmanager download --model llama-7b-chat --force

4. Check available disk space:
   df -h models/

5. Verify memory requirements:
   python -c "import psutil; print(f'Available RAM: {psutil.virtual_memory().available / 1e9:.1f}GB')"
```

##### Issue: High Memory Usage

```bash
# Symptoms
System becomes unresponsive, OOM errors

# Diagnosis
python -m backend.diagnostics memory-profile

# Solutions
1. Reduce model size in config:
   MODEL_BACKEND=llama_cpp
   MODEL_PATH=models/llama-7b-q4.gguf  # Quantized version

2. Lower concurrent request limits:
   MAX_CONCURRENT_AI_REQUESTS=1

3. Enable memory optimization:
   ENABLE_MEMORY_OPTIMIZATION=true

4. Clear caches:
   python -m backend.cache clear --all
```

##### Issue: Slow Response Times

```bash
# Symptoms
API responses taking > 30 seconds

# Diagnosis
python -m backend.diagnostics performance-profile --duration 300

# Solutions
1. Enable GPU acceleration:
   GPU=true
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

2. Optimize chunk size:
   CHUNK_SIZE=512  # Smaller chunks for faster processing

3. Enable caching:
   ENABLE_RESPONSE_CACHE=true
   CACHE_TTL=3600

4. Use faster model:
   MODEL_PATH=models/llama-7b-q4-fast.gguf
```

#### Diagnostic Tools

```python
# backend/diagnostics.py
import subprocess
import psutil
import torch
from pathlib import Path
import json

class SystemDiagnostics:
    @staticmethod
    def system_health_check() -> dict:
        """Comprehensive system health check"""
        return {
            'cpu': {
                'cores': psutil.cpu_count(),
                'usage_percent': psutil.cpu_percent(interval=1),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            'memory': {
                'total_gb': psutil.virtual_memory().total / 1e9,
                'available_gb': psutil.virtual_memory().available / 1e9,
                'usage_percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total_gb': psutil.disk_usage('.').total / 1e9,
                'free_gb': psutil.disk_usage('.').free / 1e9,
                'usage_percent': (psutil.disk_usage('.').used / psutil.disk_usage('.').total) * 100
            },
            'gpu': {
                'available': torch.cuda.is_available(),
                'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'memory_gb': torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0
            },
            'network': {
                'connections': len(psutil.net_connections())
            }
        }
    
    @staticmethod
    def validate_installation() -> dict:
        """Validate installation integrity"""
        checks = {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'required_files': {},
            'models': {},
            'permissions': {}
        }
        
        # Check required files
        required_files = [
            'backend/backend.py',
            'backend/config.yaml',
            'requirements.txt'
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            checks['required_files'][file_path] = {
                'exists': path.exists(),
                'readable': path.is_file() and os.access(path, os.R_OK) if path.exists() else False,
                'size_mb': path.stat().st_size / 1e6 if path.exists() else 0
            }
        
        # Check models
        models_dir = Path('models')
        if models_dir.exists():
            for model_file in models_dir.glob('*.gguf'):
                checks['models'][model_file.name] = {
                    'size_mb': model_file.stat().st_size / 1e6,
                    'readable': os.access(model_file, os.R_OK)
                }
        
        return checks

# Command-line diagnostic tool
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Assistant Diagnostics')
    parser.add_argument('command', choices=['health', 'validate', 'memory-profile', 'performance-profile'])
    parser.add_argument('--duration', type=int, default=60, help='Profile duration in seconds')
    
    args = parser.parse_args()
    
    if args.command == 'health':
        result = SystemDiagnostics.system_health_check()
        print(json.dumps(result, indent=2))
    
    elif args.command == 'validate':
        result = SystemDiagnostics.validate_installation()
        print(json.dumps(result, indent=2))
```

---

## 🔄 Development Workflow

### Code Standards

- **Indentation**: 4 spaces (no tabs)
- **Type Hints**: Required for public APIs
- **Docstrings**: All public functions and classes
- **Error Handling**: Comprehensive exception management

### Git Workflow

- **Branch Protection**: Main branch requires PR review
- **CI/CD**: Automated testing on all PRs
- **Coverage Gates**: Minimum 70% coverage required
- **Code Quality**: Linting and formatting checks

---

## 📋 Plugin Integration Specifications

### Architecture Overview

The Obsidian AI Assistant plugin follows a modular, event-driven architecture that integrates seamlessly with the Obsidian ecosystem. The plugin implements a clean separation between UI components, business logic, and backend communication.

#### Core Architecture Principles

- **Separation of Concerns**: UI, business logic, and data access layers are distinct
- **Event-Driven Communication**: Components communicate through Obsidian's event system
- **Asynchronous Operations**: All backend communications are non-blocking
- **Error Boundary Management**: Graceful degradation and user feedback for all failures
- **Configuration Flexibility**: Runtime configuration without plugin reload

### Plugin Manifest Configuration

```json
{
    "id": "obsidian-ai-assistant",
    "name": "AI Assistant",
    "version": "1.0.0",
    "minAppVersion": "0.15.0",
    "description": "AI assistant for Obsidian with local backend integration",
    "author": "Plugin Author",
    "authorUrl": "https://github.com/author/repo",
    "isDesktopOnly": false,
    "main": "main.js"
}
```

### TypeScript Interfaces and Types

#### Plugin Configuration Interface

```typescript
interface PluginConfig {
    backendUrl: string;          // Backend server URL (e.g., "http://localhost:8000")
    features: {
        enableVoice: boolean;    // Enable voice input functionality
        allowNetwork: boolean;   // Allow outbound network requests
        taskQueueEnabled: boolean; // Enable background task processing
        analyticsEnabled: boolean; // Enable usage analytics collection
    };
    ui: {
        ribbonIcon: boolean;     // Show ribbon icon
        statusBar: boolean;      // Show status in status bar
        commandPalette: boolean; // Register command palette entries
    };
    performance: {
        maxConcurrentTasks: number;    // Maximum parallel backend requests
        requestTimeout: number;        // Request timeout in milliseconds
        cacheEnabled: boolean;         // Enable response caching
        cacheTTL: number;             // Cache time-to-live in seconds
    };
}
```

#### Backend Communication Types

```typescript
interface BackendRequest {
    endpoint: string;
    method: 'GET' | 'POST' | 'PUT' | 'DELETE';
    data?: Record<string, any>;
    headers?: Record<string, string>;
}

interface BackendResponse<T = any> {
    success: boolean;
    data?: T;
    error?: {
        code: string;
        message: string;
        details?: Record<string, any>;
    };
    metadata?: {
        timestamp: string;
        requestId: string;
        processingTime: number;
    };
}

interface Task {
    id: string;
    type: 'ask' | 'format' | 'link' | 'analyze';
    priority: number;
    content: string;
    notePath?: string;
    metadata?: Record<string, any>;
    created: Date;
    status: 'pending' | 'processing' | 'completed' | 'failed';
}
```

### Core Plugin Class Architecture

#### Main Plugin Class

```typescript
class ObsidianAIAssistant extends Plugin {
    settings: PluginConfig;
    taskQueue: TaskQueue;
    voiceRecorder: VoiceRecorder;
    backendClient: BackendClient;
    
    // Lifecycle Methods
    async onload(): Promise<void>;
    onunload(): void;
    
    // Settings Management
    async loadSettings(): Promise<void>;
    async saveSettings(): Promise<void>;
    
    // UI Registration
    private registerUI(): void;
    private registerCommands(): void;
    private registerViews(): void;
    
    // Event Handlers
    private setupEventHandlers(): void;
    private onBackendStatusChange(status: BackendStatus): void;
    private onTaskCompleted(task: Task): void;
}
```

#### Plugin Lifecycle Management

```typescript
// Plugin initialization sequence
async onload() {
    // 1. Load user settings
    await this.loadSettings();
    
    // 2. Initialize backend client
    this.backendClient = new BackendClient(this.settings.backendUrl);
    
    // 3. Initialize task queue
    this.taskQueue = new TaskQueue(this.backendClient, this.app);
    
    // 4. Initialize voice recorder (if enabled)
    if (this.settings.features.enableVoice) {
        this.voiceRecorder = new VoiceRecorder();
    }
    
    // 5. Register UI components
    this.registerUI();
    
    // 6. Register commands
    this.registerCommands();
    
    // 7. Setup event handlers
    this.setupEventHandlers();
    
    // 8. Check backend connectivity
    await this.validateBackendConnection();
}
```

### UI Component Specifications

#### Modal Components

```typescript
class AIAssistantModal extends Modal {
    constructor(app: App, plugin: ObsidianAIAssistant);
    
    // Modal lifecycle
    onOpen(): void;
    onClose(): void;
    
    // UI rendering
    private renderHeader(): void;
    private renderInputArea(): void;
    private renderActionButtons(): void;
    private renderStatusIndicator(): void;
    
    // Event handlers
    private onSubmit(query: string): Promise<void>;
    private onVoiceInput(): Promise<void>;
    private onClear(): void;
}

class TaskQueueModal extends Modal {
    // Task queue visualization and management
    private renderQueueList(): void;
    private renderTaskItem(task: Task): HTMLElement;
    private renderQueueControls(): void;
}
```

#### View Components

```typescript
class TaskQueueView extends ItemView {
    getViewType(): string { return VIEW_TYPE_TASK_QUEUE; }
    getDisplayText(): string { return "AI Task Queue"; }
    getIcon(): string { return "list-ordered"; }
    
    // View lifecycle
    async onOpen(): Promise<void>;
    onClose(): Promise<void>;
    
    // Data management
    private refreshView(): void;
    private updateTaskStatus(taskId: string, status: TaskStatus): void;
}

class AnalyticsPane extends ItemView {
    // Analytics and usage statistics display
    private renderUsageCharts(): void;
    private renderPerformanceMetrics(): void;
    private renderErrorSummary(): void;
}
```

### Backend Integration Layer

#### HTTP Client Management

```typescript
class BackendClient {
    private baseURL: string;
    private timeout: number;
    private retryConfig: RetryConfig;
    
    constructor(baseURL: string, config?: BackendClientConfig);
    
    // Core HTTP methods
    async get<T>(endpoint: string, params?: Record<string, any>): Promise<BackendResponse<T>>;
    async post<T>(endpoint: string, data?: any): Promise<BackendResponse<T>>;
    async put<T>(endpoint: string, data?: any): Promise<BackendResponse<T>>;
    async delete<T>(endpoint: string): Promise<BackendResponse<T>>;
    
    // Specialized methods
    async checkStatus(): Promise<BackendStatus>;
    async uploadFile(file: File, endpoint: string): Promise<BackendResponse>;
    async streamRequest(endpoint: string, data: any): AsyncGenerator<BackendResponse>;
    
    // Error handling
    private handleError(error: Error): BackendResponse;
    private retry<T>(operation: () => Promise<T>, attempts: number): Promise<T>;
}
```

#### API Endpoint Mappings

```typescript
const API_ENDPOINTS = {
    // Core functionality
    ASK_QUESTION: '/api/ask',
    VOICE_TRANSCRIBE: '/api/voice_transcribe',
    FORMAT_NOTE: '/api/format_note',
    LINK_NOTES: '/api/link_notes',
    
    // Configuration
    GET_CONFIG: '/api/config',
    UPDATE_CONFIG: '/api/config',
    RELOAD_CONFIG: '/api/config/reload',
    
    // System
    STATUS: '/status',
    RESTART: '/restart',
    HEALTH: '/health',
    
    // Analytics
    GET_STATS: '/api/stats',
    GET_USAGE: '/api/usage'
} as const;
```

### Event System Integration

#### Obsidian Event Handling

```typescript
interface PluginEvents {
    'ai-response-received': (response: AIResponse) => void;
    'task-queue-updated': (queue: Task[]) => void;
    'backend-status-changed': (status: BackendStatus) => void;
    'voice-transcription-complete': (text: string) => void;
    'settings-changed': (settings: PluginConfig) => void;
}

class EventManager {
    private app: App;
    private events: EventRef[];
    
    // Event registration
    registerWorkspaceEvents(): void;
    registerVaultEvents(): void;
    registerCustomEvents(): void;
    
    // Event handlers
    private onFileModified(file: TFile): void;
    private onActiveLeafChanged(): void;
    private onLayoutReady(): void;
    
    // Cleanup
    cleanup(): void;
}
```

### Task Queue Management

#### Task Processing System

```typescript
class TaskQueue {
    private queue: Task[];
    private processing: Map<string, Promise<void>>;
    private maxConcurrent: number;
    private isRunning: boolean;
    
    // Queue operations
    addTask(task: Omit<Task, 'id' | 'created' | 'status'>): string;
    removeTask(taskId: string): boolean;
    prioritizeTask(taskId: string): void;
    
    // Queue execution
    async startQueue(): Promise<void>;
    pauseQueue(): void;
    clearQueue(): void;
    
    // Queue monitoring
    getQueueStatus(): QueueStatus;
    getTaskHistory(): Task[];
    
    // Task processing
    private async processTask(task: Task): Promise<void>;
    private async executeTask(task: Task): Promise<any>;
    private handleTaskError(task: Task, error: Error): void;
}
```

### Voice Integration System

#### Voice Recording and Processing

```typescript
class VoiceRecorder {
    private mediaRecorder: MediaRecorder | null;
    private audioChunks: Blob[];
    private isRecording: boolean;
    
    // Recording control
    async startRecording(): Promise<void>;
    async stopRecording(): Promise<Blob>;
    async pauseRecording(): void;
    async resumeRecording(): void;
    
    // Audio processing
    private configureMediaRecorder(stream: MediaStream): void;
    private processAudioChunks(): Blob;
    
    // Backend communication
    async transcribeAudio(audioBlob: Blob, mode?: TranscriptionMode): Promise<string>;
    
    // Error handling
    private handleRecordingError(error: Error): void;
}
```

### Plugin Configuration Management

#### Settings Tab Implementation

```typescript
class AIAssistantSettingTab extends PluginSettingTab {
    plugin: ObsidianAIAssistant;
    
    display(): void {
        const { containerEl } = this;
        containerEl.empty();
        
        // Render setting sections
        this.renderConnectionSettings();
        this.renderFeatureSettings();
        this.renderPerformanceSettings();
        this.renderAdvancedSettings();
    }
    
    private renderConnectionSettings(): void;
    private renderFeatureSettings(): void;
    private renderPerformanceSettings(): void;
    private renderAdvancedSettings(): void;
    
    // Setting change handlers
    private onBackendUrlChange(value: string): Promise<void>;
    private onFeatureToggle(feature: string, enabled: boolean): Promise<void>;
    private onPerformanceSettingChange(setting: string, value: any): Promise<void>;
}
```

### Error Handling and Recovery

#### Error Management Strategy

```typescript
interface ErrorHandler {
    // Error categorization
    categorizeError(error: Error): ErrorCategory;
    
    // User notification
    showUserError(error: ProcessedError): void;
    
    // Error recovery
    attemptRecovery(error: Error): Promise<boolean>;
    
    // Error logging
    logError(error: Error, context: ErrorContext): void;
}

enum ErrorCategory {
    NETWORK = 'network',
    AUTHENTICATION = 'authentication',
    VALIDATION = 'validation',
    PLUGIN = 'plugin',
    SYSTEM = 'system'
}

interface ProcessedError {
    category: ErrorCategory;
    severity: 'low' | 'medium' | 'high' | 'critical';
    userMessage: string;
    technicalDetails: string;
    recoveryOptions: RecoveryOption[];
}
```

### Performance Optimization

#### Response Caching Strategy

```typescript
class ResponseCache {
    private cache: Map<string, CacheEntry>;
    private ttl: number;
    
    // Cache operations
    set(key: string, value: any, customTTL?: number): void;
    get(key: string): any | null;
    has(key: string): boolean;
    delete(key: string): void;
    clear(): void;
    
    // Cache maintenance
    private cleanup(): void;
    private generateKey(request: BackendRequest): string;
}
```

#### Request Optimization

```typescript
class RequestOptimizer {
    // Request batching
    batchRequests(requests: BackendRequest[]): Promise<BackendResponse[]>;
    
    // Request deduplication
    deduplicateRequests(requests: BackendRequest[]): BackendRequest[];
    
    // Connection pooling
    private connectionPool: ConnectionPool;
    
    // Rate limiting
    private rateLimiter: RateLimiter;
}
```

### Plugin File Structure

```text
plugin/
├── main.js                 # Core plugin class and initialization
├── manifest.json           # Obsidian plugin metadata and requirements
├── styles.css             # UI styling and theme integration
├── config.template.json   # Configuration template for setup
├── 
├── components/            # UI Components
│   ├── modals/
│   │   ├── aiAssistantModal.js      # Main AI interaction modal
│   │   ├── taskQueueModal.js        # Task queue management modal
│   │   └── settingsModal.js         # Advanced settings modal
│   ├── views/
│   │   ├── taskQueueView.js         # Task queue sidebar view
│   │   ├── analyticsPane.js         # Usage analytics pane
│   │   └── statusBarItem.js         # Status bar integration
│   └── widgets/
│       ├── voiceButton.js           # Voice input widget
│       ├── progressBar.js           # Task progress indicator
│       └── errorBanner.js           # Error notification banner
├── 
├── core/                  # Core Business Logic
│   ├── taskQueue.js                 # Task management and processing
│   ├── backendClient.js             # Backend API communication
│   ├── eventManager.js              # Event system integration
│   ├── configManager.js             # Configuration management
│   └── errorHandler.js              # Error processing and recovery
├── 
├── integrations/          # External Integrations
│   ├── voice.js                     # Voice recording and processing
│   ├── voiceInput.js                # Voice input handling
│   ├── obsidianAPI.js               # Obsidian API wrappers
│   └── fileProcessor.js             # File content processing
├── 
├── utils/                 # Utility Functions
│   ├── cache.js                     # Response caching system
│   ├── validators.js                # Input validation utilities
│   ├── formatters.js                # Text and data formatters
│   └── constants.js                 # Plugin constants and enums
└── 
└── types/                 # TypeScript Definitions
    ├── plugin.d.ts                  # Plugin-specific types
    ├── backend.d.ts                 # Backend API types
    ├── obsidian.d.ts                # Extended Obsidian types
    └── events.d.ts                  # Event system types
```

### Integration Testing Strategy

#### Plugin Testing Framework

```typescript
class PluginTestSuite {
    // Test environment setup
    setupTestVault(): Promise<TestVault>;
    setupMockBackend(): MockBackendServer;
    
    // Integration tests
    testPluginLifecycle(): Promise<void>;
    testBackendCommunication(): Promise<void>;
    testUIInteractions(): Promise<void>;
    testEventHandling(): Promise<void>;
    
    // Performance tests
    testTaskQueuePerformance(): Promise<void>;
    testMemoryUsage(): Promise<void>;
    testResponseTimes(): Promise<void>;
    
    // Error scenario tests
    testNetworkFailures(): Promise<void>;
    testBackendErrors(): Promise<void>;
    testPluginRecovery(): Promise<void>;
}
```

---

## 🔍 Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **422**: Validation Error (Pydantic model validation)
- **500**: Internal Server Error
- **503**: Service Unavailable (model loading)

### Error Response Format

```json
{
    "error": "ValidationError",
    "message": "Field 'question' is required",
    "details": {
        "field": "question",
        "type": "missing",
        "input_value": null
    }
}
```

### Logging Strategy

- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format**: Structured JSON logging for production
- **Rotation**: Log file rotation and cleanup
- **Privacy**: No sensitive data in logs

---

## 📊 Monitoring & Analytics

### Health Metrics

- **Uptime**: Service availability tracking
- **Response Times**: Endpoint performance monitoring
- **Error Rates**: Failure rate tracking
- **Resource Usage**: CPU, memory, disk utilization

### Business Metrics

- **Query Volume**: Questions processed per day
- **Cache Hit Rate**: Caching efficiency
- **Model Usage**: Model selection patterns
- **Feature Adoption**: Plugin feature usage

---

## 🔄 Version History

### Version 1.0.0 (Current)

- ✅ Core FastAPI backend implementation
- ✅ Comprehensive configuration system
- ✅ 70%+ test coverage achievement
- ✅ PyTorch conflict resolution
- ✅ Offline-first architecture
- ✅ Plugin integration with Obsidian

### Planned Features

- 🚧 Enhanced model routing
- 🚧 Advanced caching strategies
- 🚧 Real-time collaboration features
- 🚧 Extended plugin capabilities

---

## 📞 Support & Maintenance

### Documentation

- **API Docs**: Auto-generated Swagger UI at `/docs`
- **ReDoc**: Alternative docs at `/redoc`
- **README**: Comprehensive setup guide
- **Constitution**: Project principles and standards

### Issue Tracking

- **Bug Reports**: GitHub Issues with templates
- **Feature Requests**: Community-driven roadmap
- **Security Issues**: Private reporting channel
- **Performance**: Benchmark tracking and optimization

---

© 2025 Obsidian AI Assistant - Offline-First AI for Enhanced Knowledge Management
