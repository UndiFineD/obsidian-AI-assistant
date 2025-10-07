
# Obsidian AI Assistant

**Offline-first AI assistant for Obsidian with comprehensive backend services, semantic search, and voice input support.**

---

## **Features**

### ✅ **Core Functionality (Implemented)**

- **Local LLM Integration**: Support for LLaMA/GPT4All models with hybrid routing
- **Centralized Settings Management**: Environment variables → YAML → defaults precedence
- **Semantic Search**: Vector embeddings with ChromaDB for similarity search
- **Document Indexing**: Markdown, PDF, and web page indexing with caching
- **Voice Input**: Vosk-based speech recognition with push-to-talk functionality
- **Task Queue System**: Batch processing with analytics and progress tracking
- **Comprehensive Caching**: TTL-based caching for embeddings, file hashes, and responses
- **Security**: Optional encryption for cached data with Fernet encryption
- **FastAPI Backend**: RESTful API with automatic documentation and error handling

### 🏢 **Enterprise Features (Implemented)**

- **Multi-Tenant Architecture**: Isolated data and configurations per tenant
- **SSO Authentication**: Support for Azure AD, Google, Okta, SAML, and LDAP
- **Role-Based Access Control (RBAC)**: Granular permissions and user management
- **Enterprise Admin Dashboard**: Comprehensive management interface with analytics
- **GDPR Compliance**: Data export, deletion, and consent management
- **SOC2 Compliance**: Audit logging, security monitoring, and compliance reporting
- **Enterprise Configuration**: Advanced settings for security, compliance, and integrations
- **Tenant Management**: Multi-organization support with isolated environments
- **Security Dashboard**: Real-time monitoring of security events and incidents
- **Compliance Reporting**: Automated GDPR and SOC2 compliance status tracking

### 🚧 **Enhanced Features**

- **Settings API**: Runtime configuration updates via `/api/config` endpoints
- **Status Monitoring**: Health checks and service status reporting
- **Error Handling**: Comprehensive error scenarios with graceful fallbacks
- **Test Coverage**: 70%+ test coverage with comprehensive test suites
- **Cross-Platform**: Windows/Linux/macOS support with dedicated setup scripts

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
```

![[diagram.png]]

---

## **Setup Instructions**

### **Enterprise Setup (Optional)**

For organizations requiring enterprise features, additional backend modules are available:

#### **Enterprise Backend Modules**

```bash
# Enterprise modules (automatically loaded if available)
backend/enterprise/
├── auth.py           # SSO authentication providers
├── tenant.py         # Multi-tenant management  
├── rbac.py          # Role-based access control
├── gdpr.py          # GDPR compliance tools
├── soc2.py          # SOC2 compliance monitoring
├── admin.py         # Admin dashboard API
└── integrations.py  # Enterprise integrations
```

#### **Enterprise Plugin Components**

```bash
plugin/
├── adminDashboard.js    # Admin interface
├── enterpriseAuth.js    # SSO authentication
├── enterpriseConfig.js  # Enterprise settings
└── styles.css          # Enterprise UI styling
```

#### **Enterprise Configuration**

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
```

#### **Enterprise Features Access**

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

```bash
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

```bash
# Get current configuration
GET http://localhost:8000/api/config

# Update settings
POST http://localhost:8000/api/config
Content-Type: application/json
{
  "vault_path": "new_vault",
  "chunk_size": 1000,
  "gpu": false
}

# Reload settings from file
POST http://localhost:8000/api/config/reload
```

#### **Plugin Configuration**

The plugin can optionally read `plugin/config.json` (copy from `plugin/config.template.json`):

```json
{
  "backendUrl": "http://localhost:8000",
  "vaultPath": "vault",
  "preferFastLLM": true
}
```

### Quickstart (Windows PowerShell)

```pwsh
# 1) Create a .env (optional) or set env vars in your session
$env:API_PORT=8000
$env:VAULT_PATH="$(Resolve-Path .\vault)"
$env:VOSK_MODEL_PATH="$(Resolve-Path .\models\vosk-model-small-en-us-0.15)"

# 2) Edit backend/config.yaml as needed
notepad .\backend\config.yaml

# 3) Start backend
# Option A: FastAPI with Uvicorn (full backend)
cd backend
python -m uvicorn backend:app --host 127.0.0.1 --port $env:API_PORT --reload

# Option B: Simple Python test server (no Node/NodeJS required)
# This serves the plugin files and provides mock endpoints for quick UI testing.
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
No Node/NodeJS build step is required—the plugin JS and CSS are ready-to-use.
    

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
- Requires no Node.js or complex dependencies
- Useful for plugin UI testing

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

### **8. Testing & Quality Assurance**

This project maintains high code quality with comprehensive test coverage (70%+).

#### **Test Coverage by Module**

| Module | Coverage | Test File |
|--------|----------|-----------|
| Settings | 93% | `test_settings.py` |
| LLM Router | 91% | `test_llm_router.py` |
| Voice Processing | 84% | `test_voice.py` |
| Caching | 99% | `test_caching.py`, `test_caching_extended.py` |
| Security | 100% | `test_security.py` |
| Backend API | 65% | `test_backend.py`, `test_config_endpoints.py` |
| Embeddings | 44% | `test_embeddings.py` |
| Indexing | 55% | `test_indexing.py` |
| Model Manager | 61% | `test_modelmanager.py` |

#### **Test Structure**

```text
tests/
├── backend/                     # Backend module tests
│   ├── test_backend.py         # FastAPI endpoints & integration
│   ├── test_caching.py         # Cache management 
│   ├── test_caching_extended.py # Extended cache scenarios
│   ├── test_config_endpoints.py # Configuration API
│   ├── test_embeddings.py      # Vector operations
│   ├── test_indexing.py        # Document processing
│   ├── test_llm_router.py      # Model routing logic
│   ├── test_modelmanager.py    # Model management
│   ├── test_security.py        # Encryption/decryption
│   ├── test_settings.py        # Settings management
│   ├── test_status_endpoint.py # Status API
│   └── test_voice.py           # Voice transcription
└── test_final.py               # End-to-end integration tests
```

#### **Running Tests**

**Quick Test Run:**

```bash
# Activate environment and run all tests  
source venv/bin/activate  # Linux/macOS
# or
& venv\Scripts\Activate.ps1  # Windows

# Run all tests with coverage
pytest --cov=backend --cov-report=term-missing

# Run specific module tests
pytest tests/backend/test_caching.py -v
pytest tests/backend/test_settings.py -v
```

**Full Test Suite:**

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-cov pytest-asyncio

# Run all tests with HTML coverage report
pytest --cov=backend --cov-report=html --cov-report=term

# Generate coverage report in htmlcov/ directory
# Open htmlcov/index.html in browser to see detailed coverage
```

**Development Testing:**

```bash
# Run tests in watch mode (re-run on file changes)
pytest-watch

# Run only failed tests from previous run
pytest --lf

# Run tests matching pattern
pytest -k "test_caching or test_settings" -v
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
npm install -g bats
# or: sudo apt-get install bats (Ubuntu)
# or: brew install bats-core (macOS)

# Run Bash tests
bats tests/setup/test_setup_sh.bats
```

#### **Test Coverage**

The test suite covers:

- **API Endpoints**: All FastAPI routes with mock data
- **LLM Integration**: Model loading, text generation, routing logic
- **Vector Database**: Embeddings, similarity search, document indexing
- **Caching**: TTL-based caching, persistence, cleanup
- **Security**: Encryption/decryption, token handling
- **Voice Processing**: Audio transcription, format validation
- **Setup Scripts**: Environment creation, dependency installation, error handling
- **Error Handling**: Edge cases, network failures, invalid inputs

#### **Continuous Integration**

Tests can be integrated into CI/CD pipelines. See `tests/setup/README.md` for GitHub Actions examples.

---

### **9. API Documentation**

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

### **10. Dependencies**

**Runtime Dependencies:**

- Python 3.10+
- FastAPI & Uvicorn (web framework)
- PyTorch & Sentence Transformers (embeddings)
- ChromaDB (vector database)
- LLaMA-CPP-Python & GPT4All (LLM backends)
- Vosk (speech recognition)
- PyPDF2 & BeautifulSoup4 (document processing)
- Obsidian 1.5+ (plugin host)

**Development Dependencies:**

- pytest, pytest-cov, pytest-asyncio (testing)
- Pester (PowerShell testing)
- BATS (Bash testing)

**Optional:**

- Node.js 18+ (not required for plugin usage)

---

### **11. License & Contributing**

- **Author**: Keimpe de Jong
- **License**: MIT
- **Repository**: [https://github.com/UndiFineD/obsidian-AI-assistant](https://github.com/UndiFineD/obsidian-AI-assistant)
- **Test Coverage**: 70%+ with ongoing improvements
- **Status**: Active development with comprehensive test suite
    

---

This `README.md` provides **everything a user needs** to install, configure, and start using your offline-first Obsidian LLM assistant.





