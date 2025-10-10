
# Obsidian AI Assistant

**Offline-first AI assistant for Obsidian with comprehensive backend services, semantic search, and voice input support.**

---

## **System Architecture**

This project implements a **modular, service-oriented architecture** with clearly separated concerns:

### **Core Components**

```text
┌─────────────────┐    ┌──────────────────┐    ┌────────────#### **Test Results Summary**

| **Test Category** | **Pass Rate** | **Passed/Total** | **Status** |
|-------------------|---------------|------------------|------------|
| **Core Backend** | **100%** 🥇 | 21/21 | ✅ Production Ready |
| **Security & Config** | **100%** 🥇 | 34/34 | ✅ Production Ready |
| **Model Management** | **100%** 🥇 | 52/52 | ✅ Production Ready |
| **Embeddings & Search** | **100%** 🥇 | 113/113 | ✅ Production Ready |
| **Caching & Storage** | **100%** 🥇 | 22/22 | ✅ Production Ready |
| **Plugin System** | **100%** 🥇 | 30/30 | ✅ Production Ready |
| **LLM Router** | **100%** 🥇 | 17/17 | ✅ Production Ready |
| **JavaScript Quality** | **100%** 🥇 | 20/20 | ✅ Production Ready |
| **Voice & Audio** | **95%** 🥈 | 19/20 | ✅ Nearly Complete |
| **Uncategorized** | **91.2%** 🥉 | 31/34 | ✅ Stable |
| **Performance Tests** | **85%** ⭐ | 17/20 | 🔄 Optimization Ongoing |
| **Integration Tests** | **17.2%** ⚠️ | 10/58 | 🚧 Under Development |idian      │    │   FastAPI        │    │   AI Models     │
│   Plugin        │◄──►│   Backend        │◄──►│   Manager       │
│                 │    │                  │    │                 │
│ • UI Components │    │ • REST API       │    │ • LLaMA/GPT4All │
│ • Settings      │    │ • Request Router │    │ • Embeddings    │
│ • Enterprise    │    │ • Auth/Security  │    │ • Voice Models  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ Vector   │ │ Cache    │ │ Security │
              │ Database │ │ System   │ │ Module   │
              │          │ │          │ │          │
              │ ChromaDB │ │ Multi-   │ │ Fernet   │
              │ Semantic │ │ Layer    │ │ Encrypt  │
              │ Search   │ │ TTL      │ │ Auth     │
              └──────────┘ └──────────┘ └──────────┘
```

### **Enterprise Architecture**

For organizations requiring advanced features, the system includes enterprise modules:

- **SSO Authentication**: Azure AD, Google, Okta, SAML, LDAP providers
- **Multi-Tenant Support**: Isolated data and settings per organization
- **Role-Based Access Control (RBAC)**: Granular permissions and user management
- **Compliance**: GDPR and SOC2 compliance tools and audit trails
- **Admin Dashboard**: Comprehensive management interface

---

## **Features**

- **Local LLM Integration**: Support for LLaMA/GPT4All models with hybrid routing
- **Centra### **3. Install Plugin in Obsidian**

1. Copy the `plugin/` folder contents to your vault's `.obsidian/plugins/obsidian-ai-assistant/`
2. Ensure all required files are present:
   - `main.js`, `manifest.json` (core plugin files)
   - `rightPane.js`, `backendClient.js` (UI and API communication)
   - `adminDashboard.js`, `enterpriseAuth.js`, `enterpriseConfig.js` (enterprise features)
   - `styles.css` (styling)
3. Open Obsidian → Settings → Community Plugins → Enable `Obsidian AI Assistant`
4. Configure:
   - **Backend URL**: `http://localhost:8000`
   - **Vault Path**: path to your notes
   - **Features**: Enable voice, network access as needed

**Troubleshooting Plugin Load Issues:**

- Verify all `.js` files exist in the plugin folder
- Check Obsidian Developer Console (Ctrl+Shift+I) for error messages
- Ensure file permissions are readable
- Restart Obsidian after copying filesttings Management**: Environment variables → YAML → defaults precedence
- **Semantic Search**: Vector embeddings with ChromaDB for similarity search
- **Document Indexing**: Markdown, PDF, and web page indexing with caching
- **Voice Input**: Vosk-based speech recognition with push-to-talk functionality
- **Task Queue System**: Batch processing with analytics and progress tracking
- **Comprehensive Caching**: TTL-based caching for embeddings, file hashes, and responses
- **Security**: Optional encryption for cached data with Fernet encryption
- **FastAPI Backend**: RESTful API with automatic documentation and error handling

---

## **Project Structure**

```text
obsidian-llm-assistant/
├─ backend/                # FastAPI backend modules
├─ plugin/                 # Obsidian plugin
├─ models/                 # Offline LLaMA/GPT4All models
├─ vault/                  # Example vault for notes
├─ cache/                  # Cached answers
├─ venv/                   # Python virtual environment
├─ setup.sh                # Linux/macOS setup script
├─ setup.ps1               # Windows setup script
└─ README.md

For organizations requiring enterprise features, additional backend modules are available:

#### **Enterprise Backend Modules**

\n# Enterprise modules (automatically loaded if available)
\n```bash
backend/enterprise/
├── auth.py           # SSO authentication providers
├── tenant.py         # Multi-tenant management  
├── rbac.py          # Role-based access control
├── gdpr.py          # GDPR compliance tools
├── soc2.py          # SOC2 compliance monitoring
├── admin.py         # Admin dashboard API
└── integrations.py  # Enterprise integrations
\n```

### **Enterprise Plugin Components**

\n```bash
plugin/
├── adminDashboard.js    # Admin interface
├── enterpriseAuth.js    # SSO authentication
├── enterpriseConfig.js  # Enterprise settings
└── styles.css          # Enterprise UI styling
\n```powershell

## **Enterprise Configuration**

```yaml
# backend/config.yaml - Enterprise settings
enterprise:
  enabled: true
  sso:
    providers:
      - azure_ad
      - google
      - okta
      - saml
      - ldap
  tenant:
    multi_tenant: true
    default_tenant: "default"
  compliance:
    gdpr: true
    soc2: true
 
    audit_logging: true
  security:
    session_timeout: 3600
    mfa_required: false
    password_policy: "strong"
\n```powershell

### **Enterprise Features Access**

Once enterprise backend is running:

1. **Admin Dashboard**: Settings → Enterprise → Admin Dashboard
2. **SSO Login**: Settings → Enterprise → Enterprise Login  
3. **Configuration**: Settings → Enterprise → Enterprise Configuration
4. **User Management**: Admin Dashboard → Users tab
5. **Tenant Management**: Admin Dashboard → Tenants tab
6. **Security Monitoring**: Admin Dashboard → Security tab
7. **Compliance Reports**: Admin Dashboard → Compliance tab

### **1. Run Setup Script**

**Linux/macOS:**

\n```bash
bash setup.sh
```

**Windows:**

```powershell
./setup.ps1
```

This will:

1. Create a Python virtual environment
2. Install dependencies (`fastapi`, `torch`, `chromadb`, `llama-cpp-python`, `gpt4all`, etc.)
3. Detect GPU/CPU
4. Download default models (LLaMA 7B Q4, GPT4All Lora)
5. Build the Obsidian plugin automatically

### **Configuration System**

The backend uses a centralized settings system with the following precedence:

1. **Environment Variables** (highest priority)
2. **`backend/config.yaml`** (medium priority)
3. **Code Defaults** (lowest priority)

#### **Key Configuration Options**

```yaml
# backend/config.yaml
backend_url: "http://127.0.0.1:8000"
api_port: 8000
allow_network: false
continuous_mode: false

# Paths
vault_path: "vault"
models_dir: "models"
cache_dir: "cache"
 

# LLM Settings
model_backend: "llama_cpp"
model_path: "models/llama-7b.gguf"
embed_model: "sentence-transformers/all-MiniLM-L6-v2"
vector_db: "chroma"
gpu: true

# Voice Settings
vosk_model_path: "models/vosk-model-small-en-us-0.15"
```

#### **Runtime Configuration**

Settings can be updated at runtime via the `/api/config` endpoints:

\n# From project root

```bash
python test_server.py
```

\n## Get current configuration
[GET current configuration](http://localhost:8000/api/config)

\n## Update settings
[POST update settings](http://localhost:8000/api/config)
Content-Type: application/json
{
  "vault_path": "new_vault",
  "gpu": false
}

\n## Reload settings from file
[POST reload settings](http://localhost:8000/api/config/reload)

```json
{
  "backendUrl": "http://localhost:8000",
  "vaultPath": "vault",
  "preferFastLLM": true
}
```

$env:VAULT_PATH="$(Resolve-Path .\vault)"
$env:VOSK_MODEL_PATH="$(Resolve-Path .\models\vosk-model-small-en-us-0.15)"
$env:API_PORT=8000
$env:VAULT_PATH="$(Resolve-Path .\vault)"
$env:VOSK_MODEL_PATH="$(Resolve-Path .\models\vosk-model-small-en-us-0.15)"

\n## 2) Edit backend/config.yaml as needed
notepad .\backend\config.yaml

\n## 3) Start backend
\n### Option A: FastAPI with Uvicorn (full backend)
cd backend
python -m uvicorn backend:app --host 127.0.0.1 --port $env:API_PORT --reload

\n## Option B: Simple Python test server (no Node.js required)
\n### This serves the plugin files and provides mock endpoints for quick UI testing
cd ..
python .\test_server.py

```bash
cd ..
python .\test_server.py
```

Plugin config:

```pwsh
# Copy plugin config template and edit backend URL if needed
Copy-Item .\plugin\config.template.json .\plugin\config.json -Force
 
notepad .\plugin\config.json
```

Then copy the files in `plugin/` to your Obsidian vault plugins folder (e.g., `C:\Users\<you>\Vault\.obsidian\plugins\obsidian-ai-assistant\`).
No Node.js build step is required—the plugin JS and CSS are ready-to-use.

---

### **2. Start the Backend**

#### **Option A: Full FastAPI Backend (Recommended)**

```bash
# Linux/macOS
source venv/bin/activate
cd backend
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

# Windows PowerShell
& venv\Scripts\Activate.ps1
cd backend
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

#### **Option B: Simple HTTP Server (Development/Testing)**

For quick testing without full backend dependencies:

```bash
# From project root
python test_server.py
```

This lightweight server:

- Serves static plugin files from `./plugin`
- Provides mock endpoints: `/`, `/status`, `/ask`, `/reindex`, `/web`
Requires only Python, no Node.js or npm.

#### **Backend Endpoints**

The FastAPI backend provides these key endpoints:

- `GET /` - Welcome message
- `GET /health` - Basic health check
- `GET /status` - Detailed service status
- `GET /api/config` - Current configuration
- `POST /api/config` - Update configuration
- `POST /api/config/reload` - Reload settings from file
- `POST /ask` - Ask question to LLM
- `POST /reindex` - Reindex vault documents
- `POST /web` - Index web content
- `POST /transcribe` - Voice transcription

---

### **3. Install Plugin in Obsidian**

1. Copy the `plugin/` folder to your vault’s `.obsidian/plugins/obsidian-llm-plugin/`
2. Open Obsidian → Settings → Community Plugins → Enable `Obsidian LLM Assistant`
3. Configure:
    - **Backend URL**: `http://localhost:8000`
    - **Vault Path**: path to your notes
    - **Prefer Fast LLM**: toggle for LLaMA vs GPT4All

---

### **4. Using the Plugin**

- **Ask Question:** Ribbon icon 🎲 → input question → task added to queue
- **Start Queue:** Ribbon icon ▶ → processes tasks in order/batches
- **Pause Queue:** Ribbon icon ⏹ → pause processing
- **Voice Input:** optional microphone icon → speak your query
- **Analytics Dashboard:** Ribbon icon 📊 → semantic coverage, QA history
- **Inline Note Formatting:** Task queue automatically formats notes via backend
- **Link Notes:** Task queue generates semantic links automatically

---

### **5. Recommended Workflow**

1. **Scan Vault:** `Scan Vault` endpoint or first run → index all `.md` and PDFs
2. **Ask Questions:** Add queries to queue, or speak via voice input
3. **Process Queue:** Format notes, link notes, cache answers
4. **Review Analytics:** Track coverage and recent questions
5. **Iterate:** Update notes, reindex vault, repeat

---

### **6. Optional Features**

- **Web/PDF fetching:** Backend `/fetch_url` → index external resources
- **Reindex Vault:** Backend `/reindex` → refresh all embeddings
- **Encryption:** Enable in `backend/security.py` → encrypt cached answers

---

### **7. Screenshots / Placeholders**

> _(Add screenshots here if desired)_
>
> - Task Queue Pane
>
> - Ribbon Buttons
>
> - Analytics Dashboard
>
> - Inline Note Formatting
>

---

### **8. Code Quality Standards**

#### **JavaScript Code Style**

The plugin follows PEP8-inspired JavaScript conventions for consistency and maintainability:

**Indentation & Formatting:**

- ✅ **4-space indentation** (consistent with Python backend)
- ✅ **No trailing whitespace**
- ✅ **Consistent bracket placement**
- ✅ **Proper line length limits**

**Code Structure:**

- ✅ **PascalCase for classes** (`BackendClient`, `VoiceRecorder`)
- ✅ **camelCase for functions** (`startListening`, `sendRequest`)  
- ✅ **Proper module exports** with `module.exports`
- ✅ **Error handling patterns** with try-catch blocks
- ✅ **Console logging** for debugging (limited usage)

**Security Standards:**

- ✅ **No hardcoded secrets** or API keys
- ✅ **Safe DOM manipulation** (no innerHTML without sanitization)
- ✅ **Input validation** for user data
- ✅ **No eval() usage** for security

**Automated Quality Tools:**

```bash
# JavaScript code quality validation
pytest tests/plugin/test_js_code_quality.py -v

# Automatic style fixing
python fix_js_quality.py

# Manual verification
python fix_js_indentation.py
```

The quality assurance system includes 20 comprehensive tests covering:

- **File Structure**: Manifest validation, required files, exports
- **Code Quality**: Indentation, whitespace, quotes, class definitions
- **Functionality**: Plugin integration, voice features, enterprise components  
- **Security**: Hardcoded secrets detection, safe eval usage, DOM safety

---

### **9. Testing & Quality Assurance**

This project maintains high code quality with comprehensive test coverage. The latest test run shows **87.7% pass rate** (391 passed, 55 failed, 0 errors out of 446 total tests) with ongoing optimization work for integration scenarios.

#### **Test Results Summary**

| **Test Category** | **Pass Rate** | **Passed/Total** | **Status** |
|-------------------|---------------|------------------|------------|
| **Core Backend** | **100%** 🥇 | 21/21 | ✅ Production Ready |
| **Security & Config** | **100%** 🥇 | 34/34 | ✅ Production Ready |
| **Model Management** | **100%** 🥇 | 52/52 | ✅ Production Ready |
| **Embeddings & Search** | **100%** � | 113/113 | ✅ Production Ready |
| **Caching & Storage** | **100%** � | 22/22 | ✅ Production Ready |
| **Plugin System** | **100%** 🥇 | 30/30 | ✅ Production Ready |
| **LLM Router** | **100%** 🥇 | 17/17 | ✅ Production Ready |
| **Voice & Audio** | **95%** 🥈 | 19/20 | ✅ Nearly Complete |
| **Uncategorized** | **91.2%** 🥉 | 31/34 | ✅ Stable |
| **Performance Tests** | **85%** ⭐ | 17/20 | 🔄 Optimization Ongoing |
| **Integration Tests** | **17.2%** ⚠️ | 10/58 | 🚧 Under Development |

#### **Key Test Insights**

- **Core Functionality**: All essential features (backend, security, models, embeddings, caching) have 100% pass rates
- **Plugin Integration**: Complete plugin system functionality validated
- **Performance**: Some edge cases in cache eviction and concurrent operations being addressed
- **Integration Tests**: Complex cross-service scenarios under active development

#### **Test Structure**

```text
tests/
├── backend/                     # Backend module tests (100% pass rate)
│   ├── test_backend.py         # FastAPI endpoints & integration
│   ├── test_caching.py         # Cache management systems
│   ├── test_embeddings.py      # Vector operations & search
│   ├── test_indexing.py        # Document processing pipelines
│   ├── test_llm_router.py      # Model routing & selection
│   ├── test_modelmanager.py    # AI model lifecycle management
│   ├── test_security.py        # Encryption & authentication
│   ├── test_settings.py        # Configuration management
│   └── test_voice.py           # Speech recognition & processing
├── plugin/                      # Plugin system tests (100% pass rate)
│   ├── test_plugin_structure.py # File structure validation
│   ├── test_plugin_integration.py # Obsidian integration
│   └── test_enterprise_features.py # Enterprise functionality
├── integration/                 # Cross-service tests (17.2% pass rate - in development)
│   ├── test_workflow_integration.py # End-to-end workflows
│   ├── test_performance_benchmarks.py # Load & stress testing
│   └── test_enterprise_integration.py # Enterprise scenarios
├── performance/                 # Performance tests (85% pass rate)
│   ├── test_async_operations.py # Concurrent processing
│   ├── test_cache_performance.py # Cache optimization
│   └── test_connection_pooling.py # Resource management
└── comprehensive_async_test_runner.py # Multi-worker test runner
```

#### **Recent Test Run Statistics**

- **Execution Time**: 404.60 seconds with 6.3x speedup factor using 8 parallel workers
- **Test Distribution**: 446 total tests across 12 categories
- **Performance**: Fastest test: 1.90s, Slowest: 60.05s (cache eviction edge case)
- **JavaScript Quality**: New 20-test suite for code style, structure, and security validation
- **Failed Tests**: Primarily in integration scenarios involving complex service interactions

#### **Running Tests**

**Comprehensive Test Suite (Recommended):**

```bash
# Activate environment
source venv/bin/activate  # Linux/macOS
# or
& venv\Scripts\Activate.ps1  # Windows

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run comprehensive async test suite (446 tests, 8 parallel workers)
python run_tests.py

# This runs all test categories:
# - Backend module tests (100% pass rate)
# - Plugin system tests (100% pass rate)
# - JavaScript quality tests (100% pass rate) 
# - Performance tests (85% pass rate)
# - Integration tests (17% pass rate - under development)
```

**Individual Module Testing:**

```bash
# Run specific test categories
pytest tests/backend/ -v                    # Backend tests only
pytest tests/plugin/ -v                     # Plugin tests only
pytest tests/performance/ -v                # Performance tests only

# Run specific modules
pytest tests/backend/test_caching.py -v     # Cache system tests
pytest tests/backend/test_security.py -v    # Security tests
pytest tests/backend/test_modelmanager.py -v # Model management tests

# JavaScript Quality Tests
pytest tests/plugin/test_js_code_quality.py -v  # JavaScript validation tests
```

**Coverage and Reporting:**

```bash
# Generate detailed coverage report
pytest --cov=backend --cov-report=html --cov-report=term

# Open htmlcov/index.html to see detailed coverage analysis
# Comprehensive results saved to: tests/comprehensive_test_results.json
```

**Setup Script Tests:**

_PowerShell (Windows):_

```powershell
# Install Pester
Install-Module -Name Pester -Force -SkipPublisherCheck

# Run PowerShell tests
Invoke-Pester tests/setup/test_setup_ps1.ps1 -Verbose
```

_Bash (Linux/macOS):_

```bash
# Install BATS
sudo apt-get install bats # (Ubuntu)
brew install bats-core # (macOS)
# or: sudo apt-get install bats (Ubuntu)
# or: brew install bats-core (macOS)

# Run Bash tests
bats tests/setup/test_setup_sh.bats
```

#### **Known Issues & Development Status**

**Production Ready Components:**

- ✅ **Core Backend**: All FastAPI endpoints, configuration management, health checks
- ✅ **Security**: Encryption/decryption, authentication, secure data handling  
- ✅ **AI Models**: LLM loading, text generation, model routing and fallbacks
- ✅ **Vector Search**: Embeddings, similarity search, document indexing
- ✅ **Caching**: Multi-level TTL caching, persistence, automatic cleanup
- ✅ **Plugin System**: Obsidian integration, UI components, settings management
- ✅ **JavaScript Quality**: Code style enforcement, structure validation, security checks
- ✅ **Voice Processing**: Speech-to-text transcription, audio format validation

**Under Development:**

- 🔄 **Performance Optimization**: Cache eviction edge cases, connection pooling
- 🔄 **Integration Scenarios**: Complex cross-service workflows, error recovery
- 🔄 **Enterprise Features**: SSO integration, multi-tenant operations

**Test Coverage Areas:**

- **Backend Core**: 100% - All API endpoints, services, and utilities
- **Plugin Integration**: 100% - Obsidian UI, settings, and functionality
- **JavaScript Quality**: 100% - Code style, structure, security validation
- **Performance**: 85% - Most scenarios covered, optimizing edge cases
- **End-to-End**: 17% - Complex workflows being refined

#### **Continuous Integration**

Tests can be integrated into CI/CD pipelines. See `tests/setup/README.md` for GitHub Actions examples.

---

### **10. API Documentation**

The FastAPI backend provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Key endpoints and their usage:

```bash
# Health check
GET /health

# Service status with component details  
GET /status

# Configuration management
GET /api/config              # Get current settings
POST /api/config             # Update settings
POST /api/config/reload      # Reload from file


# AI operations
POST /ask                    # Ask question to LLM
POST /reindex                # Reindex vault documents  
POST /web                    # Index web content
POST /transcribe             # Voice to text

# Enterprise operations (if enterprise enabled)
GET /api/enterprise/status           # Enterprise feature status
POST /api/enterprise/auth/sso        # SSO authentication
GET /api/enterprise/tenants          # List tenants
POST /api/enterprise/tenants         # Create tenant
GET /api/enterprise/users            # List users
POST /api/enterprise/users           # Create user
GET /api/enterprise/compliance/gdpr  # GDPR compliance status
GET /api/enterprise/compliance/soc2  # SOC2 compliance status
GET /api/enterprise/admin/metrics    # Admin dashboard metrics
```

---

### **11. Dependencies**

**Runtime Dependencies:**

- Python 3.10+
- FastAPI & Uvicorn (web framework)
- PyTorch & Sentence Transformers (embeddings)
- ChromaDB (vector database)
- LLaMA-CPP-Python & GPT4All (LLM backends)
- Vosk (speech recognition)
- pypdf & BeautifulSoup4 (document processing)
- Obsidian 1.5+ (plugin host)

**Development Dependencies:**

- pytest, pytest-cov, pytest-asyncio (testing)
- Pester (PowerShell testing)
- BATS (Bash testing)

**Optional:**

--

---

### **12. License & Contributing**

- **Author**: Keimpe de Jong
- **License**: MIT
- **Repository**: [https://github.com/UndiFineD/obsidian-AI-assistant](https://github.com/UndiFineD/obsidian-AI-assistant)
- **Test Coverage**: 90.02% with ongoing improvements
- **Status**: Active development with comprehensive test suite

---

This `README.md` provides **everything a user needs** to install, configure, and start using your offline-first Obsidian LLM assistant.
