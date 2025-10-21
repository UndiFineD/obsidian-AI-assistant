# Contributing to Obsidian AI Agent

Welcome to the Obsidian AI Agent project! This guide will help you get up and running quickly, whether you're
fixing bugs, adding features, or improving documentation.

## 🚀 Quick Start (15 minutes to first contribution)

### Prerequisites

- **Python 3.11+**
- **Git** for version control
- **Obsidian** (automatically installed by setup script if missing)
- **Windows PowerShell** (for Windows users) or **Bash** (for Linux/macOS users)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/UndiFineD/obsidian-ai-agent.git
cd obsidian-ai-agent

# Windows setup (creates venv, installs dependencies, downloads models)
./setup.ps1

# Linux/macOS setup
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all dependencies (`requirements.txt`, `requirements-dev.txt`)
- Download AI models for local testing
- Run the test suite to verify everything works
- Install Obsidian if not present

### 2. Verify Installation

```bash
# Run the test suite (should show ~1042 tests passing)
python -m pytest tests/ -v

# Start the backend server
cd agent && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

# Check health endpoint
curl http://localhost:8000/health
```

### 3. Make Your First Change

```bash
# Create a feature branch
git checkout -b fix/my-awesome-fix

# Make your changes (code, docs, tests)
# ... edit files ...

# Run tests to ensure nothing breaks
python -m pytest tests/ -v

# Commit and push
git add .
git commit -m "fix: description of your change"
git push origin fix/my-awesome-fix
```

## 📋 Project Structure

```
obsidian-ai-assistant/
├── agent/                 # FastAPI server and AI services (formerly backend/)
│   ├── backend.py          # Main FastAPI application
│   ├── settings.py         # Configuration management
│   ├── modelmanager.py     # AI model management
│   ├── embeddings.py       # Vector search and embeddings
│   ├── indexing.py         # Document indexing
│   ├── voice.py            # Speech-to-text
│   ├── performance.py      # Caching and optimization
│   ├── security.py         # Authentication and security
│   ├── health_monitoring.py # System health checks and alerts
│   └── enterprise_*.py     # Enterprise features (optional)
├── plugin/                 # Obsidian plugin (vanilla JavaScript)
│   ├── main.js             # Plugin entry point
│   ├── manifest.json       # Plugin metadata
│   ├── backendClient.js    # API client
│   └── styles.css          # Plugin styles
├── models/                 # AI models (root-level, formerly agent/models/)
│   ├── gpt4all/            # GPT4All models
│   ├── embeddings/         # Embedding models
│   └── vosk/               # Voice recognition models
├── tests/                  # Comprehensive test suite (1042+ tests)
│   ├── backend/            # Backend unit tests
│   ├── plugin/             # Plugin tests
│   ├── integration/        # End-to-end tests
│   └── test_performance.py # Load and stress tests
├── docs/                   # Project documentation
│   ├── API_REFERENCE.md    # Complete API documentation
│   ├── PERFORMANCE_BENCHMARKS.md  # Performance testing
│   ├── CONTRIBUTING.md     # This file
│   └── *.md                # Specifications and guides
├── openspec/               # Documentation governance
│   ├── AGENTS.md           # AI agent workflow guide
│   ├── changes/            # Change proposals and deltas
│   └── specs/              # Capability specifications
├── .github/                # GitHub configuration
│   ├── workflows/          # CI/CD automation
│   └── copilot-instructions.md # AI agent instructions
└── scripts/                # Utility scripts
```

### Version 0.1.35 Architecture Changes

**From v0.1.34 to v0.1.35**, major structural improvements were made:

| Aspect | v0.1.34 | v0.1.35 | Reason |
|--------|---------|---------|--------|
| Backend directory | `backend/` | `agent/` | Clearer naming: AI service context |
| Models location | `agent/models/` | `./models/` | Centralized, easier management |
| Module structure | Mixed concerns | Clear separation | Maintainability, testing |
| Test count | ~785 tests | 1042+ tests | Better coverage |
| Performance SLA | Target only | Implemented | Production-ready |
| Health monitoring | Basic | Enhanced | Proactive issue detection |

**Migration Guide**: See `.github/copilot-instructions.md` for complete v0.1.35 migration notes.

## 🧪 Testing Strategy

### Test Categories

- **Unit Tests** (`tests/agent/`, `tests/plugin/`): Fast, isolated tests
- **Integration Tests** (`tests/integration/`): API endpoint tests  
- **Performance Tests** (`tests/test_performance.py`): Load and benchmark tests
- **Security Tests**: Vulnerability and compliance tests

### Running Tests

```bash
# Full test suite (1042+ tests, ~3 minutes)
python -m pytest tests/ -v

# Backend tests only
python -m pytest tests/agent/ -v

# Plugin/frontend tests
python -m pytest tests/plugin/ -v

# Integration tests (requires running backend)
python -m pytest tests/integration/ -v

# Performance tests
python -m pytest tests/test_performance.py -v

# Coverage report (requires pytest-cov)
python -m pytest --cov=agent --cov-report=html --cov-report=term

# Run specific test file
python -m pytest tests/agent/test_backend.py -v

# Run with output on first failure
python -m pytest tests/ -x -v

# Run only tests containing "search" in name
python -m pytest tests/ -k "search" -v
```

### Test Standards

- **Coverage Target**: 85%+ for backend code
- **Test Isolation**: Use mocks for external dependencies (models, APIs)
- **Async Testing**: Use `pytest-asyncio` for async code
- **Performance**: Tests should complete in <3 minutes total
- **Reliability**: Tests must be deterministic and not flaky

### Writing Tests

**Example Unit Test**:
```python
# tests/agent/test_my_feature.py
import pytest
from agent.my_feature import my_function

@pytest.fixture
def test_data():
    return {"input": "test", "expected": "result"}

def test_my_function_basic(test_data):
    result = my_function(test_data["input"])
    assert result == test_data["expected"]

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

def test_error_handling():
    with pytest.raises(ValueError):
        my_function(None)  # Should raise
```

## 💻 Development Workflow

### 1. Setting Up Your Environment

```bash
# Activate the virtual environment
# Windows
.\venv\Scripts\Activate.ps1

# Linux/macOS  
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### 2. Code Quality Standards

#### Python Backend
- **Style**: Follow PEP 8, use `black` formatter (optional)
- **Linting**: `ruff` for fast linting (E, F, W, C, I rules)
- **Security**: `bandit` for vulnerability scanning
- **Type Hints**: Required for all public functions
- **Imports**: Use `isort` for organized imports
- **Module Structure**: Clear separation of concerns, use agent/ paths

#### JavaScript Plugin
- **Style**: 4-space indentation, double quotes
- **Naming**: PascalCase for classes, camelCase for functions
- **Error Handling**: Try-catch blocks with descriptive messages
- **No Build Step**: Vanilla JavaScript, ready-to-use files

#### Quality Commands
```bash
# Python linting and security
ruff check agent/
bandit -r agent/ -f json -o tests/bandit_report.json

# JavaScript validation
node -c plugin/main.js
python fix_js_quality.py  # Auto-fix JS style issues

# Type checking (optional)
mypy agent/ --ignore-missing-imports

# All checks together
echo "=== Python Linting ===" && ruff check agent/ && \
echo "=== Security Scan ===" && bandit -r agent/ && \
echo "=== JavaScript Check ===" && node -c plugin/main.js && \
echo "✅ All checks passed!"
```

### Pre-Submission Code Quality Checklist

Use this checklist before submitting a pull request:

**Code Standards:**
- [ ] Python code follows PEP 8 (`ruff check` passes)
- [ ] No security vulnerabilities (`bandit` scan passes)
- [ ] Type hints on all public functions
- [ ] No unnecessary imports
- [ ] Error messages are descriptive
- [ ] Logging is appropriate (not too verbose)

**Testing:**
- [ ] All new code has unit tests
- [ ] Test coverage ≥85% for new modules
- [ ] All tests pass locally (`pytest tests/ -v`)
- [ ] No flaky or timing-dependent tests
- [ ] Performance tests included for performance-critical code

**Documentation:**
- [ ] Code comments for complex logic
- [ ] Docstrings on classes and functions
- [ ] README updated (if applicable)
- [ ] API documentation updated (if API changes)
- [ ] Error scenarios documented

**Git:**
- [ ] Commit messages follow template
- [ ] Feature branch from main, not develop
- [ ] No merge conflicts
- [ ] No extraneous commits/history cleanup done

**API Changes (if applicable):**
- [ ] Request/response models defined with Pydantic
- [ ] Error responses documented
- [ ] Authentication/authorization defined
- [ ] Rate limiting considered
- [ ] Example cURL request provided

**Plugin Changes (if applicable):**
- [ ] No console errors in Obsidian
- [ ] Works in light and dark themes
- [ ] Mobile responsiveness considered
- [ ] No performance degradation

### 3. Branch Strategy

- **main**: Production-ready code, protected branch
- **develop**: Integration branch for features (if used)
- **feature/**: Feature branches (`feature/add-new-endpoint`)
- **fix/**: Bug fix branches (`fix/auth-token-expiry`)
- **docs/**: Documentation changes (`docs/update-api-reference`)

### 4. Commit Message Format

```
type(scope): brief description

Longer explanation if needed.

Closes #123
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
**Scopes**: `backend`, `plugin`, `docs`, `ci`, `test`

**Examples**:
```
feat(backend): add voice transcription endpoint
fix(plugin): resolve authentication token refresh
docs(api): update OpenAPI schema examples
test(integration): add end-to-end search tests
```

## 📚 OpenSpec Documentation Governance

This project uses **OpenSpec governance** for all major documentation changes. This ensures consistency and quality
across all project documentation.

### What Requires OpenSpec Governance?

- **Core Documentation**: `README.md`, `AGENTS.md`, `.github/copilot-instructions.md`
- **Specifications**: All files in `docs/` that end with `_SPECIFICATION.md`
- **API Changes**: Modifications to `docs/API_REFERENCE.md`
- **Architecture Changes**: Updates to system design or component interaction

### OpenSpec Workflow

#### 1. Check Existing Changes
```bash
# List pending changes
ls openspec/changes/

# Validate current state
python openspec/scripts/validate.py --strict
```

#### 2. Create a Change Proposal
```bash
# Create change directory
mkdir -p openspec/changes/update-contributing-guide/specs/project-documentation

# Create proposal.md
cat > openspec/changes/update-contributing-guide/proposal.md << 'EOF'
# Proposal: Update Contributing Guide

## Summary
Add comprehensive contributor guide with setup instructions, testing workflow, and code quality standards.

## Rationale
New contributors need clear guidance on project setup, testing, and contribution workflow.

## Implementation Approach
Create docs/CONTRIBUTING.md with:
- Quick start guide
- Development environment setup
- Testing standards
- Code quality requirements
- OpenSpec governance workflow

## Validation Criteria
- [ ] Guide enables new contributor onboarding in <15 minutes
- [ ] All development workflows documented
- [ ] OpenSpec governance explained
- [ ] Code quality standards clear
EOF

# Create tasks.md
cat > openspec/changes/update-contributing-guide/tasks.md << 'EOF'
# Implementation Tasks

- [ ] Create docs/CONTRIBUTING.md structure
- [ ] Document quick start workflow
- [ ] Add development environment setup
- [ ] Document testing standards and commands
- [ ] Explain code quality requirements
- [ ] Document OpenSpec governance workflow
- [ ] Add commit message and PR guidelines
EOF

# Create capability spec delta
cat > openspec/changes/update-contributing-guide/specs/project-documentation/spec.md << 'EOF'
## ADDED Requirements

### Requirement: Contributor onboarding documentation
The project SHALL provide comprehensive contributor documentation.

#### Scenario: Quick start for new contributors
- WHEN a new contributor follows the contributing guide
- THEN they SHALL be able to make their first contribution in under 15 minutes

### Requirement: Development environment documentation  
The project SHALL document development setup and testing procedures.

#### Scenario: Environment setup validation
- WHEN following setup instructions
- THEN all tests SHALL pass and development environment SHALL be ready
EOF
```

#### 3. Validate and Apply
```bash
# Validate the change
python openspec/scripts/validate.py update-contributing-guide --strict

# If validation passes, implement the change
# (Create the actual files as documented in the proposal)

# Apply the change (updates baselines)
python openspec/scripts/apply.py update-contributing-guide
```

### Quick Reference for OpenSpec

- **📋 List changes**: `ls openspec/changes/`
- **✅ Validate**: `python openspec/scripts/validate.py <change-id> --strict`
- **🚀 Apply**: `python openspec/scripts/apply.py <change-id>`
- **📚 Guide**: See [`openspec/AGENTS.md`](openspec/AGENTS.md) for detailed workflow

## 🔧 API Development

### Adding New Endpoints

1. **Define the endpoint** in `agent/backend.py`:
```python
@app.post("/api/my-new-endpoint", dependencies=[Depends(require_role("user"))])
async def my_new_endpoint(request: MyRequest):
    """Endpoint description."""
    try:
        # Implementation
        return {"result": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

1. **Add request/response models**:
```python
class MyRequest(BaseModel):
    field1: str
    field2: Optional[int] = None
```

1. **Write tests**:
```python
# tests/agent/test_my_endpoint.py
def test_my_new_endpoint(test_client):
    response = test_client.post("/api/my-new-endpoint", 
                               json={"field1": "test"})
    assert response.status_code == 200
    assert response.json()["result"] == "success"
```

1. **Update API documentation**:
Add the endpoint to `docs/API_REFERENCE.md` with examples.

### Authentication and Authorization

- **Authentication**: Bearer token via `Authorization: Bearer <token>`
- **Roles**: `user` (basic access), `admin` (system management)
- **Test Mode**: Authentication bypassed when `PYTEST_CURRENT_TEST` set
- **Dependencies**: Use `Depends(require_role("user"))` or `Depends(require_role("admin"))`

## 📝 Git Workflow & Best Practices

### Complete Workflow Example

**Step 1: Create Feature Branch**
```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/add-semantic-search-filter
```

**Step 2: Make Changes**
```bash
# Make your code changes
# Edit files, add features, fix bugs

# Check what changed
git status
# Output:
# On branch feature/add-semantic-search-filter
# Changes not staged for commit:
#   modified:   agent/indexing.py
#   modified:   tests/agent/test_search.py
# Untracked files:
#   new_feature.py
```

**Step 3: Stage and Commit**
```bash
# Stage specific files
git add agent/indexing.py tests/agent/test_search.py

# Verify staged changes
git diff --cached

# Commit with descriptive message
git commit -m "feat(search): add semantic filter to search results

- Add similarity_threshold parameter to search endpoint
- Filter results based on configured threshold
- Add integration tests for filter functionality
- Update API documentation with examples

Closes #123"
```

**Step 4: Push and Create Pull Request**
```bash
# Push to remote
git push origin feature/add-semantic-search-filter

# Create PR on GitHub (or use command line)
gh pr create --title "Add semantic search filter" \
  --body "Adds configurable similarity threshold filtering"
```

**Step 5: Handle Review Comments**
```bash
# Make requested changes
# Edit files based on feedback

# Commit additional changes
git commit -m "refactor(search): address PR feedback

- Improve threshold validation
- Add unit tests for edge cases
- Update documentation clarity"

# Push updates (same branch)
git push origin feature/add-semantic-search-filter
```

**Step 6: Merge After Approval**
```bash
# Option 1: Merge via GitHub UI (recommended)
# Click "Merge pull request" on GitHub

# Option 2: Command line merge
git checkout main
git pull origin main
git merge --no-ff feature/add-semantic-search-filter
git push origin main

# Delete feature branch
git branch -d feature/add-semantic-search-filter
git push origin --delete feature/add-semantic-search-filter
```

### Commit Message Template

Use this template for consistent, clear commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactor without feature changes
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling

**Scopes** (optional but recommended):
- `backend`: Agent/FastAPI changes
- `plugin`: Obsidian plugin changes
- `docs`: Documentation
- `test`: Test infrastructure
- `ci`: CI/CD configuration

**Examples**:
```bash
git commit -m "feat(backend): add voice transcription endpoint"
git commit -m "fix(plugin): resolve UI rendering bug in dark mode"
git commit -m "docs(api): update API reference with new endpoints"
git commit -m "test(integration): add end-to-end search tests"
git commit -m "refactor(performance): optimize cache invalidation logic"
```

### Handling Merge Conflicts

**Scenario: Merge conflict in agent/backend.py**

```bash
# Try to merge
git merge origin/main
# Conflict in agent/backend.py

# See conflicting files
git status
# Both modified: agent/backend.py

# Edit the file to resolve conflict
# Look for conflict markers:
# <<<<<<< HEAD
# your changes
# =======
# their changes
# >>>>>>> origin/main

# After editing, stage the file
git add agent/backend.py

# Complete the merge
git commit -m "Merge origin/main into feature branch"
git push origin feature/branch-name
```

### Keeping Fork in Sync

```bash
# Add upstream remote (one-time)
git remote add upstream https://github.com/UndiFineD/obsidian-ai-assistant.git

# Fetch latest changes
git fetch upstream main

# Update your main branch
git checkout main
git rebase upstream/main
git push origin main --force-with-lease

# Update feature branches
git checkout feature/your-feature
git rebase main
```

### Code Quality Checklist Before Push

```bash
# 1. Run tests locally
python -m pytest tests/ -v
# All tests should pass

# 2. Check code style
ruff check agent/

# 3. Security scan
bandit -r agent/

# 4. Type checking (optional)
mypy agent/ --ignore-missing-imports

# 5. Review your changes
git diff origin/main

# Only then push
git push origin feature/your-feature
```

## 🎯 Performance Guidelines

### Performance Targets (SLA)

- **Tier 1**: <100ms (health, status, config)
- **Tier 2**: <500ms (cached operations, simple search)
- **Tier 3**: <2s (AI generation, document search)
- **Tier 4**: <10s (web analysis, complex operations)
- **Tier 5**: <60s (vault reindexing, model loading)

### Optimization Patterns

```python
# Use caching for expensive operations
@cached(ttl=3600, key_func=lambda req: f"cache_key:{req.id}")
def expensive_operation(request):
    return process_request(request)

# Use connection pooling
pool = get_connection_pool("models", create_model_connection, 
                          min_size=1, max_size=3)

# Use background tasks for heavy work
@app.post("/api/heavy-task")
async def heavy_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_heavy_task)
    return {"status": "processing"}
```

### Performance Testing

```bash
# Run performance tests
python -m pytest tests/test_performance.py -v

# Load testing with locust
python -m locust -f tests/load_test.py

# Benchmark specific endpoints
python scripts/benchmark_endpoints.py
```

## 🏗️ CI/CD Pipeline

### GitHub Actions Workflows

- **ci.yml**: Main CI pipeline (linting, testing, security, build)
- **test-backend.yml**: Backend-specific tests with coverage
- **benchmark.yml**: Performance benchmarking
- **openspec-validate.yml**: Documentation governance validation
- **openspec-pr-validate.yml**: PR-specific OpenSpec validation

### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Hooks configuration (.pre-commit-config.yaml):
# - ruff (linting)
# - bandit (security) 
# - black (formatting, optional)
# - mypy (type checking)
```

### Quality Gates

- **✅ All tests pass** (785+ tests)
- **✅ Coverage ≥85%** for backend code
- **✅ No security vulnerabilities** (bandit scan)
- **✅ Code quality standards** (ruff linting)
- **✅ OpenSpec validation** (if docs changed)

## 🔒 Security Guidelines

### Security Standards

- **Input Validation**: All user inputs validated with Pydantic models
- **Authentication**: JWT tokens with role-based access control
- **Rate Limiting**: API endpoints protected from abuse
- **CSRF Protection**: CSRF tokens for state-changing operations
- **Data Sanitization**: All outputs sanitized to prevent XSS

### Security Testing

```bash
# Security vulnerability scan
bandit -r agent/ -f json -o tests/bandit_report.json

# Dependency vulnerability check (if safety installed)
safety check

# Rate limiting tests
python test_rate_limiting.py
```

### Reporting Security Issues

🔒 **Please report security vulnerabilities privately via GitHub Security Advisories or email the maintainers.**

## 🤝 Pull Request Guidelines

### Before Submitting

- [ ] All tests pass locally (`python -m pytest tests/ -v`)
- [ ] Code follows quality standards (`ruff check agent/`)
- [ ] Security scan passes (`bandit -r agent/`)
- [ ] Documentation updated (if applicable)
- [ ] OpenSpec governance followed (for doc changes)

### PR Description Template

```markdown
## Summary
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks**: CI pipeline must pass
2. **Code Review**: At least one maintainer review required
3. **Documentation**: OpenSpec validation for doc changes
4. **Testing**: New features must include tests
5. **Security**: Security-sensitive changes get additional review

## 📞 Getting Help

### Resources

- **📖 API Documentation**: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)
- **🏗️ Architecture**: [`docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md`](docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md)
- **🧪 Testing Guide**: [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md)
- **🚀 Performance**: [`docs/PERFORMANCE_BENCHMARKS.md`](docs/PERFORMANCE_BENCHMARKS.md)
- **🤖 AI Agent Guide**: [`openspec/AGENTS.md`](openspec/AGENTS.md)

### Support Channels

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/UndiFineD/obsidian-ai-agent/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/UndiFineD/obsidian-ai-agent/discussions)
- **📚 Documentation Issues**: Use OpenSpec governance workflow
- **🤝 General Questions**: GitHub Discussions

### Common Issues

#### Setup Problems
```bash
# Python version issues
python --version  # Should be 3.11+

# Virtual environment issues
rm -rf venv
python -m venv venv
# Re-run setup script

# Dependency conflicts
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Test Failures
```bash
# Clear cache and retry
rm -rf __pycache__ agent/__pycache__ tests/__pycache__
python -m pytest tests/ -v --tb=short

# Run specific test file
python -m pytest tests/agent/test_backend.py -v

# Skip slow tests
python -m pytest tests/ -v -m "not slow"
```

#### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend manually
cd backend
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

# Check logs for errors
tail -f agent/logs/app.log
```

## 🌟 Recognition

Contributors are recognized in:

- **Git History**: All contributions tracked in commit history
- **GitHub Contributors**: Automatic recognition on GitHub
- **Release Notes**: Major contributors mentioned in releases
- **Documentation**: Contributors credited in relevant docs

## 📄 License

This project is licensed under the MIT License. By contributing, you agree that your contributions will be licensed
under the same license.

---

**Happy Contributing! 🚀**

Thank you for helping make Obsidian AI Agent better for everyone. Whether you're fixing a typo, adding a feature,
or improving documentation, every contribution matters.

