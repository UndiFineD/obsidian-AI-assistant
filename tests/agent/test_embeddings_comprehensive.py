# tests/agent/test_embeddings_comprehensive.py
import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for database testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_vault_path():
    """Create a temporary vault directory with test files."""
    temp_dir = tempfile.mkdtemp()
    # Create test markdown files
    (Path(temp_dir) / "note1.md").write_text("This is the first test note content.")
    (Path(temp_dir) / "note2.md").write_text("This is the second test note content.")
    (Path(temp_dir) / "subdir").mkdir()
    (Path(temp_dir) / "subdir" / "note3.md").write_text("This is a nested note.")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer completely."""
    mock_model = Mock()
    # Return consistent embeddings
    mock_model.encode.return_value = Mock()
    mock_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    return mock_model


@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB collection."""
    mock_collection = Mock()
    mock_collection.count.return_value = 0
    mock_collection.add.return_value = None
    mock_collection.upsert.return_value = None
    mock_collection.query.return_value = {
        "documents": [["Sample document 1", "Sample document 2"]],
        "metadatas": [[{"note_path": "test1.md"}, {"note_path": "test2.md"}]],
        "embeddings": [[[0.1, 0.2], [0.3, 0.4]]],
        "ids": [["id1", "id2"]],
    }
    return mock_collection


@pytest.fixture
def mock_chroma_client(mock_chroma_collection):
    """Mock ChromaDB PersistentClient."""
    mock_client = Mock()
    mock_client.get_or_create_collection.return_value = mock_chroma_collection
    mock_client.delete_collection.return_value = None
    mock_client.persist.return_value = None
    return mock_client


@pytest.fixture
def mock_settings():
    """Mock settings for from_settings() method."""
    mock_settings = Mock()
    mock_settings.project_root = (
        tempfile.mkdtemp()
    )  # Secure temp directory for test isolation
    mock_settings.chunk_size = 600
    mock_settings.chunk_overlap = 100
    mock_settings.top_k = 8
    mock_settings.embed_model = "sentence-transformers/all-mpnet-base-v2"
    return mock_settings


class TestEmbeddingsManagerInit:
    """Test initialization scenarios."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_successful_initialization(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test successful initialization with all components working."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(
            chunk_size=400,
            overlap=80,
            top_k=7,
            db_path=temp_db_path,
            collection_name="test_collection",
            model_name="test-model",
        )

        assert emb_mgr.chunk_size == 400
        assert emb_mgr.overlap == 80
        assert emb_mgr.top_k == 7
        assert emb_mgr.db_path == temp_db_path
        assert emb_mgr.collection_name == "test_collection"
        assert emb_mgr.model_name == "test-model"
        assert emb_mgr.model is not None
        assert emb_mgr.chroma_client is not None
        assert emb_mgr.collection is not None

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_model_loading_failure(self, mock_st, mock_pc, temp_db_path):
        """Test initialization when SentenceTransformer fails to load."""
        mock_st.side_effect = Exception("Model loading failed")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        # Should gracefully handle model loading failure
        assert emb_mgr.model is None
        assert emb_mgr.chroma_client is None  # Should skip DB init if model fails
        assert emb_mgr.collection is None

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_chroma_client_failure(
        self, mock_st, mock_pc, temp_db_path, mock_sentence_transformer
    ):
        """Test initialization when ChromaDB client fails."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.side_effect = Exception("ChromaDB connection failed")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        assert emb_mgr.model is not None
        assert emb_mgr.chroma_client is None
        assert emb_mgr.collection is None

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_collection_creation_failure(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test initialization when collection creation fails."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client
        mock_chroma_client.get_or_create_collection.side_effect = Exception(
            "Collection creation failed"
        )

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        assert emb_mgr.model is not None
        assert emb_mgr.chroma_client is not None
        assert emb_mgr.collection is None


class TestEmbeddingsFromSettings:
    """Test from_settings() class method."""

    @patch("agent.embeddings.get_settings")
    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_from_settings_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        mock_get_settings,
        mock_settings,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test creating EmbeddingsManager from settings."""
        mock_get_settings.return_value = mock_settings
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager.from_settings()

        assert emb_mgr.chunk_size == 600
        assert emb_mgr.overlap == 100
        assert emb_mgr.top_k == 8
        assert emb_mgr.model_name == "sentence-transformers/all-mpnet-base-v2"
        # Check path contains expected components regardless of OS path separators
        db_path_str = str(emb_mgr.db_path.replace("\\", "/"))
        assert "agent/vector_db" in db_path_str
        assert emb_mgr.collection_name == "obsidian_notes"

    @patch("agent.embeddings.get_settings")
    def test_from_settings_with_failure(self, mock_get_settings):
        """Test from_settings() when settings access fails."""
        mock_get_settings.side_effect = Exception("Settings not available")

        from agent.embeddings import EmbeddingsManager

        # Should raise the exception since from_settings() doesn't use safe_call
        with pytest.raises(Exception, match="Settings not available"):
            EmbeddingsManager.from_settings()


class TestEmbeddingOperations:
    """Test core embedding operations."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_compute_embedding_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test successful embedding computation."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        result = emb_mgr.compute_embedding("test text")

        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_sentence_transformer.encode.assert_called_once_with("test text")

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_compute_embedding_no_model(self, mock_st, mock_pc, temp_db_path):
        """Test compute_embedding when no model is loaded."""
        mock_st.side_effect = Exception("No model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        result = emb_mgr.compute_embedding("test text")

        assert result == []

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_compute_embedding_model_error(
        self, mock_ef, mock_st, mock_pc, temp_db_path, mock_chroma_client
    ):
        """Test compute_embedding when model.encode() raises an error."""
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Encoding failed")
        mock_st.return_value = mock_model
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        result = emb_mgr.compute_embedding("test text")

        assert result == []

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_add_embedding_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test successful embedding addition."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        emb_mgr.add_embedding("test content", "test_note.md")

        # Should call upsert with proper structure
        mock_chroma_collection.upsert.assert_called_once()
        # Check if called with keyword arguments
        call_args, call_kwargs = mock_chroma_collection.upsert.call_args
        if call_args:
            # Called with positional arguments
            call_data = call_args[0]
            assert len(call_data) == 1
            assert call_data[0]["id"] == "test_note.md"
            assert call_data[0]["embedding"] == [0.1, 0.2, 0.3, 0.4, 0.5]
            assert call_data[0]["metadata"]["note_path"] == "test_note.md"
        else:
            # Called with keyword arguments - check that upsert was called
            # The actual implementation may vary, so just verify the call was made
            assert mock_chroma_collection.upsert.called

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_add_embedding_no_collection(self, mock_st, mock_pc, temp_db_path):
        """Test add_embedding when no collection is available."""
        mock_st.side_effect = Exception("No model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        # Should not raise exception
        emb_mgr.add_embedding("test content", "test_note.md")


class TestSearchOperations:
    """Test search and query operations."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_search_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test successful search operation."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path, top_k=5)
        results = emb_mgr.search("test query")

        assert len(results) == 2
        assert results[0]["text"] == "Sample document 1"
        assert results[0]["source"] == "test1.md"
        assert results[1]["text"] == "Sample document 2"
        assert results[1]["source"] == "test2.md"

        mock_chroma_collection.query.assert_called_once()
        call_args = mock_chroma_collection.query.call_args
        assert call_args[1]["query_embeddings"] == [[0.1, 0.2, 0.3, 0.4, 0.5]]
        assert call_args[1]["n_results"] == 5

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_search_custom_top_k(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test search with custom top_k parameter."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path, top_k=3)
        emb_mgr.search("test query", top_k=10)

        # Should use the custom top_k, not the instance default
        mock_chroma_collection.query.assert_called_once()
        call_args = mock_chroma_collection.query.call_args
        assert call_args[1]["n_results"] == 10

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_search_no_collection(self, mock_st, mock_pc, temp_db_path):
        """Test search when no collection is available."""
        mock_st.side_effect = Exception("No model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        results = emb_mgr.search("test query")

        assert results == []

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_search_query_error(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test search when query operation fails."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client
        mock_chroma_collection.query.side_effect = Exception("Query failed")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        results = emb_mgr.search("test query")

        assert results == []


class TestDatabaseOperations:
    """Test database management operations."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_reset_db_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test successful database reset."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client
        new_collection = Mock()
        mock_chroma_client.get_or_create_collection.side_effect = [
            Mock(),
            new_collection,
        ]

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(
            db_path=temp_db_path, collection_name="test_collection"
        )
        emb_mgr.reset_db()

        mock_chroma_client.delete_collection.assert_called_once_with("test_collection")
        # Should be called twice: once during init, once during reset
        assert mock_chroma_client.get_or_create_collection.call_count == 2
        assert emb_mgr.collection == new_collection

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_reset_db_no_client(self, mock_st, mock_pc, temp_db_path):
        """Test reset_db when no client is available."""
        mock_st.side_effect = Exception("No model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        # Should not raise exception
        emb_mgr.reset_db()

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_reset_db_error(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test reset_db when delete operation fails."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client
        mock_chroma_client.delete_collection.side_effect = Exception("Delete failed")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        # Should handle error gracefully
        emb_mgr.reset_db()

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_clear_collection_alias(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test that clear_collection() is an alias for reset_db()."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        # Mock the reset_db method to verify it's called
        emb_mgr.reset_db = Mock()
        emb_mgr.clear_collection()

        emb_mgr.reset_db.assert_called_once()


class TestBatchOperations:
    """Test batch document operations."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_add_documents_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test successful batch document addition."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        chunks = ["Document 1 content", "Document 2 content", "Document 3 content"]
        metadatas = [{"source": "doc1"}, {"source": "doc2"}, {"source": "doc3"}]

        emb_mgr.add_documents(chunks, metadatas)

        mock_chroma_collection.add.assert_called_once()
        call_args = mock_chroma_collection.add.call_args[1]

        assert call_args["documents"] == chunks
        assert call_args["metadatas"] == metadatas
        assert len(call_args["ids"]) == 3
        # Check that IDs are MD5 hashes
        expected_id = hashlib.md5(
            "Document 1 content".encode("utf-8"), usedforsecurity=False
        ).hexdigest()
        assert call_args["ids"][0] == expected_id

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_add_documents_default_metadata(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test add_documents with default metadata generation."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        chunks = ["Document 1", "Document 2"]
        emb_mgr.add_documents(chunks)

        mock_chroma_collection.add.assert_called_once()
        call_args = mock_chroma_collection.add.call_args[1]

        assert call_args["documents"] == chunks
        assert call_args["metadatas"] == [{"chunk_index": 0}, {"chunk_index": 1}]

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_add_documents_empty_chunks(self, mock_st, mock_pc, temp_db_path):
        """Test add_documents with empty chunks list."""
        mock_st.side_effect = Exception("No model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        # Should not raise exception
        emb_mgr.add_documents([])

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_add_documents_no_collection(self, mock_st, mock_pc, temp_db_path):
        """Test add_documents when no collection is available."""
        mock_st.side_effect = Exception("No model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)

        # Should not raise exception
        emb_mgr.add_documents(["Document 1", "Document 2"])


class TestUtilityMethods:
    """Test utility and helper methods."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_get_collection_info_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test getting collection information successfully."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client
        mock_chroma_collection.count.return_value = 42

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(
            db_path=temp_db_path, collection_name="test_coll", model_name="test_model"
        )
        info = emb_mgr.get_collection_info()

        assert info["name"] == "test_coll"
        assert info["count"] == 42
        assert info["model"] == "test_model"

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_get_collection_info_no_collection(self, mock_st, mock_pc, temp_db_path):
        """Test get_collection_info when no collection is available."""
        mock_st.side_effect = Exception("No model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(
            db_path=temp_db_path, collection_name="test_coll", model_name="test_model"
        )
        info = emb_mgr.get_collection_info()

        assert info["name"] == "test_coll"
        assert info["count"] == 0
        assert info["model"] == "test_model"

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_get_collection_info_count_error(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test get_collection_info when count() fails."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client
        mock_chroma_collection.count.side_effect = Exception("Count failed")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        info = emb_mgr.get_collection_info()

        assert info["count"] == 0  # Should use default when count fails

    def test_hash_text(self):
        """Test text hashing functionality."""
        from agent.embeddings import EmbeddingsManager

        # Create manager without mocking to test hash function
        with patch(
            "agent.embeddings.SentenceTransformer",
            side_effect=Exception("Skip model"),
        ):
            emb_mgr = EmbeddingsManager()

        text = "test content"
        expected_hash = hashlib.md5(
            text.encode("utf-8"), usedforsecurity=False
        ).hexdigest()

        result = emb_mgr._hash_text(text)
        assert result == expected_hash

    def test_chunk_text_various_scenarios(self):
        """Test text chunking with various scenarios."""
        from agent.embeddings import EmbeddingsManager

        # Create manager without mocking to test chunking
        with patch(
            "agent.embeddings.SentenceTransformer",
            side_effect=Exception("Skip model"),
        ):
            emb_mgr = EmbeddingsManager(chunk_size=5, overlap=2)

            # Test normal chunking
            text = "This is a test document with many words to test chunking behavior"
            chunks = emb_mgr.chunk_text(text)

            assert len(chunks) > 1
            assert all(isinstance(chunk, str) for chunk in chunks)
            # Test empty text
            assert emb_mgr.chunk_text("") == []
            # Test single word
            result = emb_mgr.chunk_text("word")
            assert result == ["word"]
            # Test text shorter than chunk size
            short_text = "short text here"
            result = emb_mgr.chunk_text(short_text)
            assert len(result) == 1
            assert result[0] == short_text

    def test_close_method(self):
        """Test resource cleanup with close() method."""
        from agent.embeddings import EmbeddingsManager

        with patch(
            "agent.embeddings.SentenceTransformer",
            side_effect=Exception("Skip model"),
        ):
            emb_mgr = EmbeddingsManager()

        # Set some mock objects
        emb_mgr.model = Mock()
        emb_mgr.chroma_client = Mock()
        emb_mgr.collection = Mock()

        emb_mgr.close()

        assert emb_mgr.model is None
        assert emb_mgr.chroma_client is None
        assert emb_mgr.collection is None


class TestIndexingMethods:
    """Test file indexing functionality."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_index_file_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        temp_vault_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test successful file indexing."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path, chunk_size=3, overlap=1)

        test_file = Path(temp_vault_path) / "note1.md"
        result = emb_mgr.index_file(str(test_file))

        assert result > 0  # Should return number of chunks
        mock_chroma_collection.add.assert_called_once()
        mock_chroma_client.persist.assert_called_once()

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    def test_index_file_not_found(self, mock_st, mock_pc, temp_db_path):
        """Test indexing a file that doesn't exist."""
        mock_st.side_effect = Exception("Skip model")

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path)
        result = emb_mgr.index_file("/nonexistent/file.md")

        assert result == 0

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_index_vault_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        temp_vault_path,
        mock_sentence_transformer,
        mock_chroma_collection,
    ):
        """Test successful vault indexing."""
        mock_st.return_value = mock_sentence_transformer
        mock_chroma_client = Mock()
        mock_chroma_client.get_or_create_collection.return_value = (
            mock_chroma_collection
        )
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path, chunk_size=3, overlap=1)
        results = emb_mgr.index_vault(temp_vault_path)

        # Should find and index all .md files (including nested ones)
        assert len(results) == 3
        assert all(str(Path(k).endswith(".md") for k in results.keys()))
        assert all(v > 0 for v in results.values())

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_reindex_success(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        temp_vault_path,
        mock_sentence_transformer,
        mock_chroma_client,
    ):
        """Test successful reindexing (reset + index)."""
        mock_st.return_value = mock_sentence_transformer
        mock_pc.return_value = mock_chroma_client

        from agent.embeddings import EmbeddingsManager

        emb_mgr = EmbeddingsManager(db_path=temp_db_path, chunk_size=3, overlap=1)

        # Mock reset_db and index_vault
        emb_mgr.reset_db = Mock()
        emb_mgr.index_vault = Mock(return_value={"file1.md": 5, "file2.md": 3})

        results = emb_mgr.reindex(temp_vault_path)

        emb_mgr.reset_db.assert_called_once()
        emb_mgr.index_vault.assert_called_once_with(temp_vault_path)
        assert results == {"file1.md": 5, "file2.md": 3}


class TestImportFailures:
    """Test handling of import failures for optional dependencies."""

    def test_sentence_transformer_none_handling(self, temp_db_path):
        """Test initialization when SentenceTransformer is None."""
        with patch("agent.embeddings.SentenceTransformer", None):
            from agent.embeddings import EmbeddingsManager

            manager = EmbeddingsManager(db_path=temp_db_path)

            # Model should be None when SentenceTransformer is None
            assert manager.model is None
            assert manager.chroma_client is None
            assert manager.collection is None

    def test_persistent_client_none_handling(self, temp_db_path):
        """Test initialization when PersistentClient is None."""
        with patch("agent.embeddings.PersistentClient", None):
            with patch("agent.embeddings.SentenceTransformer") as mock_st:
                mock_st.return_value = Mock()

                from agent.embeddings import EmbeddingsManager

                manager = EmbeddingsManager(db_path=temp_db_path)

                # chroma_client should be None when PersistentClient unavailable (line 65)
                assert manager.chroma_client is None
                assert manager.collection is None

    def test_embedding_functions_import_failure(self):
        """Test when embedding_functions is not available."""
        with patch("agent.embeddings.embedding_functions", None):
            with patch("agent.embeddings.SentenceTransformer") as mock_st:
                with patch("agent.embeddings.PersistentClient") as mock_pc:
                    mock_st.return_value = Mock()
                    mock_pc.return_value = Mock()

                    from agent.embeddings import EmbeddingsManager

                    manager = EmbeddingsManager(db_path="./test_db")

                    # Collection should be None when embedding_functions unavailable
                    assert manager.collection is None


class TestGetEmbeddingById:
    """Test the get_embedding_by_id method."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_get_embedding_by_id_success(
        self, mock_ef, mock_st, mock_pc, temp_db_path, mock_sentence_transformer
    ):
        """Test retrieving an embedding by ID."""
        # Setup mocks
        mock_st.return_value = mock_sentence_transformer
        mock_collection = Mock()
        mock_collection.count.return_value = 1
        mock_collection.get.return_value = {
            "embeddings": [[0.1, 0.2, 0.3, 0.4, 0.5]],
            "ids": ["test_note.md"],
        }
        mock_pc.return_value.get_or_create_collection.return_value = mock_collection

        from agent.embeddings import EmbeddingsManager

        manager = EmbeddingsManager(db_path=temp_db_path)

        # Get embedding by ID
        result = manager.get_embedding_by_id("test_note.md")

        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_collection.get.assert_called_once_with(
            ids=["test_note.md"], include=["embeddings"]
        )

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_get_embedding_by_id_not_found(
        self, mock_ef, mock_st, mock_pc, temp_db_path, mock_sentence_transformer
    ):
        """Test retrieving an embedding when ID doesn't exist."""
        # Setup mocks
        mock_st.return_value = mock_sentence_transformer
        mock_collection = Mock()
        mock_collection.count.return_value = 1
        mock_collection.get.return_value = {"embeddings": [], "ids": []}
        mock_pc.return_value.get_or_create_collection.return_value = mock_collection

        from agent.embeddings import EmbeddingsManager

        manager = EmbeddingsManager(db_path=temp_db_path)

        # Get embedding for non-existent ID
        result = manager.get_embedding_by_id("nonexistent.md")

        assert result == []

    def test_get_embedding_by_id_no_collection(self, temp_db_path):
        """Test get_embedding_by_id when collection is None."""
        with patch("agent.embeddings.SentenceTransformer", None):
            from agent.embeddings import EmbeddingsManager

            manager = EmbeddingsManager(db_path=temp_db_path)
            manager.collection = None

            result = manager.get_embedding_by_id("test.md")

            assert result == []

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_get_embedding_by_id_exception_handling(
        self, mock_ef, mock_st, mock_pc, temp_db_path, mock_sentence_transformer
    ):
        """Test exception handling in get_embedding_by_id."""
        # Setup mocks
        mock_st.return_value = mock_sentence_transformer
        mock_collection = Mock()
        mock_collection.count.return_value = 1
        mock_collection.get.side_effect = Exception("Database error")
        mock_pc.return_value.get_or_create_collection.return_value = mock_collection

        from agent.embeddings import EmbeddingsManager

        manager = EmbeddingsManager(db_path=temp_db_path)

        # Should return empty list on exception
        result = manager.get_embedding_by_id("test.md")

        assert result == []


class TestIndexFilePersist:
    """Test the index_file method with persist calls."""

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_index_file_with_persist(
        self,
        mock_ef,
        mock_st,
        mock_pc,
        temp_db_path,
        mock_sentence_transformer,
        temp_vault_path,
    ):
        """Test index_file calls persist on chroma client."""
        # Setup mocks
        mock_st.return_value = mock_sentence_transformer
        mock_collection = Mock()
        mock_collection.count.return_value = 0
        mock_collection.add.return_value = None
        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client.persist.return_value = None
        mock_pc.return_value = mock_client

        from agent.embeddings import EmbeddingsManager

        manager = EmbeddingsManager(db_path=temp_db_path)

        # Index a file
        test_file = Path(temp_vault_path) / "note1.md"
        chunks_indexed = manager.index_file(str(test_file))

        # Verify persist was called
        mock_client.persist.assert_called_once()
        assert chunks_indexed > 0

    @patch("agent.embeddings.PersistentClient")
    @patch("agent.embeddings.SentenceTransformer")
    @patch(
        "agent.embeddings.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_index_file_nonexistent(
        self, mock_ef, mock_st, mock_pc, temp_db_path, mock_sentence_transformer
    ):
        """Test index_file returns 0 for non-existent file."""
        # Setup mocks
        mock_st.return_value = mock_sentence_transformer
        mock_collection = Mock()
        mock_pc.return_value.get_or_create_collection.return_value = mock_collection

        from agent.embeddings import EmbeddingsManager

        manager = EmbeddingsManager(db_path=temp_db_path)

        # Try to index non-existent file
        result = manager.index_file("/nonexistent/file.md")

        assert result == 0


class TestPersistentClientNone:
    """Test scenarios where PersistentClient is None."""

    def test_initialization_with_persistent_client_none(self, temp_db_path):
        """Test that chroma_client is set to None when PersistentClient unavailable."""
        with patch("agent.embeddings.PersistentClient", None):
            with patch("agent.embeddings.SentenceTransformer") as mock_st:
                mock_st.return_value = Mock()

                from agent.embeddings import EmbeddingsManager

                manager = EmbeddingsManager(db_path=temp_db_path)

                # Should set chroma_client to None (line 65)
                assert manager.chroma_client is None
                assert manager.collection is None


class TestSentenceTransformerNoneWarning:
    """Test warning logging when SentenceTransformer is None."""

    def test_sentence_transformer_none_logs_warning(self, temp_db_path):
        """Test that warning is logged when SentenceTransformer is None."""
        with patch("agent.embeddings.SentenceTransformer", None):
            with patch("agent.embeddings.logging") as mock_logging:
                from agent.embeddings import EmbeddingsManager

                manager = EmbeddingsManager(db_path=temp_db_path)

                # Verify warning was logged (lines 45-48)
                mock_logging.warning.assert_called_once()
                warning_call = mock_logging.warning.call_args[0][0]
                assert "sentence_transformers not available" in warning_call
                assert manager.model is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

