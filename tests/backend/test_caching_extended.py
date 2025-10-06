# tests/backend/test_caching_extended.py
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock

# Import only what we need to avoid conflicts
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.caching import EmbeddingCache, FileHashCache


class TestEmbeddingCacheExtended:
    """Extended tests for EmbeddingCache class."""
    
    def test_embedding_cache_initialization(self):
        """Test EmbeddingCache initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            assert cache.cache_file.parent == Path(temp_dir)
            assert cache.data == {}
    
    def test_embedding_cache_get_or_compute_new(self):
        """Test computing new embedding and caching it."""
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
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            
            hash1 = cache._hash_key("test text")
            hash2 = cache._hash_key("test text")
            hash3 = cache._hash_key("  test text  ")  # With whitespace
            
            assert hash1 == hash2
            assert hash1 == hash3  # Should strip whitespace
    
    def test_embedding_cache_persist_and_reload(self):
        """Test that cache persists to disk and reloads."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First cache instance
            cache1 = EmbeddingCache(cache_dir=temp_dir)
            cache1.get_or_compute("test", lambda x: [1, 2, 3])
            
            # Second cache instance should load from disk
            cache2 = EmbeddingCache(cache_dir=temp_dir)
            result = cache2.get_or_compute("test", lambda x: [999, 999, 999])
            assert result == [1, 2, 3]  # Should load from disk, not compute
    
    def test_embedding_cache_with_failing_embed_function(self):
        """Test EmbeddingCache when embedding function fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            
            def failing_embed_fn(text):
                raise ValueError("Embedding failed")
            
            result = cache.get_or_compute("test", failing_embed_fn)
            assert result == []  # Should return default empty list
    
    def test_embedding_cache_corrupted_cache_file(self):
        """Test EmbeddingCache with corrupted cache file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create corrupted cache file
            cache_file = Path(temp_dir) / "embeddings.json"
            cache_file.write_text("invalid json content")
            
            # Should handle gracefully and start with empty cache
            cache = EmbeddingCache(cache_dir=temp_dir)
            assert cache.data == {}
    
    def test_embedding_cache_multiple_texts(self):
        """Test caching multiple different texts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EmbeddingCache(cache_dir=temp_dir)
            
            # Cache multiple embeddings
            result1 = cache.get_or_compute("text1", lambda x: [1, 1, 1])
            result2 = cache.get_or_compute("text2", lambda x: [2, 2, 2])
            result3 = cache.get_or_compute("text1", lambda x: [999, 999, 999])  # Should use cache
            
            assert result1 == [1, 1, 1]
            assert result2 == [2, 2, 2]
            assert result3 == [1, 1, 1]  # From cache, not new computation


class TestFileHashCacheExtended:
    """Extended tests for FileHashCache class."""
    
    def test_file_hash_cache_initialization(self):
        """Test FileHashCache initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            assert cache.cache_file.parent == Path(temp_dir)
            assert cache.data == {}
    
    def test_file_hash_cache_is_changed_new_file(self):
        """Test is_changed with a new file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            
            # Should be considered changed (new file)
            assert cache.is_changed(test_file) is True
            
            # Should not be considered changed (already cached)
            assert cache.is_changed(test_file) is False
    
    def test_file_hash_cache_detects_changes(self):
        """Test that file changes are detected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            
            # Create and cache a file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("original content")
            cache.is_changed(test_file)  # Cache it
            
            # Modify the file
            test_file.write_text("modified content")
            
            # Should detect the change
            assert cache.is_changed(test_file) is True
    
    def test_file_hash_cache_persist_and_reload(self):
        """Test that file hash cache persists and reloads."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            
            # First cache instance
            cache1 = FileHashCache(cache_dir=temp_dir)
            cache1.is_changed(test_file)  # Cache the file
            
            # Second cache instance should load from disk
            cache2 = FileHashCache(cache_dir=temp_dir)
            assert cache2.is_changed(test_file) is False  # Should be loaded from cache
    
    def test_file_hash_cache_with_nonexistent_file(self):
        """Test FileHashCache with non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            
            nonexistent_file = Path(temp_dir) / "nonexistent.txt"
            # Should handle gracefully and return True (changed/new)
            result = cache.is_changed(nonexistent_file)
            assert result is True
    
    def test_file_hash_cache_corrupted_cache_file(self):
        """Test FileHashCache with corrupted cache file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create corrupted cache file
            cache_file = Path(temp_dir) / "filehashes.json"
            cache_file.write_text("invalid json content")
            
            # Should handle gracefully and start with empty cache
            cache = FileHashCache(cache_dir=temp_dir)
            assert cache.data == {}
    
    def test_file_hash_cache_multiple_files(self):
        """Test caching multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileHashCache(cache_dir=temp_dir)
            
            # Create multiple test files
            file1 = Path(temp_dir) / "test1.txt"
            file2 = Path(temp_dir) / "test2.txt"
            file1.write_text("content 1")
            file2.write_text("content 2")
            
            # Cache both files
            assert cache.is_changed(file1) is True  # New file
            assert cache.is_changed(file2) is True  # New file
            assert cache.is_changed(file1) is False  # Cached
            assert cache.is_changed(file2) is False  # Cached
    
    def test_file_hash_consistency_across_instances(self):
        """Test that file hashes are consistent across cache instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("consistent content")
            
            # Hash with first cache instance
            cache1 = FileHashCache(cache_dir=temp_dir)
            hash1 = cache1._hash_file(test_file)
            
            # Hash with second cache instance
            cache2 = FileHashCache(cache_dir=temp_dir)
            hash2 = cache2._hash_file(test_file)
            
            assert hash1 == hash2
            assert hash1 != ""  # Should not be empty


if __name__ == "__main__":
    pytest.main([__file__])