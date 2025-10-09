# conftest.py
"""
Pytest configuration and shared fixtures for Obsidian AI Assistant tests.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict
from unittest.mock import Mock, patch, MagicMock, mock_open
import unittest.mock as _um
import pytest
# pytest_asyncio ensures plugin is importable

# Ensure Mock behaves like MagicMock so __call__ is also a Mock in tests
_um.Mock = _um.MagicMock
pytest_plugins = ("pytest_asyncio",)

# Add project root to Python path for proper package imports - STRONGER! 💪
project_root = Path(__file__).parent.parent  # Go up one level from tests to project root
sys.path.insert(0, str(project_root))

# ============================================================================
# CRITICAL: PREVENT HUGGINGFACE LIBRARY CONFLICTS
# Mock HuggingFace modules BEFORE any imports can cause metaclass conflicts
# ============================================================================

def create_mock_huggingface_hub():
    """Create comprehensive HuggingFace Hub mock module."""
    hub_mock = MagicMock()
    # Mock login function
    hub_mock.login = MagicMock(return_value=None)
    # Mock download function
    hub_mock.hf_hub_download = MagicMock(return_value="/fake/model/path.bin")
    # Mock other commonly used functions
    hub_mock.snapshot_download = MagicMock(return_value="/fake/model/dir")
    hub_mock.HfApi = MagicMock
    hub_mock.HfFolder = MagicMock
    hub_mock.Repository = MagicMock
    # Mock constants
    hub_mock.HUGGINGFACE_HUB_CACHE = "/fake/cache"
    return hub_mock

def create_mock_transformers():
    """Create comprehensive transformers mock module."""
    transformers_mock = MagicMock()
    # Mock common classes
    transformers_mock.AutoTokenizer = MagicMock
    transformers_mock.AutoModel = MagicMock
    transformers_mock.AutoModelForCausalLM = MagicMock
    transformers_mock.pipeline = MagicMock(return_value=MagicMock())
    return transformers_mock

# Apply module-level mocks BEFORE any other imports
sys.modules['huggingface_hub'] = create_mock_huggingface_hub()
sys.modules['huggingface_hub.login'] = MagicMock()
sys.modules['huggingface_hub._login'] = MagicMock()  # Prevent the problematic _login module
sys.modules['transformers'] = create_mock_transformers()

# Also mock sentence-transformers early
sentence_transformers_mock = MagicMock()
sentence_transformers_mock.SentenceTransformer = MagicMock
sys.modules['sentence_transformers'] = sentence_transformers_mock

# Mock llama_cpp and gpt4all at module level to prevent import issues
def create_mock_llama_cpp():
    """Create mock llama-cpp-python module."""
    mock = MagicMock()
    mock.Llama = MagicMock()
    return mock

def create_mock_gpt4all():
    """Create mock GPT4All module."""
    mock = MagicMock()
    # Mock GPT4All class
    gpt4all_instance = MagicMock()
    gpt4all_instance.generate.return_value = "Mock GPT4All response"
    mock.GPT4All = MagicMock(return_value=gpt4all_instance)
    return mock
    sys.modules['llama_cpp'] = create_mock_llama_cpp()
    sys.modules['gpt4all'] = create_mock_gpt4all()
    print("🔧 HuggingFace library conflicts prevented with early module mocking")

# ============================================================================
# SESSION-SCOPED FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Get the project root directory path."""
    return Path(__file__).parent.parent  # Project root is parent of tests directory

@pytest.fixture(scope="session")
def backend_path(project_root_path: Path) -> Path:
    """Get the backend directory path."""
    return project_root_path / "backend"

# ============================================================================
# FUNCTION-SCOPED FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp(prefix="obsidian_ai_test_")
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Create a temporary file for tests."""
    fd, temp_path = tempfile.mkstemp(prefix="obsidian_ai_test_", suffix=".tmp")
    os.close(fd)
    try:
        yield temp_path
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass

@pytest.fixture
def mock_env_vars() -> Generator[Dict[str, str], None, None]:
    """Provide mock environment variables and clean them up."""
    original_env = os.environ.copy()
    mock_vars = {
        "HF_TOKEN": "test_hf_token_12345",
        "VOSK_MODEL_PATH": "tests/models/vosk-test",
        "TEST_MODE": "true",
        "CUDA_VISIBLE_DEVICES": "-1"  # Disable CUDA for tests
    }
    # Set mock environment variables
    os.environ.update(mock_vars)
    try:
        yield mock_vars
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

# ============================================================================
# MOCK FIXTURES FOR EXTERNAL DEPENDENCIES
# ============================================================================

@pytest.fixture
def mock_sentence_transformers():
    """Mock sentence-transformers SentenceTransformer."""
    with patch('sentence_transformers.SentenceTransformer') as mock:
        mock_instance = Mock()
        mock_instance.encode.return_value = [[0.1, 0.2, 0.3, 0.4]]  # Mock embedding
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB client."""
    with patch('chromadb.PersistentClient') as mock_client:
        # Mock collection
        mock_collection = Mock()
        mock_collection.add.return_value = None
        mock_collection.query.return_value = {
            'documents': [['test document']],
            'distances': [[0.5]],
            'metadatas': [[{'source': 'test'}]]
        }
        mock_collection.count.return_value = 1
        # Mock client
        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client_instance.delete_collection.return_value = None
        mock_client.return_value = mock_client_instance
        
        yield mock_client_instance

@pytest.fixture
def mock_llama_cpp():
    """Mock llama-cpp-python Llama model."""
    with patch('llama_cpp.Llama') as mock:
        mock_instance = Mock()
        mock_instance.create_completion.return_value = {
            'choices': [{'text': 'Mock LLaMA response'}]
        }
        mock_instance.__call__.return_value = {
            'choices': [{'text': 'Mock LLaMA response'}]
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_gpt4all():
    """Mock GPT4All model."""
    with patch('gpt4all.GPT4All') as mock:
        mock_instance = Mock()
        mock_instance.generate.return_value = "Mock GPT4All response"
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_huggingface_hub():
    """Mock Hugging Face Hub functions - enhanced version."""
    # Use the already mocked module from sys.modules
    hub_mock = sys.modules['huggingface_hub']
    # Reset and configure mocks for this test
    hub_mock.login.reset_mock()
    hub_mock.hf_hub_download.reset_mock()
    hub_mock.login.return_value = None
    hub_mock.hf_hub_download.return_value = "/fake/path/to/model.bin"
    yield {
        'login': hub_mock.login,
        'download': hub_mock.hf_hub_download,
        'module': hub_mock
    }

@pytest.fixture
def mock_model_files():
    """Mock model file operations for comprehensive model testing."""
    with patch('os.path.exists') as mock_exists, \
        patch('os.path.isfile') as mock_isfile, \
        patch('os.path.isdir') as mock_isdir, \
        patch('pathlib.Path.exists') as mock_path_exists, \
        patch('pathlib.Path.is_file') as mock_path_isfile, \
        patch('pathlib.Path.is_dir') as mock_path_isdir:
        # Configure realistic file system responses
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        mock_path_exists.return_value = True
        mock_path_isfile.return_value = True
        mock_path_isdir.return_value = True
        yield {
            'exists': mock_exists,
            'isfile': mock_isfile,
            'isdir': mock_isdir,
            'path_exists': mock_path_exists,
            'path_isfile': mock_path_isfile,
            'path_isdir': mock_path_isdir
        }

@pytest.fixture
def mock_model_operations():
    """Comprehensive mocking for model operations including loading and initialization."""
    with patch('backend.modelmanager.load_dotenv') as mock_load_dotenv, \
        patch('backend.modelmanager.HybridLLMRouter') as mock_router, \
        patch('backend.modelmanager.huggingface_hub.login') as mock_hf_login, \
        patch('os.getenv') as mock_getenv, \
        patch('builtins.open', mock_open(read_data="test-model\nother-model\n")) as mock_file:
        # Configure environment and authentication
        mock_load_dotenv.return_value = True
        mock_getenv.side_effect = lambda key, default=None: {
            'HF_TOKEN': 'test_token_12345',
            'HUGGINGFACE_TOKEN': 'test_token_12345'
        }.get(key, default)
        mock_hf_login.return_value = None
        # Configure router
        mock_router_instance = Mock()
        mock_router_instance.generate.return_value = "Mock model response"
        mock_router_instance.get_available_models.return_value = ["test-model"]
        mock_router_instance.is_ready.return_value = True
        mock_router.return_value = mock_router_instance
        yield {
            'load_dotenv': mock_load_dotenv,
            'router': mock_router_instance,
            'hf_login': mock_hf_login,
            'getenv': mock_getenv,
            'open': mock_file
        }

@pytest.fixture
def mock_vosk():
    """Mock Vosk speech recognition."""
    with patch('vosk.Model') as mock_model, \
        patch('vosk.KaldiRecognizer') as mock_recognizer:
        # Mock model
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        # Mock recognizer
        mock_recognizer_instance = Mock()
        mock_recognizer_instance.AcceptWaveform.return_value = True
        mock_recognizer_instance.Result.return_value = '{"text": "hello world"}'
        mock_recognizer_instance.FinalResult.return_value = '{"text": "final text"}'
        mock_recognizer.return_value = mock_recognizer_instance
        yield {
            'model': mock_model_instance,
            'recognizer': mock_recognizer_instance
        }

@pytest.fixture
def mock_requests():
    """Mock requests library for web requests."""
    with patch('requests.get') as mock_get, \
        patch('requests.post') as mock_post:
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.content = b"Test content"
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.json.return_value = {'status': 'success'}
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        yield {
            'get': mock_get,
            'post': mock_post,
            'response': mock_response
        }

# ============================================================================
# FILE SYSTEM FIXTURES
# ============================================================================

@pytest.fixture
def sample_markdown_files(temp_dir: str) -> Dict[str, str]:
    """Create sample markdown files for testing."""
    files = {}
    # Sample note 1
    note1_content = """# Sample Note 1

This is a test note with some content.

## Section 1
Important information here.

#tag1 #tag2
"""
    note1_path = os.path.join(temp_dir, "note1.md")
    with open(note1_path, 'w', encoding='utf-8') as f:
        f.write(note1_content)
    files['note1'] = note1_path
    # Sample note 2
    note2_content = """# Sample Note 2

Another test note with different content.

- List item 1
- List item 2

[[Sample Note 1]]
"""
    note2_path = os.path.join(temp_dir, "note2.md")
    with open(note2_path, 'w', encoding='utf-8') as f:
        f.write(note2_content)
    files['note2'] = note2_path
    return files

@pytest.fixture
def sample_pdf_file(temp_dir: str) -> str:
    """Create a sample PDF file for testing (mock data)."""
    pdf_path = os.path.join(temp_dir, "sample.pdf")
    # Create a fake PDF file (just bytes that represent PDF structure)
    pdf_content = b"%PDF-1.4\n%Mock PDF content for testing\nendobj\n%%EOF"
    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)
    return pdf_path

@pytest.fixture
def mock_vault_structure(temp_dir: str) -> str:
    """Create a mock Obsidian vault structure."""
    vault_path = os.path.join(temp_dir, "test_vault")
    os.makedirs(vault_path, exist_ok=True)
    # Create .obsidian directory
    obsidian_dir = os.path.join(vault_path, ".obsidian")
    os.makedirs(obsidian_dir, exist_ok=True)
    # Create some sample notes
    notes = [
        ("Daily Note 2024-01-15.md", "# Daily Note\n\nToday's tasks:\n- Review code\n- Write tests"),
        ("Project Overview.md", "# Project Overview\n\nThis is the main project file."),
        ("Meeting Notes.md", "# Meeting Notes\n\nDiscussed testing strategy.")
    ]
    for filename, content in notes:
        file_path = os.path.join(vault_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    return vault_path

# ============================================================================
# MODEL FIXTURES FOR MODEL MANAGER TESTS
# ============================================================================

@pytest.fixture
def temp_models_dir() -> Generator[str, None, None]:
    """Temporary models directory for tests expecting a models_dir path."""
    d = tempfile.mkdtemp(prefix="models_")
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)

@pytest.fixture
def mock_models_file(temp_models_dir: str) -> str:
    """Create a simple models.txt file in the temporary models directory."""
    path = Path(temp_models_dir) / "models.txt"
    content = "\n".join([
        "gpt4all-lora",
        "llama-7b-q4",
        "code-llama-13b",
    ])
    path.write_text(content, encoding="utf-8")
    return str(path)

# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture
def mock_config():
    """Provide mock configuration for tests."""
    return {
        'backend_url': 'http://localhost:8000',
        'models_dir': './models',
        'cache_dir': './cache',
        'vault_path': './vault',
        'max_tokens': 256,
        'temperature': 0.7,
        'chunk_size': 512,
        'chunk_overlap': 50,
        'cache_ttl': 3600,
        'enable_encryption': False
    }

@pytest.fixture
def mock_fastapi_client():
    """Create a mock FastAPI test client."""
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    
    # Create minimal FastAPI app for testing
    app = FastAPI()
    @app.get("/health")
    def health():
        return {"status": "healthy"}
    return TestClient(app)

@pytest.fixture
def mock_all_services():
    """Comprehensive service mocking fixture for reliable test isolation across all test types."""
    # Create comprehensive mocks for all backend services
    mock_model_manager = MagicMock()
    mock_model_manager.generate.return_value = "Test response from model"
    mock_model_manager.is_ready.return_value = True
    mock_model_manager.get_available_models.return_value = ["test-model"]
    mock_model_manager.initialize.return_value = True
    mock_model_manager.cleanup.return_value = True
    mock_cache_manager = MagicMock()
    mock_cache_manager.get_cached_answer.return_value = None
    mock_cache_manager.cache_answer.return_value = True
    mock_cache_manager.clear_cache.return_value = True
    mock_embeddings_manager = MagicMock()
    mock_embeddings_manager.generate_embeddings.return_value = [0.1, 0.2, 0.3]
    mock_embeddings_manager.is_ready.return_value = True
    mock_embeddings_manager.initialize.return_value = True
    mock_vault_indexer = MagicMock()
    mock_vault_indexer.index_vault.return_value = {"files_indexed": 5}
    mock_vault_indexer.search.return_value = [{"content": "test", "score": 0.9}]
    mock_vault_indexer.reindex.return_value = True
    mock_vault_indexer.scan_vault.return_value = {"files_found": 5}
    # Mock file system operations commonly used in tests
    mock_os_path = MagicMock()
    mock_os_path.exists.return_value = True
    mock_os_path.isfile.return_value = True
    mock_os_path.isdir.return_value = True
    with patch('backend.backend.model_manager', mock_model_manager) if 'backend.backend' in sys.modules else patch('builtins.id', lambda x: x), \
        patch('backend.backend.cache_manager', mock_cache_manager) if 'backend.backend' in sys.modules else patch('builtins.id', lambda x: x), \
        patch('backend.backend.emb_manager', mock_embeddings_manager) if 'backend.backend' in sys.modules else patch('builtins.id', lambda x: x), \
        patch('backend.backend.vault_indexer', mock_vault_indexer) if 'backend.backend' in sys.modules else patch('builtins.id', lambda x: x), \
        patch('os.path.exists', mock_os_path.exists), \
        patch('os.path.isfile', mock_os_path.isfile), \
        patch('os.path.isdir', mock_os_path.isdir):
        yield {
            'model_manager': mock_model_manager,
            'cache_manager': mock_cache_manager,
            'emb_manager': mock_embeddings_manager,
            'vault_indexer': mock_vault_indexer,
            'os_path': mock_os_path
        }

# Provide a global 'client' fixture bound to the real backend FastAPI app if available
@pytest.fixture
def client():
    """TestClient for the real backend app when importable, otherwise a minimal app."""
    try:
        # Try to import the app from our backend package/module
        try:
            from backend.backend import app as real_app  # type: ignore
        except Exception:
            # Some tests add backend/ to sys.path and import app at package level
            from backend import app as real_app  # type: ignore
        from fastapi.testclient import TestClient
        return TestClient(real_app)
    except Exception:
        # Fallback minimal app
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        _app = FastAPI()
        @_app.get("/health")
        def _h():
            return {"status": "ok"}
        return TestClient(_app)

# ============================================================================
# PYTEST HOOKS AND CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    # Ensure asyncio plugin is active and mode is auto
    try:
        config.pluginmanager.import_plugin("pytest_asyncio")
    except Exception:
        pass
    try:
        # Prefer ini file, but if not present, set in-memory ini option
        if not config.getini("asyncio_mode"):
            # Set option in the in-memory ini config
            config.inicfg["asyncio_mode"] = "auto"
    except Exception:
        pass
    config.addinivalue_line(
        "markers",
        "unit: mark test as a unit test (fast, isolated)"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test (slower)"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow (model loading, etc.)"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add 'unit' marker to tests in unit test directories
        if "test_" in str(item.fspath) and "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add 'integration' marker to integration tests
        if "integration" in str(item.fspath) or "test_integration" in item.name:
            item.add_marker(pytest.mark.integration)
        # Add 'slow' marker to tests that likely load models
        if any(keyword in item.name.lower() for keyword in ['model', 'llm', 'embedding', 'download']):
            item.add_marker(pytest.mark.slow)

@pytest.fixture(autouse=True)
def test_isolation():
    """Ensure proper test isolation by cleaning up state before and after each test."""
    # Pre-test cleanup - clear any lingering state
    import gc
    import sys
    # Clear any backend modules from cache to prevent state leakage
    modules_to_clear = [k for k in sys.modules.keys() if k.startswith('backend.')]
    for module_name in modules_to_clear:
        if hasattr(sys.modules[module_name], '__dict__'):
            # Reset global variables in backend modules
            module_dict = sys.modules[module_name].__dict__
            for key, value in list(module_dict.items()):
                if key.startswith('_') or key in ['__file__', '__name__', '__package__']:
                    continue
                if callable(value) and not key.isupper():
                    continue  # Skip functions and methods
                # Reset global variables that might hold state
                if key in ['model_manager', 'cache_manager', 'embeddings_manager', 'vault_indexer']:
                    module_dict[key] = None
    
    # Force garbage collection
    gc.collect()
    yield
    # Post-test cleanup
    gc.collect()

@pytest.fixture(autouse=True) 
def cleanup_temp_files():
    """Automatically clean up temporary files after each test."""
    yield
    # Clean up any remaining temporary files using tempfile.gettempdir()
    import glob
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_patterns = [
        os.path.join(temp_dir, "obsidian_ai_test_*"),
        os.path.join(temp_dir, "test_*.tmp"),
        "temp_audio.wav",
        "*.pyc"
    ]
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors