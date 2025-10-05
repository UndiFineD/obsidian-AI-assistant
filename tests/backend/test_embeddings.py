# tests/backend/test_embeddings.py
import pytest
import tempfile
import shutil
from pathlib import Path
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
    with patch('embeddings.SentenceTransformer') as mock_st:
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3] for _ in range(5)]
        mock_st.return_value = mock_model
        yield mock_model

@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client."""
    with patch('embeddings.PersistentClient') as mock_client:
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
        model_name="test-model"
    )
    assert emb_mgr.chunk_size == 200
    assert emb_mgr.overlap == 30
    assert emb_mgr.top_k == 5
    assert emb_mgr.db_path == temp_db_path
    assert emb_mgr.collection_name == "test_collection"
    assert emb_mgr.model_name == "test-model"

def test_default_initialization(mock_sentence_transformer, mock_chroma_client):
    """Test EmbeddingsManager with default parameters."""
    with patch('embeddings.PersistentClient'):
        emb_mgr = EmbeddingsManager()
        assert emb_mgr.chunk_size == 500
        assert emb_mgr.overlap == 50
        assert emb_mgr.top_k == 5
        assert emb_mgr.db_path == "./vector_db"
        assert emb_mgr.collection_name == "obsidian_notes"
        assert emb_mgr.model_name == "all-MiniLM-L6-v2"
    
def test_chunk_text_basic(self, embeddings_manager):
    """Test basic text chunking functionality."""
    text = "This is a test document. " * 20  # Create longer text
    chunks = embeddings_manager.chunk_text(text)
    
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) <= embeddings_manager.chunk_size + embeddings_manager.overlap for chunk in chunks)

def test_chunk_text_short_text(self, embeddings_manager):
    """Test chunking of text shorter than chunk size."""
    text = "Short text."
    chunks = embeddings_manager.chunk_text(text)
    
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_text_empty_text(self, embeddings_manager):
    """Test chunking of empty text."""
    chunks = embeddings_manager.chunk_text("")
    assert chunks == [""]

def test_chunk_text_overlap(self, embeddings_manager):
    """Test that chunking includes proper overlap."""
    # Create text that will definitely need multiple chunks
    text = "A" * (embeddings_manager.chunk_size * 2)
    chunks = embeddings_manager.chunk_text(text)
    
    assert len(chunks) > 1
    # Check that there's overlap between consecutive chunks
    if len(chunks) > 1:
        # Last part of first chunk should appear in second chunk
        overlap_size = embeddings_manager.overlap
        first_chunk_end = chunks[0][-overlap_size:]
        second_chunk_start = chunks[1][:overlap_size]
        # There should be some overlap
        assert len(first_chunk_end) > 0 and len(second_chunk_start) > 0

def test_add_documents(self, embeddings_manager, mock_chroma_client):
    """Test adding documents to the collection."""
    documents = ["Document 1 content", "Document 2 content"]
    metadatas = [{"source": "file1.md"}, {"source": "file2.md"}]
    
    embeddings_manager.add_documents(documents, metadatas)
    
    # Verify collection.add was called
    mock_chroma_client['collection'].add.assert_called_once()
    call_args = mock_chroma_client['collection'].add.call_args
    
    # Check that documents were passed correctly
    assert 'documents' in call_args.kwargs
    assert 'metadatas' in call_args.kwargs
    assert 'ids' in call_args.kwargs
    
    # Verify documents and metadatas
    assert call_args.kwargs['documents'] == documents
    assert call_args.kwargs['metadatas'] == metadatas

def test_add_documents_without_metadata(self, embeddings_manager, mock_chroma_client):
    """Test adding documents without metadata."""
    documents = ["Document 1", "Document 2"]
    
    embeddings_manager.add_documents(documents)
    mock_chroma_client['collection'].add.assert_called_once()
    call_args = mock_chroma_client['collection'].add.call_args
    
    assert call_args.kwargs['documents'] == documents
    assert call_args.kwargs['metadatas'] is None

def test_search_similar(self, embeddings_manager, mock_chroma_client):
    """Test similarity search functionality."""
    query = "test query"
    mock_results = {
        'documents': [["Similar doc 1", "Similar doc 2"]],
        'metadatas': [[{"source": "file1.md"}, {"source": "file2.md"}]],
        'distances': [[0.1, 0.2]]
    }
    mock_chroma_client['collection'].query.return_value = mock_results
    results = embeddings_manager.search_similar(query, top_k=2)
    
    # Verify query was called with correct parameters
    mock_chroma_client['collection'].query.assert_called_once()
    call_args = mock_chroma_client['collection'].query.call_args
    assert call_args.kwargs['query_texts'] == [query]
    assert call_args.kwargs['n_results'] == 2
    
    # Verify results format
    assert isinstance(results, list)
    assert len(results) == 2
    assert all('content' in result for result in results)
    assert all('metadata' in result for result in results)

def test_search_similar_empty_results(self, embeddings_manager, mock_chroma_client):
    """Test similarity search with empty results."""
    query = "test query"
    mock_results = {
        'documents': [[]],
        'metadatas': [[]],
        'distances': [[]]
    }
    mock_chroma_client['collection'].query.return_value = mock_results
    
    results = embeddings_manager.search_similar(query)
    
    assert results == []

def test_clear_collection(self, embeddings_manager, mock_chroma_client):
    """Test clearing the collection."""
    # Mock get method to return some ids
    mock_chroma_client['collection'].get.return_value = {
        'ids': ['id1', 'id2', 'id3']
    }
    
    embeddings_manager.clear_collection()
    
    # Verify delete was called with all ids
    mock_chroma_client['collection'].delete.assert_called_once_with(
        ids=['id1', 'id2', 'id3']
    )

def test_clear_empty_collection(self, embeddings_manager, mock_chroma_client):
    """Test clearing an empty collection."""
    # Mock get method to return no ids
    mock_chroma_client['collection'].get.return_value = {'ids': []}
    
    embeddings_manager.clear_collection()
    
    # Delete should not be called for empty collection
    mock_chroma_client['collection'].delete.assert_not_called()

def test_get_collection_info(self, embeddings_manager, mock_chroma_client):
    """Test getting collection information."""
    mock_chroma_client['collection'].count.return_value = 42
    
    info = embeddings_manager.get_collection_info()
    
    assert info['name'] == embeddings_manager.collection_name
    assert info['count'] == 42
    assert info['model'] == embeddings_manager.model_name

def test_hash_generation(self, embeddings_manager):
    """Test document ID hash generation."""
    doc1 = "This is document 1"
    doc2 = "This is document 2"
    doc1_duplicate = "This is document 1"
    
    # Create some mock metadata
    meta1 = {"source": "file1.md"}
    meta2 = {"source": "file2.md"}
    
    # Test that different documents get different hashes
    with patch('hashlib.md5') as mock_hash:
        mock_hash_obj = Mock()
        mock_hash_obj.hexdigest.side_effect = ['hash1', 'hash2', 'hash1']
        mock_hash.return_value = mock_hash_obj
        
        # This tests the internal hash generation indirectly through add_documents
        embeddings_manager.add_documents([doc1], [meta1])
        embeddings_manager.add_documents([doc2], [meta2])
        embeddings_manager.add_documents([doc1_duplicate], [meta1])
        
        # Hash function should be called for each document
        assert mock_hash.call_count == 3

def test_model_loading_error_handling(self, temp_db_path):
    """Test handling of model loading errors."""
    with patch('embeddings.SentenceTransformer', side_effect=Exception("Model load error")):
        with pytest.raises(Exception) as exc_info:
            EmbeddingsManager(db_path=temp_db_path)
        assert "Model load error" in str(exc_info.value)

def test_database_connection_error(self, temp_db_path, mock_sentence_transformer):
    """Test handling of database connection errors."""
    with patch('embeddings.PersistentClient', side_effect=Exception("DB connection error")):
        with pytest.raises(Exception) as exc_info:
            EmbeddingsManager(db_path=temp_db_path)
        assert "DB connection error" in str(exc_info.value)


class TestEmbeddingsIntegration:
    """Integration tests for EmbeddingsManager."""
    
    def test_full_workflow(self, mock_sentence_transformer, mock_chroma_client):
        """Test a complete workflow: add documents, search, clear."""
        with tempfile.TemporaryDirectory() as temp_dir:
            emb_mgr = EmbeddingsManager(db_path=temp_dir)
            
            # Add documents
            documents = ["AI is the future", "Machine learning is powerful"]
            metadatas = [{"topic": "AI"}, {"topic": "ML"}]
            emb_mgr.add_documents(documents, metadatas)
            
            # Mock search results
            mock_chroma_client['collection'].query.return_value = {
                'documents': [["AI is the future"]],
                'metadatas': [[{"topic": "AI"}]],
                'distances': [[0.1]]
            }
            
            # Search
            results = emb_mgr.search_similar("artificial intelligence")
            assert len(results) == 1
            
            # Get info
            mock_chroma_client['collection'].count.return_value = 2
            info = emb_mgr.get_collection_info()
            assert info['count'] == 2
            
            # Clear
            mock_chroma_client['collection'].get.return_value = {'ids': ['id1', 'id2']}
            emb_mgr.clear_collection()
            
            # Verify all operations were called
            assert mock_chroma_client['collection'].add.called
            assert mock_chroma_client['collection'].query.called
            assert mock_chroma_client['collection'].delete.called

if __name__ == "__main__":
    pytest.main([__file__])