"""
Cache Management API Endpoints for Obsidian AI Assistant

This module provides REST API endpoints for managing the enhanced caching system,
including cache statistics, optimization, invalidation, and warming operations.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

try:
    from backend.enhanced_caching import (
        CacheStrategy,
        CacheType,
        get_unified_cache_manager,
    )
    from backend.error_handling import SystemError, ValidationError, error_context
    from backend.security import require_role
except ImportError:
    # Minimal fallback for testing
    def error_context(name, reraise=True):
        class MockContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return MockContext()

    class ValidationError(Exception):
        pass

    class SystemError(Exception):
        pass

    def require_role(role):
        return lambda: None

    # Mock enhanced caching
    class CacheType:
        pass

    class CacheStrategy:
        pass

    def get_unified_cache_manager():
        class MockCache:
            def get_comprehensive_stats(self):
                return {}

            def clear(self):
                return True

            def optimize(self):
                return {}

        return MockCache()


logger = logging.getLogger(__name__)

# Create router for cache management endpoints
cache_router = APIRouter(prefix="/api/cache", tags=["cache"])


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics"""

    status: str
    unified_cache: Dict[str, Any]
    multi_level_cache: Dict[str, Any]
    dependency_graph: Dict[str, Any]
    subsystems: Dict[str, Any]
    cache_routing: Dict[str, Any]
    timestamp: float


class CacheOperationRequest(BaseModel):
    """Request model for cache operations"""

    keys: Optional[List[str]] = None
    pattern: Optional[str] = None
    cache_type: Optional[str] = None
    ttl: Optional[int] = None


class CacheOptimizationResponse(BaseModel):
    """Response model for cache optimization"""

    status: str
    l1_evictions: int
    l2_evictions: int
    expired_removals: int
    dependency_cleanup: int
    optimization_time: float
    message: str


class CacheWarmingResponse(BaseModel):
    """Response model for cache warming"""

    status: str
    results: Dict[str, bool]
    total_keys: int
    successful_warms: int
    message: str


@cache_router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Get comprehensive cache statistics and performance metrics"""
    with error_context("get_cache_statistics", reraise=False):
        try:
            cache_manager = get_unified_cache_manager()
            stats = cache_manager.get_comprehensive_stats()

            import time

            return CacheStatsResponse(status="success", timestamp=time.time(), **stats)

        except Exception as e:
            raise SystemError(
                "Failed to retrieve cache statistics",
                suggestion="Check cache system health and try again",
            ) from e


@cache_router.post("/clear", dependencies=[Depends(require_role("admin"))])
async def clear_all_caches():
    """Clear all cache levels and reset statistics"""
    with error_context("clear_all_caches", reraise=False):
        try:
            cache_manager = get_unified_cache_manager()
            success = cache_manager.clear()

            if success:
                return {
                    "status": "success",
                    "message": "All caches cleared successfully",
                    "timestamp": __import__("time").time(),
                }
            else:
                raise SystemError(
                    "Failed to clear caches",
                    suggestion="Check cache system permissions and try again",
                )

        except SystemError:
            raise
        except Exception as e:
            raise SystemError(
                "Cache clear operation failed",
                suggestion="Check system resources and cache permissions",
            ) from e


@cache_router.post("/optimize", dependencies=[Depends(require_role("admin"))])
async def optimize_caches():
    """Perform cache optimization including cleanup of expired entries"""
    with error_context("optimize_caches", reraise=False):
        try:
            cache_manager = get_unified_cache_manager()
            results = cache_manager.optimize()

            if "error" in results:
                raise SystemError(
                    f"Cache optimization failed: {results['error']}",
                    suggestion="Check cache system health and available resources",
                )

            return CacheOptimizationResponse(
                status="success",
                message="Cache optimization completed successfully",
                **results,
            )

        except SystemError:
            raise
        except Exception as e:
            raise SystemError(
                "Cache optimization operation failed",
                suggestion="Check system resources and cache health",
            ) from e


@cache_router.post("/invalidate", dependencies=[Depends(require_role("admin"))])
async def invalidate_cache_pattern(request: CacheOperationRequest):
    """Invalidate cache entries matching a specific pattern"""
    with error_context("invalidate_cache_pattern", reraise=False):
        try:
            if not request.pattern:
                raise ValidationError(
                    "Pattern is required for cache invalidation",
                    field="pattern",
                    suggestion="Provide a pattern to match cache keys for invalidation",
                )

            cache_manager = get_unified_cache_manager()
            invalidated_count = cache_manager.invalidate_pattern(request.pattern)

            return {
                "status": "success",
                "pattern": request.pattern,
                "invalidated_keys": invalidated_count,
                "message": f"Invalidated {invalidated_count} cache entries matching pattern '{request.pattern}'",
                "timestamp": __import__("time").time(),
            }

        except ValidationError:
            raise
        except Exception as e:
            raise SystemError(
                f"Cache invalidation failed for pattern '{request.pattern}'",
                suggestion="Check pattern syntax and cache system health",
            ) from e


@cache_router.post("/warm", dependencies=[Depends(require_role("user"))])
async def warm_cache(request: CacheOperationRequest):
    """Warm cache by preloading specified keys"""
    with error_context("warm_cache", reraise=False):
        try:
            if not request.keys:
                raise ValidationError(
                    "Keys are required for cache warming",
                    field="keys",
                    suggestion="Provide a list of cache keys to warm",
                )

            cache_manager = get_unified_cache_manager()
            results = cache_manager.warm_cache(request.keys)

            successful_warms = sum(1 for result in results.values() if result)

            return CacheWarmingResponse(
                status="success",
                results=results,
                total_keys=len(request.keys),
                successful_warms=successful_warms,
                message=f"Cache warming completed: {successful_warms}/{len(request.keys)} keys already cached",
            )

        except ValidationError:
            raise
        except Exception as e:
            raise SystemError(
                "Cache warming operation failed",
                suggestion="Check key format and cache system health",
            ) from e


@cache_router.get("/health")
async def get_cache_health():
    """Get cache system health status"""
    with error_context("get_cache_health", reraise=False):
        try:
            cache_manager = get_unified_cache_manager()
            stats = cache_manager.get_comprehensive_stats()

            # Determine health status based on metrics
            health_status = "healthy"
            issues = []

            # Check hit rate
            unified_stats = stats.get("unified_cache", {})
            hit_rate = unified_stats.get("hit_rate", 0)
            if hit_rate < 0.3:  # Less than 30% hit rate
                health_status = "degraded"
                issues.append("Low cache hit rate")

            # Check error rate
            errors = unified_stats.get("errors", 0)
            total_ops = (
                unified_stats.get("hits", 0)
                + unified_stats.get("misses", 0)
                + unified_stats.get("writes", 0)
            )
            if total_ops > 0 and (errors / total_ops) > 0.05:  # More than 5% error rate
                health_status = "unhealthy"
                issues.append("High error rate")

            # Check if caching is enabled
            if not unified_stats.get("enabled", False):
                health_status = "disabled"
                issues.append("Caching system is disabled")

            return {
                "status": health_status,
                "enabled": unified_stats.get("enabled", False),
                "hit_rate": hit_rate,
                "error_rate": errors / max(total_ops, 1),
                "issues": issues,
                "stats_summary": {
                    "total_hits": unified_stats.get("hits", 0),
                    "total_misses": unified_stats.get("misses", 0),
                    "total_writes": unified_stats.get("writes", 0),
                    "total_errors": errors,
                    "avg_access_time": unified_stats.get("avg_access_time", 0),
                },
                "timestamp": __import__("time").time(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "enabled": False,
                "error": str(e),
                "message": "Failed to retrieve cache health status",
                "timestamp": __import__("time").time(),
            }


@cache_router.get("/config")
async def get_cache_config():
    """Get current cache configuration"""
    with error_context("get_cache_config", reraise=False):
        try:
            cache_manager = get_unified_cache_manager()

            return {
                "status": "success",
                "config": {
                    "enabled": cache_manager.enabled,
                    "cache_dir": str(cache_manager.cache_dir),
                    "providers": {
                        "multi_level_cache": {
                            "l1_max_size": cache_manager.multi_level_cache.l1_max_size,
                            "l2_max_size": cache_manager.multi_level_cache.l2_max_size,
                            "l3_max_size": getattr(
                                cache_manager.multi_level_cache, "l3_max_size", 0
                            ),
                            "compression_enabled": getattr(
                                cache_manager.multi_level_cache,
                                "enable_compression",
                                False,
                            ),
                            "prediction_enabled": getattr(
                                cache_manager.multi_level_cache,
                                "enable_prediction",
                                False,
                            ),
                        },
                        "subsystems": {
                            "legacy_cache": cache_manager.legacy_cache is not None,
                            "embedding_cache": cache_manager.embedding_cache
                            is not None,
                            "file_cache": cache_manager.file_cache is not None,
                        },
                    },
                    "routing": {
                        "patterns_tracked": len(cache_manager.router.access_patterns),
                        "adaptive_optimization": True,
                    },
                },
                "timestamp": __import__("time").time(),
            }

        except Exception as e:
            raise SystemError(
                "Failed to retrieve cache configuration",
                suggestion="Check cache system initialization",
            ) from e


@cache_router.post("/enable", dependencies=[Depends(require_role("admin"))])
async def enable_caching():
    """Enable the caching system"""
    with error_context("enable_caching", reraise=False):
        try:
            cache_manager = get_unified_cache_manager()
            cache_manager.enabled = True

            return {
                "status": "success",
                "message": "Caching system enabled",
                "enabled": True,
                "timestamp": __import__("time").time(),
            }

        except Exception as e:
            raise SystemError(
                "Failed to enable caching system",
                suggestion="Check cache system health",
            ) from e


@cache_router.post("/disable", dependencies=[Depends(require_role("admin"))])
async def disable_caching():
    """Disable the caching system"""
    with error_context("disable_caching", reraise=False):
        try:
            cache_manager = get_unified_cache_manager()
            cache_manager.enabled = False

            return {
                "status": "success",
                "message": "Caching system disabled",
                "enabled": False,
                "timestamp": __import__("time").time(),
            }

        except Exception as e:
            raise SystemError(
                "Failed to disable caching system",
                suggestion="Check cache system health",
            ) from e
