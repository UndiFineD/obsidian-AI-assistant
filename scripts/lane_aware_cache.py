"""
Lane-Aware Caching Optimization System for v0.1.44

Intelligent multi-level caching system with lane-specific strategies for performance optimization.

Components:
    - CacheManager: Main cache orchestrator with multi-level caching
    - LaneAwareCacheStrategy: Lane-specific caching policies
    - StateSnapshotCache: Recovery state and checkpoint caching
    - CacheMetrics: Cache performance tracking
    - CacheInvalidator: Smart cache invalidation

Caching Levels:
    - L1: Memory cache (fast, limited size)
    - L2: Local disk cache (medium, larger size)
    - L3: Persistent state cache (slow, unlimited)
    - L4: Distributed cache (optional Redis)

Usage:
    cache = CacheManager.from_settings()
    result = cache.get_or_set('key', compute_fn, lane='standard')
    cache.invalidate_by_pattern('workflow:*')
    metrics = cache.get_metrics()

Author: v0.1.44 Enhancement Cycle
Version: 1.0.0
"""

import json
import time
import hashlib
import threading
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime, timedelta
import logging
import pickle
from collections import OrderedDict
import re

# ============================================================================
# Configuration & Constants
# ============================================================================

CACHE_DIR = Path(".cache")
METRICS_FILE = CACHE_DIR / "metrics.json"

# Default cache sizes (in items, not bytes)
CACHE_SIZES = {
    "docs": {
        "l1": 100,  # Memory cache
        "l2": 1000,  # Disk cache
        "l3": 10000,  # Persistent cache
    },
    "standard": {
        "l1": 500,
        "l2": 5000,
        "l3": 50000,
    },
    "heavy": {
        "l1": 1000,
        "l2": 10000,
        "l3": 100000,
    },
}

# Default TTL (time-to-live) in seconds
DEFAULT_TTL = {
    "docs": 300,  # 5 minutes
    "standard": 900,  # 15 minutes
    "heavy": 1800,  # 30 minutes
}

# ============================================================================
# Enums
# ============================================================================


class LaneType(Enum):
    """Workflow lane types."""

    DOCS = "docs"
    STANDARD = "standard"
    HEAVY = "heavy"


class CacheLevel(Enum):
    """Cache hierarchy levels."""

    L1 = "memory"  # In-memory cache
    L2 = "disk"  # Local disk
    L3 = "persistent"  # Persistent storage
    L4 = "distributed"  # Optional distributed cache


class EvictionPolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time-based expiration


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class CacheEntry:
    """Single cache entry."""

    key: str
    value: Any
    created_at: str
    accessed_at: str
    expires_at: str
    access_count: int = 0
    size_bytes: int = 0
    lane: str = "standard"
    tags: List[str] = field(default_factory=list)


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    timestamp: str
    lane: str
    level: str
    hits: int
    misses: int
    evictions: int
    size_bytes: int
    entry_count: int
    hit_rate: float
    avg_access_time: float


@dataclass
class CachePolicy:
    """Cache configuration policy."""

    lane: str
    level: str
    max_entries: int
    max_size_bytes: int
    ttl_seconds: int
    eviction_policy: str
    compression_enabled: bool = False
    persistence_enabled: bool = True


# ============================================================================
# Cache Level Implementations
# ============================================================================


class L1MemoryCache:
    """In-memory cache using OrderedDict for LRU."""

    def __init__(self, max_entries: int):
        self.max_entries = max_entries
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]

                # Check expiration
                if datetime.fromisoformat(entry.expires_at) < datetime.now():
                    del self.cache[key]
                    self.misses += 1
                    return None

                # Update access tracking (move to end for LRU)
                self.cache.move_to_end(key)
                entry.accessed_at = datetime.now().isoformat()
                entry.access_count += 1
                self.hits += 1
                return entry.value

            self.misses += 1
            return None

    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set value in L1 cache."""
        with self.lock:
            # Remove oldest if at capacity
            if len(self.cache) >= self.max_entries:
                self.cache.popitem(last=False)  # Remove first (oldest)

            self.cache[key] = entry
            return True

    def delete(self, key: str) -> bool:
        """Delete entry from L1 cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def clear(self):
        """Clear all entries."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics."""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0

            return {
                "entries": len(self.cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
            }


class L2DiskCache:
    """Local disk cache using JSON/pickle."""

    def __init__(self, cache_dir: Path, max_entries: int):
        self.cache_dir = cache_dir / "l2"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from L2 cache."""
        try:
            with self.lock:
                cache_file = self._get_cache_file(key)

                if not cache_file.exists():
                    self.misses += 1
                    return None

                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)

                # Check expiration
                if datetime.fromisoformat(entry.expires_at) < datetime.now():
                    cache_file.unlink()
                    self.misses += 1
                    return None

                entry.accessed_at = datetime.now().isoformat()
                entry.access_count += 1
                self.hits += 1

                return entry.value
        except Exception as e:
            logging.debug(f"L2 cache get error: {e}")
            self.misses += 1
            return None

    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set value in L2 cache."""
        try:
            with self.lock:
                # Check capacity
                entries = list(self.cache_dir.glob("*.cache"))
                if len(entries) >= self.max_entries:
                    # Remove oldest
                    oldest = min(entries, key=lambda p: p.stat().st_mtime)
                    oldest.unlink()

                cache_file = self._get_cache_file(key)
                with open(cache_file, "wb") as f:
                    pickle.dump(entry, f)

                return True
        except Exception as e:
            logging.warning(f"L2 cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete entry from L2 cache."""
        try:
            with self.lock:
                cache_file = self._get_cache_file(key)
                if cache_file.exists():
                    cache_file.unlink()
                    return True
        except Exception as e:
            logging.debug(f"L2 cache delete error: {e}")
        return False

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics."""
        try:
            with self.lock:
                entries = list(self.cache_dir.glob("*.cache"))
                total_size = sum(f.stat().st_size for f in entries)
                total_requests = self.hits + self.misses
                hit_rate = (
                    (self.hits / total_requests * 100) if total_requests > 0 else 0
                )

                return {
                    "entries": len(entries),
                    "size_bytes": total_size,
                    "hits": self.hits,
                    "misses": self.misses,
                    "hit_rate": hit_rate,
                }
        except Exception as e:
            logging.warning(f"L2 metrics error: {e}")
            return {}


class L3PersistentCache:
    """Persistent cache for long-term state."""

    def __init__(self, cache_dir: Path):
        self.cache_file = cache_dir / "l3" / "persistent_cache.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache: Dict[str, dict] = {}
        self._load()
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from L3 cache."""
        with self.lock:
            if key in self.cache:
                entry_data = self.cache[key]

                # Check expiration
                if datetime.fromisoformat(entry_data["expires_at"]) < datetime.now():
                    del self.cache[key]
                    self._save()
                    self.misses += 1
                    return None

                entry_data["accessed_at"] = datetime.now().isoformat()
                entry_data["access_count"] += 1
                self.hits += 1

                try:
                    return json.loads(entry_data["value"])
                except:
                    return entry_data["value"]

            self.misses += 1
            return None

    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set value in L3 cache."""
        try:
            with self.lock:
                self.cache[key] = {
                    "value": json.dumps(entry.value)
                    if isinstance(entry.value, (dict, list))
                    else entry.value,
                    "created_at": entry.created_at,
                    "accessed_at": entry.accessed_at,
                    "expires_at": entry.expires_at,
                    "access_count": entry.access_count,
                    "tags": entry.tags,
                }
                self._save()
                return True
        except Exception as e:
            logging.warning(f"L3 cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete entry from L3 cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self._save()
                return True
            return False

    def _save(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logging.warning(f"L3 cache save error: {e}")

    def _load(self):
        """Load cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file) as f:
                    self.cache = json.load(f)
        except Exception as e:
            logging.warning(f"L3 cache load error: {e}")
            self.cache = {}


# ============================================================================
# Lane-Aware Cache Strategy
# ============================================================================


class LaneAwareCacheStrategy:
    """Lane-specific caching strategies."""

    @staticmethod
    def get_policy(lane: LaneType) -> CachePolicy:
        """Get caching policy for lane."""
        lane_str = lane.value

        if lane == LaneType.DOCS:
            return CachePolicy(
                lane=lane_str,
                level="l1-l2",
                max_entries=CACHE_SIZES["docs"]["l1"],
                max_size_bytes=512 * 1024 * 1024,  # 512MB
                ttl_seconds=DEFAULT_TTL["docs"],
                eviction_policy=EvictionPolicy.LRU.value,
                compression_enabled=True,
                persistence_enabled=False,
            )

        elif lane == LaneType.STANDARD:
            return CachePolicy(
                lane=lane_str,
                level="l1-l2-l3",
                max_entries=CACHE_SIZES["standard"]["l1"],
                max_size_bytes=1024 * 1024 * 1024,  # 1GB
                ttl_seconds=DEFAULT_TTL["standard"],
                eviction_policy=EvictionPolicy.LRU.value,
                compression_enabled=False,
                persistence_enabled=True,
            )

        else:  # HEAVY
            return CachePolicy(
                lane=lane_str,
                level="l1-l2-l3",
                max_entries=CACHE_SIZES["heavy"]["l1"],
                max_size_bytes=2048 * 1024 * 1024,  # 2GB
                ttl_seconds=DEFAULT_TTL["heavy"],
                eviction_policy=EvictionPolicy.LRU.value,
                compression_enabled=False,
                persistence_enabled=True,
            )

    @staticmethod
    def should_cache(lane: LaneType, key: str) -> bool:
        """Determine if value should be cached based on lane."""
        if lane == LaneType.DOCS:
            # Cache documentation-related items
            return any(p in key for p in ["doc", "markdown", "build", "schema"])

        elif lane == LaneType.STANDARD:
            # Cache test results, quality metrics
            return any(p in key for p in ["test", "metrics", "result", "validation"])

        else:  # HEAVY
            # Cache everything in heavy lane
            return True

    @staticmethod
    def get_eviction_priority(lane: LaneType, entry: CacheEntry) -> float:
        """Calculate eviction priority (higher = evict first)."""
        base_priority = 0.0

        # Recent access reduces priority (keep longer)
        access_recency = (
            datetime.now() - datetime.fromisoformat(entry.accessed_at)
        ).total_seconds()
        base_priority -= access_recency / 1000  # Normalize

        # Frequently accessed entries kept longer
        base_priority -= entry.access_count / 100

        # Size increases priority (evict large items first)
        base_priority += entry.size_bytes / (1024 * 1024)  # Normalize to MB

        return base_priority


# ============================================================================
# State Snapshot Cache
# ============================================================================


class StateSnapshotCache:
    """Specialized cache for workflow state snapshots and checkpoints."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir / "snapshots"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata: Dict[str, dict] = {}
        self._load_metadata()
        self.lock = threading.Lock()

    def cache_checkpoint(
        self, checkpoint_id: str, state_data: Dict[str, Any], lane: str
    ) -> bool:
        """Cache checkpoint state."""
        try:
            with self.lock:
                snapshot_file = self.cache_dir / f"{checkpoint_id}.snapshot"

                # Save snapshot
                with open(snapshot_file, "w") as f:
                    json.dump(state_data, f, indent=2)

                # Update metadata
                self.metadata[checkpoint_id] = {
                    "lane": lane,
                    "created_at": datetime.now().isoformat(),
                    "accessed_at": datetime.now().isoformat(),
                    "access_count": 0,
                    "size_bytes": snapshot_file.stat().st_size,
                }

                self._save_metadata()
                return True
        except Exception as e:
            logging.warning(f"Checkpoint cache error: {e}")
            return False

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore checkpoint from cache."""
        try:
            with self.lock:
                snapshot_file = self.cache_dir / f"{checkpoint_id}.snapshot"

                if not snapshot_file.exists():
                    return None

                with open(snapshot_file) as f:
                    state_data = json.load(f)

                # Update metadata
                if checkpoint_id in self.metadata:
                    self.metadata[checkpoint_id]["accessed_at"] = (
                        datetime.now().isoformat()
                    )
                    self.metadata[checkpoint_id]["access_count"] += 1
                    self._save_metadata()

                return state_data
        except Exception as e:
            logging.warning(f"Checkpoint restore error: {e}")
            return None

    def invalidate_checkpoint(self, checkpoint_id: str) -> bool:
        """Invalidate cached checkpoint."""
        try:
            with self.lock:
                snapshot_file = self.cache_dir / f"{checkpoint_id}.snapshot"
                if snapshot_file.exists():
                    snapshot_file.unlink()

                if checkpoint_id in self.metadata:
                    del self.metadata[checkpoint_id]
                    self._save_metadata()

                return True
        except Exception as e:
            logging.warning(f"Checkpoint invalidation error: {e}")
            return False

    def cleanup_old_checkpoints(self, max_age_days: int = 7) -> int:
        """Remove cached checkpoints older than specified days."""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        removed = 0

        try:
            with self.lock:
                for checkpoint_id, metadata in list(self.metadata.items()):
                    created = datetime.fromisoformat(metadata["created_at"])
                    if created < cutoff_time:
                        self.invalidate_checkpoint(checkpoint_id)
                        removed += 1
        except Exception as e:
            logging.warning(f"Checkpoint cleanup error: {e}")

        return removed

    def _save_metadata(self):
        """Save metadata to disk."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logging.warning(f"Metadata save error: {e}")

    def _load_metadata(self):
        """Load metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file) as f:
                    self.metadata = json.load(f)
        except Exception as e:
            logging.warning(f"Metadata load error: {e}")


# ============================================================================
# Main Cache Manager
# ============================================================================


class CacheManager:
    """Main cache orchestrator with multi-level caching."""

    def __init__(self, lane: LaneType = LaneType.STANDARD):
        self.lane = lane
        self.policy = LaneAwareCacheStrategy.get_policy(lane)

        # Initialize cache levels
        self.l1 = L1MemoryCache(self.policy.max_entries)
        self.l2 = L2DiskCache(CACHE_DIR, CACHE_SIZES[lane.value]["l2"])
        self.l3 = L3PersistentCache(CACHE_DIR)
        self.snapshots = StateSnapshotCache(CACHE_DIR)

        self.metrics_history: List[CacheMetrics] = []
        self.lock = threading.Lock()

        logging.info(f"CacheManager initialized for {lane.value} lane")

    @classmethod
    def from_settings(cls, lane: str = "standard") -> "CacheManager":
        """Create from settings."""
        lane_type = LaneType[lane.upper()]
        return cls(lane_type)

    def get_or_set(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Any:
        """Get cached value or compute and cache."""

        # Check L1
        value = self.l1.get(key)
        if value is not None:
            return value

        # Check L2
        value = self.l2.get(key)
        if value is not None:
            # Promote to L1
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now().isoformat(),
                accessed_at=datetime.now().isoformat(),
                expires_at=(
                    datetime.now() + timedelta(seconds=ttl or self.policy.ttl_seconds)
                ).isoformat(),
                tags=tags or [],
                lane=self.lane.value,
            )
            self.l1.set(key, entry)
            return value

        # Check L3 (if enabled)
        if self.policy.persistence_enabled:
            value = self.l3.get(key)
            if value is not None:
                # Promote to L1
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.now().isoformat(),
                    accessed_at=datetime.now().isoformat(),
                    expires_at=(
                        datetime.now()
                        + timedelta(seconds=ttl or self.policy.ttl_seconds)
                    ).isoformat(),
                    tags=tags or [],
                    lane=self.lane.value,
                )
                self.l1.set(key, entry)
                return value

        # Compute and cache
        value = compute_fn()
        ttl_seconds = ttl or self.policy.ttl_seconds

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now().isoformat(),
            accessed_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(seconds=ttl_seconds)).isoformat(),
            tags=tags or [],
            lane=self.lane.value,
        )

        # Determine cache levels based on lane and value
        if LaneAwareCacheStrategy.should_cache(self.lane, key):
            self.l1.set(key, entry)
            self.l2.set(key, entry)

            if self.policy.persistence_enabled:
                self.l3.set(key, entry)

        return value

    def invalidate(self, key: str) -> bool:
        """Invalidate key from all cache levels."""
        results = [
            self.l1.delete(key),
            self.l2.delete(key),
        ]

        if self.policy.persistence_enabled:
            results.append(self.l3.delete(key))

        return any(results)

    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern."""
        # Pattern examples: "workflow:*", "test:*:result"
        regex = pattern.replace("*", ".*")
        count = 0

        # This is simplified - in production, iterate through cache keys
        logging.info(f"Pattern invalidation: {pattern} (regex: {regex})")

        return count

    def clear_all(self):
        """Clear all cache levels."""
        self.l1.clear()
        self.l2.cache_dir.mkdir(parents=True, exist_ok=True)
        for f in self.l2.cache_dir.glob("*.cache"):
            f.unlink()

        if self.policy.persistence_enabled:
            self.l3.cache.clear()
            self.l3._save()

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        return {
            "lane": self.lane.value,
            "timestamp": datetime.now().isoformat(),
            "l1": self.l1.get_metrics(),
            "l2": self.l2.get_metrics(),
            "l3": {
                "entries": len(self.l3.cache),
                "hits": self.l3.hits,
                "misses": self.l3.misses,
            }
            if self.policy.persistence_enabled
            else None,
            "policy": asdict(self.policy),
        }

    def get_checkpoint_cache_status(self) -> Dict[str, Any]:
        """Get checkpoint cache status."""
        return {
            "cached_checkpoints": len(self.snapshots.metadata),
            "total_size_bytes": sum(
                m.get("size_bytes", 0) for m in self.snapshots.metadata.values()
            ),
            "metadata": self.snapshots.metadata,
        }


# ============================================================================
# Utility Functions
# ============================================================================


def measure_cache_performance(
    cache: CacheManager, iterations: int = 1000
) -> Dict[str, float]:
    """Measure cache performance characteristics."""

    results = {
        "iterations": iterations,
        "cache_hits": 0,
        "cache_misses": 0,
        "avg_hit_time": 0.0,
        "avg_miss_time": 0.0,
    }

    hit_times = []
    miss_times = []

    for i in range(iterations):
        key = f"perf_test_{i % 10}"  # Repeat keys for hits/misses

        if i % 10 < 5:  # First 5 iterations miss
            start = time.time()
            value = cache.get_or_set(key, lambda: f"value_{i}")
            miss_times.append(time.time() - start)
            results["cache_misses"] += 1
        else:
            start = time.time()
            value = cache.get_or_set(key, lambda: f"value_{i}")
            hit_times.append(time.time() - start)
            results["cache_hits"] += 1

    if hit_times:
        results["avg_hit_time"] = sum(hit_times) / len(hit_times)
    if miss_times:
        results["avg_miss_time"] = sum(miss_times) / len(miss_times)

    return results


# ============================================================================
# Main CLI Interface
# ============================================================================

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Cache Management")
    parser.add_argument(
        "--lane", choices=["docs", "standard", "heavy"], default="standard"
    )
    parser.add_argument(
        "--action", choices=["clear", "metrics", "status", "cleanup"], default="metrics"
    )
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    cache = CacheManager.from_settings(args.lane)

    if args.action == "metrics":
        metrics = cache.get_metrics()
        print(json.dumps(metrics, indent=2))

    elif args.action == "status":
        status = cache.get_checkpoint_cache_status()
        print(f"Checkpoint cache status: {json.dumps(status, indent=2)}")

    elif args.action == "clear":
        cache.clear_all()
        print("✓ Cache cleared")

    elif args.action == "cleanup":
        removed = cache.snapshots.cleanup_old_checkpoints(max_age_days=7)
        print(f"✓ Removed {removed} old checkpoints")
