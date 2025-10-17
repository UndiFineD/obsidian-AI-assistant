"""
Enhanced Caching Infrastructure for Obsidian AI Assistant

This module provides a comprehensive, multi-level caching system that integrates
with the existing caching.py and performance.py modules to provide:

- Unified cache interface
- Intelligent cache routing based on data type and access patterns
- Cache invalidation strategies  
- Performance monitoring and optimization
- Cache warming and preloading
- Distributed cache support (future)
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union

try:
    from backend.error_handling import error_context, ConfigurationError, SystemError
    from backend.performance import get_cache_manager, MultiLevelCache
    from backend.caching import CacheManager, EmbeddingCache, FileHashCache
    from backend.utils import safe_call
except ImportError:
    # Minimal fallback implementations for testing
    def error_context(name, reraise=True):
        class MockContext:
            def __enter__(self): return self
            def __exit__(self, *args): pass
        return MockContext()
    
    class ConfigurationError(Exception): pass
    class SystemError(Exception): pass
    
    def safe_call(func, *args, **kwargs):
        try:
            return func(*args)
        except Exception:
            return kwargs.get('default')
    
    # Mock cache classes for testing
    class MultiLevelCache:
        def __init__(self, *args, **kwargs):
            self.cache = {}
            self.l1_cache = {}
            self.l2_cache = {}
            self._l2_lock = object()
            self.l1_max_size = 1000
            self.l2_max_size = 10000
        def get(self, key, default=None): return self.cache.get(key, default)
        def set(self, key, value, ttl=3600): self.cache[key] = value; return True
        def get_stats(self): return {'hits': 0, 'misses': 0}
    
    def get_cache_manager(): return MultiLevelCache()
    
    class CacheManager:
        def __init__(self, *args): pass
        def get_cached_answer(self, q): return None
        def store_answer(self, q, a): pass
    
    class EmbeddingCache:
        def __init__(self, *args): 
            self.data = {}
            self.cache_file = None
        def _hash_key(self, text): return str(hash(text))
    
    class FileHashCache:
        def __init__(self, *args): pass
        def is_changed(self, path): return False

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Cache type enumeration for routing decisions"""
    EPHEMERAL = "ephemeral"        # Very short-lived data (< 1 minute)
    TRANSIENT = "transient"        # Short-lived data (1-15 minutes)  
    SESSION = "session"            # Session-scoped data (15 minutes - 1 hour)
    PERSISTENT = "persistent"      # Long-lived data (1 hour - 1 day)
    PERMANENT = "permanent"        # Very long-lived data (> 1 day)


class CacheStrategy(Enum):
    """Cache strategy for different data types"""
    LRU = "lru"                    # Least Recently Used
    LFU = "lfu"                    # Least Frequently Used  
    FIFO = "fifo"                  # First In, First Out
    TTL = "ttl"                    # Time To Live based
    ADAPTIVE = "adaptive"          # Adaptive based on access patterns


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    writes: int = 0
    evictions: int = 0
    errors: int = 0
    total_size: int = 0
    avg_access_time: float = 0.0
    hit_rate: float = 0.0
    memory_usage: int = 0


class CacheProvider(Protocol):
    """Protocol for cache providers"""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        ...
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        ...
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        ...
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        ...


class SmartCacheRouter:
    """
    Intelligent cache router that determines the best cache strategy
    and provider based on data characteristics and access patterns
    """
    
    def __init__(self):
        self.access_patterns: Dict[str, List[float]] = {}
        self.size_patterns: Dict[str, List[int]] = {}
        self.type_patterns: Dict[str, CacheType] = {}
        
    def analyze_key(self, key: str, value: Any = None) -> Dict[str, Any]:
        """Analyze cache key to determine optimal caching strategy"""
        with error_context("cache_key_analysis", reraise=False):
            # Determine data type and size
            value_size = len(str(value)) if value else 0
            
            # Pattern analysis
            key_patterns = {
                # AI model responses - high compute cost, medium frequency
                'ask:': {'type': CacheType.PERSISTENT, 'strategy': CacheStrategy.LRU, 'ttl': 3600},
                'generate:': {'type': CacheType.PERSISTENT, 'strategy': CacheStrategy.LRU, 'ttl': 3600},
                
                # Embeddings - very high compute cost, high reuse potential
                'embed:': {'type': CacheType.PERMANENT, 'strategy': CacheStrategy.LFU, 'ttl': 86400},
                'embedding:': {'type': CacheType.PERMANENT, 'strategy': CacheStrategy.LFU, 'ttl': 86400},
                
                # File operations - moderate cost, change-dependent
                'file:': {'type': CacheType.SESSION, 'strategy': CacheStrategy.TTL, 'ttl': 900},
                'hash:': {'type': CacheType.PERSISTENT, 'strategy': CacheStrategy.TTL, 'ttl': 7200},
                
                # API responses - low cost, high frequency
                'api:': {'type': CacheType.TRANSIENT, 'strategy': CacheStrategy.LRU, 'ttl': 300},
                'health:': {'type': CacheType.EPHEMERAL, 'strategy': CacheStrategy.TTL, 'ttl': 60},
                
                # Configuration - low frequency, high importance
                'config:': {'type': CacheType.PERMANENT, 'strategy': CacheStrategy.TTL, 'ttl': 3600},
                'settings:': {'type': CacheType.PERMANENT, 'strategy': CacheStrategy.TTL, 'ttl': 3600},
                
                # Search results - moderate cost, session-scoped
                'search:': {'type': CacheType.SESSION, 'strategy': CacheStrategy.LRU, 'ttl': 1800},
                'query:': {'type': CacheType.SESSION, 'strategy': CacheStrategy.LRU, 'ttl': 1800},
            }
            
            # Find matching pattern
            for pattern, config in key_patterns.items():
                if pattern in key.lower():
                    return {
                        'cache_type': config['type'],
                        'strategy': config['strategy'],
                        'ttl': config['ttl'],
                        'size_category': self._categorize_size(value_size),
                        'estimated_cost': self._estimate_compute_cost(key),
                    }
            
            # Default pattern for unknown keys
            return {
                'cache_type': CacheType.TRANSIENT,
                'strategy': CacheStrategy.ADAPTIVE,
                'ttl': 900,  # 15 minutes
                'size_category': self._categorize_size(value_size),
                'estimated_cost': 'medium',
            }
    
    def _categorize_size(self, size: int) -> str:
        """Categorize data size for cache routing"""
        if size < 1024:          # < 1KB
            return 'tiny'
        elif size < 10240:       # < 10KB
            return 'small'
        elif size < 102400:      # < 100KB
            return 'medium'
        elif size < 1048576:     # < 1MB
            return 'large'
        else:                    # >= 1MB
            return 'huge'
    
    def _estimate_compute_cost(self, key: str) -> str:
        """Estimate computational cost of regenerating cached data"""
        expensive_patterns = ['embed', 'generate', 'ask', 'model', 'ai']
        moderate_patterns = ['search', 'query', 'index', 'process']
        
        key_lower = key.lower()
        
        if any(pattern in key_lower for pattern in expensive_patterns):
            return 'high'
        elif any(pattern in key_lower for pattern in moderate_patterns):
            return 'medium'
        else:
            return 'low'
    
    def record_access(self, key: str, access_time: float):
        """Record access pattern for adaptive optimization"""
        current_time = time.time()
        
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        
        self.access_patterns[key].append(current_time)
        
        # Keep only recent history (last 100 accesses or 24 hours)
        cutoff_time = current_time - 86400  # 24 hours
        self.access_patterns[key] = [
            t for t in self.access_patterns[key][-100:] 
            if t >= cutoff_time
        ]


class UnifiedCacheManager:
    """
    Unified cache manager that orchestrates multiple cache providers
    and provides intelligent routing, invalidation, and optimization
    """
    
    def __init__(self, cache_dir: str = "./backend/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache providers
        self.multi_level_cache = get_cache_manager()
        self.legacy_cache = None
        self.embedding_cache = None
        self.file_cache = None
        
        # Initialize router and metrics
        self.router = SmartCacheRouter()
        self.metrics = CacheMetrics()
        self.enabled = True
        
        # Cache invalidation tracking
        self.invalidation_rules: Dict[str, List[str]] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # Initialize subsystem caches
        self._init_subsystem_caches()
    
    def _init_subsystem_caches(self):
        """Initialize specialized cache subsystems"""
        with error_context("cache_subsystem_init", reraise=False):
            try:
                self.legacy_cache = CacheManager(str(self.cache_dir))
                self.embedding_cache = EmbeddingCache(str(self.cache_dir))
                self.file_cache = FileHashCache(str(self.cache_dir))
                logger.info("Cache subsystems initialized successfully")
            except Exception as e:
                logger.warning(f"Some cache subsystems failed to initialize: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Intelligent cache get with automatic provider selection
        """
        if not self.enabled:
            return default
            
        start_time = time.time()
        
        with error_context("unified_cache_get", reraise=False):
            try:
                # Analyze key to determine best provider
                analysis = self.router.analyze_key(key)
                
                # Route to appropriate cache provider
                result = self._route_get(key, analysis, default)
                
                # Record metrics
                access_time = time.time() - start_time
                self.router.record_access(key, access_time)
                
                if result is not default:
                    self.metrics.hits += 1
                else:
                    self.metrics.misses += 1
                
                self.metrics.avg_access_time = (
                    (self.metrics.avg_access_time * (self.metrics.hits + self.metrics.misses - 1) + access_time) /
                    (self.metrics.hits + self.metrics.misses)
                )
                
                return result
                
            except Exception as e:
                self.metrics.errors += 1
                logger.warning(f"Cache get error for key {key}: {e}")
                return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Intelligent cache set with automatic provider selection and optimization
        """
        if not self.enabled:
            return False
            
        with error_context("unified_cache_set", reraise=False):
            try:
                # Analyze key and value for optimal caching
                analysis = self.router.analyze_key(key, value)
                
                # Use analysis TTL if not specified
                if ttl is None:
                    ttl = analysis['ttl']
                
                # Route to appropriate cache provider
                success = self._route_set(key, value, analysis, ttl)
                
                if success:
                    self.metrics.writes += 1
                    self._update_dependencies(key, value)
                
                return success
                
            except Exception as e:
                self.metrics.errors += 1
                logger.warning(f"Cache set error for key {key}: {e}")
                return False
    
    def _route_get(self, key: str, analysis: Dict[str, Any], default: Any) -> Any:
        """Route get request to appropriate cache provider"""
        cache_type = analysis['cache_type']
        size_category = analysis['size_category']
        
        # Route based on data characteristics
        if 'embed' in key.lower() and self.embedding_cache:
            # Special handling for embeddings
            return self._get_from_embedding_cache(key, default)
        
        elif 'file' in key.lower() or 'hash' in key.lower():
            # File-related caching
            return self._get_from_file_cache(key, default)
        
        elif size_category in ['huge', 'large'] or cache_type in [CacheType.PERMANENT, CacheType.PERSISTENT]:
            # Large data or long-term storage - use multi-level cache
            return self.multi_level_cache.get(key, default)
        
        elif self.legacy_cache and cache_type in [CacheType.TRANSIENT, CacheType.SESSION]:
            # Medium-term data - use legacy cache
            return self.legacy_cache.get_cached_answer(key) or default
        
        else:
            # Default to multi-level cache
            return self.multi_level_cache.get(key, default)
    
    def _route_set(self, key: str, value: Any, analysis: Dict[str, Any], ttl: int) -> bool:
        """Route set request to appropriate cache provider"""
        cache_type = analysis['cache_type']
        size_category = analysis['size_category']
        
        success = False
        
        # Route based on data characteristics
        if 'embed' in key.lower() and self.embedding_cache:
            # Special handling for embeddings
            success = self._set_in_embedding_cache(key, value)
        
        elif 'file' in key.lower() or 'hash' in key.lower():
            # File-related caching
            success = self._set_in_file_cache(key, value)
        
        # Always try to store in multi-level cache for redundancy
        multi_success = self.multi_level_cache.set(key, value, ttl)
        
        # Also store in legacy cache for backward compatibility
        if self.legacy_cache and isinstance(value, str) and 'ask' in key.lower():
            # Extract question from key for legacy cache
            question = key.split(':', 1)[-1] if ':' in key else key
            self.legacy_cache.store_answer(question, value)
        
        return success or multi_success
    
    def _get_from_embedding_cache(self, key: str, default: Any) -> Any:
        """Get from embedding cache with fallback"""
        try:
            # Embedding cache expects text and compute function
            # For get operations, we can't recompute, so check if cached
            text = key.split(':', 1)[-1] if ':' in key else key
            # This is a simplified approach - in practice, we'd need the embedding data
            return default  # Fallback for now
        except Exception:
            return default
    
    def _set_in_embedding_cache(self, key: str, value: Any) -> bool:
        """Set in embedding cache"""
        try:
            if self.embedding_cache and isinstance(value, list):
                text = key.split(':', 1)[-1] if ':' in key else key
                # Store directly in the cache data
                cache_key = self.embedding_cache._hash_key(text)
                self.embedding_cache.data[cache_key] = value
                # Persist to disk
                def do_store():
                    with open(self.embedding_cache.cache_file, "w", encoding="utf-8") as f:
                        json.dump(self.embedding_cache.data, f)
                safe_call(do_store, error_msg="[EnhancedCache] Error writing embedding cache")
                return True
        except Exception as e:
            logger.warning(f"Error setting embedding cache: {e}")
        return False
    
    def _get_from_file_cache(self, key: str, default: Any) -> Any:
        """Get from file cache"""
        # File cache is primarily for change detection, not value storage
        return default
    
    def _set_in_file_cache(self, key: str, value: Any) -> bool:
        """Set in file cache"""
        try:
            if self.file_cache and 'path' in key.lower():
                # Extract path from key
                path_str = key.split(':', 1)[-1] if ':' in key else key
                file_path = Path(path_str)
                if file_path.exists():
                    # Update file hash cache
                    self.file_cache.is_changed(file_path)
                    return True
        except Exception as e:
            logger.warning(f"Error setting file cache: {e}")
        return False
    
    def _update_dependencies(self, key: str, value: Any):
        """Update cache dependency graph for invalidation"""
        # Simple dependency tracking based on key patterns
        if ':' in key:
            namespace = key.split(':', 1)[0]
            if namespace not in self.dependency_graph:
                self.dependency_graph[namespace] = []
            if key not in self.dependency_graph[namespace]:
                self.dependency_graph[namespace].append(key)
    
    def delete(self, key: str) -> bool:
        """Delete key from all cache providers"""
        success = False
        
        with error_context("unified_cache_delete", reraise=False):
            try:
                # Delete from multi-level cache
                if hasattr(self.multi_level_cache, 'delete'):
                    success |= self.multi_level_cache.delete(key)
                else:
                    # Manual deletion from cache levels
                    if key in self.multi_level_cache.l1_cache:
                        del self.multi_level_cache.l1_cache[key]
                        success = True
                    
                    with self.multi_level_cache._l2_lock:
                        if key in self.multi_level_cache.l2_cache:
                            del self.multi_level_cache.l2_cache[key]
                            success = True
                
                # Delete from legacy cache (limited capability)
                # Legacy cache doesn't have direct delete, so we skip
                
                # Clean up dependencies
                self._clean_dependencies(key)
                
                return success
                
            except Exception as e:
                logger.warning(f"Cache delete error for key {key}: {e}")
                return False
    
    def _clean_dependencies(self, key: str):
        """Clean up dependency graph when key is deleted"""
        for namespace, keys in self.dependency_graph.items():
            if key in keys:
                keys.remove(key)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern"""
        invalidated = 0
        
        with error_context("cache_pattern_invalidation", reraise=False):
            try:
                # Invalidate from multi-level cache
                keys_to_delete = []
                
                # Check L1 cache
                for key in list(self.multi_level_cache.l1_cache.keys()):
                    if pattern in key:
                        keys_to_delete.append(key)
                
                # Check L2 cache
                with self.multi_level_cache._l2_lock:
                    for key in list(self.multi_level_cache.l2_cache.keys()):
                        if pattern in key and key not in keys_to_delete:
                            keys_to_delete.append(key)
                
                # Delete all matching keys
                for key in keys_to_delete:
                    if self.delete(key):
                        invalidated += 1
                
                return invalidated
                
            except Exception as e:
                logger.warning(f"Pattern invalidation error for pattern {pattern}: {e}")
                return invalidated
    
    def clear(self) -> bool:
        """Clear all caches"""
        with error_context("unified_cache_clear", reraise=False):
            try:
                success = True
                
                # Clear multi-level cache
                self.multi_level_cache.l1_cache.clear()
                with self.multi_level_cache._l2_lock:
                    self.multi_level_cache.l2_cache.clear()
                    self.multi_level_cache._persist_l2_cache()
                
                # Clear dependency graph
                self.dependency_graph.clear()
                
                # Reset metrics
                self.metrics = CacheMetrics()
                
                logger.info("All caches cleared successfully")
                return success
                
            except Exception as e:
                logger.error(f"Cache clear error: {e}")
                return False
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            # Get multi-level cache stats
            ml_stats = self.multi_level_cache.get_stats()
            
            # Calculate overall hit rate
            total_requests = self.metrics.hits + self.metrics.misses
            hit_rate = self.metrics.hits / max(total_requests, 1)
            
            return {
                'unified_cache': {
                    'hits': self.metrics.hits,
                    'misses': self.metrics.misses,
                    'writes': self.metrics.writes,
                    'errors': self.metrics.errors,
                    'hit_rate': hit_rate,
                    'avg_access_time': self.metrics.avg_access_time,
                    'enabled': self.enabled,
                },
                'multi_level_cache': ml_stats,
                'dependency_graph': {
                    'namespaces': len(self.dependency_graph),
                    'total_dependencies': sum(len(deps) for deps in self.dependency_graph.values()),
                },
                'subsystems': {
                    'legacy_cache_available': self.legacy_cache is not None,
                    'embedding_cache_available': self.embedding_cache is not None,
                    'file_cache_available': self.file_cache is not None,
                },
                'cache_routing': {
                    'patterns_tracked': len(self.router.access_patterns),
                    'size_patterns_tracked': len(self.router.size_patterns),
                    'type_patterns_tracked': len(self.router.type_patterns),
                }
            }
            
        except Exception as e:
            logger.warning(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    def optimize(self) -> Dict[str, Any]:
        """Perform cache optimization tasks"""
        with error_context("cache_optimization", reraise=False):
            optimization_results = {
                'l1_evictions': 0,
                'l2_evictions': 0,
                'expired_removals': 0,
                'dependency_cleanup': 0,
                'optimization_time': 0,
            }
            
            start_time = time.time()
            
            try:
                # Clean expired entries from L1
                expired_l1_keys = []
                for key, entry in self.multi_level_cache.l1_cache.items():
                    if entry.is_expired():
                        expired_l1_keys.append(key)
                
                for key in expired_l1_keys:
                    del self.multi_level_cache.l1_cache[key]
                    optimization_results['expired_removals'] += 1
                
                # Clean expired entries from L2
                with self.multi_level_cache._l2_lock:
                    expired_l2_keys = []
                    for key, entry in self.multi_level_cache.l2_cache.items():
                        if entry.is_expired():
                            expired_l2_keys.append(key)
                    
                    for key in expired_l2_keys:
                        del self.multi_level_cache.l2_cache[key]
                        optimization_results['expired_removals'] += 1
                    
                    # Persist L2 changes
                    self.multi_level_cache._persist_l2_cache()
                
                # Clean up empty dependency graph entries
                empty_namespaces = []
                for namespace, deps in self.dependency_graph.items():
                    if not deps:
                        empty_namespaces.append(namespace)
                
                for namespace in empty_namespaces:
                    del self.dependency_graph[namespace]
                    optimization_results['dependency_cleanup'] += 1
                
                optimization_results['optimization_time'] = time.time() - start_time
                
                logger.info(f"Cache optimization completed: {optimization_results}")
                return optimization_results
                
            except Exception as e:
                logger.error(f"Cache optimization error: {e}")
                optimization_results['error'] = str(e)
                return optimization_results
    
    def warm_cache(self, keys: List[str]) -> Dict[str, bool]:
        """Warm cache with predictive loading"""
        results = {}
        
        with error_context("cache_warming", reraise=False):
            for key in keys:
                try:
                    # Check if key exists in any cache level
                    if self.get(key) is not None:
                        results[key] = True  # Already cached
                    else:
                        results[key] = False  # Not found
                except Exception as e:
                    logger.warning(f"Cache warming error for key {key}: {e}")
                    results[key] = False
        
        return results


# Global unified cache manager
_unified_cache_manager = None


def get_unified_cache_manager() -> UnifiedCacheManager:
    """Get global unified cache manager instance"""
    global _unified_cache_manager
    if _unified_cache_manager is None:
        _unified_cache_manager = UnifiedCacheManager()
    return _unified_cache_manager


def cached_with_intelligence(
    ttl: Optional[int] = None,
    cache_type: Optional[CacheType] = None,
    strategy: Optional[CacheStrategy] = None
):
    """
    Intelligent caching decorator that uses unified cache manager
    
    Args:
        ttl: Time to live in seconds (auto-determined if None)
        cache_type: Cache type hint for routing
        strategy: Cache strategy hint for routing
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_unified_cache_manager()
            
            # Generate cache key
            key_base = f"{func.__module__}.{func.__name__}"
            args_hash = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()[:16]
            cache_key = f"{key_base}:{args_hash}"
            
            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Set in cache with intelligent routing
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
