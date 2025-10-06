# tests/backend/conftest.py
"""
Global test configuration and fixtures for backend tests.
This ensures proper mocking of ML libraries before any imports happen.
"""
import sys
from unittest.mock import MagicMock
import pytest

# Mock all ML libraries at module level to prevent import errors
mock_modules = {
    'torch': MagicMock(),
    'transformers': MagicMock(),
    'sentence_transformers': MagicMock(),
    'llama_cpp': MagicMock(),
    'vosk': MagicMock(),
    'chromadb': MagicMock(),
    'chromadb.utils': MagicMock(),
    'chromadb.utils.embedding_functions': MagicMock(),
    'faiss': MagicMock(),
    'openai': MagicMock(),
    'anthropic': MagicMock(),
    'dotenv': MagicMock(),
    'PyPDF2': MagicMock(),
    'requests': MagicMock()
}

# Apply mocks globally
for module_name, mock_module in mock_modules.items():
    sys.modules[module_name] = mock_module

# Configure specific mock behaviors
sentence_transformer_mock = MagicMock()
sentence_transformer_mock.encode.return_value = [[0.1, 0.2, 0.3]]
sys.modules['sentence_transformers'].SentenceTransformer = MagicMock(return_value=sentence_transformer_mock)

persistent_client_mock = MagicMock()
sys.modules['chromadb'].PersistentClient = MagicMock(return_value=persistent_client_mock)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure test environment is properly configured."""
    # Mocking already done at module level
    yield