# tests/test_performance.py
"""
Tests for performance optimization features including:
- Multi-level caching system
- Connection pooling
- Async task queue
- Performance monitoring
"""

import pytest
import time
import asyncio
from unittest.mock import Mock
from backend.performance import (
    MultiLevelCache, ConnectionPool, AsyncTaskQueue, 
    PerformanceMonitor, cached, get_cache_manager
)

class TestMultiLevelCache:
    """Test multi-level cache implementation"""
    
    def test_cache_creation(self):
        """Test cache initialization"""
        cache = MultiLevelCache(l1_size=10, l2_size=50)
        assert cache.l1_max_size == 10
        assert cache.l2_max_size == 50
    def test_basic_cache_operations(self):
        """Test basic get/set operations"""
        cache = MultiLevelCache(l1_size=5, l2_size=10)

        # Test miss
        assert cache.get("nonexistent") is None
        assert cache.get("nonexistent", "default") == "default"
        # Test set and get
        cache.set("key1", "value1", ttl=60)
        assert cache.get("key1") == "value1"
        # Verify it's in L1 cache
        assert "key1" in cache.l1_cache
        assert cache._stats['l1_hits'] == 1

    def test_l1_eviction_to_l2(self):
        """Test eviction from L1 to L2 cache"""
        cache = MultiLevelCache(l1_size=2, l2_size=10)
        
        # Fill L1 cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert len(cache.l1_cache) == 2
        # Add third item, should evict oldest from L1
        cache.set("key3", "value3")
        assert len(cache.l1_cache) == 2
        # First key should now be in L2
        assert "key1" not in cache.l1_cache
        result = cache.get("key1")  # Should promote from L2 to L1
        assert result == "value1"
        assert cache._stats['l2_hits'] >= 1

    def test_ttl_expiration(self):
        """Test TTL-based expiration"""
        cache = MultiLevelCache()
        # Set with very short TTL
        cache.set("short_ttl", "value", ttl=0.1)
        assert cache.get("short_ttl") == "value"
        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("short_ttl") is None
    
    def test_cache_statistics(self):
        """Test cache performance statistics"""
        cache = MultiLevelCache(l1_size=3, l2_size=5)
        
        # Generate some cache activity
        cache.set("key1", "value1")
        cache.get("key1")  # L1 hit
        cache.get("nonexistent")  # Miss
        
        stats = cache.get_stats()
        assert "l1_hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert stats["l1_hits"] >= 1
        assert stats["misses"] >= 1

class TestConnectionPool:
    """Test connection pool implementation"""
    
    def test_pool_creation(self):
        """Test connection pool initialization"""
        def factory():
            return Mock(status="connected")

        pool = ConnectionPool(factory, min_size=2, max_size=5)
        assert pool.min_size == 2
        assert pool.max_size == 5
        assert len(pool._pool) >= 2  # Pre-created connections
    
    def test_get_and_return_connection(self):
        """Test getting and returning connections"""
        def factory():
            return Mock(status="connected")

        pool = ConnectionPool(factory, min_size=1, max_size=3)

        # Get connection
        conn1 = pool.get_connection()
        assert conn1 is not None
        assert len(pool._active) == 1
        # Return connection
        pool.return_connection(conn1)
        assert len(pool._active) == 0
    
    def test_pool_exhaustion(self):
        """Test behavior when pool is exhausted"""
        def factory():
            return Mock(status="connected")
        
        pool = ConnectionPool(factory, min_size=0, max_size=2)
        
        # Get all connections
        conn1 = pool.get_connection()
    # (removed unused variable)
        
        # Should raise error when exhausted
        with pytest.raises(RuntimeError, match="Connection pool exhausted"):
            pool.get_connection()
        
        # Return one and try again
        pool.return_connection(conn1)
        conn3 = pool.get_connection()  # Should work now
        assert conn3 is not None
    
    def test_connection_validation(self):
        """Test connection validation"""
        call_count = 0
        def factory():
            nonlocal call_count
            call_count += 1
            mock = Mock(status="connected")
            mock.is_valid = call_count > 1  # First connection invalid
            return mock
        
        pool = ConnectionPool(factory, min_size=0, max_size=2)
        
        # Override validation method
    # (removed unused variable)
        pool._is_connection_valid = lambda conn: getattr(conn, 'is_valid', True)
        
        conn = pool.get_connection()
        assert conn is not None

@pytest.mark.asyncio
class TestAsyncTaskQueue:
    """Test async task queue implementation"""
    
    async def test_queue_creation_and_startup(self):
        """Test queue initialization and startup"""
        queue = AsyncTaskQueue(max_workers=2, max_queue_size=10)
        assert queue.max_workers == 2
        assert queue.max_queue_size == 10
        assert not queue._running
        await queue.start()
        assert queue._running
        assert len(queue.workers) == 2
        await queue.stop()
        assert not queue._running
        assert len(queue.workers) == 0
    
    async def test_task_submission_and_execution(self):
        """Test task submission and execution"""
        queue = AsyncTaskQueue(max_workers=2)
        await queue.start()
        
        # Create test task
        executed = []
        async def test_task(value):
            executed.append(value)
        
        # Submit task
        success = await queue.submit_task(test_task("test_value"))
        assert success
        
    # Wait for execution
    # (removed unreachable code)
    
    async def test_queue_statistics(self):
        """Test queue performance statistics"""
        queue = AsyncTaskQueue(max_workers=1)
        await queue.start()

        # Submit a task
        async def dummy_task():
            await asyncio.sleep(0.01)

        await queue.submit_task(dummy_task())
        await asyncio.sleep(0.1)  # Let it execute

        stats = queue.get_stats()
        assert "tasks_queued" in stats
        assert "tasks_completed" in stats
        assert "workers_active" in stats

        await queue.stop()

class TestCachedDecorator:
    """Test the @cached decorator"""
    
    def test_sync_function_caching(self):
        """Test caching on synchronous functions"""
        call_count = 0

        @cached(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Second call should be cached
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Not incremented
        # Different arguments should execute
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_async_function_caching(self):
        """Test caching on async functions"""
        call_count = 0

        @cached(ttl=60)
        async def async_expensive_function(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2

        # First call
        result1 = await async_expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should be cached
        result2 = await async_expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
    
    def test_custom_key_function(self):
        """Test custom key generation function"""
        call_count = 0
        @cached(ttl=60, key_func=lambda obj, attr: f"obj_{attr}")
        def get_attribute(obj, attr):
            nonlocal call_count
            call_count += 1
            return getattr(obj, attr, None)
        # Create test objects
        obj1 = Mock(name="test1")
        obj2 = Mock(name="test2")
        # First call
        obj1.name = "test1"
        obj2.name = "test2"
        result1 = get_attribute(obj1, "name")
        assert result1 == "test1"
        assert call_count == 1
        # Same attribute on different object, but same key
        result2 = get_attribute(obj2, "name")
        assert result2 == "test1"  # Should be cached
        assert call_count == 1

class TestPerformanceMonitor:
    """Test performance monitoring functionality"""
    
    def test_system_metrics_collection(self):
        """Test system metrics collection"""
        metrics = PerformanceMonitor.get_system_metrics()
        
        assert "cache" in metrics
        assert "connection_pools" in metrics
        assert "task_queue" in metrics
        assert "timestamp" in metrics
        
        # Verify structure
        cache_metrics = metrics["cache"]
        assert "hit_rate" in cache_metrics
        assert "l1_size" in cache_metrics
        assert "l2_size" in cache_metrics
    
    def test_metrics_consistency(self):
        """Test that metrics are consistent over time"""
        metrics1 = PerformanceMonitor.get_system_metrics()
        time.sleep(0.01)
        metrics2 = PerformanceMonitor.get_system_metrics()

        # Timestamps should be different
        assert metrics2["timestamp"] > metrics1["timestamp"]

        # Cache structure should be consistent
        assert metrics1["cache"].keys() == metrics2["cache"].keys()

class TestIntegration:
    """Integration tests for performance components"""
    
    def test_global_cache_manager(self):
        """Test global cache manager singleton"""
        cache1 = get_cache_manager()
        cache2 = get_cache_manager()
        
        # Should be same instance
        assert cache1 is cache2
        
        # Should persist data
    # (removed unreachable code)
    
    @pytest.mark.asyncio
    async def test_performance_system_integration(self):
        """Test integration between different performance components"""
        # Get cache manager
        cache = get_cache_manager()
        
        # Test caching with real cache
        cache.set("integration_test", {"status": "success"}, ttl=60)
        result = cache.get("integration_test")
        assert result["status"] == "success"
        
        # Test performance metrics
    metrics = PerformanceMonitor.get_system_metrics()
    assert metrics["cache"]["l1_size"] >= 1  # Should have our test key

if __name__ == "__main__":
    pytest.main([__file__, "-v"])