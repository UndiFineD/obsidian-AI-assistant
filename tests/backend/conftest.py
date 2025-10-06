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

@pytest.fixture
def mock_all_services():
    """Comprehensive service mocking fixture for reliable test isolation."""
    from unittest.mock import patch, MagicMock
    
    # Create comprehensive mocks for all backend services
    mock_model_manager = MagicMock()
    mock_model_manager.generate.return_value = "Test response from model"
    mock_model_manager.is_ready.return_value = True
    mock_model_manager.get_available_models.return_value = ["test-model"]
    
    mock_cache_manager = MagicMock()
    mock_cache_manager.get_cached_answer.return_value = None
    mock_cache_manager.cache_answer.return_value = True
    
    mock_embeddings_manager = MagicMock()
    mock_embeddings_manager.generate_embeddings.return_value = [0.1, 0.2, 0.3]
    
    mock_vault_indexer = MagicMock()
    mock_vault_indexer.index_vault.return_value = {"files_indexed": 5}
    mock_vault_indexer.search.return_value = [{"content": "test", "score": 0.9}]
    
    with patch('backend.backend.model_manager', mock_model_manager), \
         patch('backend.backend.cache_manager', mock_cache_manager), \
         patch('backend.backend.embeddings_manager', mock_embeddings_manager), \
         patch('backend.backend.vault_indexer', mock_vault_indexer):
        
        yield {
            'model': mock_model_manager,
            'cache': mock_cache_manager,
            'embeddings': mock_embeddings_manager,
            'vault': mock_vault_indexer
        }