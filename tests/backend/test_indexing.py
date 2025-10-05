# tests/backend/test_indexing.py
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from indexing import VaultIndexer
from embeddings import EmbeddingsManager


class TestVaultIndexer:
    """Test suite for the VaultIndexer class."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary directory for cache testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_embeddings_manager(self):
        """Mock EmbeddingsManager."""
        mock_emb = Mock(spec=EmbeddingsManager)
        mock_emb.add_documents = Mock()
        mock_emb.clear_collection = Mock()
        mock_emb.chunk_text = Mock(return_value=["chunk1", "chunk2"])
        return mock_emb
    
    @pytest.fixture
    def vault_indexer(self, mock_embeddings_manager, temp_cache_dir):
        """Create a VaultIndexer instance for testing."""
        return VaultIndexer(emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir)
    
    def test_vault_indexer_initialization(self, temp_cache_dir):
        """Test VaultIndexer initialization."""
        with patch('indexing.EmbeddingsManager') as MockEmb:
            mock_emb_instance = Mock()
            MockEmb.return_value = mock_emb_instance
            
            indexer = VaultIndexer(cache_dir=temp_cache_dir)
            
            assert indexer.cache_dir == Path(temp_cache_dir)
            assert indexer.cache_dir.exists()
            # Should create EmbeddingsManager if not provided
            MockEmb.assert_called_once()
    
    def test_initialization_with_existing_embeddings_manager(self, mock_embeddings_manager, temp_cache_dir):
        """Test initialization with existing EmbeddingsManager."""
        indexer = VaultIndexer(emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir)
        
        assert indexer.emb_mgr is mock_embeddings_manager
        assert indexer.cache_dir == Path(temp_cache_dir)
    
    def test_hash_url(self, vault_indexer):
        """Test URL hashing functionality."""
        url1 = "https://example.com"
        url2 = "https://different.com"
        url1_duplicate = "https://example.com"
        
        hash1 = vault_indexer._hash_url(url1)
        hash2 = vault_indexer._hash_url(url2)
        hash1_dup = vault_indexer._hash_url(url1_duplicate)
        
        # Same URLs should produce same hash
        assert hash1 == hash1_dup
        # Different URLs should produce different hashes
        assert hash1 != hash2
        # Hashes should be strings
        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 hash length
    
    def test_cache_file(self, vault_indexer):
        """Test caching text to file."""
        key = "test_key"
        text = "This is test content to cache"
        
        cache_path = vault_indexer._cache_file(key, text)
        
        # Verify file was created
        assert cache_path.exists()
        assert cache_path.name == f"{key}.txt"
        
        # Verify content
        with open(cache_path, 'r', encoding='utf-8') as f:
            cached_content = f.read()
        assert cached_content == text
    
    def test_load_cached_file_exists(self, vault_indexer):
        """Test loading existing cached file."""
        key = "existing_key"
        content = "Cached content"
        
        # Create cache file
        cache_path = vault_indexer.cache_dir / f"{key}.txt"
        cache_path.write_text(content, encoding='utf-8')
        
        # Load cached content
        loaded_content = vault_indexer._load_cached(key)
        assert loaded_content == content
    
    def test_load_cached_file_not_exists(self, vault_indexer):
        """Test loading non-existing cached file."""
        key = "non_existing_key"
        
        loaded_content = vault_indexer._load_cached(key)
        assert loaded_content is None
    
    def test_load_cached_file_error(self, vault_indexer):
        """Test loading cached file with read error."""
        key = "error_key"
        
        # Create file but mock read to raise exception
        cache_path = vault_indexer.cache_dir / f"{key}.txt"
        cache_path.write_text("content")
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            loaded_content = vault_indexer._load_cached(key)
            assert loaded_content is None
    
    def test_read_markdown_file(self, vault_indexer, temp_cache_dir):
        """Test reading markdown file."""
        # Create test markdown file
        md_file = Path(temp_cache_dir) / "test.md"
        md_content = "# Test Markdown\n\nThis is a test markdown file."
        md_file.write_text(md_content, encoding='utf-8')
        
        content = vault_indexer._read_markdown(str(md_file))
        assert content == md_content
    
    def test_read_markdown_file_not_exists(self, vault_indexer):
        """Test reading non-existing markdown file."""
        content = vault_indexer._read_markdown("non_existing_file.md")
        assert content is None
    
    def test_read_markdown_file_error(self, vault_indexer, temp_cache_dir):
        """Test reading markdown file with error."""
        md_file = Path(temp_cache_dir) / "test.md"
        md_file.write_text("content")
        
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'error')):
            content = vault_indexer._read_markdown(str(md_file))
            assert content is None
    
    @patch('indexing.PdfReader')
    def test_read_pdf_success(self, mock_pdf_reader, vault_indexer, temp_cache_dir):
        """Test successful PDF reading."""
        # Mock PDF reader
        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        
        # Create dummy PDF file
        pdf_file = Path(temp_cache_dir) / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        content = vault_indexer._read_pdf(str(pdf_file))
        assert content == "Page 1 content\nPage 2 content"
    
    @patch('indexing.PdfReader')
    def test_read_pdf_error(self, mock_pdf_reader, vault_indexer, temp_cache_dir):
        """Test PDF reading with error."""
        mock_pdf_reader.side_effect = Exception("PDF read error")
        
        pdf_file = Path(temp_cache_dir) / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        content = vault_indexer._read_pdf(str(pdf_file))
        assert content is None
    
    def test_read_pdf_file_not_exists(self, vault_indexer):
        """Test reading non-existing PDF file."""
        content = vault_indexer._read_pdf("non_existing_file.pdf")
        assert content is None
    
    @patch('indexing.requests.get')
    @patch('indexing.Document')
    def test_fetch_web_content_success(self, mock_document, mock_requests, vault_indexer):
        """Test successful web content fetching."""
        # Mock requests response
        mock_response = Mock()
        mock_response.text = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        mock_response.raise_for_status = Mock()
        mock_requests.return_value = mock_response
        
        # Mock readability Document
        mock_doc = Mock()
        mock_doc.summary.return_value = "<h1>Title</h1><p>Content</p>"
        mock_document.return_value = mock_doc
        
        # Mock BeautifulSoup (via patch in the actual call)
        with patch('indexing.BeautifulSoup') as mock_bs:
            mock_soup = Mock()
            mock_soup.get_text.return_value = "Title\nContent"
            mock_bs.return_value = mock_soup
            
            url = "https://example.com"
            content = vault_indexer._fetch_web_content(url)
            
            assert content == "Title\nContent"
            mock_requests.assert_called_once_with(url, timeout=10)
    
    @patch('indexing.requests.get')
    def test_fetch_web_content_request_error(self, mock_requests, vault_indexer):
        """Test web content fetching with request error."""
        mock_requests.side_effect = Exception("Network error")
        
        content = vault_indexer._fetch_web_content("https://example.com")
        assert content is None
    
    @patch('indexing.requests.get')
    def test_fetch_web_content_http_error(self, mock_requests, vault_indexer):
        """Test web content fetching with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_requests.return_value = mock_response
        
        content = vault_indexer._fetch_web_content("https://example.com")
        assert content is None
    
    def test_reindex_vault_with_markdown_files(self, vault_indexer, temp_cache_dir, mock_embeddings_manager):
        """Test reindexing vault with markdown files."""
        # Create test vault directory
        vault_dir = Path(temp_cache_dir) / "vault"
        vault_dir.mkdir()
        
        # Create markdown files
        (vault_dir / "file1.md").write_text("# File 1\nContent 1")
        (vault_dir / "file2.md").write_text("# File 2\nContent 2")
        (vault_dir / "subdir").mkdir()
        (vault_dir / "subdir" / "file3.md").write_text("# File 3\nContent 3")
        
        # Mock chunk_text method
        mock_embeddings_manager.chunk_text.return_value = ["chunk1", "chunk2"]
        
        result = vault_indexer.reindex(str(vault_dir))
        
        # Verify clear_collection was called
        mock_embeddings_manager.clear_collection.assert_called_once()
        
        # Verify add_documents was called for each file
        assert mock_embeddings_manager.add_documents.call_count == 3
        
        # Verify result structure
        assert "files" in result
        assert "chunks" in result
        assert result["files"] == 3
        assert result["chunks"] == 6  # 3 files * 2 chunks each
    
    def test_reindex_vault_with_mixed_files(self, vault_indexer, temp_cache_dir, mock_embeddings_manager):
        """Test reindexing vault with mixed file types."""
        vault_dir = Path(temp_cache_dir) / "vault"
        vault_dir.mkdir()
        
        # Create different file types
        (vault_dir / "note.md").write_text("# Markdown Note")
        (vault_dir / "document.pdf").write_bytes(b"fake pdf")
        (vault_dir / "ignored.txt").write_text("This should be ignored")
        
        # Mock PDF reading
        with patch.object(vault_indexer, '_read_pdf', return_value="PDF content"):
            mock_embeddings_manager.chunk_text.return_value = ["chunk1"]
            
            result = vault_indexer.reindex(str(vault_dir))
            
            # Should process markdown and PDF, ignore txt
            assert result["files"] == 2
            assert result["chunks"] == 2
    
    def test_reindex_empty_vault(self, vault_indexer, temp_cache_dir, mock_embeddings_manager):
        """Test reindexing empty vault."""
        vault_dir = Path(temp_cache_dir) / "empty_vault"
        vault_dir.mkdir()
        
        result = vault_indexer.reindex(str(vault_dir))
        
        # Should still clear collection
        mock_embeddings_manager.clear_collection.assert_called_once()
        
        # No files should be processed
        assert result["files"] == 0
        assert result["chunks"] == 0
        mock_embeddings_manager.add_documents.assert_not_called()
    
    def test_reindex_nonexistent_vault(self, vault_indexer, mock_embeddings_manager):
        """Test reindexing non-existent vault directory."""
        result = vault_indexer.reindex("non_existent_directory")
        
        # Should still clear collection
        mock_embeddings_manager.clear_collection.assert_called_once()
        
        # No files should be processed
        assert result["files"] == 0
        assert result["chunks"] == 0
    
    def test_index_web_content_new_url(self, vault_indexer, mock_embeddings_manager):
        """Test indexing new web content."""
        url = "https://example.com"
        
        with patch.object(vault_indexer, '_fetch_web_content', return_value="Web content"):
            mock_embeddings_manager.chunk_text.return_value = ["chunk1", "chunk2"]
            
            result = vault_indexer.index_web_content(url)
            
            # Should fetch and index content
            assert result["url"] == url
            assert result["chunks"] == 2
            mock_embeddings_manager.add_documents.assert_called_once()
    
    def test_index_web_content_cached(self, vault_indexer, mock_embeddings_manager):
        """Test indexing cached web content."""
        url = "https://example.com"
        cached_content = "Cached web content"
        
        # Cache content first
        url_hash = vault_indexer._hash_url(url)
        vault_indexer._cache_file(f"web_{url_hash}", cached_content)
        
        mock_embeddings_manager.chunk_text.return_value = ["chunk1"]
        
        result = vault_indexer.index_web_content(url)
        
        # Should use cached content
        assert result["url"] == url
        assert result["chunks"] == 1
        mock_embeddings_manager.add_documents.assert_called_once()
    
    def test_index_web_content_fetch_failure(self, vault_indexer, mock_embeddings_manager):
        """Test indexing web content when fetching fails."""
        url = "https://example.com"
        
        with patch.object(vault_indexer, '_fetch_web_content', return_value=None):
            result = vault_indexer.index_web_content(url)
            
            # Should return error result
            assert result["url"] == url
            assert result["chunks"] == 0
            assert "error" in result
            mock_embeddings_manager.add_documents.assert_not_called()


class TestVaultIndexerIntegration:
    """Integration tests for VaultIndexer."""
    
    def test_complete_workflow(self, mock_embeddings_manager):
        """Test complete indexing workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            indexer = VaultIndexer(emb_mgr=mock_embeddings_manager, cache_dir=temp_dir)
            
            # Create vault with content
            vault_dir = Path(temp_dir) / "vault"
            vault_dir.mkdir()
            (vault_dir / "note.md").write_text("# Test Note\nContent")
            
            # Index vault
            mock_embeddings_manager.chunk_text.return_value = ["chunk1"]
            vault_result = indexer.reindex(str(vault_dir))
            
            # Index web content
            with patch.object(indexer, '_fetch_web_content', return_value="Web content"):
                web_result = indexer.index_web_content("https://example.com")
            
            # Verify both operations succeeded
            assert vault_result["files"] == 1
            assert web_result["chunks"] == 1
            
            # Verify embeddings manager was called appropriately
            assert mock_embeddings_manager.clear_collection.called
            assert mock_embeddings_manager.add_documents.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])