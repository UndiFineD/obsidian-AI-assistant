import os
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

# Import after path setup
from backend.embeddings import EmbeddingsManager  # noqa: E402


class TestEmbeddingsManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_db_path = "test_vector_db"
        self.test_vault_path = "test_vault"
        
        # Create test directories
        for path in [self.test_db_path, self.test_vault_path]:
            Path(path).mkdir(exist_ok=True)

        # Create a small test model to minimize memory usage
        self.emb_mgr = EmbeddingsManager(
            db_path=self.test_db_path,
            collection_name="test_collection",
            model_name="all-MiniLM-L6-v2"
        )

    def tearDown(self):
        """Clean up test environment."""
        # Close ChromaDB connection first
        if hasattr(self, 'emb_mgr'):
            if hasattr(self.emb_mgr, 'collection'):
                self.emb_mgr.collection = None
            if hasattr(self.emb_mgr, 'chroma_client'):
                self.emb_mgr.chroma_client = None
        import shutil
        for path in [self.test_db_path, self.test_vault_path]:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except PermissionError:
                    # If we can't remove it now, try again later
                    pass

    def test_initialization(self):
        """Test manager initialization with custom settings."""
        mgr = EmbeddingsManager(
            chunk_size=100,
            overlap=10,
            top_k=3,
            db_path=self.test_db_path,
            collection_name="custom_test",
            model_name="all-MiniLM-L6-v2"
        )
        self.assertEqual(mgr.chunk_size, 100)
        self.assertEqual(mgr.overlap, 10)
        self.assertEqual(mgr.top_k, 3)
        self.assertEqual(mgr.db_path, self.test_db_path)
        self.assertEqual(mgr.collection_name, "custom_test")

    def test_compute_embedding(self):
        """Test embedding computation."""
        test_text = "This is a test sentence."
        embedding = self.emb_mgr.compute_embedding(test_text)
        
        # Check embedding properties
        self.assertIsInstance(embedding, list)
        self.assertTrue(all(isinstance(x, float) for x in embedding))
        self.assertTrue(len(embedding) > 0)

    def test_add_and_search_embedding(self):
        """Test adding and searching embeddings."""
        test_text = "This is a test note about AI."
        test_path = "test_note.md"
        
        # Add embedding
        self.emb_mgr.add_embedding(test_text, test_path)
        
        # Search with exact match
        results = self.emb_mgr.search(test_text, top_k=1)
        self.assertEqual(len(results), 1)
        
        # Search with semantic similarity
        similar_query = "Tell me about artificial intelligence"
        results = self.emb_mgr.search(similar_query, top_k=5)
        self.assertTrue(len(results) > 0)

    def test_get_embedding_text(self):
        """Test retrieving embedding text."""
        test_text = "This is a test note."
        test_path = "test_note.md"
        
        # Add embedding and retrieve
        self.emb_mgr.add_embedding(test_text, test_path)
        result = self.emb_mgr.get_embedding_text(test_path)
        self.assertIsInstance(result, str)

    def test_reset_db(self):
        """Test database reset functionality."""
        # Add some test data
        test_texts = [
            "First test note",
            "Second test note",
            "Third test note"
        ]
        for i, text in enumerate(test_texts):
            self.emb_mgr.add_embedding(text, f"note_{i}.md")
        
        # Reset database
        self.emb_mgr.reset_db()
        
        # Verify reset
        results = self.emb_mgr.search("test", top_k=5)
        self.assertEqual(len(results), 0)

    def test_text_chunking(self):
        """Test text chunking functionality."""
        # Create a long text with known word count
        words = ["word"] * 1000
        test_text = " ".join(words)
        
        chunks = self.emb_mgr.chunk_text(test_text)
        
        # Check chunk properties
        self.assertTrue(len(chunks) > 1)
        for chunk in chunks[:-1]:  # All but last chunk
            chunk_words = chunk.split()
            self.assertLessEqual(
                len(chunk_words),
                self.emb_mgr.chunk_size
            )

    def test_index_file(self):
        """Test file indexing."""
        # Create a test markdown file
        test_file = Path(self.test_vault_path) / "test.md"
        test_content = [
            "# Test Note",
            "",
            "This is a test note with multiple paragraphs.",
            "",
            "Second paragraph with more content.",
            "",
            "Third paragraph to ensure chunking."
        ]
        test_content = "\n".join(test_content)
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Index the file
        chunk_count = self.emb_mgr.index_file(str(test_file))
        self.assertTrue(chunk_count > 0)
        
        # Search for content
        results = self.emb_mgr.search("test note")
        self.assertTrue(len(results) > 0)
        # Check that one of the results contains our test file path
        found = any(str(test_file) == result["source"] for result in results)
        self.assertTrue(
            found,
            f"Expected to find {test_file} in results: {results}"
        )

    def test_index_vault(self):
        """Test vault indexing."""
        # Create multiple test files
        file_contents = {
            "note1.md": "First test note about AI",
            "note2.md": "Second test note about ML",
            "subfolder/note3.md": "Third test note about NLP"
        }
        
        for path, content in file_contents.items():
            full_path = Path(self.test_vault_path) / path
            full_path.parent.mkdir(exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Index vault
        results = self.emb_mgr.index_vault(self.test_vault_path)
        
        # Verify results
        self.assertEqual(len(results), len(file_contents))
        for path in file_contents:
            full_path = str(Path(self.test_vault_path) / path)
            self.assertIn(full_path, results)
            self.assertTrue(results[full_path] > 0)

    def test_reindex(self):
        """Test reindexing functionality."""
        # First index
        test_file = Path(self.test_vault_path) / "test.md"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Initial content")
        
        first_results = self.emb_mgr.index_vault(self.test_vault_path)
        
        # Modify content
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Modified content")
        
        # Reindex
        reindex_results = self.emb_mgr.reindex(self.test_vault_path)
        
        # Verify reindexing
        self.assertEqual(len(first_results), len(reindex_results))
        results = self.emb_mgr.search("Modified")
        self.assertTrue(len(results) > 0)


if __name__ == '__main__':
    unittest.main()
