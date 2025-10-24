# Obsidian AI Agent - AI Agent Instructions

## Architecture Overview

This is a **modular, service-oriented offline-first AI agent** for Obsidian with separated concerns:

- **Backend**: FastAPI server (`agent/`) with REST APIs, vector search (ChromaDB), LLM routing, caching layers

- **Plugin**: Obsidian plugin (JavaScript in plugin directory) with vanilla JS (no build step), enterprise features optional

- **Models**: Local AI models (GPT4All, LLaMA, embeddings, Vosk) stored in `./models/` root directory (organized by type)

- **Configuration**: Hierarchical settings (env vars → `agent/config.yaml` → `agent/settings.py` defaults)

## API Endpoint Reference

### Health & Monitoring

- `GET /health` and `GET /api/health`: Returns full system health, config snapshot, and service status. Target: <100ms.

- `GET /status`: Lightweight liveness probe. Target: <100ms.

- `GET /api/performance/metrics`: Real-time performance metrics (cache, pools, queue, timestamp).

- `POST /api/performance/cache/clear`: Clears L1/L2 cache.

- `POST /api/performance/optimize`: Triggers background optimization tasks.

### Configuration Management

- `GET /api/config`: Returns current runtime config (whitelisted fields only).

- `POST /api/config`: Updates runtime config (only keys in `_ALLOWED_UPDATE_KEYS`).

- `POST /api/config/reload`: Reloads config from `agent/config.yaml`.

### AI Operations

- `POST /ask` and `POST /api/ask`: Main AI question endpoint. Supports context, prompt, model selection, and caching.

- `POST /reindex` and `POST /api/reindex`: Rebuilds vector DB index for vault documents.

- `POST /web` and `POST /api/web`: Indexes web content and generates AI responses.

- `POST /transcribe`: Speech-to-text from base64 audio (Vosk, Whisper, etc).

- `POST /api/search`: Semantic similarity search across indexed docs.

- `POST /api/index_pdf`: Indexes a PDF for semantic search.

### Health Monitoring Endpoints

- `GET /api/health/detailed`: Enhanced health with service status, system metrics, alert summary

- `GET /api/health/metrics`: Aggregated metrics over configurable time windows

- `GET /api/health/alerts`: Active and resolved alerts with severity levels

- `POST /api/health/alerts/{alert_id}/acknowledge`: Acknowledge alert awareness

### Enterprise Endpoints (if enabled)

- `GET /api/enterprise/status`: Returns enterprise feature status.

- `POST /api/enterprise/auth/sso`: SSO authentication.

- `GET /api/enterprise/tenants`, `POST /api/enterprise/tenants`: Tenant management.

- `GET /api/enterprise/users`, `POST /api/enterprise/users`: User management.

- `GET /api/enterprise/compliance/gdpr`, `GET /api/enterprise/compliance/soc2`: Compliance status.

## Performance Requirements & Optimization

### Performance Tiers

- **Tier 1**: <100ms (health, status, config, cache lookup)

- **Tier 2**: <500ms (cached ask, simple search, voice)

- **Tier 3**: <2s (AI generation, document search, embedding)

- **Tier 4**: <10s (web analysis, large doc indexing)

- **Tier 5**: <60s (vault reindex, model loading)

### Optimization Strategies

- Multi-level caching: L1 (memory), L2 (disk), L3 (persistent)

- Connection pooling: DB and model instance pools

- Async task queue: Background processing for indexing, optimization

- Load balancing: Round-robin model instances, priority queues

- Resource management: Smart memory allocation, CPU affinity, process priority

### Monitoring & SLA

- Real-time metrics: `/api/performance/metrics` (cache, pools, queue)

- Health monitoring: `/api/health/detailed` (service status, system metrics, alerts)

- SLA targets: <100ms health, <500ms cached, <2s AI, <10s complex, <60s batch

- Availability: 95% dev, 99% prod, 99.9% mission critical

### Health Monitoring System

- **Service Health Checks**: Monitors model_manager, embeddings, cache with timeout protection

- **System Metrics**: CPU, memory, disk usage, network connections, process count

- **Alert Management**: Threshold-based alerts (CPU 70/85/95%, memory 75/90/95%, disk 80/90/95%)

- **Alert Lifecycle**: Generation → Acknowledgement → Resolution

- **Metrics History**: 1000-entry rolling history for trending and aggregation

- **Status Levels**: HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN

- **Consecutive Failures**: Tracks failure sequences for severity escalation (1→WARNING, 2→ERROR, 3→CRITICAL)

See `docs/HEALTH_MONITORING.md` for complete documentation.

## Testing Strategy & Quality Gates

### Coverage & Test Types

- **Backend**: 85%+ coverage (FastAPI, services, error handling)

- **Plugin**: 90%+ coverage (JS code quality, UI, enterprise features)

- **Integration**: 70%+ API coverage (end-to-end workflows)

- **Performance**: Load, stress, spike, SLA compliance

- **Security**: Input validation, encryption, dependency scanning

### Patterns

- ML mocking: Patch torch/transformers in `conftest.py` before backend import

- Service mocking: Mock global instances (`backend.model_manager`), not classes

- Error testing: Flexible status code assertions ([200, 400, 422, 500])

- API reality: Test actual endpoints, not assumptions

### CI/CD Integration

- GitHub Actions: Lint, security scan, unit/integration tests, coverage upload

- Pre-commit hooks: black, flake8, mypy, bandit

- Coverage: HTML/XML reports, 70%+ threshold

### Running Tests

- `pytest tests/ -v` (full suite - 1042 tests, 46 files)

- `pytest tests/backend/ -v` (backend only)

- `pytest tests/plugin/ -v` (plugin only)

- `pytest --cov=agent --cov-report=html` (coverage)

- `python -m locust -f tests/load_test.py` (load testing)

### Current Test Status (October 17, 2025)

- **Test Suite**: 1021/1042 passed (98.2% success rate)

- **Test Files**: 46 Python files (optimized, duplicates removed)

- **Execution Time**: ~3 minutes (180.42s)

- **OpenSpec Compliance**: 98.9% governance tests passing

- **Recent Improvements**: +116 tests, +29.5% coverage across 4 critical modules

- **Coverage**: 88%+ backend (see docs/TEST_COVERAGE_IMPROVEMENTS_OCTOBER_2025.md)

## Configuration & Deployment

### Configuration Precedence

1. Environment variables (highest)

2. `agent/config.yaml` (medium)

3. Code defaults (lowest)

### Key Config Options

- **Core**: `api_port` (8000), `backend_url` (<http://localhost:8000>), `allow_network` (false)

- **Models**: `gpu` (auto-detect), `model_backend` (gpt4all), `model_path`, `embed_model` (all-MiniLM-L6-v2)

- **Storage**: `vault_path`, `models_dir` (./models), `cache_dir` (./agent/cache)

- **Vector DB**: `vector_db` (chromadb), `top_k` (5), `chunk_size` (1000), `chunk_overlap` (200), `similarity_threshold` (0.7)

- **Voice**: `vosk_model_path` (./models/vosk-model-small-en-us-0.15)

- **Enterprise**: `enterprise_enabled`, `sso_providers`, `tenant_isolation`, `compliance_mode`

### Deployment Environments

#### Local Development

```powershell

# Windows setup (creates venv, installs dependencies, downloads models)

./setup.ps1

# Start backend with hot reload

cd agent && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

# Install plugin to Obsidian vault

./setup-plugin.ps1 -VaultPath "C:\Users\...\Documents\ObsidianVault"
```

#### Production Deployment

```bash

# Linux/macOS production setup

./setup.sh --production

# Run with production settings

cd agent && python -m uvicorn backend:app --host 0.0.0.0 --port 8000 --workers 4

# Process management with systemd/supervisor

sudo systemctl start obsidian-ai-agent

# Health monitoring

curl http://localhost:8000/health
```

#### Docker Deployment

```dockerfile

# Multi-stage build for production

FROM python:3.11-slim as backend
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent/ agent/
EXPOSE 8000
CMD ["uvicorn", "agent.backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Enterprise Cloud Deployment

```yaml

# Kubernetes deployment example

apiVersion: apps/v1
kind: Deployment
metadata:
    name: obsidian-ai-agent
spec:
    replicas: 3
    selector:
        matchLabels:
            app: obsidian-ai-agent
    template:
        spec:
            containers:

- name: backend
                  image: obsidian-ai-agent:latest
                  ports:

- containerPort: 8000
                  env:

- name: GPU
                        value: 'true'

- name: ENTERPRISE_ENABLED
                        value: 'true'
                  resources:
                      requests:
                          memory: '8Gi'
                          cpu: '4'
                      limits:
                          memory: '32Gi'
                          cpu: '16'
```

### Integration Patterns

#### Plugin-Backend Integration

```javascript
// Plugin initialization with backend discovery
class ObsidianAIAgent extends Plugin {
    async onload() {
        // Auto-discover backend endpoint
        this.backendClient = new BackendClient({
            baseUrl: this.settings.backend_url || 'http://localhost:8000',
            timeout: 30000,
            retryAttempts: 3,
        });

        // Health check with fallback
        await this.backendClient.healthCheck();
    }
}
```

#### API Integration Patterns

```python

# Backend service integration

class ServiceIntegration:
    def __init__(self):
        self.embeddings = EmbeddingsManager.from_settings()
        self.vector_db = VectorDBManager.from_settings()
        self.cache = CacheManager.from_settings()

    async def process_request(self, request):
        # Multi-service orchestration
        embeddings = await self.embeddings.embed(request.text)
        results = await self.vector_db.search(embeddings)
        return await self.cache.get_or_set(request.cache_key, results)
```

#### External System Integration

```python

# Enterprise SSO integration

class SSOIntegration:
    def __init__(self):
        self.providers = {
            'azure': AzureADProvider(),
            'google': GoogleOAuthProvider(),
            'okta': OktaSAMLProvider()
        }

    async def authenticate(self, provider, credentials):
        return await self.providers[provider].validate(credentials)
```

### Environment Configuration

#### Development Environment Variables

```bash

# Core settings

export API_PORT=8000
export DEBUG=true
export LOG_LEVEL=debug

# Model settings

export GPU=false
export MODEL_BACKEND=gpt4all
export MODELS_DIR=./models

# Database settings

export VECTOR_DB=chromadb
export CACHE_BACKEND=memory
```

#### Production Environment Variables

```bash

# Performance settings

export WORKERS=4
export MAX_CONNECTIONS=1000
export CACHE_TTL=3600

# Security settings

export CORS_ORIGINS=https://yourdomain.com
export API_KEY_REQUIRED=true
export RATE_LIMIT=100

# Monitoring settings

export METRICS_ENABLED=true
export HEALTH_CHECK_INTERVAL=30
```

#### Enterprise Environment Variables

```bash

# Enterprise features

export ENTERPRISE_ENABLED=true
export TENANT_ISOLATION=true
export COMPLIANCE_MODE=gdpr,soc2

# SSO configuration

export SSO_PROVIDERS=azure,google,okta
export AZURE_TENANT_ID=your-tenant-id
export GOOGLE_CLIENT_ID=your-client-id

# Multi-tenant settings

export DEFAULT_TENANT=default
export TENANT_STORAGE_QUOTA=100GB
```

### System Requirements & Scaling

#### Minimum Requirements

- **CPU**: 2 cores, 2.4GHz

- **RAM**: 4GB (8GB recommended)

- **Storage**: 5GB SSD

- **Network**: 10Mbps

- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

#### Production Requirements

- **CPU**: 8+ cores, 3.2GHz+ (Intel Xeon/AMD EPYC)

- **RAM**: 32GB+ (64GB for enterprise)

- **Storage**: 100GB+ NVMe SSD, 3000+ IOPS

- **GPU**: NVIDIA RTX 4080+ or Tesla V100+ (optional)

- **Network**: Gigabit ethernet, <10ms latency

#### Scaling Guidelines

- **Horizontal**: Load balance across 3+ backend instances

- **Vertical**: Scale RAM for model loading, CPU for concurrent requests

- **Caching**: Redis cluster for multi-instance cache sharing

- **Database**: Separate vector DB instances for tenant isolation

- **Models**: Model serving with dedicated GPU instances

## Troubleshooting & Utility Patterns

### Common Issues

- Plugin not loading: Check `plugin/manifest.json`, all `.js` files present

- Backend connection: Verify `http://localhost:8000/health`

- Model loading: Check `models/` for `.gguf` files

- Cache issues: Clear with `POST /api/performance/cache/clear`

- Performance: Check `/api/performance/metrics` for bottlenecks

### Error-Safe Execution

```python
from agent.utils import safe_call
result = safe_call(risky_function, default=None, error_msg="Custom error message")
```

### Performance Decorators

```python
@cached(ttl=3600, key_func=lambda req: f"cache_key:{req.id}")
def expensive_operation(request):
    return process_request(request)
```

### Factory Patterns

```python
embeddings_manager = EmbeddingsManager.from_settings()
settings = get_settings()  # Cached singleton
```

### Enterprise Feature Detection

```javascript
try {
    EnterpriseAuth = require('./enterpriseAuth.js');
    ENTERPRISE_AVAILABLE = true;
} catch (error) {
    console.log('Enterprise features not available');
}
```

## File Structure Reference

```text
├── agent/            # FastAPI server modules (main backend)
├── plugin/           # Obsidian plugin (no build step)
├── models/           # AI models (GPT4All, LLaMA, embeddings, Vosk)
├── tests/            # Comprehensive test suite (1042 tests)
├── agent/cache/      # Cached embeddings and responses
├── agent/logs/       # Application logs
├── agent/vector_db/  # ChromaDB vector database storage
├── docs/             # Documentation and specifications
├── openspec/         # OpenSpec governance and compliance
├── scripts/          # Utility scripts
├── setup.ps1/.sh     # Primary installation scripts
├── setup-plugin.ps1  # Plugin-focused setup
├── setup-venv311.ps1 # Virtual environment setup
└── Makefile          # Development commands
```

## Key Development Patterns

### 1. Backend Architecture (`agent/`)

- **Entry point**: `agent/backend.py` - FastAPI app with auto-documentation

- **Settings cascade**: `agent/settings.py` uses Pydantic BaseModel with `_ALLOWED_UPDATE_KEYS` for runtime updates

- **Service pattern**: Each module (embeddings, indexing, caching, security) is self-contained with clear interfaces

- **Enterprise modules**: Optional enterprise features (`enterprise_*.py`) loaded dynamically

- **External secrets**: `_load_external_env()` loads from `%USERPROFILE%/DEV/obsidian-llm-assistant/venv.txt`

### 2. Plugin System (`plugin/`)

- **No build step**: Ready-to-use JavaScript files copied directly to Obsidian

- **Enterprise detection**: Optional enterprise modules loaded with try-catch pattern

- **Configuration**: Uses `config.json` adjacent to `main.js` for deployment settings

- **Code style**: PEP8-inspired JavaScript (4-space indentation, PascalCase classes, camelCase functions)

### 3. Configuration Management

```python

# Runtime config updates via API

POST /api/config
{
    "vault_path": "./new_vault",
    "chunk_size": 1000,
    "gpu": true  # Only keys in _ALLOWED_UPDATE_KEYS
}
```

### 4. Testing Strategy (442 total tests, 99.8% success rate)

- **Backend tests**: `tests/backend/` - Unit tests for all modules (85%+ coverage)

- **Plugin tests**: `tests/plugin/` - JavaScript code quality validation (90%+ coverage)

- **Integration tests**: `tests/integration/` - End-to-end workflows (70%+ API coverage)

- **Performance tests**: Load testing, stress testing, spike testing with SLA compliance

- **Test runner**: `tests/comprehensive_test_runner.py` - Colored output with timing

- **ML mocking**: Always mock torch/transformers with `conftest.py` patterns

- **Service mocking**: Mock global instances (`backend.model_manager`), not classes

- **Error testing**: Use status code ranges (`[200, 400, 422]`) for flexibility

## Critical Workflows

### Setup & Deployment

```powershell

# Primary setup (creates venv, installs models, tests everything)

./setup.ps1

# Plugin-only setup (copies files to Obsidian vault)

./setup-plugin.ps1 -VaultPath "C:\Users\...\Vault"

# Backend-only mode (starts server without plugin install)

./setup-plugin.ps1 -BackendOnly
```

### Development Commands

```bash

# Run comprehensive test suite (production validation)

python -m pytest tests/ -v  # Expected: 441 passed, 1 skipped

# Start backend with auto-reload

cd agent && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

# Code quality validation

pytest tests/plugin/test_js_code_quality.py -v  # JavaScript validation
python fix_js_quality.py  # Auto-fix JavaScript style issues

# Performance testing

pytest tests/test_performance.py -v  # Load, stress, and benchmark tests
python -m locust -f tests/load_test.py  # Load testing with web UI

# Coverage reporting

pytest --cov=agent --cov-report=html --cov-report=term  # Generate coverage reports
```

### API Health Checks

- `GET /health` - Basic health check (<100ms SLA)

- `GET /status` - Detailed service status with component details

- `GET /docs` - Interactive Swagger documentation

- `GET /redoc` - Alternative API documentation

- `GET /api/config` - Current configuration state

- `GET /api/performance/metrics` - Real-time performance metrics

- `POST /api/cache/clear` - Clear performance cache

- `POST /api/performance/optimize` - Trigger background optimization

## Integration Points

### Plugin ↔ Backend Communication

- **BackendClient** (`plugin/backendClient.js`): Handles all API communication

- **Endpoints**: `/ask`, `/reindex`, `/web`, `/transcribe`, `/api/config`

- **Error handling**: Graceful degradation when backend unavailable

- **Retry logic**: Exponential backoff for transient failures

### Model Management

- **ModelManager** (`agent/modelmanager.py`): Unified interface for GPT4All, LLaMA-cpp, embeddings

- **LLM Router** (`agent/llm_router.py`): Intelligent model selection with fallbacks

- **Model storage**: `models/` directory with automated downloads via setup scripts

- **Connection pooling**: `performance.py` manages AI model instance pools (1-3 instances)

### Vector Search Pipeline

- **Indexing** (`agent/indexing.py`): Markdown, PDF, web content → embeddings

- **ChromaDB**: Vector database with HNSW indexing for similarity search

- **Multi-level caching**: L1 (memory), L2 (disk), L3 (persistent), L4 (vector DB)

- **EmbeddingsManager**: Centralized vector operations with `from_settings()` factory pattern

### Performance Architecture

- **Multi-level cache hierarchy**: `performance.py` implements L1-L4 caching strategy

- **Connection pools**: Database and model instance pools with health checks

- **Async task queue**: Background processing for indexing and optimization

- **Performance monitoring**: `PerformanceMonitor.get_system_metrics()` for real-time metrics

- **SLA targets**: <100ms health checks, <500ms cached ops, <2s AI generation, <10s complex ops

- **Resource optimization**: Smart memory allocation, CPU affinity, process priority management

- **Load balancing**: Round-robin AI model instances, request prioritization, queue management

## Code Quality Standards

### JavaScript (Plugin)

#### JavaScript Style & Formatting

- **4-space indentation**: Consistent with Python backend

- **No trailing whitespace**: Clean line endings

- **Double quotes preferred**: For string literals (consistency)

- **Semicolons**: Use semicolons for statement termination

- **Line length**: 100 characters maximum

#### Naming Conventions

- **PascalCase**: Classes (`BackendClient`, `EnterpriseAuth`, `AdminDashboard`)

- **camelCase**: Functions and variables (`startListening`, `sendRequest`, `currentView`)

- **UPPER_CASE**: Constants (`ENTERPRISE_AVAILABLE`, `DEFAULT_TIMEOUT`)

- **Private members**: Prefix with underscore (`_privateMethod`)

#### Code Structure

- **Module exports**: `module.exports = ClassName` for classes

- **Error handling**: Try-catch blocks with descriptive error messages

- **Async patterns**: Use async/await for asynchronous operations

- **Event listeners**: Proper cleanup in destroy() methods

#### JavaScript Examples

```javascript
// Good: Class definition with proper formatting
class BackendClient {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.timeout = options.timeout || 30000;
        this._retryAttempts = options.retryAttempts || 3;
    }

    async request(endpoint, options) {
        try {
            const response = await this._makeRequest(endpoint, options);
            return this._handleResponse(response);
        } catch (error) {
            console.error(`Request failed: ${error.message}`);
            throw new Error(`Backend request failed: ${error.message}`);
        }
    }
}

// Good: Enterprise feature detection
try {
    const EnterpriseAuth = require('./enterpriseAuth.js');
    this.enterpriseFeatures = new EnterpriseAuth(this.plugin);
} catch (error) {
    console.log('Enterprise features not available');
    this.enterpriseFeatures = null;
}
```

### Python (Backend)

#### Python Style & Formatting

- **PEP 8 compliance**: Follow Python style guide

- **4-space indentation**: Consistent formatting

- **Line length**: 88 characters (Black formatter)

- **Import sorting**: Use isort for organized imports

- **Type hints**: Required for all public functions

#### Code Quality Tools

- **Ruff**: Fast Python linter (E, F, W, C, I rules enabled)

- **Bandit**: Security vulnerability scanning

- **Black**: Code formatting (optional but recommended)

- **mypy**: Static type checking

#### Patterns & Architecture

- **Pydantic models**: All request/response models and settings

- **Dependency injection**: Use `from_settings()` factory methods

- **Error handling**: HTTPException with appropriate status codes

- **Async/await**: All I/O operations should be async

- **Resource management**: Context managers for file/DB operations

#### Python Examples

```python

# Good: Pydantic model with validation

from pydantic import BaseModel, Field
from typing import Optional, List

class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    context: Optional[str] = None
    model: Optional[str] = Field(default="gpt4all", regex=r"^[a-zA-Z0-9_-]+$")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

# Good: Service with proper error handling

class EmbeddingsManager:
    def __init__(self, model_name: str, cache_manager: CacheManager):
        self.model_name = model_name
        self.cache = cache_manager

    @classmethod
    def from_settings(cls) -> "EmbeddingsManager":
        settings = get_settings()
        cache_manager = CacheManager.from_settings()
        return cls(settings.embed_model, cache_manager)

    async def embed_text(self, text: str) -> List[float]:
        try:
            cache_key = f"embed:{hash(text)}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result

            embeddings = await self._compute_embeddings(text)
            await self.cache.set(cache_key, embeddings, ttl=3600)
            return embeddings

        except Exception as error:
            logger.error(f"Embedding failed: {error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Embedding generation failed: {str(error)}"
            )
```

### Quality Automation

#### Pre-commit Hooks

```bash

# Install pre-commit hooks

pip install pre-commit
pre-commit install

# Hooks configuration (.pre-commit-config.yaml)

# - ruff (linting)

# - bandit (security)

# - black (formatting, optional)

# - mypy (type checking)

```

#### JavaScript Quality Fixes

```bash

# Auto-fix JavaScript quality issues

python fix_js_quality.py

# Manual quality checks

node -c plugin/filename.js  # Syntax validation
```

#### Python Quality Checks

```bash

# Linting and security

ruff check agent/
bandit -r agent/ -f json -o tests/bandit_report.json

# Type checking

mypy agent/ --ignore-missing-imports

# Test coverage

pytest --cov=agent --cov-report=html --cov-report=term
```

## Enterprise Features (Optional)

### Enterprise Module Architecture

When enterprise modules are available (`enterprise_*.py`, `enterpriseAuth.js`):

#### Authentication & SSO (`enterprise_auth.py`)

- **SSO Providers**: Azure AD, Google Workspace, Okta, SAML, LDAP

- **JWT Token Management**: Secure token generation and validation

- **Session Management**: Multi-tenant session isolation

- **API Key Management**: Enterprise API key authentication

#### Multi-Tenant Management (`enterprise_tenant.py`)

- **Tenant Tiers**: Free, Professional, Enterprise, Custom

- **Resource Isolation**: Per-tenant data, storage, and compute limits

- **Usage Tracking**: API calls, storage, user activity monitoring

- **Billing Integration**: Usage-based billing and cost allocation

#### Role-Based Access Control (`enterprise_rbac.py`)

- **Role Hierarchy**: Admin, Manager, Analyst, User roles

- **Permission Matrix**: Granular permissions for resources and operations

- **Resource-Level Security**: Document, model, and feature access control

- **Audit Logging**: Complete access and permission change tracking

#### Compliance Management

- **GDPR Compliance** (`enterprise_gdpr.py`): Data processing, user rights, consent management

- **SOC2 Compliance** (`enterprise_soc2.py`): Security controls, monitoring, incident response

- **Data Retention**: Automated data lifecycle and retention policies

- **Audit Trails**: Comprehensive logging for compliance reporting

#### Admin Dashboard (`enterprise_admin.py`)

- **User Management**: Bulk operations, role assignments, deactivation

- **Tenant Management**: Resource allocation, usage monitoring, billing

- **Security Dashboard**: Incidents, access reviews, vulnerability scanning

- **Compliance Reporting**: GDPR, SOC2, and custom compliance reports

### Enterprise Endpoints

```python

# Admin Dashboard

GET  /api/enterprise/dashboard    # Overview metrics and health
GET  /api/enterprise/users        # User management interface
POST /api/enterprise/users        # Create/update users
GET  /api/enterprise/tenants      # Tenant management interface
POST /api/enterprise/tenants      # Create/update tenants

# Authentication

POST /api/enterprise/auth/sso     # SSO login initiation
GET  /api/enterprise/auth/callback # SSO callback handler
POST /api/enterprise/auth/logout  # SSO logout

# Compliance

GET  /api/enterprise/compliance/gdpr  # GDPR compliance status
GET  /api/enterprise/compliance/soc2 # SOC2 compliance status
POST /api/enterprise/compliance/audit # Generate audit reports

# Security

GET  /api/enterprise/security     # Security dashboard
POST /api/enterprise/security/scan # Trigger security scan
GET  /api/enterprise/audit        # Access audit logs
```

### Enterprise Feature Detection (Plugin)

```javascript
// Plugin enterprise feature loading
class EnterpriseFeatures {
    constructor() {
        this.features = {
            auth: this.loadModule('./enterpriseAuth.js'),
            config: this.loadModule('./enterpriseConfig.js'),
            admin: this.loadModule('./adminDashboard.js'),
        };
    }

    loadModule(path) {
        try {
            return require(path);
        } catch (error) {
            console.log(`Enterprise module ${path} not available`);
            return null;
        }
    }

    isAvailable(feature) {
        return this.features[feature] !== null;
    }
}
```

### Enterprise Configuration

```yaml

# agent/config.yaml enterprise settings

enterprise:
    enabled: true
    features:

- sso

- multi_tenant

- rbac

- compliance

- admin_dashboard

    sso:
        providers:

- azure_ad

- google_workspace

- okta
        default_provider: azure_ad

    tenants:
        isolation: strict
        default_tier: professional
        storage_quota_gb: 100

    compliance:
        gdpr_enabled: true
        soc2_enabled: true
        audit_retention_days: 2555 # 7 years
```

## Troubleshooting Patterns

### Common Issues (Development)

1. **Plugin not loading**: Check `plugin/manifest.json` and ensure all `.js` files copied

2. **Backend connection**: Verify `http://localhost:8000/health` responds

3. **Model loading**: Check `models/` directory exists and contains `.gguf` files

4. **Tests failing**: Run `python -m pytest tests/backend/ -v` to isolate backend issues

5. **Cache issues**: Clear with `GET /api/cache/clear` or restart backend

6. **Performance degradation**: Check `/api/performance/metrics` for bottlenecks

### Development Debugging

- **Backend logs**: FastAPI auto-logging with uvicorn (`--log-level debug`)

- **Plugin debugging**: Use Obsidian Developer Console (Ctrl+Shift+I)

- **Configuration**: Check environment variables override config.yaml settings

- **Performance**: Use `/status` endpoint to monitor component health

- **Error handling**: All functions use `safe_call()` utility for graceful failure

- **Test isolation**: Use `mock.patch.dict('sys.modules', ...)` for ML library mocking

### Error Handling Patterns

- **JavaScript**: Try-catch blocks with user-friendly error messages

- **Python**: `HTTPException` with proper status codes (400, 422, 500)

- **API responses**: Flexible assertions accept multiple valid status codes

- **Retry logic**: Exponential backoff with `ErrorHandler.withRetry()` pattern

- **Logging**: Structured logging with `logger.error(..., exc_info=True)`

## System Requirements & Deployment

### Development Environment

- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

- **CPU**: 2+ cores, 2GHz

- **RAM**: 4GB minimum

- **Storage**: 2GB SSD

- **Python**: 3.11+

### Production Environment

- **CPU**: 8+ cores, 3.5GHz

- **RAM**: 16GB+ (32GB+ for enterprise)

- **Storage**: 50GB+ SSD with >1000 IOPS

- **GPU**: CUDA 11.8+ compatible (optional, 3-5x performance boost)

- **Network**: Gigabit connection for high-throughput

### Performance Targets

- **Tier 1**: <100ms (health checks, status)

- **Tier 2**: <500ms (cached operations, voice)

- **Tier 3**: <2s (AI generation, document search)

- **Tier 4**: <10s (web analysis, complex operations)

- **Tier 5**: <60s (vault reindexing, model loading)

## File Structure Reference (Summary)

```text
├── agent/            # FastAPI server modules
├── plugin/           # Obsidian plugin (no build step)
├── models/           # AI models (GPT4All, LLaMA, embeddings, Vosk)
├── tests/            # Comprehensive test suite (1042 tests)
├── agent/cache/      # Cached embeddings and responses
├── agent/logs/       # Application logs
├── agent/vector_db/  # ChromaDB vector database storage
├── docs/             # Documentation and specifications
├── openspec/         # OpenSpec governance and compliance
├── scripts/          # Utility scripts
├── setup.ps1/.sh     # Primary installation scripts
├── setup-plugin.ps1  # Plugin-focused setup
└── Makefile          # Development commands
```

## Continuous Improvement & Feedback

### Contributing to Documentation

This specification is a living document that should evolve with the codebase. Contributors and AI agents are encouraged to:

#### Suggest Improvements

- **Clarity**: Identify unclear instructions or missing context

- **Completeness**: Point out gaps in architecture, workflows, or patterns

- **Accuracy**: Report outdated information or incorrect examples

- **Usability**: Recommend better organization or additional examples

#### Update Process

1. **File Issues**: Report documentation problems via GitHub issues

2. **Submit PRs**: Contribute improvements directly to `.github/copilot-instructions.md`

3. **Discuss Changes**: Use discussions for architectural decisions

4. **Regular Reviews**: Schedule periodic documentation audits

#### Quality Metrics

- **Onboarding Time**: New contributors should be productive within 1 hour

- **Error Reduction**: Clear instructions should minimize common mistakes

- **Test Coverage**: Documentation examples should match actual test patterns

- **Consistency**: Standards should be uniformly applied across all modules

### Feedback Channels

#### For AI Agents

- **Performance Issues**: Report slow responses or failed operations

- **Missing Patterns**: Identify recurring tasks that lack documented patterns

- **Error Scenarios**: Document common failure modes and solutions

- **Integration Points**: Highlight complex or confusing integration steps

#### For Human Contributors

- **GitHub Issues**: `documentation` label for spec improvements

- **Pull Requests**: Direct contributions to copilot instructions

- **Code Reviews**: Flag documentation updates needed during code changes

- **Team Discussions**: Architecture decisions affecting these instructions

### Validation Process

#### Regular Audits

- **Monthly**: Review against latest codebase changes

- **Release Cycles**: Update for new features and deprecations

- **Performance Reviews**: Validate SLA targets and benchmarks

- **Security Audits**: Update threat models and compliance requirements

#### Automated Checks

```bash

# Validate documentation against codebase

# Documentation validation moved to test suite

python -m pytest tests/ -k "doc"

# Reference checking integrated into tests

python -m pytest tests/ -k "reference"

# Code examples tested in integration tests

python -m pytest tests/integration/ -v
```

### Success Criteria

These instructions are successful when:

- ✅ New AI agents can start contributing within 15 minutes

- ✅ Common integration issues are documented and resolved quickly

- ✅ Code quality remains consistently high across all contributions

- ✅ Performance targets are met or exceeded

- ✅ Security and compliance requirements are properly implemented

## Architecture Migration Notes (v0.1.34 → v0.1.35)

This section documents key architectural changes from v0.1.34 to v0.1.35 that affect development workflows.

### Module Naming & Directory Structure

**Changes:**
- Renamed `backend/` directory to `agent/` for clarity about the service's role
- Restructured models directory from `backend/models/` to root-level `models/`
- All FastAPI-related files now in `agent/` with consistent import patterns

**Migration Impact:**
- Update all imports from `backend.*` to `agent.*`
- Update all file paths referencing `backend/` to use `agent/`
- Model references should use `./models/` (relative to workspace root)
- Cache and logs now stored in `agent/cache/` and `agent/logs/`

**Example Migration:**
```python
# Old (v0.1.34)
from backend.modelmanager import ModelManager
from backend.settings import get_settings

# New (v0.1.35)
from agent.modelmanager import ModelManager
from agent.settings import get_settings
```

### Service Interfaces & Patterns

**New Conventions:**
- **Factory Methods**: All services use `from_settings()` class method for instantiation
- **Dependency Injection**: Services accept dependencies in `__init__`, not instantiated internally
- **Async-First**: All I/O operations use async/await pattern
- **Error Handling**: HTTPException with specific status codes over generic exceptions

**Application Pattern:**
```python
# Initialize services with dependency injection
embeddings = EmbeddingsManager.from_settings()
cache = CacheManager.from_settings()
model_manager = ModelManager.from_settings()

# Services use async operations
embeddings_vector = await embeddings.embed_text(text)
cached_result = await cache.get(cache_key)
```

### Configuration Management

**Three-Level Hierarchy (unchanged but reinforced):**
1. Environment variables (highest priority)
2. `agent/config.yaml` (medium priority)
3. Code defaults in `agent/settings.py` (lowest priority)

**Runtime Configuration Updates:**
- Only whitelisted keys in `_ALLOWED_UPDATE_KEYS` can be updated via API
- Changes are in-memory; restart required to reload from `config.yaml`
- Use `/api/config` endpoint to view current runtime configuration

### Testing Strategy Updates

**Key Changes:**
- Consolidated test structure under `tests/` with clear subdirectories
- Backend tests in `tests/backend/` for agent module testing
- Plugin tests in `tests/plugin/` for JavaScript validation
- Integration tests in `tests/integration/` for end-to-end workflows

**Updated Test Commands:**
```bash
# Run tests against agent/ module
pytest tests/backend/ -v

# Run plugin quality checks
pytest tests/plugin/test_js_code_quality.py -v

# Full suite with coverage
pytest --cov=agent --cov-report=html tests/
```

### Performance Architecture

**Enhancements:**
- Multi-level caching now consistently implemented across all services
- Connection pooling for model instances (1-3 per pool)
- Async task queue for background operations
- Health monitoring with alert thresholds and escalation

**Performance Tiers (SLA):**
- Tier 1: <100ms (health checks, status)
- Tier 2: <500ms (cached operations)
- Tier 3: <2s (AI generation)
- Tier 4: <10s (complex operations)
- Tier 5: <60s (batch operations)

### Development Workflow Updates

**Setup Process:**
```powershell
# Primary setup script handles all initialization
./setup.ps1

# Plugin-specific setup
./setup-plugin.ps1 -VaultPath "C:\Path\To\Vault"

# Verify backend health
curl http://localhost:8000/health
```

**Development Server:**
```bash
# From workspace root, NOT from agent/ directory
cd agent && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

**Code Quality:**
```bash
# Validate Python code in agent/ directory
ruff check agent/
bandit -r agent/
mypy agent/ --ignore-missing-imports

# Validate JavaScript code in plugin/
pytest tests/plugin/test_js_code_quality.py -v
```

### OpenSpec Workflow System (v0.1.42+)

The workflow system in `scripts/workflow.py` manages 13-step OpenSpec changes with enhanced capabilities:

#### Workflow Execution

**Basic workflow execution:**
```powershell
# Run all steps (default: interactive mode)
python scripts/workflow.py --change-id my-change --title "My Feature" --owner kdejo

# Run specific step
python scripts/workflow.py --change-id my-change --step 0 --title "My Feature" --owner kdejo

# Run multiple specific steps
python scripts/workflow.py --change-id my-change --step 0 --step 1 --step 2 --title "My Feature" --owner kdejo
```

#### Advanced Workflow Flags (v0.1.42+)

**Preview changes without modifying files:**
```powershell
# --dry-run mode: Preview all changes, don't modify files
# Useful for: Testing workflow logic, previewing changes, validating before commit
python scripts/workflow.py --change-id test-change --step 0 --step 1 --dry-run

# Output shows [DRY RUN] messages for each file operation
# [DRY RUN] Would create: .../todo.md
# [DRY RUN] Would write: .../version_snapshot.md
```

**Skip validation for local development:**
```powershell
# --skip-quality-gates flag: Skip quality validation (⚠️ NOT for production)
# Useful for: Faster local iteration, testing workflow logic
python scripts/workflow.py --change-id my-change --skip-quality-gates

# Output shows warning when flag used:
# ⚠️  Quality gates SKIPPED - output may not meet production standards
```

**Combine flags for maximum flexibility:**
```powershell
# Combine --dry-run and --skip-quality-gates for fast local testing
python scripts/workflow.py --change-id test-change --step 0 --step 1 --dry-run --skip-quality-gates

# Both warnings/previews will show
# Perfect for: Testing new features, validating workflow logic, development iteration
```

#### Workflow Options

| Flag | Type | Default | Description | Use Case |
|------|------|---------|-------------|----------|
| `--change-id` | string | Required | Unique identifier for the change | Workflow naming |
| `--step N` | int | Interactive | Specific step(s) to run (0-12) | Run subset of workflow |
| `--title` | string | Required | Human-readable title | Change documentation |
| `--owner` | string | Required | Change owner (GitHub username) | Attribution and permissions |
| `--dry-run` | flag | false | Preview changes without modification | Testing and validation |
| `--skip-quality-gates` | flag | false | Skip quality checks (⚠️ not for production) | Local development |
| `--release-type` | string | patch | Version bump type (major/minor/patch) | Version control |
| `--lane` | string | standard | Change classification (docs/standard/heavy) | Validation level |
| `--template` | string | default | Template for generated docs | Customization |
| `--enable-checkpoints` | flag | true | Enable checkpoint/resumption system | State recovery |

#### Workflow Resumption (v0.1.42+)

**Automatic detection of incomplete workflows:**
```powershell
# If a workflow was interrupted, run the same command again
# System will detect incomplete workflow and prompt:
# 
# ❓ Incomplete workflow detected: my-change (last step: 3)
# Would you like to:
#   1. Resume from step 4
#   2. Start fresh (will recreate files)
# 
# Answer 1 to resume from checkpoint

python scripts/workflow.py --change-id my-change --title "My Feature" --owner kdejo
```

The checkpoint system automatically:
- Tracks completed steps in `.checkpoints/state.json`
- Captures file snapshots for recovery
- Records git commits at each checkpoint
- Enables recovery from any interruption

#### Workflow Status Tracking (v0.1.42+)

**Monitor workflow progress:**
```powershell
# Check status of incomplete workflow
python scripts/workflow.py --change-id my-change --title "My Feature" --owner kdejo

# Output shows current state and available options
# [Last completed: Step 3 - Task Breakdown]
# [Files saved: proposal.md, spec.md, tasks.md]
```

All workflow state is persisted to:
- `.checkpoints/state.json` - Complete history with timestamps
- `.checkpoints/checkpoint-*/` - Directory per step with snapshots

#### Environment Validation (v0.1.42+)

**Pre-flight checks ensure tools are available:**
```powershell
# Validation runs automatically on workflow start
# Checks for:
#   ✓ Python version (requires 3.11+)
#   ✓ Required tools (pytest, ruff, mypy, bandit)
#   ✓ File permissions
#   ✓ Git configuration

# If issues found, workflow displays:
# ⚠️  Environment validation failed:
# - Python 3.10 detected (requires 3.11+)
# - Action: Update Python or create Python 3.11+ venv
```

#### Workflow Steps Overview

| Step | Name | Purpose | Key Output |
|------|------|---------|------------|
| 0 | Create TODOs | Initialize task tracking | `todo.md` |
| 1 | Version Bump | Increment version number | `version_snapshot.md` |
| 2 | Proposal Review | Review high-level proposal | Review feedback |
| 3 | Capability Spec | Define technical specification | `spec.md` |
| 4 | Task Breakdown | Create detailed task list | `tasks.md` |
| 5 | Implementation Checklist | Build implementation plan | Checklist with requirements |
| 6 | Script Generation | Generate test/impl scripts | `test.py`, `implement.py` |
| 7 | Document Review | Final validation of docs | Review report |
| 8-12 | Implementation | Execute feature implementation | Feature code |

#### Common Workflow Patterns

**Pattern 1: Quick local test of workflow logic**
```powershell
# Test workflow steps without modifying anything
python scripts/workflow.py --change-id test-local --step 0 --step 1 --dry-run

# Verify: No files created, [DRY RUN] messages shown
```

**Pattern 2: Development iteration without quality checks**
```powershell
# Skip validation while developing locally
python scripts/workflow.py --change-id dev-feature --skip-quality-gates

# Verify: Warnings shown, feature still created
```

**Pattern 3: Resume after interruption**
```powershell
# Initial run interrupted at step 3
python scripts/workflow.py --change-id my-feature --title "Feature" --owner kdejo
# ... interrupted ...

# Resume from checkpoint
python scripts/workflow.py --change-id my-feature --title "Feature" --owner kdejo
# System detects checkpoint and prompts to resume
```

**Pattern 4: Production-ready workflow with full validation**
```powershell
# Run with all checks enabled (default behavior)
python scripts/workflow.py --change-id release-feature --title "Release Feature" --owner kdejo

# Verify: All quality gates pass, all documents complete
```

### Key Files to Understand

1. **`agent/backend.py`**: FastAPI application entry point with all route definitions
2. **`agent/settings.py`**: Pydantic-based settings with hierarchical configuration
3. **`agent/modelmanager.py`**: Unified interface for different model backends
4. **`agent/embeddings.py`**: Vector embedding operations and caching
5. **`agent/indexing.py`**: Document processing and vector database management
6. **`agent/performance.py`**: Multi-level caching, connection pooling, monitoring
7. **`plugin/main.js`**: Obsidian plugin entry point
8. **`plugin/backendClient.js`**: Plugin-to-backend communication layer

### Common Development Tasks

#### Adding a New API Endpoint

1. Define request/response models in `agent/backend.py` using Pydantic
2. Create service method in appropriate module (e.g., `agent/indexing.py`)
3. Add route handler with dependency injection
4. Add unit tests in `tests/backend/`
5. Add integration test in `tests/integration/`

#### Adding a New Service

1. Create module in `agent/` (e.g., `agent/my_service.py`)
2. Implement `from_settings()` class method
3. Use async/await for all I/O operations
4. Add error handling with HTTPException
5. Create tests in `tests/backend/test_my_service.py`

#### Debugging Performance Issues

1. Check real-time metrics: `GET /api/performance/metrics`
2. Review cache hit rates and pool utilization
3. Check system metrics: `/api/health/detailed`
4. Use trace logging: Set `LOG_LEVEL=debug` and restart backend
5. Run performance tests: `pytest tests/test_performance.py -v`

# Copilot Instructions

## OpenSpec Documentation Governance

This file is governed by OpenSpec documentation requirements:

- All changes tracked via proposals in `openspec/changes/`

- Each change directory must include `proposal.md`, `tasks.md`, and capability spec files

- See `README.md` and `AGENTS.md` for compliance details

Refer to `openspec/specs/project-documentation.md` for full specification.

