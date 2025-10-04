import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from backend.backend import app, get_model_manager, get_cache_manager, get_emb_manager, get_vault_indexer


class TestBackend(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.client = TestClient(app)
        self.test_vault_path = "test_vault"
        self.test_cache_dir = "test_cache"
        self.test_vector_db = "test_vector_db"
        
        # Create test directories
        os.makedirs(self.test_vault_path, exist_ok=True)
        os.makedirs(self.test_cache_dir, exist_ok=True)
        os.makedirs(self.test_vector_db, exist_ok=True)

    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove test directories and their contents
        test_paths = [
            self.test_vault_path,
            self.test_cache_dir,
            self.test_vector_db
        ]
        for path in test_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(path)

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("backend.backend.get_model_manager")
    @patch("backend.backend.get_cache_manager")
    @patch("backend.backend.get_emb_manager")
    def test_ask_endpoint(
        self,
        mock_emb_fn,
        mock_cache_fn,
        mock_model_fn
    ):
        """Test the ask endpoint with various scenarios."""
        # Set up mock model
        mock_model_mgr = MagicMock()
        mock_model = MagicMock()
        mock_model.query.return_value = "Fresh answer"
        mock_model.generate.return_value = "Generated answer"
        mock_model_mgr.load_text_model.return_value = mock_model
        mock_model_fn.return_value = mock_model_mgr

        # Set up mock cache
        mock_cache = MagicMock()
        mock_cache.get_cached_answer.side_effect = None
        mock_cache.get_cached_answer.return_value = None
        mock_cache_fn.return_value = mock_cache

        # Set up mock embeddings
        mock_emb = MagicMock()
        mock_emb.get_embedding_text.return_value = "Embedded text"
        mock_emb_fn.return_value = mock_emb

        # Test 1: Cached response
        mock_cache.get_cached_answer.return_value = "Cached answer"
        response = self.client.post(
            "/api/ask",
            json={
                "question": "test question",
                "model_name": "test-model"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["answer"], "Cached answer")
        self.assertTrue(data["cached"])
        self.assertEqual(data["model"], "test-model")

        # Test 2: Non-cached response with generation
        mock_cache.get_cached_answer.return_value = None
        response = self.client.post(
            "/api/ask",
            json={
                "question": "test question",
                "model_name": "test-model",
                "prompt": "Custom prompt",
                "max_tokens": 100
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["answer"], "Generated answer")
        self.assertFalse(data["cached"])

        # Test 3: Non-cached response with context
        response = self.client.post(
            "/api/ask",
            json={
                "question": "test question",
                "model_name": "test-model",
                "context_paths": ["note1.md", "note2.md"],
                "prefer_fast": True
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["answer"], "Fresh answer")
        self.assertFalse(data["cached"])

        # Test 3: Response with context paths
        mock_emb.get_embedding_text.return_value = "Context text"
        mock_model.query.return_value = "Contextual answer"
        response = self.client.post(
            "/api/ask",
            json={
                "question": "test question",
                "model_name": "test-model",
                "context_paths": ["note1.md", "note2.md"]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Contextual answer")

        # Test 4: Custom prompt
        mock_model.generate.return_value = "Generated answer"
        response = self.client.post(
            "/api/ask",
            json={
                "question": "test question",
                "model_name": "test-model",
                "prompt": "Custom prompt",
                "max_tokens": 100
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Generated answer")

        # Test 5: Error handling
        mock_model_mgr.load_text_model.side_effect = Exception("Model error")
        response = self.client.post(
            "/api/ask",
            json={
                "question": "test question",
                "model_name": "test-model"
            }
        )
        self.assertEqual(response.status_code, 500)

    @patch("backend.backend.get_model_manager")
    def test_format_note_endpoint(self, mock_model_fn):
        """Test the note formatting endpoint."""
        # Set up test file
        test_note_path = os.path.join(self.test_vault_path, "test.md")
        test_content = "Test note content"
        with open(test_note_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Set up mock model
        mock_model_mgr = MagicMock()
        mock_model = MagicMock()
        mock_model.query.return_value = "Improved note content"
        mock_model_mgr.load_text_model.return_value = mock_model
        mock_model_fn.return_value = mock_model_mgr

        # Test successful case
        response = self.client.post(
            "/api/format_note",
            json={
                "note_path": test_note_path,
                "content": test_content
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["suggestions"], "Improved note content")

        # Test missing file
        response = self.client.post(
            "/api/format_note",
            json={
                "note_path": "nonexistent.md",
                "content": "test"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["error"], "note not found")

        # Test error handling
        mock_model.query.side_effect = Exception("Format failed")
        response = self.client.post(
            "/api/format_note",
            json={
                "note_path": test_note_path,
                "content": test_content
            }
        )
        self.assertEqual(response.status_code, 500)

    @patch("backend.backend.get_emb_manager")
    def test_link_notes_endpoint(self, mock_emb_fn):
        """Test the note linking endpoint."""
        # Set up mock embeddings
        mock_emb = MagicMock()
        mock_search_results = [
            {"text": "Note 1 content", "source": "note1.md"},
            {"text": "Note 2 content", "source": "note2.md"},
            {"text": "Test content", "source": "test.md"}
        ]
        mock_emb.search.return_value = mock_search_results
        mock_emb_fn.return_value = mock_emb

        # Test successful case
        response = self.client.post(
            "/api/link_notes",
            json={
                "note_path": "test.md",
                "content": "Test content"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["related_notes"]), 2)
        self.assertIn("note1.md", data["related_notes"])
        self.assertIn("note2.md", data["related_notes"])

        # Test error handling
        mock_emb.search.side_effect = Exception("Search failed")
        response = self.client.post(
            "/api/link_notes",
            json={
                "note_path": "test.md",
                "content": "Test content"
            }
        )
        self.assertEqual(response.status_code, 500)

    def test_save_note_changes_endpoint(self):
        """Test saving note changes."""
        test_note_path = os.path.join(self.test_vault_path, "new_note.md")
        test_content = "New note content"

        response = self.client.post(
            "/api/save_note_changes",
            json={
                "note_path": test_note_path,
                "content": test_content
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists(test_note_path))
        with open(test_note_path, "r") as f:
            self.assertEqual(f.read(), test_content)

    @patch("backend.backend.get_vault_indexer")
    def test_scan_vault_endpoint(self, mock_vault_fn):
        """Test vault scanning functionality."""
        # Set up mock indexer
        mock_vault = MagicMock()
        mock_vault.index_vault.return_value = ["file1.md", "file2.md"]
        mock_vault_fn.return_value = mock_vault

        # Test successful case
        response = self.client.post(
            "/api/scan_vault",
            params={"vault_path": self.test_vault_path}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["indexed_files"]), 2)
        self.assertEqual(data["status"], "success")

        # Test error case
        mock_vault.index_vault.side_effect = Exception("Scan failed")
        response = self.client.post(
            "/api/scan_vault",
            params={"vault_path": self.test_vault_path}
        )
        self.assertEqual(response.status_code, 500)

    @patch("backend.backend.get_vault_indexer")
    def test_fetch_url_endpoint(self, mock_vault_fn):
        """Test URL fetching and indexing."""
        mock_vault = MagicMock()
        mock_vault.fetch_web_page.return_value = "Web page content"
        mock_vault_fn.return_value = mock_vault
        
        response = self.client.post(
            "/api/fetch_url",
            json={"url": "http://test.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"url": "http://test.com", "status": "fetched"}
        )

    @patch("backend.backend.get_emb_manager")
    @patch("backend.backend.get_vault_indexer")
    def test_reindex_endpoint(self, mock_vault_fn, mock_emb_fn):
        """Test reindexing functionality."""
        # Set up mocks
        mock_emb = MagicMock()
        mock_emb_fn.return_value = mock_emb
        
        mock_vault = MagicMock()
        mock_vault.reindex_all.return_value = ["file1.md", "file2.md"]
        mock_vault_fn.return_value = mock_vault

        # Test successful case
        response = self.client.post(
            "/api/reindex",
            params={"vault_path": self.test_vault_path}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "reindexed")
        self.assertEqual(len(data["indexed_files"]), 2)

        # Test error case
        mock_vault.reindex_all.side_effect = Exception("Reindex failed")
        response = self.client.post(
            "/api/reindex",
            params={"vault_path": self.test_vault_path}
        )
        self.assertEqual(response.status_code, 500)

    @patch("backend.backend.get_emb_manager")
    def test_search_endpoint(self, mock_emb_fn):
        """Test search functionality."""
        # Set up mock embeddings
        mock_emb = MagicMock()
        mock_results = [
            {"text": "First note content", "source": "note1.md"},
            {"text": "Second note content", "source": "note2.md"}
        ]
        mock_emb.search.return_value = mock_results
        mock_emb_fn.return_value = mock_emb

        # Test successful case
        response = self.client.post(
            "/api/search",
            params={"query": "test query", "top_k": 2}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"], mock_results)

        # Test with different top_k
        response = self.client.post(
            "/api/search",
            params={"query": "test query", "top_k": 1}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"], mock_results)

        # Test error handling
        mock_emb.search.side_effect = Exception("Search failed")
        response = self.client.post(
            "/api/search",
            params={"query": "test query"}
        )
        self.assertEqual(response.status_code, 500)

    @patch("backend.backend.get_vault_indexer")
    def test_index_pdf_endpoint(self, mock_vault_fn):
        """Test PDF indexing functionality."""
        mock_vault = MagicMock()
        mock_vault.index_pdf.return_value = 5  # 5 chunks indexed
        mock_vault_fn.return_value = mock_vault
        
        response = self.client.post(
            "/api/index_pdf",
            params={"pdf_path": "test.pdf"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["chunks_indexed"], 5)


if __name__ == '__main__':
    unittest.main()
