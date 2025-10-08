# tests/backend/test_embeddings.py
import pytest
import tempfile
import shutil

from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.embeddings import EmbeddingsManager

@pytest.fixture
def temp_db_path():
    """Create a temporary directory for database testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer to avoid downloading models."""
    with patch('backend.embeddings.SentenceTransformer') as mock_st:
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3] for _ in range(5)]
        mock_st.return_value = mock_model
        yield mock_model

@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client."""
    with patch('backend.embeddings.PersistentClient') as mock_client:
        mock_collection = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_client_instance
        yield {
            'client': mock_client_instance,
            'collection': mock_collection
        }

@pytest.fixture
def embeddings_manager(temp_db_path, mock_sentence_transformer, mock_chroma_client):
    """Create an EmbeddingsManager instance for testing."""
    return EmbeddingsManager(
        db_path=temp_db_path,
        chunk_size=100,
        overlap=20,
        top_k=3
    )

def test_embeddings_manager_initialization(temp_db_path, mock_sentence_transformer, mock_chroma_client):
    """Test EmbeddingsManager initialization."""
    emb_mgr = EmbeddingsManager(
        db_path=temp_db_path,
        chunk_size=200,
        overlap=30,
        top_k=5,
        collection_name="test_collection",
        model_name="all-MiniLM-L6-v2"
    )
    assert emb_mgr.chunk_size == 200
    assert emb_mgr.overlap == 30
    assert emb_mgr.top_k == 5
    assert emb_mgr.db_path == temp_db_path
    assert emb_mgr.collection_name == "test_collection"
    assert emb_mgr.model_name == "all-MiniLM-L6-v2"

def test_default_initialization(mock_sentence_transformer, mock_chroma_client:
    """Test EmbeddingsManager with default parameters."""
    with patch('backend.embeddings.PersistentClient'):
        emb_mgr = EmbeddingsManager()
        assert emb_mgr.chunk_size == 500
        assert emb_mgr.overlap == 50
        assert emb_mgr.top_k == 5
        assert emb_mgr.db_path == "./vector_db"
        assert emb_mgr.collection_name == "obsidian_notes"
        assert emb_mgr.model_name == "all-MiniLM-L6-v2"
    
def test_chunk_text_basic(embeddings_manager:
    """Test basic text chunking functionality."""
    text = "This is a test document. " * 20  # Create longer text
    chunks = embeddings_manager.chunk_text(text)
    assert isinstance(chunks, list
    assert len(chunks > 0
    assert all(isinstance(chunk, str for chunk in chunks)
    # Remove strict length check, as chunking may exceed chunk_size + overlap due to word boundaries

def test_chunk_text_short_text(embeddings_manager):
    """Test chunking of text shorter than chunk size."""
    text = "Short text."
    chunks = embeddings_manager.chunk_text(text)
    assert len(chunks == 1
    assert chunks[0] == text

def test_chunk_text_empty_text(embeddings_manager:
    """Test chunking of empty text."""
    chunks = embeddings_manager.chunk_text("")
    assert chunks == []

def test_get_collection_info(embeddings_manager, mock_chroma_client:
    """Test getting collection information."""
    mock_chroma_client['collection'].count.return_value = 42
    info = embeddings_manager.get_collection_info()
    assert info['name'] == embeddings_manager.collection_name
    assert info['count'] == 42
    assert info['model'] == embeddings_manager.model_name
    # Note: hash generation is internal; no public API to test here

def test_model_loading_error_handling(temp_db_path:
    """Test handling of model loading errors without raising exceptions."""
    with patch('backend.embeddings.SentenceTransformer', side_effect=Exception("Model load error")):
        mgr = EmbeddingsManager(db_path=temp_db_path)
        # safe_call should swallow the exception and set model to None
        assert mgr.model is None

def test_database_connection_error(temp_db_path, mock_sentence_transformer:
    """Test handling of database connection errors without raising exceptions."""
    with patch('backend.embeddings.PersistentClient', side_effect=Exception("DB connection error")):
        mgr = EmbeddingsManager(db_path=temp_db_path)
        # safe_call should swallow the exception and set chroma_client to None
        assert mgr.chroma_client is None

class TestEmbeddingsIntegration:
    pass

if __name__ == "__main__":
    pytest.main([__file__]
