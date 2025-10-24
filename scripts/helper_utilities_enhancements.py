#!/usr/bin/env python3
"""
Helper Utilities Enhancements for OpenSpec Workflow

Provides comprehensive utility functions for performance profiling, caching, encryption,
progress tracking, and diagnostic analysis.

Key Features:
    - Performance profiling with timing analysis
    - Advanced caching utilities with TTL and invalidation
    - Encryption/decryption support for sensitive data
    - Progress bars and spinners for long operations
    - Diagnostic utilities for debugging
    - Memory and resource monitoring
    - Data serialization helpers
    - Retry logic with exponential backoff

Classes:
    PerformanceProfiler: Timing and performance analysis
    CacheManager: Advanced caching with TTL
    EncryptionHelper: Data encryption utilities
    ProgressTracker: Progress bar management
    DiagnosticHelper: System diagnostics
    ResourceMonitor: Resource usage tracking

Usage:
    profiler = PerformanceProfiler()
    with profiler.measure("operation"):
        # Do work
        pass
    
    print(profiler.get_report())

Author: Obsidian AI Agent Team
License: MIT
Version: 0.1.45
"""

import base64
import json
import os
import psutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic, Tuple


T = TypeVar('T')


class Color:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Colorize text with ANSI codes."""
        if not sys.stdout.isatty():
            return text
        return f"{color}{text}{Color.RESET}"


@dataclass
class TimingEntry:
    """Single timing measurement."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def finish(self) -> float:
        """Finish timing and return duration."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return self.duration


class PerformanceProfiler:
    """Performance profiling with timing analysis."""
    
    def __init__(self):
        """Initialize profiler."""
        self.timings: Dict[str, List[TimingEntry]] = {}
        self.total_start = time.time()
    
    def start_timer(self, name: str, metadata: Optional[Dict] = None) -> TimingEntry:
        """
        Start a named timer.
        
        Args:
            name: Timer name
            metadata: Optional metadata
            
        Returns:
            Timing entry
        """
        entry = TimingEntry(
            name=name,
            start_time=time.time(),
            metadata=metadata or {},
        )
        
        if name not in self.timings:
            self.timings[name] = []
        
        return entry
    
    def stop_timer(self, entry: TimingEntry) -> float:
        """
        Stop a timer.
        
        Args:
            entry: Timing entry
            
        Returns:
            Duration in seconds
        """
        duration = entry.finish()
        self.timings[entry.name].append(entry)
        return duration
    
    def measure(self, name: str, metadata: Optional[Dict] = None):
        """
        Context manager for measuring execution time.
        
        Usage:
            with profiler.measure("operation"):
                # Do work
        """
        return _TimingContext(self, name, metadata or {})
    
    def get_statistics(self, name: Optional[str] = None) -> Dict[str, float]:
        """
        Get timing statistics.
        
        Args:
            name: Optional specific timer name
            
        Returns:
            Statistics dictionary
        """
        if name and name in self.timings:
            entries = self.timings[name]
        elif name:
            return {}
        else:
            entries = []
            for timing_list in self.timings.values():
                entries.extend(timing_list)
        
        if not entries:
            return {}
        
        durations = [e.duration for e in entries if e.duration is not None]
        
        if not durations:
            return {}
        
        return {
            'count': len(durations),
            'total': sum(durations),
            'min': min(durations),
            'max': max(durations),
            'average': sum(durations) / len(durations),
            'median': sorted(durations)[len(durations) // 2],
        }
    
    def get_report(self) -> str:
        """Get formatted performance report."""
        lines = [
            "\n" + "="*60,
            "Performance Profile Report",
            "="*60,
        ]
        
        for name in sorted(self.timings.keys()):
            stats = self.get_statistics(name)
            if not stats:
                continue
            
            lines.append(f"\n{name}:")
            lines.append(f"  Count:   {stats['count']}")
            lines.append(f"  Total:   {stats['total']:.3f}s")
            lines.append(f"  Average: {stats['average']:.3f}s")
            lines.append(f"  Min:     {stats['min']:.3f}s")
            lines.append(f"  Max:     {stats['max']:.3f}s")
        
        total_duration = time.time() - self.total_start
        lines.append(f"\nTotal execution time: {total_duration:.3f}s")
        lines.append("="*60)
        
        return "\n".join(lines)


class _TimingContext:
    """Context manager for timing."""
    
    def __init__(self, profiler: PerformanceProfiler, name: str, metadata: Dict):
        self.profiler = profiler
        self.entry = profiler.start_timer(name, metadata)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.stop_timer(self.entry)


class CacheManager(Generic[T]):
    """Advanced caching with TTL and invalidation."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for persistent cache
        """
        self.memory_cache: Dict[str, Tuple[T, float]] = {}
        self.cache_dir = Path(cache_dir or ".cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str, ttl: int = 3600) -> Optional[T]:
        """
        Get cached value.
        
        Args:
            key: Cache key
            ttl: Time-to-live in seconds
            
        Returns:
            Cached value or None
        """
        # Check memory cache
        if key in self.memory_cache:
            value, timestamp = self.memory_cache[key]
            if time.time() - timestamp < ttl:
                self.hit_count += 1
                return value
            else:
                del self.memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                saved_time = data.get('timestamp', 0)
                if time.time() - saved_time < ttl:
                    value = data.get('value')
                    self.memory_cache[key] = (value, time.time())
                    self.hit_count += 1
                    return value
                else:
                    cache_file.unlink()
            except (json.JSONDecodeError, IOError):
                cache_file.unlink()
        
        self.miss_count += 1
        return None
    
    def set(self, key: str, value: T) -> None:
        """
        Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Memory cache
        self.memory_cache[key] = (value, time.time())
        
        # Disk cache
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'value': value,
                    'timestamp': time.time(),
                }, f)
        except (TypeError, IOError):
            # Skip if not JSON serializable
            pass
    
    def invalidate(self, pattern: Optional[str] = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            pattern: Optional glob pattern
            
        Returns:
            Number of entries cleared
        """
        count = 0
        
        if pattern:
            import fnmatch
            keys_to_remove: List[str] = [
                k for k in self.memory_cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            for key in keys_to_remove:
                del self.memory_cache[key]
                count += 1
        else:
            count = len(self.memory_cache)
            self.memory_cache.clear()
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (
            (self.hit_count / total * 100) if total > 0 else 0
        )
        
        return {
            'entries': len(self.memory_cache),
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': hit_rate,
            'total_requests': total,
        }


class EncryptionHelper:
    """Encryption/decryption for sensitive data."""
    
    @staticmethod
    def simple_encrypt(data: str, key: str) -> str:
        """
        Simple XOR-based encryption (for basic obfuscation only).
        
        For production, use proper encryption libraries.
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Encrypted data (base64 encoded)
        """
        encrypted = bytes(
            ord(c) ^ ord(key[i % len(key)])
            for i, c in enumerate(data)
        )
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def simple_decrypt(encrypted_data: str, key: str) -> str:
        """
        Simple XOR-based decryption.
        
        Args:
            encrypted_data: Encrypted data (base64 encoded)
            key: Decryption key
            
        Returns:
            Decrypted data
        """
        encrypted = base64.b64decode(encrypted_data)
        decrypted = bytes(
            b ^ ord(key[i % len(key)])
            for i, b in enumerate(encrypted)
        )
        return decrypted.decode()
    
    @staticmethod
    def hash_data(data: str, algorithm: str = 'sha256') -> str:
        """
        Hash data.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm
            
        Returns:
            Hex digest
        """
        import hashlib
        h = hashlib.new(algorithm)
        h.update(data.encode())
        return h.hexdigest()


class ProgressTracker:
    """Progress bar and status tracking."""
    
    def __init__(self, total: int, desc: str = "Progress"):
        """
        Initialize progress tracker.
        
        Args:
            total: Total steps
            desc: Description
        """
        self.total = total
        self.desc = desc
        self.current = 0
        self.start_time = time.time()
    
    def update(self, amount: int = 1) -> None:
        """
        Update progress.
        
        Args:
            amount: Number of steps to advance
        """
        self.current = min(self.current + amount, self.total)
    
    def get_bar(self, width: int = 40) -> str:
        """
        Get progress bar string.
        
        Args:
            width: Bar width
            
        Returns:
            Progress bar
        """
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(width * percent)
        bar = '█' * filled + '░' * (width - filled)
        
        elapsed = time.time() - self.start_time
        if self.current > 0:
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            eta = f"ETA: {remaining:.0f}s"
        else:
            eta = "ETA: --"
        
        return f"\r{self.desc}: |{bar}| {self.current}/{self.total} {eta}"
    
    def close(self) -> None:
        """Close progress bar."""
        print()


class ResourceMonitor:
    """Monitor system resource usage."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information."""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids()),
            }
        except Exception:
            return {}
    
    @staticmethod
    def get_process_info() -> Dict[str, Any]:
        """Get current process information."""
        try:
            process = psutil.Process(os.getpid())
            return {
                'pid': process.pid,
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(interval=0.1),
                'threads': process.num_threads(),
            }
        except Exception:
            return {}
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get memory usage details."""
        try:
            mem = psutil.virtual_memory()
            return {
                'total_mb': mem.total / 1024 / 1024,
                'available_mb': mem.available / 1024 / 1024,
                'used_mb': mem.used / 1024 / 1024,
                'percent': mem.percent,
            }
        except Exception:
            return {}


class RetryHelper:
    """Retry logic with exponential backoff."""
    
    @staticmethod
    def with_retry(
        func: Callable,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
    ) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Backoff multiplier
            exceptions: Exception types to catch
            
        Returns:
            Function result
            
        Raises:
            The last exception if all retries fail
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                
                if attempt < max_attempts - 1:
                    print(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
        
        if last_exception:
            raise last_exception


class DiagnosticHelper:
    """Diagnostic utilities for debugging."""
    
    @staticmethod
    def print_environment() -> None:
        """Print environment information."""
        print("\n📋 Environment Information:")
        print(f"  Python Version: {sys.version}")
        print(f"  Platform: {sys.platform}")
        print(f"  Executable: {sys.executable}")
        print(f"  Working Directory: {os.getcwd()}")
    
    @staticmethod
    def print_module_info(module: Any) -> None:
        """Print module information."""
        print(f"\n📦 Module: {module.__name__}")
        print(f"  File: {module.__file__}")
        if hasattr(module, '__version__'):
            print(f"  Version: {module.__version__}")
    
    @staticmethod
    def get_call_stack() -> List[str]:
        """Get formatted call stack."""
        import traceback
        return traceback.format_stack()


if __name__ == "__main__":
    print("🔧 Helper Utilities Examples\n")
    
    # Performance profiling
    profiler = PerformanceProfiler()
    
    with profiler.measure("example_operation"):
        time.sleep(0.1)
    
    print(profiler.get_report())
    
    # Caching
    cache: CacheManager = CacheManager()
    cache.set("key1", {"data": "value"})
    value = cache.get("key1")
    print(f"\nCache stats: {cache.get_stats()}")
    
    # Progress tracking
    progress = ProgressTracker(100, "Processing")
    for i in range(100):
        progress.update()
        if i % 10 == 0:
            print(progress.get_bar())
    progress.close()
    
    # Resource monitoring
    print("\nSystem info:", ResourceMonitor.get_system_info())
    print("Process info:", ResourceMonitor.get_process_info())
