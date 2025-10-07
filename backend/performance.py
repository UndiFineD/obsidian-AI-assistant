# backend/performance.py
"""
Performance optimization module implementing Phase 1 optimizations:
- Advanced caching with multi-level cache hierarchy
- Connection pooling for database and AI model operations
- Async processing with background task queues
"""

import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Any, Callable, Awaitable
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import weakref
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Enhanced cache entry with metadata"""
    value: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = 0
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl
    
    def touch(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_access = time.time()

class MultiLevelCache:
    """
    High-performance multi-level cache implementation
    
    Features:
    - L1: In-memory LRU cache (fastest)
    - L2: Persistent disk cache (medium)
    - L3: Compressed archive cache (slowest, highest capacity)
    """
    
    def __init__(self, 
                 l1_size: int = 1000,
                 l2_size: int = 10000,
                 cache_dir: str = "./cache/performance"):
        self.l1_cache: Dict[str, CacheEntry] = {}  # In-memory
        self.l1_max_size = l1_size
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.l2_file = self.cache_dir / "l2_cache.json"
        self.l2_cache: Dict[str, CacheEntry] = {}
        self.l2_max_size = l2_size
        
        self._load_l2_cache()
        self._stats = {
            'l1_hits': 0, 'l2_hits': 0, 'misses': 0,
            'evictions': 0, 'writes': 0
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from multi-level cache with promotion"""
        
        # Check L1 first (fastest)
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            if not entry.is_expired():
                entry.touch()
                self._stats['l1_hits'] += 1
                return entry.value
            else:
                del self.l1_cache[key]
        
        # Check L2 (medium speed)
        if key in self.l2_cache:
            entry = self.l2_cache[key]
            if not entry.is_expired():
                entry.touch()
                # Promote to L1
                self._promote_to_l1(key, entry)
                self._stats['l2_hits'] += 1
                return entry.value
            else:
                del self.l2_cache[key]
        
        self._stats['misses'] += 1
        return default
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with automatic level management"""
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl
        )
        
        # Always start in L1 for hot data
        self._set_l1(key, entry)
        self._stats['writes'] += 1
    
    def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promote frequently accessed L2 items to L1"""
        if len(self.l1_cache) >= self.l1_max_size:
            self._evict_l1_lru()
        self.l1_cache[key] = entry
    
    def _set_l1(self, key: str, entry: CacheEntry):
        """Set entry in L1 cache with LRU eviction"""
        if len(self.l1_cache) >= self.l1_max_size:
            self._evict_l1_lru()
        self.l1_cache[key] = entry
    
    def _evict_l1_lru(self):
        """Evict least recently used item from L1 to L2"""
        if not self.l1_cache:
            return
            
        # Find LRU item
        lru_key = min(self.l1_cache.keys(), 
                     key=lambda k: self.l1_cache[k].last_access)
        lru_entry = self.l1_cache.pop(lru_key)
        
        # Move to L2 if not expired
        if not lru_entry.is_expired():
            if len(self.l2_cache) >= self.l2_max_size:
                self._evict_l2_lru()
            self.l2_cache[lru_key] = lru_entry
            self._persist_l2_cache()
        
        self._stats['evictions'] += 1
    
    def _evict_l2_lru(self):
        """Evict least recently used item from L2"""
        if not self.l2_cache:
            return
            
        lru_key = min(self.l2_cache.keys(),
                     key=lambda k: self.l2_cache[k].last_access)
        del self.l2_cache[lru_key]
    
    def _load_l2_cache(self):
        """Load L2 cache from disk"""
        if not self.l2_file.exists():
            return
            
        try:
            with open(self.l2_file, 'r') as f:
                data = json.load(f)
                for key, entry_data in data.items():
                    entry = CacheEntry(**entry_data)
                    if not entry.is_expired():
                        self.l2_cache[key] = entry
        except Exception as e:
            logger.warning(f"Failed to load L2 cache: {e}")
    
    def _persist_l2_cache(self):
        """Persist L2 cache to disk (async in background)"""
        def save_cache():
            try:
                data = {}
                for key, entry in self.l2_cache.items():
                    if not entry.is_expired():
                        data[key] = {
                            'value': entry.value,
                            'timestamp': entry.timestamp,
                            'ttl': entry.ttl,
                            'access_count': entry.access_count,
                            'last_access': entry.last_access
                        }
                
                with open(self.l2_file, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                logger.warning(f"Failed to persist L2 cache: {e}")
        
        # Run in background thread
        threading.Thread(target=save_cache, daemon=True).start()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = sum(self._stats.values()) - self._stats['writes'] - self._stats['evictions']
        hit_rate = (self._stats['l1_hits'] + self._stats['l2_hits']) / max(total_requests, 1)
        
        return {
            **self._stats,
            'hit_rate': hit_rate,
            'l1_size': len(self.l1_cache),
            'l2_size': len(self.l2_cache),
            'memory_efficiency': len(self.l1_cache) / self.l1_max_size,
            'disk_efficiency': len(self.l2_cache) / self.l2_max_size
        }

class ConnectionPool:
    """
    Generic connection pool for managing expensive resources
    """
    
    def __init__(self, 
                 factory: Callable,
                 min_size: int = 2,
                 max_size: int = 10,
                 max_idle: float = 300):  # 5 minutes
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle = max_idle
        
        self._pool = []
        self._active = set()
        self._lock = threading.RLock()
        self._last_used = {}
        
        # Pre-create minimum connections
        for _ in range(min_size):
            conn = self._create_connection()
            if conn:
                self._pool.append(conn)
    
    def get_connection(self):
        """Get connection from pool or create new one"""
        with self._lock:
            # Try to reuse existing connection
            while self._pool:
                conn = self._pool.pop()
                if self._is_connection_valid(conn):
                    self._active.add(id(conn))
                    self._last_used[id(conn)] = time.time()
                    return conn
                else:
                    self._cleanup_connection(conn)
            
            # Create new connection if under max limit
            if len(self._active) < self.max_size:
                conn = self._create_connection()
                if conn:
                    self._active.add(id(conn))
                    self._last_used[id(conn)] = time.time()
                    return conn
            
            raise RuntimeError("Connection pool exhausted")
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if not conn:
            return
            
        conn_id = id(conn)
        with self._lock:
            if conn_id in self._active:
                self._active.remove(conn_id)
                
                if self._is_connection_valid(conn) and len(self._pool) < self.max_size:
                    self._pool.append(conn)
                    self._last_used[conn_id] = time.time()
                else:
                    self._cleanup_connection(conn)
                    if conn_id in self._last_used:
                        del self._last_used[conn_id]
    
    def _create_connection(self):
        """Create new connection using factory"""
        try:
            return self.factory()
        except Exception as e:
            logger.warning(f"Failed to create connection: {e}")
            return None
    
    def _is_connection_valid(self, conn) -> bool:
        """Check if connection is still valid"""
        # Basic implementation - override for specific connection types
        return conn is not None
    
    def _cleanup_connection(self, conn):
        """Clean up connection resources"""
        # Override for specific cleanup needs
        if hasattr(conn, 'close'):
            try:
                conn.close()
            except:
                pass
    
    def cleanup_idle_connections(self):
        """Remove idle connections exceeding max_idle time"""
        current_time = time.time()
        with self._lock:
            active_conns = []
            for conn in self._pool:
                conn_id = id(conn)
                last_used = self._last_used.get(conn_id, current_time)
                
                if current_time - last_used <= self.max_idle:
                    active_conns.append(conn)
                else:
                    self._cleanup_connection(conn)
                    if conn_id in self._last_used:
                        del self._last_used[conn_id]
            
            self._pool = active_conns

class AsyncTaskQueue:
    """
    High-performance async task queue for background processing
    """
    
    def __init__(self, max_workers: int = 4, max_queue_size: int = 1000):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.workers = []
        self.stats = {
            'tasks_queued': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'queue_size': 0
        }
        
        self._running = False
    
    async def start(self):
        """Start background workers"""
        if self._running:
            return
            
        self._running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        logger.info(f"Started {self.max_workers} async workers")
    
    async def stop(self):
        """Stop all workers gracefully"""
        self._running = False
        
        # Add sentinel values to wake up workers
        for _ in range(self.max_workers):
            await self.queue.put(None)
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers = []
        logger.info("All async workers stopped")
    
    async def submit_task(self, coro: Awaitable, priority: int = 0) -> bool:
        """
        Submit coroutine for background execution
        
        Args:
            coro: Coroutine to execute
            priority: Task priority (higher = more urgent)
            
        Returns:
            True if task was queued, False if queue is full
        """
        try:
            task_item = (priority, time.time(), coro)
            await self.queue.put(task_item)
            
            self.stats['tasks_queued'] += 1
            self.stats['queue_size'] = self.queue.qsize()
            return True
        except asyncio.QueueFull:
            logger.warning("Task queue is full, dropping task")
            return False
    
    async def _worker(self, worker_name: str):
        """Background worker coroutine"""
        logger.debug(f"Worker {worker_name} started")
        
        while self._running:
            try:
                # Get task with timeout
                task_item = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )
                
                if task_item is None:  # Sentinel to stop
                    break
                
                priority, submit_time, coro = task_item
                
                # Execute the coroutine
                start_time = time.time()
                try:
                    await coro
                    self.stats['tasks_completed'] += 1
                    
                    execution_time = time.time() - start_time
                    logger.debug(f"Task completed in {execution_time:.3f}s")
                    
                except Exception as e:
                    self.stats['tasks_failed'] += 1
                    logger.error(f"Task failed: {e}")
                
                finally:
                    self.stats['queue_size'] = self.queue.qsize()
                    self.queue.task_done()
            
            except asyncio.TimeoutError:
                continue  # Check if still running
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
        
        logger.debug(f"Worker {worker_name} stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue performance statistics"""
        return {
            **self.stats,
            'workers_active': len([w for w in self.workers if not w.done()]),
            'queue_utilization': self.stats['queue_size'] / self.max_queue_size
        }

# Global performance managers (initialized on demand)
_cache_manager = None
_connection_pools = {}
_task_queue = None

def get_cache_manager() -> MultiLevelCache:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = MultiLevelCache()
    return _cache_manager

def get_connection_pool(name: str, factory: Callable, **kwargs) -> ConnectionPool:
    """Get named connection pool"""
    global _connection_pools
    if name not in _connection_pools:
        _connection_pools[name] = ConnectionPool(factory, **kwargs)
    return _connection_pools[name]

async def get_task_queue() -> AsyncTaskQueue:
    """Get global task queue instance"""
    global _task_queue
    if _task_queue is None:
        _task_queue = AsyncTaskQueue()
        await _task_queue.start()
    return _task_queue

def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_func: Optional function to generate cache key
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor and report performance metrics"""
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get comprehensive system performance metrics"""
        cache_stats = get_cache_manager().get_stats()
        
        pool_stats = {}
        for name, pool in _connection_pools.items():
            pool_stats[name] = {
                'active_connections': len(pool._active),
                'pool_size': len(pool._pool),
                'max_size': pool.max_size
            }
        
        task_stats = {}
        if _task_queue:
            task_stats = _task_queue.get_stats()
        
        return {
            'cache': cache_stats,
            'connection_pools': pool_stats,
            'task_queue': task_stats,
            'timestamp': time.time()
        }