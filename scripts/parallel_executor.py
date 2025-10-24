#!/usr/bin/env python3
"""
Parallel Execution Engine for OpenSpec Workflow

Manages parallelization of workflow stages using ThreadPoolExecutor.
Ensures deterministic ordering of results and proper error handling.

This module enables:
- Parallel execution of stages 2-6 (Proposal, Spec, Tasks, Tests, Scripts)
- Configurable worker pool (default: 3 workers)
- Per-task timeout handling
- Deterministic output ordering
- Progress tracking
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Any
from enum import Enum
import sys
from datetime import datetime

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import workflow_helpers as helpers
except ImportError:
    helpers = None


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: int
    task_name: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration: float
    result: Any
    error: Optional[str]
    output: Optional[str]
    
    def __post_init__(self):
        """Calculate duration if end_time provided."""
        if self.end_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


class ParallelExecutor:
    """
    Manages parallel execution of workflow stages.
    
    Attributes:
        max_workers: Number of concurrent workers (default: 3)
        timeout_per_task: Timeout per task in seconds (default: 300)
        deterministic_order: Maintain task ordering in results (default: True)
    """
    
    def __init__(
        self,
        max_workers: int = 3,
        timeout_per_task: int = 300,
        deterministic_order: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize the parallel executor.
        
        Args:
            max_workers: Number of concurrent workers
            timeout_per_task: Timeout per task in seconds
            deterministic_order: Maintain task ordering in results
            verbose: Enable verbose output
        """
        self.max_workers = max_workers
        self.timeout_per_task = timeout_per_task
        self.deterministic_order = deterministic_order
        self.verbose = verbose
        
        # Tracking
        self.tasks: Dict[int, TaskResult] = {}
        self.lock = threading.Lock()
        self.completed_count = 0
        self.failed_count = 0
        self.timeout_count = 0
    
    def _log(self, message: str, level: str = "info"):
        """Log a message if verbose."""
        if not self.verbose:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "info": "ℹ",
            "success": "✓",
            "error": "✗",
            "warning": "⚠",
        }.get(level, "·")
        
        print(f"[{timestamp}] {prefix} {message}")
    
    def execute_parallel(
        self,
        tasks: List[Tuple[int, str, Callable, List, Dict]],
        progress_callback: Optional[Callable] = None,
    ) -> List[TaskResult]:
        """
        Execute tasks in parallel.
        
        Args:
            tasks: List of tuples (task_id, task_name, callable, args, kwargs)
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of TaskResult objects, ordered by task_id if deterministic_order=True
        """
        self._log(f"Starting parallel execution with {self.max_workers} workers")
        
        results = {}
        futures_to_task = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            for task_id, task_name, func, args, kwargs in tasks:
                self._log(f"Submitting task {task_id}: {task_name}")
                
                future = executor.submit(
                    self._execute_task_with_timeout,
                    task_id,
                    task_name,
                    func,
                    args,
                    kwargs,
                )
                futures_to_task[future] = (task_id, task_name)
            
            # Process completed futures
            completed = 0
            total = len(tasks)
            
            for future in as_completed(futures_to_task):
                task_id, task_name = futures_to_task[future]
                completed += 1
                
                try:
                    result = future.result(timeout=self.timeout_per_task)
                    results[task_id] = result
                    
                    if result.status == TaskStatus.COMPLETED:
                        self.completed_count += 1
                        self._log(
                            f"Task {task_id} completed ({result.duration:.2f}s)",
                            level="success",
                        )
                    elif result.status == TaskStatus.FAILED:
                        self.failed_count += 1
                        self._log(
                            f"Task {task_id} failed: {result.error}",
                            level="error",
                        )
                    elif result.status == TaskStatus.TIMEOUT:
                        self.timeout_count += 1
                        self._log(
                            f"Task {task_id} timeout ({self.timeout_per_task}s)",
                            level="warning",
                        )
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(
                            completed,
                            total,
                            task_id,
                            result.status.value,
                        )
                
                except TimeoutError:
                    self.timeout_count += 1
                    self._log(
                        f"Task {task_id} timeout during result retrieval",
                        level="error",
                    )
                    result = TaskResult(
                        task_id=task_id,
                        task_name=task_name,
                        status=TaskStatus.TIMEOUT,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration=self.timeout_per_task,
                        result=None,
                        error=f"Timeout after {self.timeout_per_task}s",
                        output=None,
                    )
                    results[task_id] = result
                
                except Exception as e:
                    self.failed_count += 1
                    self._log(
                        f"Task {task_id} error: {str(e)}",
                        level="error",
                    )
                    result = TaskResult(
                        task_id=task_id,
                        task_name=task_name,
                        status=TaskStatus.FAILED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration=0,
                        result=None,
                        error=str(e),
                        output=None,
                    )
                    results[task_id] = result
        
        # Return results in order if deterministic_order enabled
        if self.deterministic_order:
            ordered_results = [
                results.get(task_id) for task_id, _, _, _, _ in tasks
            ]
            return [r for r in ordered_results if r is not None]
        
        return list(results.values())
    
    def _execute_task_with_timeout(
        self,
        task_id: int,
        task_name: str,
        func: Callable,
        args: List,
        kwargs: Dict,
    ) -> TaskResult:
        """
        Execute a single task with timeout handling.
        
        Args:
            task_id: Unique task identifier
            task_name: Human-readable task name
            func: Callable to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            TaskResult with execution details
        """
        start_time = datetime.now()
        result_obj = None
        error_msg = None
        output = None
        status = TaskStatus.COMPLETED
        
        try:
            self._log(f"Executing task {task_id}: {task_name}")
            
            # Execute with timeout using threading
            result_container = []
            error_container = []
            
            def execute_with_capture():
                try:
                    result = func(*args, **kwargs)
                    result_container.append(result)
                except Exception as e:
                    error_container.append(e)
            
            thread = threading.Thread(target=execute_with_capture, daemon=True)
            thread.start()
            thread.join(timeout=self.timeout_per_task)
            
            if thread.is_alive():
                # Task timed out
                status = TaskStatus.TIMEOUT
                error_msg = f"Task exceeded timeout of {self.timeout_per_task}s"
            elif error_container:
                # Task had exception
                status = TaskStatus.FAILED
                error_msg = str(error_container[0])
            else:
                # Task succeeded
                result_obj = result_container[0] if result_container else None
                status = TaskStatus.COMPLETED
        
        except Exception as e:
            status = TaskStatus.FAILED
            error_msg = str(e)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return TaskResult(
            task_id=task_id,
            task_name=task_name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            result=result_obj,
            error=error_msg,
            output=output,
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get execution summary.
        
        Returns:
            Dictionary with execution statistics
        """
        total = self.completed_count + self.failed_count + self.timeout_count
        success_rate = (
            (self.completed_count / total * 100) if total > 0 else 0
        )
        
        return {
            "total_tasks": total,
            "completed": self.completed_count,
            "failed": self.failed_count,
            "timeout": self.timeout_count,
            "success_rate": success_rate,
            "max_workers": self.max_workers,
            "timeout_per_task": self.timeout_per_task,
        }


def print_execution_summary(results: List[TaskResult], title: str = "Parallel Execution Summary"):
    """
    Print a formatted execution summary.
    
    Args:
        results: List of TaskResult objects
        title: Summary title
    """
    if not results:
        return
    
    print()
    print("╔" + "═" * 58 + "╗")
    print(f"║  {title:<54}  ║")
    print("╠" + "═" * 58 + "╣")
    
    total_duration = sum(r.duration for r in results)
    completed = sum(1 for r in results if r.status == TaskStatus.COMPLETED)
    failed = sum(1 for r in results if r.status == TaskStatus.FAILED)
    timeout = sum(1 for r in results if r.status == TaskStatus.TIMEOUT)
    
    print(f"║  Total Tasks: {len(results):<6} Completed: {completed:<6} Failed: {failed:<6}  ║")
    print(f"║  Timeout: {timeout:<6} Total Duration: {total_duration:.2f}s{' ' * 16}║")
    print("╠" + "═" * 58 + "╣")
    
    # Task details
    for result in results:
        status_symbol = {
            TaskStatus.COMPLETED: "✓",
            TaskStatus.FAILED: "✗",
            TaskStatus.TIMEOUT: "⏱",
            TaskStatus.SKIPPED: "⊘",
        }.get(result.status, "?")
        
        status_color = {
            TaskStatus.COMPLETED: "\033[92m",  # Green
            TaskStatus.FAILED: "\033[91m",     # Red
            TaskStatus.TIMEOUT: "\033[93m",    # Yellow
            TaskStatus.SKIPPED: "\033[90m",    # Gray
        }.get(result.status, "")
        
        reset_color = "\033[0m"
        
        line = f"║  {status_color}{status_symbol}{reset_color} Task {result.task_id}: {result.task_name:<30} {result.duration:>6.2f}s  ║"
        print(line)
        
        if result.error:
            error_line = f"║    Error: {result.error[:49]:<49}  ║"
            print(error_line)
    
    print("╚" + "═" * 58 + "╝")
    print()


if __name__ == "__main__":
    # Simple test
    def sample_task(task_id, delay):
        """Sample task for testing."""
        time.sleep(delay)
        return f"Result from task {task_id}"
    
    executor = ParallelExecutor(max_workers=3, verbose=True)
    
    tasks = [
        (1, "Task 1", sample_task, [1, 0.5], {}),
        (2, "Task 2", sample_task, [2, 1.0], {}),
        (3, "Task 3", sample_task, [3, 0.3], {}),
        (4, "Task 4", sample_task, [4, 0.8], {}),
    ]
    
    results = executor.execute_parallel(tasks)
    
    print_execution_summary(results)
    
    summary = executor.get_summary()
    print(f"Success rate: {summary['success_rate']:.1f}%")
