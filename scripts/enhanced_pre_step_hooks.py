#!/usr/bin/env python3
"""
Enhanced Pre-Step Hooks System for OpenSpec Workflow

Provides extensibility framework, dependency management, and caching support for
pre-step validation hooks in the workflow execution pipeline.

Key Features:
    - Plugin-based extensibility framework
    - Dependency management and resolution
    - Hook result caching with TTL
    - Hook composition and chaining
    - Context propagation through pipeline
    - Hook profiling and performance tracking
    - Error recovery and retry policies

Classes:
    Hook: Base class for workflow hooks
    HookRegistry: Registry for hook management
    HookContext: Execution context for hooks
    HookCache: Caching system for hook results
    HookComposer: Hook composition and chaining
    DependencyResolver: Hook dependency resolution

Usage:
    registry = HookRegistry()

    @registry.register("check_python_version")
    class PythonVersionHook(Hook):
        def execute(self, context):
            # Implementation
            pass

    hooks = registry.get_hooks_for_stage(0)
    context = HookContext(stage_num=0)
    for hook in hooks:
        result = hook.execute(context)

Author: Obsidian AI Agent Team
License: MIT
Version: 0.1.45
"""

import functools
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class HookStatus(Enum):
    """Hook execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class HookResult:
    """Result of hook execution."""

    hook_name: str
    status: HookStatus
    duration: float
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    cached: bool = False

    def is_success(self) -> bool:
        """Check if hook succeeded."""
        return self.status in (HookStatus.SUCCESS, HookStatus.WARNING)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hook_name": self.hook_name,
            "status": self.status.value,
            "duration": self.duration,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "cached": self.cached,
        }


@dataclass
class HookContext:
    """Execution context for hooks."""

    stage_num: int
    stage_name: str = ""
    change_id: str = ""
    lane: str = "standard"
    metadata: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, HookResult] = field(default_factory=dict)

    def get_result(self, hook_name: str) -> Optional[HookResult]:
        """Get result from previous hook execution."""
        return self.results.get(hook_name)

    def set_result(self, hook_name: str, result: HookResult) -> None:
        """Set result from hook execution."""
        self.results[hook_name] = result


class Hook(ABC):
    """Base class for workflow hooks."""

    def __init__(self, name: str, depends_on: Optional[List[str]] = None):
        """
        Initialize hook.

        Args:
            name: Unique hook identifier
            depends_on: List of hook names this hook depends on
        """
        self.name = name
        self.depends_on = depends_on or []
        self.executed = False
        self.execution_time = 0.0

    @abstractmethod
    def execute(self, context: HookContext) -> HookResult:
        """
        Execute hook.

        Args:
            context: Hook execution context

        Returns:
            Hook execution result
        """
        pass

    def can_execute(self, context: HookContext) -> bool:
        """
        Check if hook can execute (dependencies satisfied).

        Args:
            context: Hook execution context

        Returns:
            True if dependencies are satisfied
        """
        for dep in self.depends_on:
            result = context.get_result(dep)
            if result is None:
                return False
            if not result.is_success():
                return False
        return True

    def validate_dependencies(self, registry: "HookRegistry") -> bool:
        """
        Validate that dependencies exist.

        Args:
            registry: Hook registry

        Returns:
            True if all dependencies exist
        """
        for dep in self.depends_on:
            if dep not in registry.hooks:
                return False
        return True


class CachedHook(Hook):
    """Hook with built-in caching."""

    def __init__(
        self, name: str, cache_ttl: int = 300, depends_on: Optional[List[str]] = None
    ):
        """
        Initialize cached hook.

        Args:
            name: Unique hook identifier
            cache_ttl: Cache time-to-live in seconds
            depends_on: List of hook dependencies
        """
        super().__init__(name, depends_on)
        self.cache_ttl = cache_ttl
        self.cache_time = 0.0
        self.cached_result: Optional[HookResult] = None

    def _is_cache_valid(self) -> bool:
        """Check if cached result is still valid."""
        if self.cached_result is None:
            return False

        elapsed = time.time() - self.cache_time
        return elapsed < self.cache_ttl

    def execute(self, context: HookContext) -> HookResult:
        """Execute with caching."""
        if self._is_cache_valid() and self.cached_result is not None:
            self.cached_result.cached = True
            return self.cached_result

        start_time = time.time()
        try:
            result = self._execute_impl(context)
            result.duration = time.time() - start_time
        except Exception as e:
            result = HookResult(
                hook_name=self.name,
                status=HookStatus.ERROR,
                duration=time.time() - start_time,
                message=f"Error: {str(e)}",
                error=str(e),
            )

        # Cache result
        self.cached_result = result
        self.cache_time = time.time()

        return result

    @abstractmethod
    def _execute_impl(self, context: HookContext) -> HookResult:
        """Actual hook implementation (override this)."""
        pass


class HookRegistry:
    """Registry for hook management and discovery."""

    def __init__(self):
        """Initialize hook registry."""
        self.hooks: Dict[str, Hook] = {}
        self.stage_hooks: Dict[int, List[str]] = {}
        self.execution_history: List[HookResult] = []

    def register(self, name: str, stages: Optional[List[int]] = None) -> Callable:
        """
        Decorator to register a hook.

        Args:
            name: Hook name
            stages: Stages where hook should execute

        Returns:
            Decorator function
        """

        def decorator(hook_class: type) -> type:
            hook_instance = hook_class(name)
            self.hooks[name] = hook_instance

            # Register for stages
            if stages:
                for stage in stages:
                    if stage not in self.stage_hooks:
                        self.stage_hooks[stage] = []
                    if name not in self.stage_hooks[stage]:
                        self.stage_hooks[stage].append(name)

            return hook_class

        return decorator

    def get_hooks_for_stage(self, stage_num: int) -> List[Hook]:
        """
        Get hooks for a specific stage.

        Args:
            stage_num: Stage number

        Returns:
            List of hooks for stage
        """
        hook_names = self.stage_hooks.get(stage_num, [])
        return [self.hooks[name] for name in hook_names if name in self.hooks]

    def execute_hooks(
        self, stage_num: int, context: HookContext, fail_fast: bool = True
    ) -> List[HookResult]:
        """
        Execute hooks for a stage.

        Args:
            stage_num: Stage number
            context: Hook context
            fail_fast: Stop on first failure

        Returns:
            List of hook results
        """
        results = []
        hooks = self.get_hooks_for_stage(stage_num)

        # Resolve dependencies and execute
        resolved_hooks = DependencyResolver.resolve(hooks)

        for hook in resolved_hooks:
            if not hook.can_execute(context):
                # Skip if dependencies not satisfied
                result = HookResult(
                    hook_name=hook.name,
                    status=HookStatus.SKIPPED,
                    duration=0,
                    message="Dependencies not satisfied",
                )
            else:
                result = hook.execute(context)

            results.append(result)
            context.set_result(hook.name, result)
            self.execution_history.append(result)

            if fail_fast and not result.is_success():
                break

        return results

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of hook executions."""
        successful = sum(
            1 for r in self.execution_history if r.status == HookStatus.SUCCESS
        )
        failed = sum(1 for r in self.execution_history if r.status == HookStatus.ERROR)
        warnings = sum(
            1 for r in self.execution_history if r.status == HookStatus.WARNING
        )
        total_duration = sum(r.duration for r in self.execution_history)

        return {
            "total_executed": len(self.execution_history),
            "successful": successful,
            "failed": failed,
            "warnings": warnings,
            "total_duration": total_duration,
            "average_duration": (
                total_duration / len(self.execution_history)
                if self.execution_history
                else 0
            ),
        }


class DependencyResolver:
    """Resolves hook dependencies in execution order."""

    @staticmethod
    def resolve(hooks: List[Hook]) -> List[Hook]:
        """
        Resolve hooks in dependency order.

        Args:
            hooks: List of hooks to resolve

        Returns:
            Hooks sorted by dependency order

        Raises:
            ValueError: If circular dependency detected
        """
        hook_map = {hook.name: hook for hook in hooks}
        resolved: List[Hook] = []

        def visit(hook: Hook, path: Set[str]) -> None:
            if hook.name in path:
                raise ValueError(f"Circular dependency detected: {' -> '.join(path)}")

            if hook.name in {h.name for h in resolved}:
                return  # Already resolved

            path.add(hook.name)

            for dep_name in hook.depends_on:
                if dep_name in hook_map:
                    visit(hook_map[dep_name], path.copy())

            resolved.append(hook)

        for hook in hooks:
            if hook.name not in {h.name for h in resolved}:
                visit(hook, set())

        return resolved


class HookComposer:
    """Composes multiple hooks into a composite hook."""

    def __init__(self, name: str, hooks: List[Hook]):
        """
        Initialize hook composer.

        Args:
            name: Composite hook name
            hooks: List of hooks to compose
        """
        self.name = name
        self.hooks = DependencyResolver.resolve(hooks)

    def execute(self, context: HookContext) -> HookResult:
        """
        Execute composed hooks.

        Args:
            context: Hook context

        Returns:
            Composite result
        """
        results = []
        start_time = time.time()

        for hook in self.hooks:
            result = hook.execute(context)
            results.append(result)
            context.set_result(hook.name, result)

            if not result.is_success():
                # Stop on first failure
                break

        # Create composite result
        all_success = all(r.is_success() for r in results)
        status = HookStatus.SUCCESS if all_success else HookStatus.ERROR

        messages = [r.message for r in results]

        return HookResult(
            hook_name=self.name,
            status=status,
            duration=time.time() - start_time,
            message=" → ".join(messages),
            data={"sub_results": [r.to_dict() for r in results]},
        )


class HookProfiler:
    """Profiles hook execution for performance analysis."""

    def __init__(self):
        """Initialize profiler."""
        self.profiles: Dict[str, List[float]] = {}

    def profile(self, hook_name: str) -> Callable:
        """
        Decorator for hook profiling.

        Args:
            hook_name: Name of hook to profile

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start

                if hook_name not in self.profiles:
                    self.profiles[hook_name] = []

                self.profiles[hook_name].append(duration)
                return result

            return wrapper

        return decorator

    def get_stats(self, hook_name: str) -> Dict[str, float]:
        """Get profiling statistics for a hook."""
        if hook_name not in self.profiles:
            return {}

        times = self.profiles[hook_name]

        return {
            "count": len(times),
            "total": sum(times),
            "average": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
        }


class HookCache:
    """Caching system for hook results."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize hook cache.

        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = Path(cache_dir or ".hook_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Tuple[HookResult, float]] = {}

    def get(self, key: str, ttl: int = 300) -> Optional[HookResult]:
        """
        Get cached result.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            Cached result or None
        """
        # Check memory cache first
        if key in self.memory_cache:
            result, timestamp = self.memory_cache[key]
            if time.time() - timestamp < ttl:
                return result
            else:
                del self.memory_cache[key]

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)

                # Check age
                saved_time = data.get("timestamp", 0)
                if time.time() - saved_time < ttl:
                    # Recreate HookResult
                    result = HookResult(
                        hook_name=data["hook_name"],
                        status=HookStatus(data["status"]),
                        duration=data["duration"],
                        message=data["message"],
                        data=data.get("data", {}),
                        error=data.get("error"),
                        cached=True,
                    )

                    # Update memory cache
                    self.memory_cache[key] = (result, time.time())
                    return result
                else:
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink()

        return None

    def set(self, key: str, result: HookResult) -> None:
        """
        Cache a result.

        Args:
            key: Cache key
            result: Result to cache
        """
        # Memory cache
        self.memory_cache[key] = (result, time.time())

        # Disk cache
        cache_file = self.cache_dir / f"{key}.json"
        data = result.to_dict()
        data["timestamp"] = time.time()

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache.

        Args:
            pattern: Optional glob pattern to clear specific entries

        Returns:
            Number of entries cleared
        """
        count = 0

        if pattern:
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
                count += 1
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1

        # Clear memory cache
        if not pattern:
            self.memory_cache.clear()

        return count


if __name__ == "__main__":
    # Example usage
    registry = HookRegistry()

    class ExampleHook(Hook):
        def execute(self, context: HookContext) -> HookResult:
            return HookResult(
                hook_name=self.name,
                status=HookStatus.SUCCESS,
                duration=0.1,
                message="Example hook executed",
            )

    # Register hook
    hook = ExampleHook("example_hook")
    registry.hooks["example_hook"] = hook
    registry.stage_hooks[0] = ["example_hook"]

    # Execute
    context = HookContext(stage_num=0, change_id="test")
    results = registry.execute_hooks(0, context)

    print(f"Executed {len(results)} hooks")
    for result in results:
        print(f"  {result.hook_name}: {result.status.value}")
