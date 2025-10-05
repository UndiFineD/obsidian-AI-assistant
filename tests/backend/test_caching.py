# tests/backend/test_caching.py
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import pytest
from backend.caching import CacheManager

# For other modules:
from backend.caching import CacheManager
from backend.embeddings import EmbeddingsManager
from backend.indexing import VaultIndexer
from backend.llm_router import HybridLLMRouter

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
        assert str(cache_mgr.cache_dir) == "cache"
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

def test_concurrent_access_simulation():
    """Test behavior under simulated concurrent access."""
    import threading
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_manager = CacheManager(cache_dir=temp_dir, ttl=3600)
        results = []


def cache_worker(i):
    question = f"Question {i}"
    answer = f"Answer {i}"
    cache_manager.store_answer(question, answer)
    result = cache_manager.get_cached_answer(question)
    results.append(result == answer)
    # Create multiple threads
    threads = []
    for i in range(10):
        thread = threading.Thread(target=cache_worker, args=(i,))
        threads.append(thread)
        thread.start()
    # Wait for all threads
    for thread in threads:
        thread.join()
    # All operations should succeed
    assert all(results)

if __name__ == "__main__":
    pytest.main([__file__])
