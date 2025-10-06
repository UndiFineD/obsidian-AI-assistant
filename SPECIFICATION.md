# 📋 Obsidian AI Assistant - Technical Specification

## **📌 Document Overview**
- **Version**: 1.0.0
- **Last Updated**: October 6, 2025
- **Author**: Keimpe de Jong
- **Project**: Obsidian AI Assistant
- **Repository**: obsidian-AI-assistant

---

## **🎯 Project Mission**
**Offline-first AI assistant for Obsidian with comprehensive backend services, semantic search, and voice input support.**

---

## **🏗️ System Architecture**

### **Core Components**
```
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

### **Module Structure**
```
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

## **🔧 API Specification**

### **Base Configuration**
- **Protocol**: HTTP/HTTPS
- **Default Host**: `127.0.0.1`
- **Default Port**: `8000`
- **Framework**: FastAPI
- **Base URL**: `http://127.0.0.1:8000`

### **CORS Configuration**
```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

---

## **📡 API Endpoints**

### **Health & Status Endpoints**

#### **GET /health**
**Purpose**: Comprehensive health check with system information

**Response Format**:
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
    "gpu": true
}
```

#### **GET /status**
**Purpose**: Lightweight status check for liveness monitoring

**Response Format**:
```json
{
    "status": "ok"
}
```

#### **GET /api/health**
**Purpose**: API-versioned health endpoint (alias for /health)

---

### **Configuration Management**

#### **GET /api/config**
**Purpose**: Retrieve current configuration

**Response Format**:
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
    "top_k": 10,
    "chunk_size": 2000,
    "chunk_overlap": 200,
    "similarity_threshold": 0.75,
    "continuous_mode": false,
    "vault_path": "test_vault"
}
```

#### **POST /api/config**
**Purpose**: Update configuration settings

**Request Format**:
```json
{
    "vault_path": "new_vault",
    "chunk_size": 1000,
    "gpu": false
}
```

**Response Format**:
```json
{
    "message": "Config updated",
    "updated_fields": ["vault_path", "chunk_size", "gpu"]
}
```

#### **POST /api/config/reload**
**Purpose**: Reload configuration from YAML file

**Response Format**:
```json
{
    "message": "Config reloaded"
}
```

---

### **AI Operations**

#### **POST /ask**
**Purpose**: Main AI question processing endpoint

**Request Model**: `AskRequest`
```json
{
    "question": "What is the capital of France?",
    "prefer_fast": true,
    "max_tokens": 256,
    "context_paths": ["optional/path1.md", "optional/path2.md"],
    "prompt": "optional system prompt",
    "model_name": "llama-7b"
}
```

**Response Format**:
```json
{
    "answer": "Paris is the capital of France.",
    "cached": false,
    "model_used": "llama-7b",
    "processing_time": 1.234,
    "context_used": ["path1.md", "path2.md"]
}
```

**Status Codes**:
- `200`: Success
- `422`: Validation error (missing question field)
- `500`: AI generation failure

#### **POST /api/ask**
**Purpose**: API-versioned ask endpoint (alias for /ask)

---

### **Document Management**

#### **POST /reindex**
**Purpose**: Reindex vault documents for semantic search

**Request Model**: `ReindexRequest`
```json
{
    "vault_path": "./vault"
}
```

**Response Format**:
```json
{
    "status": "success",
    "files_processed": 25,
    "chunks_indexed": 150,
    "processing_time": 5.67
}
```

#### **POST /api/reindex**
**Purpose**: API-versioned reindex endpoint

#### **POST /web**
**Purpose**: Index web content for semantic search

**Request Model**: `WebRequest`
```json
{
    "url": "https://example.com",
    "question": "What is this page about?"
}
```

**Response Format**:
```json
{
    "answer": "This page discusses...",
    "url_processed": "https://example.com",
    "content_indexed": true
}
```

#### **POST /api/web**
**Purpose**: API-versioned web indexing endpoint

---

### **Search Operations**

#### **POST /api/search**
**Purpose**: Semantic search across indexed documents

**Request Parameters**:
- `query` (string): Search query
- `top_k` (int, default=5): Number of results to return

**Response Format**:
```json
{
    "results": [
        {
            "content": "Relevant text snippet...",
            "score": 0.95,
            "source": "document1.md",
            "chunk_id": "chunk_123"
        },
        {
            "content": "Another relevant snippet...",
            "score": 0.87,
            "source": "document2.md", 
            "chunk_id": "chunk_456"
        }
    ]
}
```

#### **POST /api/scan_vault**
**Purpose**: Scan and index vault directory

**Request Parameters**:
- `vault_path` (string, default="vault"): Path to scan

**Response Format**:
```json
{
    "indexed_files": ["file1.md", "file2.md", "file3.pdf"],
    "total_files": 3,
    "processing_time": 2.34
}
```

---

### **Audio Processing**

#### **POST /transcribe**
**Purpose**: Convert audio to text using Vosk

**Request Model**: `TranscribeRequest`
```json
{
    "audio_data": "base64encodedaudiodata",
    "format": "webm",
    "language": "en"
}
```

**Response Format**:
```json
{
    "text": "Transcribed speech text",
    "confidence": 0.95,
    "processing_time": 0.123,
    "language": "en"
}
```

---

### **Utility Endpoints**

#### **POST /api/index_pdf**
**Purpose**: Index PDF file for search

**Request Parameters**:
- `pdf_path` (string): Path to PDF file

**Response Format**:
```json
{
    "chunks_indexed": 15,
    "file_processed": "document.pdf",
    "status": "success"
}
```

---

## **📊 Data Models**

### **Request Models**

#### **AskRequest**
```python
class AskRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    question: str                          # Required: User question
    prefer_fast: bool = True              # Prefer fast model over accuracy
    max_tokens: int = 256                 # Maximum response tokens
    context_paths: Optional[List[str]] = None    # Optional context files
    prompt: Optional[str] = None          # Optional system prompt
    model_name: Optional[str] = "llama-7b" # Model selection
```

#### **ReindexRequest**
```python
class ReindexRequest(BaseModel):
    vault_path: str = "./vault"           # Path to vault directory
```

#### **WebRequest**
```python
class WebRequest(BaseModel):
    url: str                              # Required: URL to process
    question: Optional[str] = None        # Optional question about content
```

#### **TranscribeRequest**
```python
class TranscribeRequest(BaseModel):
    audio_data: str                       # Required: Base64 encoded audio
    format: str = "webm"                  # Audio format
    language: str = "en"                  # Language code
```

---

## **⚙️ Configuration System**

### **Configuration Precedence**
1. **Environment Variables** (highest priority)
2. **backend/config.yaml** (medium priority)
3. **Code Defaults** (lowest priority)

### **Settings Model**
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

### **Environment Variables**
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

## **🧪 Testing Standards**

### **Coverage Requirements**
- **Target**: 70%+ overall coverage
- **Critical Modules**: 90%+ (settings, caching, security)
- **API Endpoints**: 65%+ coverage
- **Integration Tests**: End-to-end scenarios

### **Test Architecture**
```
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

### **PyTorch Conflict Resolution**
```python
# Module-level mocking strategy
@patch.dict(sys.modules, {
    'torch': Mock(),
    'transformers': Mock(),
    'sentence_transformers': Mock(),
})
```

### **Test Execution**
```bash
# Full test suite with coverage
pytest --cov=backend --cov-report=term-missing --cov-report=html

# Individual module tests
pytest tests/backend/test_backend_simple.py -v

# Coverage target validation
pytest --cov=backend --cov-fail-under=70
```

---

## **🔒 Security Specifications**

### **Data Protection**
- **Local Processing**: All data remains on local machine
- **Optional Encryption**: Fernet-based cache encryption
- **No External Calls**: Offline-first architecture
- **Secure Defaults**: Network access disabled by default

### **Authentication**
- **API Keys**: Optional model provider authentication
- **Token Management**: Secure environment variable handling
- **Session Security**: No session persistence by default

---

## **📈 Performance Standards**

### **Response Time Targets**
- **Health Endpoints**: < 100ms
- **Configuration**: < 200ms
- **Search Operations**: < 1000ms
- **AI Generation**: Variable (model-dependent)

### **Caching Strategy**
- **TTL-Based**: Configurable time-to-live
- **Multi-Level**: Embeddings, responses, file hashes
- **Automatic Cleanup**: Expired cache removal
- **Optional Encryption**: Secure cache storage

### **Resource Management**
- **GPU Detection**: Automatic CPU/GPU selection
- **Memory Optimization**: Efficient vector operations
- **Concurrent Processing**: Async/await patterns
- **Batch Operations**: Queue-based task management

---

## **🚀 Deployment Specifications**

### **System Requirements**
- **Python**: 3.10+
- **Memory**: 4GB+ recommended
- **Storage**: 2GB+ for models
- **OS**: Windows 10+, Ubuntu 20.04+, macOS 10.15+

### **Dependencies**
```python
# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# AI/ML Stack
torch>=2.0.0
sentence-transformers>=2.2.0
chromadb>=0.4.0
llama-cpp-python>=0.2.0
gpt4all>=2.0.0

# Audio Processing
vosk>=0.3.45

# Document Processing
pypdf2>=3.0.0
beautifulsoup4>=4.12.0

# Utilities
pydantic>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

### **Setup Commands**
```bash
# Windows
.\setup.ps1

# Linux/macOS
bash setup.sh
```

---

## **🔄 Development Workflow**

### **Code Standards**
- **Indentation**: 4 spaces (no tabs)
- **Type Hints**: Required for public APIs
- **Docstrings**: All public functions and classes
- **Error Handling**: Comprehensive exception management

### **Git Workflow**
- **Branch Protection**: Main branch requires PR review
- **CI/CD**: Automated testing on all PRs
- **Coverage Gates**: Minimum 70% coverage required
- **Code Quality**: Linting and formatting checks

---

## **📋 Plugin Specification**

### **Obsidian Plugin Interface**
```typescript
interface PluginConfig {
    backendUrl: string;          // Backend server URL
    features: {
        enableVoice: boolean;    // Enable voice input
        allowNetwork: boolean;   // Allow network requests
    }
}
```

### **UI Components**
- **Ribbon Icons**: Quick access to AI functions
- **Task Queue View**: Processing queue management
- **Analytics Pane**: Usage statistics and coverage
- **Voice Input Modal**: Speech-to-text interface

### **Plugin Files**
```
plugin/
├── main.ts                 # Core plugin class
├── manifest.json           # Obsidian plugin metadata
├── styles.css             # UI styling
├── config.template.json   # Configuration template
├── analyticsPane.ts       # Analytics dashboard
├── taskQueue.ts           # Task management logic
├── taskQueueView.ts       # Queue UI components
├── voice.ts               # Voice processing
└── voiceInput.ts          # Voice input handling
```

---

## **🔍 Error Handling**

### **HTTP Status Codes**
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **422**: Validation Error (Pydantic model validation)
- **500**: Internal Server Error
- **503**: Service Unavailable (model loading)

### **Error Response Format**
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

### **Logging Strategy**
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format**: Structured JSON logging for production
- **Rotation**: Log file rotation and cleanup
- **Privacy**: No sensitive data in logs

---

## **📊 Monitoring & Analytics**

### **Health Metrics**
- **Uptime**: Service availability tracking
- **Response Times**: Endpoint performance monitoring
- **Error Rates**: Failure rate tracking
- **Resource Usage**: CPU, memory, disk utilization

### **Business Metrics**
- **Query Volume**: Questions processed per day
- **Cache Hit Rate**: Caching efficiency
- **Model Usage**: Model selection patterns
- **Feature Adoption**: Plugin feature usage

---

## **🔄 Version History**

### **Version 1.0.0** (Current)
- ✅ Core FastAPI backend implementation
- ✅ Comprehensive configuration system
- ✅ 70%+ test coverage achievement
- ✅ PyTorch conflict resolution
- ✅ Offline-first architecture
- ✅ Plugin integration with Obsidian

### **Planned Features**
- 🚧 Enhanced model routing
- 🚧 Advanced caching strategies
- 🚧 Real-time collaboration features
- 🚧 Extended plugin capabilities

---

## **📞 Support & Maintenance**

### **Documentation**
- **API Docs**: Auto-generated Swagger UI at `/docs`
- **ReDoc**: Alternative docs at `/redoc`
- **README**: Comprehensive setup guide
- **Constitution**: Project principles and standards

### **Issue Tracking**
- **Bug Reports**: GitHub Issues with templates
- **Feature Requests**: Community-driven roadmap
- **Security Issues**: Private reporting channel
- **Performance**: Benchmark tracking and optimization

---

**© 2025 Obsidian AI Assistant - Offline-First AI for Enhanced Knowledge Management**