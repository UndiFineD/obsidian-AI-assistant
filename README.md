
# Obsidian AI Assistant

**Offline-first AI assistant for Obsidian with task queue, semantic linking, and analytics.**

---

## **Features**

## Phase 1: Core Functionality

- Ask questions to local LLaMA/GPT4All models
    
- Hybrid LLM routing (fast LLaMA vs deeper GPT4All)
    
- Session memory for context
    
- Automatic note creation (`Assistant_${timestamp}.md`)
    
- Task queue with inline previews
    

## Phase 2: Medium-Term Enhancements

- Batch processing of multiple notes
    
- Vault scanning and indexing (`.md`, PDF, web pages)
    
- Semantic linking of notes
    
- Note formatting via LLM
    

## Phase 3: Advanced Features

- Analytics dashboard: semantic coverage & QA history
    
- Queue search & filter
    
- Voice input support
    
- Optional caching & encryption for answers
    
- Multi-vault support
    

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

### **1. Run Setup Script**

**Linux/macOS:**

```bash
bash setup.sh
```

**Windows:**

```powershell
.\setup.ps1
```

This will:

1. Create a Python virtual environment
    
2. Install dependencies (`fastapi`, `torch`, `chromadb`, `llama-cpp-python`, `gpt4all`, etc.)
    
3. Detect GPU/CPU
    
4. Download default models (LLaMA 7B Q4, GPT4All Lora)
    
5. Build the Obsidian plugin automatically

### Central Configuration

Backend reads settings from environment variables and `backend/config.yaml`, with this precedence:

1) Environment variables (e.g., API_PORT, VAULT_PATH, MODEL_PATH, VOSK_MODEL_PATH)
2) `backend/config.yaml`
3) Code defaults

The plugin can optionally read `plugin/config.json` (copy from `plugin/config.template.json`). If present, it overrides the built-in defaults (e.g., `backendUrl`).

Key keys:

- backend_url / API_PORT
- vault_path, models_dir, cache_dir
- model_backend, model_path, embed_model, vector_db
- vosk_model_path (for voice)

### Quickstart (Windows PowerShell)

```pwsh
# 1) Create a .env (optional) or set env vars in your session
$env:API_PORT=8000
$env:VAULT_PATH="$(Resolve-Path .\vault)"
$env:VOSK_MODEL_PATH="$(Resolve-Path .\models\vosk-model-small-en-us-0.15)"

# 2) Edit backend/config.yaml as needed
notepad .\backend\config.yaml

# 3) Start backend
cd backend
python -m uvicorn backend:app --host 127.0.0.1 --port $env:API_PORT --reload
```

Plugin config:

```pwsh
# Copy plugin config template and edit backend URL if needed
Copy-Item .\plugin\config.template.json .\plugin\config.json -Force
notepad .\plugin\config.json
```

Then copy the files in `plugin/` to your Obsidian vault plugins folder (e.g., `C:\Users\<you>\Vault\.obsidian\plugins\obsidian-ai-assistant\`).
    

---

### **2. Activate Backend**

**Linux/macOS:**

```bash
source venv/bin/activate
python backend/backend.py
```

**Windows:**

```powershell
& venv\Scripts\Activate.ps1
python backend\backend.py
```

The backend will start at `http://localhost:8000` by default.

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

### **8. Testing**

This project includes comprehensive test suites to ensure reliability and maintainability.

#### **Test Structure**

```text
tests/                           # All tests organized in single directory
├─ backend/                      # Python backend tests
│  ├─ test_backend.py           # FastAPI endpoint tests
│  ├─ test_caching.py           # Cache management tests
│  ├─ test_embeddings.py        # Vector database tests
│  ├─ test_indexing.py          # Document indexing tests
│  ├─ test_llm_router.py        # LLM routing tests
│  ├─ test_modelmanager.py      # Model management tests
│  ├─ test_security.py          # Encryption/security tests
│  └─ test_voice.py             # Voice transcription tests
├─ setup/                        # Setup script tests
│  ├─ test_setup_ps1.ps1        # PowerShell setup tests
│  ├─ test_setup_sh.bats        # Bash setup tests
│  └─ README.md                 # Setup testing documentation
├─ comprehensive_integration_test.py  # Complete integration test
├─ test_final.py                 # Plugin integration tests
├─ test_plugin*.py               # Plugin functionality tests
├─ test_server.py                # Development server tests
├─ microphone_test.html          # Microphone permission testing
├─ test_push_to_talk.html        # Voice input testing
├─ conftest.py                   # Pytest configuration and fixtures
├─ pytest.ini                   # Pytest settings and coverage config
└─ run_tests_stronger.py         # Enhanced test runner script

run_tests.py                     # Main test runner (project root)
```

#### **Running Tests**

**All Tests (Recommended):**
```bash
# Run all tests using the main test runner
python run_tests.py

# Run all tests with verbose output
python run_tests.py -v

# Run specific test files or patterns
python run_tests.py backend/test_backend.py
python run_tests.py test_plugin*.py

# Collect tests without running (useful for debugging)
python run_tests.py --collect-only
```

**Backend Tests (Python):**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
& venv\Scripts\Activate.ps1  # Windows

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests from project root
python run_tests.py

# Or run directly from tests directory
cd tests
pytest -v

# Run with coverage (generates coverage reports)
pytest --cov=../backend --cov-report=html

# Run specific test file
pytest backend/test_backend.py -v

# Run comprehensive integration test
python comprehensive_integration_test.py
```

**Setup Script Tests:**

*PowerShell (Windows):*
```powershell
# Install Pester
Install-Module -Name Pester -Force -SkipPublisherCheck

# Run PowerShell tests
Invoke-Pester tests/setup/test_setup_ps1.ps1 -Verbose
```

*Bash (Linux/macOS):*
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

### **9. Dependencies**

- Python 3.10+
    
- Node.js 18+ (for plugin build)
    
- `fastapi`, `uvicorn`, `torch`, `sentence-transformers`, `chromadb`
    
- `llama-cpp-python`, `gpt4all`
    
- `beautifulsoup4`, `readability-lxml`, `PyPDF2`
    
- Obsidian 1.5+

**Development Dependencies:**
- `pytest`, `pytest-cov`, `pytest-asyncio` (Python testing)
- `Pester` (PowerShell testing)
- `bats` (Bash testing)
    

---

### **10. License / Author**

- Author: **Keimpe de Jong**
    
- License: MIT
    
- GitHub: _(https://github.com/UndiFineD/obsidian-AI-assistant)_
    

---

This `README.md` provides **everything a user needs** to install, configure, and start using your offline-first Obsidian LLM assistant.





