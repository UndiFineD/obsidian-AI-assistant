# conftest.py
"""
Pytest configuration and shared fixtures for Obsidian AI Assistant tests.
"""

import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Generator, Dict

# Add project root to Python path for proper package imports - STRONGER! 💪
project_root = Path(__file__).parent.parent  # Go up one level from tests to project root
sys.path.insert(0, str(project_root))


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
    """Mock Hugging Face Hub functions."""
    with patch('huggingface_hub.login') as mock_login, \
         patch('huggingface_hub.hf_hub_download') as mock_download:
        
        mock_login.return_value = None
        mock_download.return_value = "/fake/path/to/model.bin"
        
        yield {
            'login': mock_login,
            'download': mock_download
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