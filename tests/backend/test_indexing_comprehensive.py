# tests/backend/test_indexing_comprehensive.py
# flake8: noqa: B101
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
def temp_cache_dir():
    """Create a temporary directory for cache testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_vault_dir():
    """Create a temporary vault directory with test files."""
    temp_dir = tempfile.mkdtemp()
    vault_dir = Path(temp_dir) / "vault"
    vault_dir.mkdir()

    # Create test files
    (vault_dir / "note1.md").write_text("# Note 1\nThis is the first note content.")
    (vault_dir / "note2.md").write_text("# Note 2\nThis is the second note content.")
    (vault_dir / "document.pdf").write_bytes(b"fake pdf content")
    (vault_dir / "README.txt").write_text("This is a text file that should be ignored.")

    # Create subdirectory
    subdir = vault_dir / "subfolder"
    subdir.mkdir()
    (subdir / "nested.md").write_text("# Nested Note\nNested content.")
    (subdir / "nested.pdf").write_bytes(b"nested pdf content")

    yield vault_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_embeddings_manager():
    """Mock EmbeddingsManager with all necessary methods."""
    mock_emb = Mock()
    mock_emb.add_embedding = Mock()
    mock_emb.add_documents = Mock()
    mock_emb.clear_collection = Mock()
    mock_emb.reset_db = Mock()
    mock_emb.chunk_text = Mock(return_value=["chunk1", "chunk2", "chunk3"])
    mock_emb.index_file = Mock(return_value=3)
    return mock_emb


@pytest.fixture
def mock_settings():
    """Mock settings for from_settings() method."""
    mock_settings = Mock()
    # Use secure temporary directory creation for testing
    temp_dir = tempfile.mkdtemp(prefix="test_cache_")
    mock_settings.abs_cache_dir = Path(temp_dir)
    return mock_settings


class TestVaultIndexerInit:
    """Test VaultIndexer initialization scenarios."""

    @patch("backend.indexing.EmbeddingsManager")
    @patch("backend.indexing.get_settings")
    def test_default_initialization(
        self, mock_get_settings, mock_emb_class, temp_cache_dir, mock_settings
    ):
        """Test initialization with default parameters."""
        mock_settings.abs_cache_dir = Path(temp_cache_dir)
        mock_get_settings.return_value = mock_settings
        mock_emb_instance = Mock()
        mock_emb_class.return_value = mock_emb_instance

        from backend.indexing import VaultIndexer

        indexer = VaultIndexer()

        assert indexer.emb_mgr == mock_emb_instance
        assert indexer.cache_dir == Path(temp_cache_dir)
        mock_emb_class.assert_called_once()

    @patch("backend.indexing.get_settings")
    def test_initialization_with_params(
        self, mock_get_settings, mock_embeddings_manager, temp_cache_dir
    ):
        """Test initialization with provided parameters."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        assert indexer.emb_mgr == mock_embeddings_manager
        assert indexer.cache_dir == Path(temp_cache_dir)
        assert indexer.cache_dir.exists()

    @patch("backend.indexing.EmbeddingsManager")
    @patch("backend.indexing.get_settings")
    def test_initialization_settings_fallback(self, mock_get_settings, mock_emb_class):
        """Test initialization when settings fail, falls back to 'cache'."""
        mock_get_settings.side_effect = Exception("Settings unavailable")
        mock_emb_instance = Mock()
        mock_emb_class.return_value = mock_emb_instance

        from backend.indexing import VaultIndexer

        indexer = VaultIndexer()

        assert indexer.cache_dir == Path("cache")
        assert indexer.cache_dir.exists()


class TestUtilityMethods:
    """Test utility and helper methods."""

    def test_hash_url_consistency(self):
        """Test URL hashing produces consistent results."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir="test")

        url1 = "https://example.com/page"
        url2 = "https://different.com/page"
        url1_duplicate = "https://example.com/page"

        hash1 = indexer._hash_url(url1)
        hash2 = indexer._hash_url(url2)
        hash1_dup = indexer._hash_url(url1_duplicate)

        # Same URLs should produce same hash
        assert hash1 == hash1_dup
        # Different URLs should produce different hashes
        assert hash1 != hash2
        # Hashes should be MD5 format
        assert len(hash1) == 32
        assert all(c in "0123456789abcdef" for c in hash1)

    def test_cache_file_creation(self, temp_cache_dir):
        """Test caching text to file."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        key = "test_content_key"
        text = "This is test content to cache for later retrieval."

        cache_path = indexer._cache_file(key, text)

        # Verify file was created with correct name and location
        assert cache_path.exists()
        assert cache_path.name == f"{key}.txt"
        assert cache_path.parent == Path(temp_cache_dir)
        # Verify content was written correctly
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_content = f.read()
        assert cached_content == text

    def test_load_cached_existing_file(self, temp_cache_dir):
        """Test loading existing cached file."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        key = "existing_cache_key"
        content = "Previously cached content"

        # Create cache file directly
        cache_path = indexer.cache_dir / f"{key}.txt"
        cache_path.write_text(content, encoding="utf-8")

        # Load and verify
        loaded_content = indexer._load_cached(key)
        assert loaded_content == content

    def test_load_cached_missing_file(self, temp_cache_dir):
        """Test loading non-existent cached file."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        loaded_content = indexer._load_cached("nonexistent_key")
        assert loaded_content is None

    def test_load_cached_read_error(self, temp_cache_dir):
        """Test loading cached file with read error."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        key = "error_key"

        # Create file but make read fail
        cache_path = indexer.cache_dir / f"{key}.txt"
        cache_path.write_text("content")

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            loaded_content = indexer._load_cached(key)
            assert loaded_content is None


class TestMarkdownProcessing:
    pass
    pass
    """Test markdown file processing methods."""
    pass
    """Test markdown file processing methods."""

    def test_read_markdown_success(self, temp_cache_dir):
        """Test successful markdown file reading."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        # Create test markdown file
        md_file = Path(temp_cache_dir) / "test_note.md"
        md_content = "# Test Markdown File\n\nThis is **markdown** content with *formatting*.\n\n- List item 1\n- List item 2"
        md_file.write_text(md_content, encoding="utf-8")

        content = indexer._read_markdown(str(md_file))
        assert content == md_content

    def test_read_markdown_file_not_exists(self, temp_cache_dir):
        """Test reading non-existent markdown file."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        content = indexer._read_markdown("nonexistent_file.md")
        assert content is None

    def test_read_markdown_encoding_error(self, temp_cache_dir):
        """Test reading markdown file with encoding error."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        md_file = Path(temp_cache_dir) / "bad_encoding.md"
        md_file.write_text("content", encoding="utf-8")

        with patch(
            "builtins.open",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
        ):
            content = indexer._read_markdown(str(md_file))
            assert content is None

    def test_read_markdown_permission_error(self, temp_cache_dir):
        """Test reading markdown file with permission error."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        md_file = Path(temp_cache_dir) / "restricted.md"
        md_file.write_text("content", encoding="utf-8")

        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            content = indexer._read_markdown(str(md_file))
            assert content is None


class TestPDFProcessing:
    """Test PDF file processing methods."""

    @patch("backend.indexing.PdfReader")
    def test_read_pdf_success_single_page(self, mock_pdf_reader, temp_cache_dir):
        """Test successful PDF reading with single page."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        # Mock PDF reader with single page
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Single page PDF content"
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        # Create fake PDF file
        pdf_file = Path(temp_cache_dir) / "single_page.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        content = indexer._read_pdf(str(pdf_file))
        assert content == "Single page PDF content"

    @patch("backend.indexing.PdfReader")
    def test_read_pdf_success_multiple_pages(self, mock_pdf_reader, temp_cache_dir):
        """Test successful PDF reading with multiple pages."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        # Mock PDF reader with multiple pages
        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "First page content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Second page content"
        mock_page3 = Mock()
        mock_page3.extract_text.return_value = ""  # Empty page
        mock_page4 = Mock()
        mock_page4.extract_text.return_value = "Fourth page content"
        mock_reader.pages = [mock_page1, mock_page2, mock_page3, mock_page4]
        mock_pdf_reader.return_value = mock_reader

        pdf_file = Path(temp_cache_dir) / "multi_page.pdf"
        pdf_file.write_bytes(b"fake multi-page pdf content")

        content = indexer._read_pdf(str(pdf_file))
        # Should join non-empty pages with newlines
        assert content == "First page content\nSecond page content\nFourth page content"

    @patch("backend.indexing.PdfReader")
    def test_read_pdf_empty_pages(self, mock_pdf_reader, temp_cache_dir):
        """Test reading PDF with all empty pages."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = ""
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = None
        mock_page3 = Mock()
        mock_page3.extract_text.return_value = "   "  # Whitespace only
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf_reader.return_value = mock_reader

        pdf_file = Path(temp_cache_dir) / "empty.pdf"
        pdf_file.write_bytes(b"fake empty pdf")

        content = indexer._read_pdf(str(pdf_file))
        assert content == ""

    @patch("backend.indexing.PdfReader")
    def test_read_pdf_parsing_error(self, mock_pdf_reader, temp_cache_dir):
        """Test PDF reading with parsing error."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        mock_pdf_reader.side_effect = Exception("PDF parsing failed")

        pdf_file = Path(temp_cache_dir) / "corrupt.pdf"
        pdf_file.write_bytes(b"corrupt pdf content")

        content = indexer._read_pdf(str(pdf_file))
        assert content is None

    def test_read_pdf_file_not_exists(self, temp_cache_dir):
        """Test reading non-existent PDF file."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        content = indexer._read_pdf("nonexistent.pdf")
        assert content is None


class TestWebContentFetching:
    """Test web content fetching methods."""

    @patch("backend.indexing.BeautifulSoup")
    @patch("backend.indexing.Document")
    @patch("backend.indexing.requests.get")
    def test_fetch_web_content_success(
        self, mock_requests, mock_document, mock_bs, temp_cache_dir
    ):
        """Test successful web content fetching."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        # Mock requests response
        mock_response = Mock()
        mock_response.text = "<html><head><title>Test</title></head><body><h1>Article Title</h1><p>Article content goes here.</p><div class='ads'>Advertisement</div></body></html>"
        mock_response.raise_for_status = Mock()
        mock_requests.return_value = mock_response

        # Mock readability Document
        mock_doc = Mock()
        mock_doc.summary.return_value = (
            "<h1>Article Title</h1><p>Article content goes here.</p>"
        )
        mock_document.return_value = mock_doc

        # Mock BeautifulSoup
        mock_soup = Mock()
        mock_soup.get_text.return_value = "Article Title\nArticle content goes here."
        mock_bs.return_value = mock_soup

        url = "https://example.com/article"
        content = indexer._fetch_web_content(url)

        assert content == "Article Title\nArticle content goes here."
        mock_requests.assert_called_once_with(url, timeout=10)
        mock_document.assert_called_once_with(mock_response.text)
        mock_bs.assert_called_once_with(mock_doc.summary.return_value, "html.parser")

    @patch("backend.indexing.requests.get")
    def test_fetch_web_content_request_timeout(self, mock_requests, temp_cache_dir):
        """Test web content fetching with timeout."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        mock_requests.side_effect = Exception("Connection timeout")

        content = indexer._fetch_web_content("https://example.com")
        assert content is None

    @patch("backend.indexing.requests.get")
    def test_fetch_web_content_http_error(self, mock_requests, temp_cache_dir):
        """Test web content fetching with HTTP error."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404 Not Found")
        mock_requests.return_value = mock_response

        content = indexer._fetch_web_content("https://example.com/not-found")
        assert content is None

    @patch("backend.indexing.BeautifulSoup")
    @patch("backend.indexing.Document")
    @patch("backend.indexing.requests.get")
    def test_fetch_web_content_empty_result(
        self, mock_requests, mock_document, mock_bs, temp_cache_dir
    ):
        """Test web content fetching that returns empty content."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        # Mock successful request but empty content
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = Mock()
        mock_requests.return_value = mock_response

        mock_doc = Mock()
        mock_doc.summary.return_value = ""
        mock_document.return_value = mock_doc

        mock_soup = Mock()
        mock_soup.get_text.return_value = ""
        mock_bs.return_value = mock_soup

        content = indexer._fetch_web_content("https://example.com/empty")
        assert content is None


class TestVaultIndexing:
    """Test vault indexing methods."""

    def test_index_vault_mixed_files(
        self, temp_vault_dir, mock_embeddings_manager, temp_cache_dir
    ):
        """Test indexing vault with mixed file types."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        # Mock PDF processing - mock the _read_pdf method to return content for our fake PDFs
        with patch.object(indexer, "_read_pdf", return_value="Mocked PDF content"):
            results = indexer.index_vault(str(temp_vault_dir))

        # Should find all .md and .pdf files (including nested ones)
        md_files = [k for k in results.keys() if k.endswith(".md")]
        pdf_files = [k for k in results.keys() if k.endswith(".pdf")]

        assert len(md_files) == 3  # note1.md, note2.md, nested.md
        assert len(pdf_files) == 2  # document.pdf, nested.pdf

        # Should ignore .txt files
        txt_files = [k for k in results.keys() if k.endswith(".txt")]
        assert len(txt_files) == 0

    def test_index_vault_error_handling(
        self, temp_vault_dir, mock_embeddings_manager, temp_cache_dir
    ):
        """Test vault indexing with file processing errors."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        # Mock file operations to raise errors
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            with patch.object(indexer, "index_pdf", side_effect=Exception("PDF error")):
                results = indexer.index_vault(str(temp_vault_dir))

        # Should handle errors gracefully and continue processing
        assert isinstance(results, dict)

    def test_reindex_with_clear_collection(
        self, temp_vault_dir, mock_embeddings_manager, temp_cache_dir
    ):
        """Test reindexing with clear_collection method available."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        # Ensure clear_collection is available
        mock_embeddings_manager.clear_collection = Mock()

        result = indexer.reindex(str(temp_vault_dir))

        # Should call clear_collection
        mock_embeddings_manager.clear_collection.assert_called_once()

        # Should process files
        assert result["files"] > 0
        assert result["chunks"] > 0

        # Should call add_documents for each file
        assert mock_embeddings_manager.add_documents.call_count > 0

    def test_reindex_with_reset_db_fallback(
        self, temp_vault_dir, mock_embeddings_manager, temp_cache_dir
    ):
        """Test reindexing with reset_db fallback when clear_collection unavailable."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        # Remove clear_collection, keep reset_db
        delattr(mock_embeddings_manager, "clear_collection")
        mock_embeddings_manager.reset_db = Mock()

        result = indexer.reindex(str(temp_vault_dir))

        # Should call reset_db as fallback
        mock_embeddings_manager.reset_db.assert_called_once()

        assert result["files"] > 0

    def test_reindex_nonexistent_directory(
        self, mock_embeddings_manager, temp_cache_dir
    ):
        """Test reindexing non-existent directory."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        result = indexer.reindex("nonexistent_directory")

        # Should still attempt to clear collection
        mock_embeddings_manager.clear_collection.assert_called_once()

        # Should return empty result
        assert result["files"] == 0
        assert result["chunks"] == 0

    def test_reindex_empty_directory(self, temp_cache_dir, mock_embeddings_manager):
        """Test reindexing empty directory."""
        from backend.indexing import VaultIndexer

        empty_dir = Path(temp_cache_dir) / "empty"
        empty_dir.mkdir()

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        result = indexer.reindex(str(empty_dir))

        mock_embeddings_manager.clear_collection.assert_called_once()
        assert result["files"] == 0
        assert result["chunks"] == 0

    def test_reindex_unsupported_files(self, temp_cache_dir, mock_embeddings_manager):
        """Test reindexing directory with only unsupported files."""
        from backend.indexing import VaultIndexer

        test_dir = Path(temp_cache_dir) / "unsupported"
        test_dir.mkdir()
        (test_dir / "image.jpg").write_bytes(b"fake image")
        (test_dir / "document.docx").write_bytes(b"fake word doc")
        (test_dir / "data.json").write_text('{"key": "value"}')

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        result = indexer.reindex(str(test_dir))

        # Should clear but not process any files
        mock_embeddings_manager.clear_collection.assert_called_once()
        assert result["files"] == 0
        assert result["chunks"] == 0


class TestPDFIndexing:
    """Test PDF-specific indexing methods."""

    @patch("backend.indexing.PdfReader")
    def test_extract_pdf_text_success(self, mock_pdf_reader, temp_cache_dir):
        """Test successful PDF text extraction."""
        from backend.indexing import VaultIndexer
        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)
        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        pdf_path = str(Path(temp_cache_dir) / "test.pdf")
        # Create a dummy file so the path exists
        Path(pdf_path).write_bytes(b"dummy pdf content")
        text = indexer._read_pdf(pdf_path)
        assert text == "Page 1 content\nPage 2 content"

    @patch("backend.indexing.PdfReader")
    def test_extract_pdf_text_error(self, mock_pdf_reader, temp_cache_dir):
        """Test PDF text extraction with error."""
        from backend.indexing import VaultIndexer
        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)
        mock_pdf_reader.side_effect = Exception("PDF parsing failed")
        pdf_path = str(Path(temp_cache_dir) / "corrupt.pdf")
        # Create a dummy file so the path exists
        Path(pdf_path).write_bytes(b"corrupt pdf content")
        text = indexer._read_pdf(pdf_path)
        assert text is None

    def test_index_pdf_success(self, temp_cache_dir, mock_embeddings_manager):
        """Test successful PDF indexing."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        pdf_path = str(Path(temp_cache_dir) / "document.pdf")

        with patch.object(indexer, "_read_pdf", return_value="PDF content"):
            result = indexer.index_pdf(pdf_path)

        assert result == 3  # Mock index_file returns 3
        mock_embeddings_manager.index_file.assert_called_once()

    def test_index_pdf_empty_text(self, temp_cache_dir, mock_embeddings_manager):
        """Test PDF indexing with empty extracted text."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        pdf_path = str(Path(temp_cache_dir) / "empty.pdf")

        with patch.object(indexer, "_read_pdf", return_value=""):
            result = indexer.index_pdf(pdf_path)

        assert result == 0
        mock_embeddings_manager.index_file.assert_not_called()

    def test_index_pdf_extraction_error(self, temp_cache_dir, mock_embeddings_manager):
        """Test PDF indexing with extraction error."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        pdf_path = str(Path(temp_cache_dir) / "corrupt.pdf")

        with patch.object(
            indexer, "_read_pdf", side_effect=Exception("Extraction failed")
        ):
            result = indexer.index_pdf(pdf_path)

        assert result == 0


class TestWebPageIndexing:
    """Test web page indexing methods."""

    def test_fetch_web_page_new_content(self, temp_cache_dir):
        """Test fetching new web page content."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        url = "https://example.com/article"
        content = "Fetched web content"

        # Mock the requests.get and Document processing
        mock_response = Mock()
        mock_response.text = "<html><body>Fetched web content</body></html>"
        mock_response.raise_for_status = Mock()
        with patch(
            "backend.indexing.requests.get", return_value=mock_response
        ) as mock_get, patch("backend.indexing.Document") as mock_doc_class, patch(
            "backend.indexing.BeautifulSoup"
        ) as mock_soup_class:

            # Setup Document mock
            mock_doc = Mock()
            mock_doc.summary.return_value = "<p>Fetched web content</p>"
            mock_doc_class.return_value = mock_doc

            # Setup BeautifulSoup mock
            mock_soup = Mock()
            mock_soup.get_text.return_value = content
            mock_soup_class.return_value = mock_soup

            result = indexer.fetch_web_page(url)
            assert result == content
            mock_get.assert_called_once_with(
                url, timeout=10, headers={"User-Agent": "ObsidianAssistant/1.0"}
            )
            # Should have cached the content
            cache_key = indexer._hash_url(url)
            cache_path = indexer.cache_dir / f"{cache_key}.txt"
            assert cache_path.exists()

    def test_fetch_web_page_cached_content(self, temp_cache_dir):
        """Test fetching cached web page content."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        url = "https://example.com/cached"
        cached_content = "Previously cached content"

        # Pre-populate cache
        cache_key = indexer._hash_url(url)
        cache_path = indexer.cache_dir / f"{cache_key}.txt"
        cache_path.write_text(cached_content, encoding="utf-8")

        with patch.object(indexer, "_fetch_web_content") as mock_fetch:
            result = indexer.fetch_web_page(url, force=False)

        assert result == cached_content
        mock_fetch.assert_not_called()  # Should use cache, not fetch

    def test_fetch_web_page_force_refresh(self, temp_cache_dir):
        """Test forcing web page refresh despite cache."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        url = "https://example.com/forced"
        cached_content = "Old cached content"
        new_content = "Fresh fetched content"

        # Pre-populate cache
        cache_key = indexer._hash_url(url)
        cache_path = indexer.cache_dir / f"{cache_key}.txt"
        cache_path.write_text(cached_content, encoding="utf-8")

        # Mock the requests.get and Document processing for force refresh
        mock_response = Mock()
        mock_response.text = "<html><body>Fresh fetched content</body></html>"
        mock_response.raise_for_status = Mock()

        with patch(
            "backend.indexing.requests.get", return_value=mock_response
        ) as mock_get, patch("backend.indexing.Document") as mock_doc_class, patch(
            "backend.indexing.BeautifulSoup"
        ) as mock_soup_class:

            # Setup Document mock
            mock_doc = Mock()
            mock_doc.summary.return_value = "<p>Fresh fetched content</p>"
            mock_doc_class.return_value = mock_doc

            # Setup BeautifulSoup mock
            mock_soup = Mock()
            mock_soup.get_text.return_value = new_content
            mock_soup_class.return_value = mock_soup

            result = indexer.fetch_web_page(url, force=True)

        assert result == new_content
        mock_get.assert_called_once_with(
            url, timeout=10, headers={"User-Agent": "ObsidianAssistant/1.0"}
        )

    def test_fetch_web_page_cache_read_error(self, temp_cache_dir):
        """Test fetching web page with cache read error returns None."""
        from backend.indexing import VaultIndexer

        with patch("backend.indexing.EmbeddingsManager"):
            indexer = VaultIndexer(cache_dir=temp_cache_dir)

        url = "https://example.com/cache-error"

        # Create cache file but make it unreadable
        cache_key = indexer._hash_url(url)
        cache_path = indexer.cache_dir / f"{cache_key}.txt"
        cache_path.write_text("content")

        # Mock cache read failure - should not fallback to web fetch when cache exists
        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("Cache read failed")
        ):
            result = indexer.fetch_web_page(url, force=False)

        # Should return None when cache read fails (doesn't fallback to fetch when cache exists)
        assert result is None

    def test_index_web_page_success(self, temp_cache_dir, mock_embeddings_manager):
        """Test successful web page indexing."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        url = "https://example.com/page"

        with patch.object(indexer, "fetch_web_page", return_value="Web page content"):
            result = indexer.index_web_page(url)

        assert result == 3  # Mock index_file returns 3
        mock_embeddings_manager.index_file.assert_called_once()

    def test_index_web_page_fetch_failure(
        self, temp_cache_dir, mock_embeddings_manager
    ):
        """Test web page indexing with fetch failure."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        url = "https://example.com/failed"

        with patch.object(indexer, "fetch_web_page", return_value=None):
            result = indexer.index_web_page(url)

        assert result == 0
        mock_embeddings_manager.index_file.assert_not_called()

    def test_index_web_content_success(self, temp_cache_dir, mock_embeddings_manager):
        """Test successful web content indexing."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        url = "https://example.com/content"

        with patch.object(indexer, "_fetch_web_content", return_value="Web content"):
            result = indexer.index_web_content(url)

        assert result["url"] == url
        assert result["chunks"] == 3  # Mock chunk_text returns 3 chunks
        assert "error" not in result
        mock_embeddings_manager.add_documents.assert_called_once()

    def test_index_web_content_cached(self, temp_cache_dir, mock_embeddings_manager):
        """Test web content indexing using cached content."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        url = "https://example.com/cached-content"
        cached_content = "Cached web content"

        # Pre-cache content
        url_hash = indexer._hash_url(url)
        indexer._cache_file(f"web_{url_hash}", cached_content)

        with patch.object(indexer, "_fetch_web_content") as mock_fetch:
            result = indexer.index_web_content(url)

        assert result["chunks"] == 3
        mock_fetch.assert_not_called()  # Should use cached content
        mock_embeddings_manager.add_documents.assert_called_once()

    def test_index_web_content_fetch_failure(
        self, temp_cache_dir, mock_embeddings_manager
    ):
        """Test web content indexing with fetch failure."""
        from backend.indexing import VaultIndexer

        indexer = VaultIndexer(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        url = "https://example.com/failed-content"

        with patch.object(indexer, "_fetch_web_content", return_value=None):
            result = indexer.index_web_content(url)

        assert result["url"] == url
        assert result["chunks"] == 0
        assert "error" in result
        mock_embeddings_manager.add_documents.assert_not_called()


class TestIndexingService:
    pass
    """Test IndexingService wrapper class."""
    pass
    pass
    pass
    """Test IndexingService wrapper class."""

    @patch("backend.indexing.EmbeddingsManager")
    @patch("backend.indexing.get_settings")
    def test_indexing_service_default_init(
        self, mock_get_settings, mock_emb_class, mock_settings
    ):
        """Test IndexingService default initialization."""
        mock_emb_instance = Mock()
        mock_emb_class.return_value = mock_emb_instance
        mock_get_settings.return_value = mock_settings

        from backend.indexing import IndexingService

        service = IndexingService()

        assert service.emb_mgr == mock_emb_instance
        assert service.vault_indexer is not None
        mock_emb_class.assert_called_once()

    def test_indexing_service_with_params(
        self, mock_embeddings_manager, temp_cache_dir
    ):
        """Test IndexingService with provided parameters."""
        from backend.indexing import IndexingService

        service = IndexingService(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        assert service.emb_mgr == mock_embeddings_manager
        assert service.vault_indexer.emb_mgr == mock_embeddings_manager

    @patch("backend.embeddings.EmbeddingsManager")
    @patch("backend.indexing.get_settings")
    def test_from_settings_success(
        self, mock_get_settings, mock_emb_class, mock_settings
    ):
        """Test IndexingService.from_settings() success."""
        # Mock EmbeddingsManager with from_settings method
        mock_emb_instance = Mock()
        mock_emb_class.from_settings = Mock(return_value=mock_emb_instance)
        mock_get_settings.return_value = mock_settings

        from backend.indexing import IndexingService

        service = IndexingService.from_settings()

        assert service.emb_mgr == mock_emb_instance
        mock_emb_class.from_settings.assert_called_once()

    @patch("backend.embeddings.EmbeddingsManager")
    @patch("backend.indexing.get_settings")
    def test_from_settings_embeddings_fallback(
        self, mock_get_settings, mock_emb_class, mock_settings
    ):
        """Test IndexingService.from_settings() with embeddings fallback."""
        # Mock EmbeddingsManager without from_settings method
        mock_emb_instance = Mock()
        mock_emb_class.return_value = mock_emb_instance

        # Remove from_settings attribute to test fallback path
        if hasattr(mock_emb_class, "from_settings"):
            delattr(mock_emb_class, "from_settings")

        mock_get_settings.return_value = mock_settings

        from backend.indexing import IndexingService

        service = IndexingService.from_settings()

        assert service.emb_mgr == mock_emb_instance
        mock_emb_class.assert_called_once()

    def test_from_settings_full_fallback(self):
        """Test IndexingService.from_settings() with settings fallback."""
        from backend.indexing import IndexingService

        # Test settings fallback by mocking get_settings to fail
        with patch(
            "backend.indexing.get_settings",
            side_effect=Exception("Settings unavailable"),
        ):
            service = IndexingService.from_settings()

            # Should still create service with default cache_dir when settings fail
            assert service is not None
            assert hasattr(service, "emb_mgr")
            assert hasattr(service, "vault_indexer")
            # When settings fail, should use default "cache" dir
            assert service.vault_indexer.cache_dir.name == "cache"

    def test_indexing_service_delegation(self, mock_embeddings_manager, temp_cache_dir):
        """Test IndexingService method delegation to VaultIndexer."""
        from backend.indexing import IndexingService

        service = IndexingService(
            emb_mgr=mock_embeddings_manager, cache_dir=temp_cache_dir
        )

        # Mock VaultIndexer methods
        service.vault_indexer.index_file = Mock(return_value=1)
        service.vault_indexer.index_vault = Mock(return_value={"file1.md": 1})
        service.vault_indexer.index_pdf = Mock(return_value=2)
        service.vault_indexer.index_web_page = Mock(return_value=3)
        service.vault_indexer.reindex_all = Mock(return_value={"file2.md": 1})

        # Test delegation
        assert service.index_file("test.md") == 1
        assert service.index_vault("vault") == {"file1.md": 1}
        assert service.index_pdf("test.pdf") == 2
        assert service.index_web_page("https://example.com") == 3
        assert service.reindex_all() == {"file2.md": 1}

        # Verify calls were delegated
        service.vault_indexer.index_file.assert_called_once_with("test.md")
        service.vault_indexer.index_vault.assert_called_once_with("vault")
        service.vault_indexer.index_pdf.assert_called_once_with("test.pdf")
        service.vault_indexer.index_web_page.assert_called_once_with(
            "https://example.com", force=False
        )
        service.vault_indexer.reindex_all.assert_called_once_with("./vault")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
