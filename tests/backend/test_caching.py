# tests/backend/test_caching.py
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
from backend.caching import CacheManager

@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def cache_manager(temp_cache_dir):
    """Create a CacheManager instance for testing."""
    return CacheManager(cache_dir=temp_cache_dir, ttl=3600)

def test_cache_manager_initialization(temp_cache_dir):
    """Test CacheManager initialization."""
    cache_mgr = CacheManager(cache_dir=temp_cache_dir, ttl=1800)
    assert cache_mgr.cache_dir == Path(temp_cache_dir)
    assert cache_mgr.ttl == 1800
    assert cache_mgr.cache_dir.exists()
    assert isinstance(cache_mgr.cache, dict)

def test_cache_manager_with_default_values():
    """Test CacheManager with default values."""
    with patch('pathlib.Path.mkdir'):
        cache_mgr = CacheManager()
        assert str(cache_mgr.cache_dir == "cache")
        assert cache_mgr.ttl == 86400  # Default 24 hours

def test_cache_manager_store_and_retrieve(cache_manager):
    """Test storing and retrieving answers."""
    question = "Test question"
    answer = "Test answer"
    cache_manager.store_answer(question, answer)
    retrieved = cache_manager.get_cached_answer(question)
    assert retrieved == answer

def test_cache_manager_error_handling_save(cache_manager):
    """Test error handling during cache save."""
    question = "Test question"
    answer = "Test answer"
    # Mock file operations to raise exception
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        # Should not raise exception, just continue
        cache_manager.store_answer(question, answer)
        # Answer should still be in memory cache
        assert cache_manager.get_cached_answer(question) == answer

def test_cache_manager_error_handling_load(temp_cache_dir):
    """Test error handling during cache load."""
    # Create invalid cache file
    cache_file = Path(temp_cache_dir) / "answers.json"
    cache_file.write_text("invalid json content")
    # Should initialize with empty cache without crashing
    cache_mgr = CacheManager(cache_dir=temp_cache_dir)
    assert cache_mgr.cache == {}

def test_cache_manager_long_question(cache_manager):
    """Test that question hashing works correctly for long questions."""
    # Create a very long question that would exceed filename limits
    long_question = "This is a very long question " * 100
    answer = "Answer to long question"
    # Should handle long questions gracefully
    cache_manager.store_answer(long_question, answer)
    retrieved = cache_manager.get_cached_answer(long_question)
    assert retrieved == answer

def test_cache_manager_overwrite(cache_manager):
    """Test overwriting existing cache entries."""
    question = "What is AI?"
    answer1 = "First answer about AI"
    answer2 = "Updated answer about AI"
    # Cache first answer
    cache_manager.store_answer(question, answer1)
    assert cache_manager.get_cached_answer(question) == answer1
    # Overwrite with second answer
    cache_manager.store_answer(question, answer2)
    assert cache_manager.get_cached_answer(question) == answer2

def test_cache_file_creation(temp_cache_dir):
    """Test that cache file is created properly."""
    cache_mgr = CacheManager(cache_dir=temp_cache_dir)
    question = "Test creation"
    answer = "Test answer"
    cache_mgr.store_answer(question, answer)
    cache_file = Path(temp_cache_dir) / "answers.json"
    assert cache_file.exists()

def test_empty_question_and_answer():
    """Test handling of empty strings."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_mgr = CacheManager(cache_dir=temp_dir)
        cache_mgr.store_answer("", "")
        assert cache_mgr.get_cached_answer("") == ""

def test_none_values():
    """Test handling of None values."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_mgr = CacheManager(cache_dir=temp_dir)
        # Should handle None gracefully
        result = cache_mgr.get_cached_answer(None)
        assert result is None



class TestEmbeddingCache:
    """Test EmbeddingCache class specifically."""
    
    def test_embedding_cache_initialization(self):
        """Test EmbeddingCache initialization."""
        from backend.caching import EmbeddingCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            assert cache.cache_file.parent == Path(temp_dir)
            assert cache.data == {}
    
    def test_embedding_cache_get_or_compute_new(self):
        """Test computing new embedding and caching it."""
        from backend.caching import EmbeddingCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            def mock_embed_fn(text):
                return [0.1, 0.2, 0.3]  # Mock embedding
            result = cache.get_or_compute("test text", mock_embed_fn)
            assert result == [0.1, 0.2, 0.3]
            # Should be cached now
            result2 = cache.get_or_compute("test text", lambda x: [999, 999, 999])
            assert result2 == [0.1, 0.2, 0.3]  # Should return cached, not compute new
    
    def test_embedding_cache_hash_key_consistent(self):
        """Test that hash keys are consistent."""
        from backend.caching import EmbeddingCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            hash1 = cache._hash_key("test text")
            hash2 = cache._hash_key("test text")
            hash3 = cache._hash_key("  test text  ")  # With whitespace
            assert hash1 == hash2
            assert hash1 == hash3  # Should strip whitespace
    
    def test_embedding_cache_persist_and_reload(self):
        """Test that cache persists to disk and reloads."""
        from backend.caching import EmbeddingCache
        with tempfile.TemporaryDirectory() as temp_dir:
            # First cache instance
            cache1 = EmbeddingCache(cache_dir=temp_dir)
            cache1.get_or_compute("test", lambda x: [1, 2, 3])
            # Second cache instance should load from disk
            cache2 = EmbeddingCache(cache_dir=temp_dir)
            result = cache2.get_or_compute("test", lambda x: [999, 999, 999])
            assert result == [1, 2, 3]  # Should load from disk, not compute


class TestFileHashCache:
    """Test FileHashCache class specifically."""
    
    def test_file_hash_cache_initialization(self):
        """Test FileHashCache initialization."""
        from backend.caching import FileHashCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            assert cache.cache_file.parent == Path(temp_dir)
            assert cache.data == {}
    
    def test_file_hash_cache_is_changed_new_file(self):
        """Test is_changed with a new file."""
        from backend.caching import FileHashCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            # Should be considered changed (new file)
            assert cache.is_changed(test_file is True)
            # Should not be considered changed (already cached)
            assert cache.is_changed(test_file is False)
    
    def test_file_hash_cache_detects_changes(self):
        """Test that file changes are detected."""
        from backend.caching import FileHashCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            # Create and cache a file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("original content")
            cache.is_changed(test_file)  # Cache it
            # Modify the file
            test_file.write_text("modified content")
            # Should detect the change
            assert cache.is_changed(test_file is True)
    
    def test_file_hash_cache_persist_and_reload(self):
        """Test that file hash cache persists and reloads."""
        from backend.caching import FileHashCache
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            # First cache instance
            cache1 = FileHashCache(cache_dir=temp_dir)
            cache1.is_changed(test_file)  # Cache the file
            # Second cache instance should load from disk
            cache2 = FileHashCache(cache_dir=temp_dir)
            assert cache2.is_changed(test_file is False)  # Should be loaded from cache


class TestCachingErrorScenarios:
    """Test error handling scenarios in caching."""
    
    def test_embedding_cache_with_failing_embed_function(self):
        """Test EmbeddingCache when embedding function fails."""
        from backend.caching import EmbeddingCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            def failing_embed_fn(text):
                raise ValueError("Embedding failed")
            result = cache.get_or_compute("test", failing_embed_fn)
            assert result == []  # Should return default empty list
    
    def test_file_hash_cache_with_nonexistent_file(self):
        """Test FileHashCache with non-existent file."""
        from backend.caching import FileHashCache
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            nonexistent_file = Path(temp_dir) / "nonexistent.txt"
            # Should handle gracefully and return True (changed/new)
            result = cache.is_changed(nonexistent_file)
            assert result is True
    
    def test_embedding_cache_corrupted_cache_file(self):
        """Test EmbeddingCache with corrupted cache file."""
        from backend.caching import EmbeddingCache
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create corrupted cache file
            cache_file = Path(temp_dir) / "embeddings.json"
            cache_file.write_text("invalid json content")
            # Should handle gracefully and start with empty cache
            cache = EmbeddingCache(cache_dir=temp_dir)
            assert cache.data == {}
    
    def test_file_hash_cache_corrupted_cache_file(self):
        """Test FileHashCache with corrupted cache file."""
        from backend.caching import FileHashCache
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create corrupted cache file
            cache_file = Path(temp_dir) / "filehashes.json"
            cache_file.write_text("invalid json content")
            # Should handle gracefully and start with empty cache
            cache = FileHashCache(cache_dir=temp_dir)
            assert cache.data == {}


if __name__ == "__main__":
    pytest.main([__file__])
