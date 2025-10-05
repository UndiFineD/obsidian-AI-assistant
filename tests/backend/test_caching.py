# tests/backend/test_caching.py
import pytest
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
import sys

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from caching import CacheManager


class TestCacheManager:
    """Test suite for the CacheManager class."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary directory for cache testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Create a CacheManager instance for testing."""
        return CacheManager(cache_dir=temp_cache_dir, ttl=3600)
    
    def test_cache_manager_initialization(self, temp_cache_dir):
        """Test CacheManager initialization."""
        cache_mgr = CacheManager(cache_dir=temp_cache_dir, ttl=1800)
        
        assert cache_mgr.cache_dir == Path(temp_cache_dir)
        assert cache_mgr.ttl == 1800
        assert cache_mgr.cache_dir.exists()
        assert isinstance(cache_mgr.cache, dict)
    
    def test_cache_manager_default_values(self):
        """Test CacheManager with default values."""
        with patch('pathlib.Path.mkdir'):
            cache_mgr = CacheManager()
            
            assert str(cache_mgr.cache_dir) == "./cache"
            assert cache_mgr.ttl == 86400  # Default 24 hours
    
    def test_cache_answer_and_retrieval(self, cache_manager):
        """Test caching and retrieving an answer."""
        question = "What is Python?"
        answer = "Python is a programming language."
        
        # Cache the answer
        cache_manager.cache_answer(question, answer)
        
        # Retrieve the answer
        retrieved = cache_manager.get_cached_answer(question)
        assert retrieved == answer
    
    def test_cache_miss(self, cache_manager):
        """Test cache miss scenario."""
        result = cache_manager.get_cached_answer("Non-existent question")
        assert result is None
    
    def test_cache_persistence(self, temp_cache_dir):
        """Test that cache persists across instances."""
        question = "What is FastAPI?"
        answer = "FastAPI is a web framework."
        
        # Create first instance and cache answer
        cache_mgr1 = CacheManager(cache_dir=temp_cache_dir)
        cache_mgr1.cache_answer(question, answer)
        
        # Create second instance and check persistence
        cache_mgr2 = CacheManager(cache_dir=temp_cache_dir)
        retrieved = cache_mgr2.get_cached_answer(question)
        assert retrieved == answer
    
    def test_cache_ttl_expiry(self, cache_manager):
        """Test that cached entries expire after TTL."""
        question = "What expires?"
        answer = "This will expire"
        
        # Cache with short TTL
        cache_manager.ttl = 1  # 1 second TTL
        cache_manager.cache_answer(question, answer)
        
        # Immediate retrieval should work
        assert cache_manager.get_cached_answer(question) == answer
        
        # Wait for expiry and mock time
        with patch('time.time', return_value=time.time() + 2):
            result = cache_manager.get_cached_answer(question)
            assert result is None
    
    def test_cache_without_ttl(self, cache_manager):
        """Test caching behavior when entries don't have timestamps."""
        question = "Old format question"
        answer = "Old format answer"
        
        # Manually add entry without timestamp (simulating old cache format)
        cache_manager.cache[question] = {"answer": answer}
        
        # Should still retrieve successfully
        retrieved = cache_manager.get_cached_answer(question)
        assert retrieved == answer
    
    def test_save_cache_error_handling(self, cache_manager):
        """Test error handling during cache save."""
        question = "Test question"
        answer = "Test answer"
        
        # Mock file operations to raise exception
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            # Should not raise exception, just continue
            cache_manager.cache_answer(question, answer)
            
            # Answer should still be in memory cache
            assert cache_manager.get_cached_answer(question) == answer
    
    def test_load_cache_error_handling(self, temp_cache_dir):
        """Test error handling during cache load."""
        # Create invalid cache file
        cache_file = Path(temp_cache_dir) / "answers.json"
        cache_file.write_text("invalid json content")
        
        # Should initialize with empty cache without crashing
        cache_mgr = CacheManager(cache_dir=temp_cache_dir)
        assert cache_mgr.cache == {}
    
    def test_hash_generation(self, cache_manager):
        """Test that question hashing works correctly for long questions."""
        # Create a very long question that would exceed filename limits
        long_question = "This is a very long question " * 100
        answer = "Answer to long question"
        
        # Should handle long questions gracefully
        cache_manager.cache_answer(long_question, answer)
        retrieved = cache_manager.get_cached_answer(long_question)
        assert retrieved == answer
    
    def test_cache_overwrite(self, cache_manager):
        """Test overwriting existing cache entries."""
        question = "What is AI?"
        answer1 = "First answer about AI"
        answer2 = "Updated answer about AI"
        
        # Cache first answer
        cache_manager.cache_answer(question, answer1)
        assert cache_manager.get_cached_answer(question) == answer1
        
        # Overwrite with second answer
        cache_manager.cache_answer(question, answer2)
        assert cache_manager.get_cached_answer(question) == answer2
    
    def test_cache_file_creation(self, temp_cache_dir):
        """Test that cache file is created properly."""
        cache_mgr = CacheManager(cache_dir=temp_cache_dir)
        question = "Test creation"
        answer = "Test answer"
        
        cache_mgr.cache_answer(question, answer)
        
        cache_file = Path(temp_cache_dir) / "answers.json"
        assert cache_file.exists()
        
        # Verify file contents
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert question in data
            assert data[question]["answer"] == answer
            assert "timestamp" in data[question]
    
    def test_unicode_handling(self, cache_manager):
        """Test handling of unicode characters in questions and answers."""
        question = "¿Qué es Python? 🐍"
        answer = "Python es un lenguaje de programación 💻"
        
        cache_manager.cache_answer(question, answer)
        retrieved = cache_manager.get_cached_answer(question)
        assert retrieved == answer


class TestCacheManagerEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_empty_question_and_answer(self):
        """Test handling of empty strings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_mgr = CacheManager(cache_dir=temp_dir)
            
            cache_mgr.cache_answer("", "")
            assert cache_mgr.get_cached_answer("") == ""
    
    def test_none_values(self):
        """Test handling of None values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_mgr = CacheManager(cache_dir=temp_dir)
            
            # Should handle None gracefully
            result = cache_mgr.get_cached_answer(None)
            assert result is None
    
    def test_concurrent_access_simulation(self, cache_manager):
        """Test behavior under simulated concurrent access."""
        import threading
        import time
        
        results = []
        
        def cache_worker(i):
            question = f"Question {i}"
            answer = f"Answer {i}"
            cache_manager.cache_answer(question, answer)
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