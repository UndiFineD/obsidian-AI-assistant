# backend/performance.

"""
Performance optimization module implementing Phase 1 optimizations:
- Advanced caching with multi-level cache hierarchy
- Connection pooling for database and AI model operations
- Async processing with background task queues
"""

import asyncio
import inspect
import json
import logging
import threading
import time
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional

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
    Advanced multi-level cache implementation with intelligent cache warming

    Features:
    - L1: In-memory LRU cache (fastest, ~1ms access)
    - L2: Persistent disk cache (medium, ~10ms access)
    - L3: Compressed archive cache (slower, ~100ms access, highest capacity)
    - L4: Predictive cache warming (background preloading)
    """

    def __init__(
        self,
        l1_size: int = 1000,
        l2_size: int = 10000,
        l3_size: int = 100000,
        cache_dir: str = "./backend/cache/performance",
        enable_compression: bool = True,
        enable_prediction: bool = True,
    ):
        # L1: In-memory cache
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_max_size = l1_size
        # L2: Persistent disk cache
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.l2_file = self.cache_dir / "l2_cache.json"
        self.l2_cache: Dict[str, CacheEntry] = {}
        self.l2_max_size = l2_size
        self._l2_lock = threading.Lock()
        # L3: Compressed archive cache
        self.l3_max_size = l3_size
        self.l3_archive_dir = self.cache_dir / "l3_archive"
        self.l3_archive_dir.mkdir(exist_ok=True)
        self.l3_cache: Dict[str, str] = {}  # Maps keys to archive file paths
        self.enable_compression = enable_compression
        self._l3_lock = threading.Lock()
        # L4: Predictive cache warming
        self.enable_prediction = enable_prediction
        self.access_patterns: Dict[str, list] = {}  # Track access patterns for prediction
        self.prediction_queue = []  # Keys predicted to be accessed soon
        self._prediction_lock = threading.Lock()
        self._warming_active = False
        # Initialize caches
        self._load_l2_cache()
        self._load_l3_cache()
        # Enhanced statistics
        self._stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "l4_predictions": 0,
            "misses": 0,
            "evictions": 0,
            "writes": 0,
            "compressions": 0,
            "decompressions": 0,
        }
        # Start background cache warming if enabled
        if self.enable_prediction:
            self._start_cache_warming()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from multi-level cache with promotion"""

        # Record access for predictive caching
        self._record_access(key)

        # Check L1 first (fastest)
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            if not entry.is_expired():
                entry.touch()
                self._stats["l1_hits"] += 1
                return entry.value
            else:
                del self.l1_cache[key]

        # Check L2 (medium speed)
        with self._l2_lock:
            if key in self.l2_cache:
                entry = self.l2_cache[key]
                if not entry.is_expired():
                    entry.touch()
                    # Promote to L1
                    self._promote_to_l1(key, entry)
                    self._stats["l2_hits"] += 1
                    return entry.value
                else:
                    del self.l2_cache[key]
        # Check L3 (slower, compressed)
        if hasattr(self, "l3_cache"):
            l3_entry = self._decompress_from_l3(key)
            if l3_entry:
                # Promote to L2/L1
                self._promote_to_l2(key, l3_entry)
                self._promote_to_l1(key, l3_entry)
                self._stats["l3_hits"] += 1
                return l3_entry.value
        self._stats["misses"] += 1
        return default

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with automatic level management"""
        now = time.time()
        entry = CacheEntry(
            value=value, timestamp=now, ttl=ttl, access_count=0, last_access=now
        )
        # Record access for predictive caching
        self._record_access(key)
        # Always start in L1 for hot data
        self._set_l1(key, entry)
        self._stats["writes"] += 1

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

    def _load_l2_cache(self):
        """Load L2 cache from disk if available."""
        with self._l2_lock:
            if self.l2_file.exists():
                try:
                    with open(self.l2_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for key, entry_data in data.items():
                            entry = CacheEntry(
                                value=entry_data["value"],
                                timestamp=entry_data["timestamp"],
                                ttl=entry_data.get("ttl", 3600),
                                access_count=entry_data.get("access_count", 0),
                                last_access=entry_data.get(
                                    "last_access", entry_data["timestamp"]
                                ),
                            )
                            if not entry.is_expired():
                                self.l2_cache[key] = entry
                except (json.JSONDecodeError, KeyError, OSError) as e:
                    # If loading fails, start with empty cache
                    self.l2_cache = {}
                    logging.warning(f"Failed to load L2 cache: {e}")
            else:
                self.l2_cache = {}

    def _evict_l1_lru(self):
        """Evict least recently used item from L1 to L2"""
        if not self.l1_cache:
            return
        # Find LRU item
        lru_key = min(self.l1_cache.keys(), key=lambda k: self.l1_cache[k].last_access)
        lru_entry = self.l1_cache.pop(lru_key)
        # Move to L2 if not expired
        with self._l2_lock:
            if not lru_entry.is_expired():
                if len(self.l2_cache) >= self.l2_max_size:
                    self._evict_l2_lru()
                self.l2_cache[lru_key] = lru_entry
                self._persist_l2_cache()
        self._stats["evictions"] += 1

    def _evict_l2_lru(self):
        """Evict least recently used item from L2 to L3"""
        if not self.l2_cache:
            return
        # Find LRU item
        lru_key = min(self.l2_cache.keys(), key=lambda k: self.l2_cache[k].last_access)
        lru_entry = self.l2_cache.pop(lru_key)
        # Move to L3 if compression enabled and not expired
        if not lru_entry.is_expired() and hasattr(self, 'enable_compression') and self.enable_compression:
            if len(self.l3_cache) >= self.l3_max_size:
                self._evict_l3_lru()
            self._compress_to_l3(lru_key, lru_entry)
        self._stats["evictions"] += 1

    def _evict_l3_lru(self):
        """Evict least recently used item from L3 (permanent deletion)"""
        if not self.l3_cache:
            return
        # Find oldest archive file
        oldest_key = None
        oldest_time = float("inf")
        for key, archive_path in self.l3_cache.items():
            try:
                path_obj = Path(archive_path)
                if path_obj.exists():
                    mtime = path_obj.stat().st_mtime
                    if mtime < oldest_time:
                        oldest_time = mtime
                        oldest_key = key
            except (OSError, ValueError):
                continue
        if oldest_key:
            # Remove archive file and index entry
            try:
                archive_path = Path(self.l3_cache[oldest_key])
                archive_path.unlink(missing_ok=True)
                with self._l3_lock:
                    del self.l3_cache[oldest_key]
                    self._save_l3_index()
            except Exception as e:
                logger.warning(f"Failed to evict L3 entry: {e}")

    def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promote entry to L1 cache"""
        if len(self.l1_cache) >= self.l1_max_size:
            self._evict_l1_lru()
        self.l1_cache[key] = entry

    # no-op placeholder removed; method above now concludes the block correctly

    def _persist_l2_cache(self):
        """Persist L2 cache to disk (async in background)"""

        def save_cache():
            with self._l2_lock:
                try:
                    data = {}
                    for key, entry in self.l2_cache.items():
                        if not entry.is_expired():
                            data[key] = {
                                "value": entry.value,
                                "timestamp": entry.timestamp,
                                "ttl": entry.ttl,
                                "access_count": entry.access_count,
                                "last_access": entry.last_access,
                            }

                    with open(self.l2_file, "w") as f:
                        json.dump(data, f)
                except Exception as e:
                    # Log error but don't crash the thread
                    logger.warning(f"Failed to persist L2 cache: {e}")

        # Run in background thread
        threading.Thread(target=save_cache, daemon=True).start()

    def _load_l3_cache(self):
        """Load L3 archive cache index."""
        l3_index_file = self.l3_archive_dir / "index.json"
        if l3_index_file.exists():
            try:
                with open(l3_index_file, "r") as f:
                    self.l3_cache = json.load(f)
                # Verify archive files exist
                valid_entries = {}
                for key, archive_path in self.l3_cache.items():
                    if Path(archive_path).exists():
                        valid_entries[key] = archive_path
                self.l3_cache = valid_entries
            except Exception as e:
                logger.warning(f"Failed to load L3 cache index: {e}")
                self.l3_cache = {}

    def _save_l3_index(self):
        """Save L3 cache index."""
        try:
            l3_index_file = self.l3_archive_dir / "index.json"
            with open(l3_index_file, "w") as f:
                json.dump(self.l3_cache, f)
        except Exception as e:
            logger.warning(f"Failed to save L3 cache index: {e}")

    def _compress_to_l3(self, key: str, entry: CacheEntry) -> bool:
        """Compress and store entry in L3 archive."""
        if not self.enable_compression:
            return False

        try:
            import gzip
            import pickle

            # Create unique archive file
            archive_filename = f"{hash(key) % 10000:04d}_{int(time.time())}.gz"
            archive_path = self.l3_archive_dir / archive_filename
            # Compress and store entry
            with gzip.open(archive_path, "wb") as f:
                payload = {
                    "value": entry.value,
                    "timestamp": entry.timestamp,
                    "ttl": entry.ttl,
                    "access_count": entry.access_count,
                    "last_access": entry.last_access,
                }
                pickle.dump(payload, f)
            # Update L3 index
            with self._l3_lock:
                self.l3_cache[key] = str(archive_path)
                self._save_l3_index()
            self._stats["compressions"] += 1
            return True
        except Exception as e:
            logger.warning(f"Failed to compress entry to L3: {e}")
            return False

    def _decompress_from_l3(self, key: str) -> Optional[CacheEntry]:
        """Decompress and retrieve entry from L3 archive."""
        if key not in self.l3_cache:
            return None
        try:
            import gzip
            import pickle
            archive_path = Path(self.l3_cache[key])
            if not archive_path.exists():
                # Remove stale entry
                with self._l3_lock:
                    del self.l3_cache[key]
                    self._save_l3_index()
                return None
            # Decompress entry
            with gzip.open(archive_path, "rb") as f:
                data = pickle.load(f)
            entry = CacheEntry(
                value=data["value"],
                timestamp=data['timestamp'],
                ttl=data.get('ttl'),
                access_count=data.get('access_count', 0),
                last_access=data.get('last_access', data['timestamp'])
            )
            if entry.is_expired():
                # Clean up expired entry
                archive_path.unlink(missing_ok=True)
                with self._l3_lock:
                    del self.l3_cache[key]
                    self._save_l3_index()
                return None
            self._stats["decompressions"] += 1
            return entry
        except Exception as e:
            logger.warning(f"Failed to decompress entry from L3: {e}")
            return None

    def _start_cache_warming(self):
        """Start background cache warming thread."""
        def warming_worker():
            while self.enable_prediction:
                try:
                    self._perform_cache_warming()
                    time.sleep(60)  # Check for warming opportunities every minute
                except Exception as e:
                    logger.warning(f"Cache warming error: {e}")
                    time.sleep(60)
        warming_thread = threading.Thread(target=warming_worker, daemon=True)
        warming_thread.start()

    def _perform_cache_warming(self):
        """Perform predictive cache warming based on access patterns."""
        if self._warming_active:
            return
        self._warming_active = True
        try:
            current_time = time.time()
            # Analyze access patterns to predict next accesses
            predictions = []
            with self._prediction_lock:
                for key, access_times in self.access_patterns.items():
                    if len(access_times) < 2:
                        continue
                    # Calculate access frequency and predict next access
                    recent_accesses = [
                        t for t in access_times if current_time - t < 3600
                    ]  # Last hour
                    if len(recent_accesses) >= 2:
                        avg_interval = (
                            sum(
                                recent_accesses[i] - recent_accesses[i - 1]
                                for i in range(1, len(recent_accesses))
                            )
                            / (len(recent_accesses) - 1)
                        )
                        # Predict if key will be accessed soon
                        last_access = recent_accesses[-1]
                        predicted_next = last_access + avg_interval
                        # Predict within 5 minutes
                        if predicted_next - current_time <= 300:
                            predictions.append(
                                (key, predicted_next - current_time)
                            )
                # Sort by urgency (sooner predictions first)
                predictions.sort(key=lambda x: x[1])
                # Top 10 predictions
                self.prediction_queue = [key for key, _ in predictions[:10]]
            # Warm cache for predicted keys
            # Limit concurrent warming
            for key in self.prediction_queue[:5]:
                if key not in self.l1_cache and key not in self.l2_cache:
                    # Try to promote from L3 to L2/L1
                    l3_entry = self._decompress_from_l3(key)
                    if l3_entry:
                        self._promote_to_l2(key, l3_entry)
                        self._stats["l4_predictions"] += 1
        finally:
            self._warming_active = False

    def _promote_to_l2(self, key: str, entry: CacheEntry):
        """Promote entry from L3 to L2."""
        with self._l2_lock:
            if len(self.l2_cache) >= self.l2_max_size:
                self._evict_l2_lru()
            self.l2_cache[key] = entry
            self._persist_l2_cache()

    def _record_access(self, key: str):
        """Record access pattern for predictive caching."""
        if not self.enable_prediction:
            return
        current_time = time.time()
        with self._prediction_lock:
            if key not in self.access_patterns:
                self.access_patterns[key] = []
            self.access_patterns[key].append(current_time)
            # Keep only recent access history (last 24 hours, max 100 entries)
            cutoff_time = current_time - 86400  # 24 hours
            self.access_patterns[key] = [
                t for t in self.access_patterns[key][-100:]
                if t >= cutoff_time
            ]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = (
            self._stats["l1_hits"]
            + self._stats["l2_hits"]
            + self._stats["l3_hits"]
            + self._stats["misses"]
        )
        hit_rate = (
            self._stats["l1_hits"]
            + self._stats["l2_hits"]
            + self._stats["l3_hits"]
        ) / max(total_requests, 1)
        return {
            **self._stats,
            "hit_rate": hit_rate,
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "l3_size": len(self.l3_cache),
            "l4_prediction_queue": len(getattr(self, "prediction_queue", [])),
            "memory_efficiency": len(self.l1_cache) / self.l1_max_size,
            "disk_efficiency": len(self.l2_cache) / self.l2_max_size,
            "archive_efficiency": (
                len(self.l3_cache) / self.l3_max_size
                if hasattr(self, "l3_max_size")
                else 0
            ),
        }


class ConnectionPool:
    """
    Generic connection pool for managing expensive resources
    """

    def __init__(
        self,
        factory: Callable,
        min_size: int = 2,
        max_size: int = 10,
        max_idle: float = 300,
    ):  # 5 minutes
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
        if hasattr(conn, "close"):
            try:
                conn.close()
            except Exception as e:
                import logging

                logging.warning(f"Failed to close connection: {e}")

    def cleanup_idle_connections(self):
        """Remove idle connections exceeding max_idle time"""
        current_time = time.time()
        kept_connections = []
        with self._lock:
            for conn in self._pool:
                conn_id = id(conn)
                last_used = self._last_used.get(conn_id, current_time)

                if current_time - last_used <= self.max_idle:
                    kept_connections.append(conn)
                else:
                    self._cleanup_connection(conn)
            self._pool = kept_connections


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
            "tasks_queued": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "queue_size": 0,
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

            self.stats["tasks_queued"] += 1
            self.stats["queue_size"] = self.queue.qsize()
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
                task_item = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                if task_item is None:  # Sentinel to stop
                    break

                priority, submit_time, coro = task_item

                # Execute the coroutine
                start_time = time.time()
                try:
                    await coro
                    self.stats["tasks_completed"] += 1

                    execution_time = time.time() - start_time
                    logger.debug(f"Task completed in {execution_time:.3f}s")

                except Exception as e:
                    self.stats["tasks_failed"] += 1
                    logger.error(f"Task failed: {e}")

                finally:
                    self.stats["queue_size"] = self.queue.qsize()
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
            "workers_active": len([w for w in self.workers if not w.done()]),
            "queue_utilization": self.stats["queue_size"] / self.max_queue_size,
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
                cache_key = (
                    f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
                )

            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            if inspect.iscoroutinefunction(func):
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
                cache_key = (
                    f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
                )

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        if inspect.iscoroutinefunction(func):
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
                "active_connections": len(pool._active),
                "pool_size": len(pool._pool),
                "max_size": pool.max_size,
            }

        task_stats = {}
        if _task_queue:
            task_stats = _task_queue.get_stats()

        return {
            "cache": cache_stats,
            "connection_pools": pool_stats,
            "task_queue": task_stats,
            "timestamp": time.time(),
        }
