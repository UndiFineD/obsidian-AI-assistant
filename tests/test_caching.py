import os
import sys
import time
import json
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

# Import after path setup
from backend.caching import CacheManager, EmbeddingCache, FileHashCache  # noqa


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_cache_dir = "test_cache"
        self.cache_mgr = CacheManager(self.test_cache_dir, ttl=1)
        Path(self.test_cache_dir).mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def test_init_with_nonexistent_cache(self):
        """Test initialization with no existing cache file."""
        cache_mgr = CacheManager(self.test_cache_dir)
        self.assertEqual(cache_mgr.cache, {})
        self.assertTrue(os.path.exists(self.test_cache_dir))

    def test_init_with_existing_cache(self):
        """Test initialization with existing cache file."""
        cache_data = {
            "test_q": {
                "answer": "test_a",
                "timestamp": time.time()
            }
        }
        cache_file = Path(self.test_cache_dir) / "answers.json"
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)

        cache_mgr = CacheManager(self.test_cache_dir)
        self.assertEqual(cache_mgr.cache, cache_data)

    def test_store_and_retrieve_answer(self):
        """Test storing and retrieving answers."""
        question = "test question"
        answer = "test answer"
        
        # Store answer
        self.cache_mgr.store_answer(question, answer)
        
        # Retrieve answer
        cached = self.cache_mgr.get_cached_answer(question)
        self.assertEqual(cached, answer)
        
        # Verify file persistence
        with open(Path(self.test_cache_dir) / "answers.json") as f:
            data = json.load(f)
            self.assertEqual(data[question]["answer"], answer)

    def test_ttl_expiration(self):
        """Test TTL-based cache expiration."""
        self.cache_mgr.store_answer("q1", "a1")
        time.sleep(1.1)  # Wait for TTL to expire
        self.assertIsNone(self.cache_mgr.get_cached_answer("q1"))


class TestEmbeddingCache(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_cache_dir = "test_cache"
        self.emb_cache = EmbeddingCache(self.test_cache_dir)
        Path(self.test_cache_dir).mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def test_hash_key_generation(self):
        """Test consistent hash key generation."""
        text = "test text"
        key1 = self.emb_cache._hash_key(text)
        key2 = self.emb_cache._hash_key(text)
        self.assertEqual(key1, key2)
        
        # Test with whitespace variations
        key3 = self.emb_cache._hash_key(text + "  ")
        self.assertEqual(key1, key3)

    def test_get_or_compute_new(self):
        """Test computing and storing new embeddings."""
        text = "test text"
        mock_embedding = [0.1, 0.2, 0.3]
        
        def mock_fn(x):
            return mock_embedding

        result = self.emb_cache.get_or_compute(text, mock_fn)
        self.assertEqual(result, mock_embedding)
        
        # Verify cache persistence
        with open(Path(self.test_cache_dir) / "embeddings.json") as f:
            data = json.load(f)
            key = self.emb_cache._hash_key(text)
            self.assertEqual(data[key], mock_embedding)

    def test_get_or_compute_cached(self):
        """Test retrieving cached embeddings."""
        text = "test text"
        mock_embedding = [0.1, 0.2, 0.3]
        
        def mock_compute(x):
            return mock_embedding

        # First call computes
        self.emb_cache.get_or_compute(text, mock_compute)
        
        def mock_never_called(x):
            return [0.9, 0.9, 0.9]

        # Second call should retrieve from cache
        result = self.emb_cache.get_or_compute(text, mock_never_called)
        self.assertEqual(result, mock_embedding)


class TestFileHashCache(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_cache_dir = "test_cache"
        self.test_files_dir = "test_files"
        self.hash_cache = FileHashCache(self.test_cache_dir)
        Path(self.test_cache_dir).mkdir(exist_ok=True)
        Path(self.test_files_dir).mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        for path in [self.test_cache_dir, self.test_files_dir]:
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_hash_file(self):
        """Test file hash computation."""
        test_file = Path(self.test_files_dir) / "test.txt"
        content = b"test content"
        with open(test_file, "wb") as f:
            f.write(content)

        hash1 = self.hash_cache._hash_file(test_file)
        hash2 = self.hash_cache._hash_file(test_file)
        self.assertEqual(hash1, hash2)
        
        # Modify file and check hash change
        with open(test_file, "wb") as f:
            f.write(b"modified content")
        hash3 = self.hash_cache._hash_file(test_file)
        self.assertNotEqual(hash1, hash3)

    def test_is_changed_detection(self):
        """Test file change detection."""
        test_file = Path(self.test_files_dir) / "test.txt"
        
        # Initial file
        with open(test_file, "wb") as f:
            f.write(b"initial content")
        
        # First check should detect as changed
        self.assertTrue(self.hash_cache.is_changed(test_file))
        
        # Second check with same content should not detect change
        self.assertFalse(self.hash_cache.is_changed(test_file))
        
        # Modify file
        with open(test_file, "wb") as f:
            f.write(b"modified content")
        
        # Should detect change
        self.assertTrue(self.hash_cache.is_changed(test_file))


if __name__ == '__main__':
    unittest.main()
