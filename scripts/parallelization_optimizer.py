"""
Parallelization Engine Optimizer for v0.1.45

Improvements to Stages 2-6 parallel execution:
  1. Adaptive worker pool sizing (1-8 workers based on CPU count)
  2. Per-stage timing metrics with SLA enforcement
  3. Worker pool health monitoring
  4. Performance profiling and bottleneck detection
  5. Performance tuning recommendations
  6. Configurable parallelization strategies
  
Author: @kdejo
Date: 2025-10-24
"""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Any
import logging
import threading
from collections import deque
import psutil  # For CPU and memory monitoring

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParallelizationStrategy(Enum):
    """Different parallelization strategies."""
    THREAD_POOL = "thread_pool"      # Best for I/O-bound tasks
    PROCESS_POOL = "process_pool"    # Best for CPU-bound tasks
    HYBRID = "hybrid"                 # Mix of thread and process pools
    SEQUENTIAL = "sequential"         # No parallelization
    ADAPTIVE = "adaptive"             # Choose based on task characteristics


@dataclass
class StageMetrics:
    """Metrics for a single workflow stage."""
    stage_number: int
    stage_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    worker_id: Optional[int] = None
    success: bool = False
    error_message: str = ""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    parallelized: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "stage_number": self.stage_number,
            "stage_name": self.stage_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "worker_id": self.worker_id,
            "success": self.success,
            "error_message": self.error_message,
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
            "parallelized": self.parallelized,
        }


@dataclass
class WorkerPoolMetrics:
    """Metrics for worker pool health and performance."""
    pool_size: int
    strategy: str
    total_tasks: int
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_duration_seconds: float = 0.0
    avg_task_duration_seconds: float = 0.0
    min_task_duration_seconds: float = float('inf')
    max_task_duration_seconds: float = 0.0
    worker_utilization: float = 0.0  # Percentage (0-100)
    throughput_tasks_per_second: float = 0.0
    stage_metrics: List[StageMetrics] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "pool_size": self.pool_size,
            "strategy": self.strategy,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "total_duration_seconds": self.total_duration_seconds,
            "avg_task_duration_seconds": self.avg_task_duration_seconds,
            "min_task_duration_seconds": self.min_task_duration_seconds,
            "max_task_duration_seconds": self.max_task_duration_seconds,
            "worker_utilization": self.worker_utilization,
            "throughput_tasks_per_second": self.throughput_tasks_per_second,
            "stage_metrics": [m.to_dict() for m in self.stage_metrics],
            "bottlenecks": self.bottlenecks,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
        }


@dataclass
class SLATarget:
    """Service Level Agreement target for stages."""
    stage_number: int
    max_duration_seconds: float
    critical: bool = False  # Block workflow if exceeded
    warning_threshold: float = 0.8  # Warn at 80% of max
    
    def check(self, actual_duration: float) -> Tuple[bool, str]:
        """
        Check if SLA is met.
        
        Returns:
            Tuple of (meets_sla, message)
        """
        if actual_duration > self.max_duration_seconds:
            return False, f"SLA exceeded: {actual_duration:.2f}s > {self.max_duration_seconds:.2f}s"
        
        if actual_duration > self.max_duration_seconds * self.warning_threshold:
            return True, f"SLA warning: {actual_duration:.2f}s approaching limit ({self.max_duration_seconds:.2f}s)"
        
        return True, f"SLA met: {actual_duration:.2f}s < {self.max_duration_seconds:.2f}s"


class WorkerPoolOptimizer:
    """Optimize worker pool size and configuration based on system resources."""
    
    @staticmethod
    def get_optimal_worker_count(strategy: ParallelizationStrategy = ParallelizationStrategy.ADAPTIVE) -> int:
        """
        Calculate optimal worker count based on CPU and memory.
        
        Rules:
        - Thread pool (I/O): CPU count * 2
        - Process pool (CPU): CPU count
        - Adaptive: Based on available memory and CPU
        """
        cpu_count = os.cpu_count() or 4
        
        if strategy == ParallelizationStrategy.THREAD_POOL:
            return min(cpu_count * 2, 16)  # Cap at 16
        
        elif strategy == ParallelizationStrategy.PROCESS_POOL:
            return min(cpu_count, 8)  # Cap at 8
        
        elif strategy == ParallelizationStrategy.ADAPTIVE:
            # Adaptive: Consider memory availability
            try:
                mem = psutil.virtual_memory()
                available_gb = mem.available / (1024**3)
                
                if available_gb > 8:
                    return min(cpu_count * 2, 16)
                elif available_gb > 4:
                    return min(cpu_count, 8)
                else:
                    return min(cpu_count // 2, 4)
            except Exception:
                return cpu_count
        
        elif strategy == ParallelizationStrategy.HYBRID:
            return max(2, cpu_count // 2)
        
        return 3  # Default conservative size


class AdaptiveWorkerPool:
    """Manages adaptive worker pool with health monitoring."""
    
    def __init__(self, strategy: ParallelizationStrategy = ParallelizationStrategy.THREAD_POOL,
                 initial_size: Optional[int] = None):
        self.strategy = strategy
        self.size = initial_size or WorkerPoolOptimizer.get_optimal_worker_count(strategy)
        self.executor = self._create_executor()
        self.metrics = WorkerPoolMetrics(
            pool_size=self.size,
            strategy=strategy.value,
            total_tasks=0,
        )
        self.stage_futures = {}
        self.lock = threading.Lock()
    
    def _create_executor(self):
        """Create appropriate executor based on strategy."""
        if self.strategy == ParallelizationStrategy.THREAD_POOL:
            return ThreadPoolExecutor(max_workers=self.size)
        elif self.strategy in (ParallelizationStrategy.PROCESS_POOL, ParallelizationStrategy.HYBRID):
            return ProcessPoolExecutor(max_workers=self.size)
        return ThreadPoolExecutor(max_workers=1)  # Sequential fallback
    
    def submit_stage(self, stage_num: int, stage_name: str, 
                    task_func: Callable, *args, **kwargs) -> Any:
        """
        Submit a stage task to the worker pool.
        
        Returns:
            Future object for the task
        """
        metrics = StageMetrics(
            stage_number=stage_num,
            stage_name=stage_name,
            start_time=datetime.now(),
            parallelized=(self.strategy != ParallelizationStrategy.SEQUENTIAL),
        )
        
        # Wrap task function to capture metrics
        def wrapper():
            try:
                start = time.time()
                result = task_func(*args, **kwargs)
                duration = time.time() - start
                
                metrics.end_time = datetime.now()
                metrics.duration_seconds = duration
                metrics.success = True
                
                return result
            except Exception as e:
                metrics.end_time = datetime.now()
                metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
                metrics.success = False
                metrics.error_message = str(e)
                raise
        
        with self.lock:
            future = self.executor.submit(wrapper)
            self.stage_futures[stage_num] = (future, metrics)
            self.metrics.total_tasks += 1
        
        return future
    
    def wait_all(self) -> Tuple[bool, List[str]]:
        """
        Wait for all submitted tasks to complete.
        
        Returns:
            Tuple of (all_successful, error_messages)
        """
        errors = []
        
        for stage_num, (future, metrics) in self.stage_futures.items():
            try:
                future.result(timeout=300)  # 5 minute timeout per task
                self.metrics.completed_tasks += 1
            except Exception as e:
                errors.append(f"Stage {stage_num}: {str(e)}")
                self.metrics.failed_tasks += 1
            
            # Update metrics
            self.metrics.stage_metrics.append(metrics)
            if metrics.duration_seconds < self.metrics.min_task_duration_seconds:
                self.metrics.min_task_duration_seconds = metrics.duration_seconds
            if metrics.duration_seconds > self.metrics.max_task_duration_seconds:
                self.metrics.max_task_duration_seconds = metrics.duration_seconds
        
        # Calculate aggregated metrics
        if self.metrics.total_tasks > 0:
            self.metrics.avg_task_duration_seconds = (
                sum(m.duration_seconds for m in self.metrics.stage_metrics) / 
                self.metrics.total_tasks
            )
            self.metrics.total_duration_seconds = sum(
                m.duration_seconds for m in self.metrics.stage_metrics
            )
            self.metrics.throughput_tasks_per_second = (
                self.metrics.completed_tasks / max(self.metrics.total_duration_seconds, 0.1)
            )
        
        self._analyze_bottlenecks()
        self._generate_recommendations()
        
        return (len(errors) == 0, errors)
    
    def _analyze_bottlenecks(self):
        """Analyze performance data to identify bottlenecks."""
        if not self.metrics.stage_metrics:
            return
        
        # Find slowest stages
        sorted_stages = sorted(
            self.metrics.stage_metrics,
            key=lambda m: m.duration_seconds,
            reverse=True
        )
        
        avg_duration = self.metrics.avg_task_duration_seconds
        
        for stage in sorted_stages[:3]:  # Top 3 slowest
            if stage.duration_seconds > avg_duration * 1.5:
                self.metrics.bottlenecks.append(
                    f"Stage {stage.stage_number} ({stage.stage_name}): "
                    f"{stage.duration_seconds:.2f}s (50% slower than average)"
                )
    
    def _generate_recommendations(self):
        """Generate performance tuning recommendations."""
        if not self.metrics.stage_metrics:
            return
        
        # Recommendation 1: Worker pool size
        utilization = (self.metrics.completed_tasks / max(self.metrics.total_tasks, 1)) * 100
        self.metrics.worker_utilization = utilization
        
        if utilization < 50:
            self.metrics.recommendations.append(
                f"Worker pool utilization is {utilization:.1f}%. "
                f"Consider reducing pool size from {self.size} to {max(2, self.size // 2)}"
            )
        elif utilization > 90:
            self.metrics.recommendations.append(
                f"Worker pool utilization is {utilization:.1f}%. "
                f"Consider increasing pool size from {self.size} to {self.size + 2}"
            )
        
        # Recommendation 2: Task distribution
        durations = [m.duration_seconds for m in self.metrics.stage_metrics]
        if max(durations) > min(durations) * 3:
            self.metrics.recommendations.append(
                "Uneven task distribution detected. "
                "Some stages are 3x slower than others. "
                "Consider load balancing or task prioritization."
            )
        
        # Recommendation 3: Parallelization strategy
        if self.strategy == ParallelizationStrategy.THREAD_POOL:
            cpu_time = sum(m.cpu_percent for m in self.metrics.stage_metrics) / len(self.metrics.stage_metrics)
            if cpu_time > 80:
                self.metrics.recommendations.append(
                    "High CPU usage detected with thread pool strategy. "
                    "Consider using process pool for CPU-bound tasks."
                )
    
    def shutdown(self):
        """Shutdown the executor pool."""
        self.executor.shutdown(wait=True)


class ParallelizationProfiler:
    """Profile stages to determine optimal parallelization strategy."""
    
    def __init__(self, num_iterations: int = 3):
        self.num_iterations = num_iterations
        self.profile_results = {}
    
    def profile_stage(self, stage_num: int, stage_name: str,
                     task_func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Profile a stage to determine its characteristics.
        
        Returns:
            Profile data including CPU intensity, I/O wait, variability
        """
        times = []
        cpu_samples = []
        
        for i in range(self.num_iterations):
            start_time = time.time()
            try:
                task_func(*args, **kwargs)
            except Exception:
                pass
            duration = time.time() - start_time
            times.append(duration)
            
            if psutil:
                try:
                    cpu_samples.append(psutil.cpu_percent(interval=0.1))
                except Exception:
                    pass
        
        # Analyze results
        avg_duration = sum(times) / len(times) if times else 0
        variability = max(times) - min(times) if times else 0
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        
        profile = {
            "stage_number": stage_num,
            "stage_name": stage_name,
            "avg_duration_seconds": avg_duration,
            "variability_seconds": variability,
            "avg_cpu_percent": avg_cpu,
            "recommended_strategy": self._recommend_strategy(avg_cpu, avg_duration),
            "parallelizable": variability < avg_duration * 0.5,  # Low variability = good for parallelization
        }
        
        self.profile_results[stage_num] = profile
        return profile
    
    def _recommend_strategy(self, avg_cpu: float, duration: float) -> str:
        """Recommend parallelization strategy based on characteristics."""
        if avg_cpu > 70:
            return "process_pool"  # CPU-bound
        elif duration > 5:
            return "thread_pool"   # I/O-bound (longer duration)
        else:
            return "thread_pool"   # Default to thread pool


class ParallelizationSLAManager:
    """Manage and enforce SLA targets for stages."""
    
    DEFAULT_SLAS = {
        2: SLATarget(stage_number=2, max_duration_seconds=30),
        3: SLATarget(stage_number=3, max_duration_seconds=30),
        4: SLATarget(stage_number=4, max_duration_seconds=30),
        5: SLATarget(stage_number=5, max_duration_seconds=30),
        6: SLATarget(stage_number=6, max_duration_seconds=30),
    }
    
    def __init__(self, slas: Optional[Dict[int, SLATarget]] = None):
        self.slas = slas or self.DEFAULT_SLAS.copy()
        self.violations = []
        self.warnings = []
    
    def check_stage_sla(self, stage_num: int, actual_duration: float) -> bool:
        """
        Check if stage meets SLA.
        
        Returns:
            True if SLA met, False if critical violation
        """
        sla = self.slas.get(stage_num)
        if not sla:
            return True  # No SLA defined
        
        met, message = sla.check(actual_duration)
        
        if not met and sla.critical:
            self.violations.append(f"CRITICAL: Stage {stage_num} - {message}")
            return False
        elif not met:
            self.warnings.append(f"WARNING: Stage {stage_num} - {message}")
        
        return True
    
    def check_all_stages(self, metrics: WorkerPoolMetrics) -> bool:
        """Check SLA compliance for all completed stages."""
        all_met = True
        
        for stage_metric in metrics.stage_metrics:
            if not self.check_stage_sla(stage_metric.stage_number, stage_metric.duration_seconds):
                all_met = False
        
        return all_met
    
    def update_sla(self, stage_num: int, new_max_seconds: float, critical: bool = False):
        """Update SLA target for a stage."""
        self.slas[stage_num] = SLATarget(
            stage_number=stage_num,
            max_duration_seconds=new_max_seconds,
            critical=critical,
        )


class ParallelizationDashboard:
    """Generate visualization and reports for parallelization metrics."""
    
    @staticmethod
    def format_metrics_report(metrics: WorkerPoolMetrics) -> str:
        """Format worker pool metrics as readable report."""
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║          PARALLELIZATION PERFORMANCE DASHBOARD                ║
╚═══════════════════════════════════════════════════════════════╝

Pool Configuration
  Strategy:           {metrics.strategy}
  Pool Size:          {metrics.pool_size} workers
  Total Tasks:        {metrics.total_tasks}

Execution Results
  Completed:          {metrics.completed_tasks}/{metrics.total_tasks}
  Failed:             {metrics.failed_tasks}
  Success Rate:       {(metrics.completed_tasks/max(metrics.total_tasks,1)*100):.1f}%

Performance Metrics
  Total Duration:     {metrics.total_duration_seconds:.2f}s
  Average Task:       {metrics.avg_task_duration_seconds:.2f}s
  Fastest Task:       {metrics.min_task_duration_seconds:.2f}s
  Slowest Task:       {metrics.max_task_duration_seconds:.2f}s
  Throughput:         {metrics.throughput_tasks_per_second:.2f} tasks/sec
  Worker Utilization: {metrics.worker_utilization:.1f}%

Stage Breakdown
"""
        for stage_metric in metrics.stage_metrics:
            status = "✓" if stage_metric.success else "✗"
            parallel = "||" if stage_metric.parallelized else "→"
            report += f"  {status} Stage {stage_metric.stage_number:2d} {parallel} {stage_metric.stage_name:30s} {stage_metric.duration_seconds:7.2f}s"
            if stage_metric.error_message:
                report += f" [{stage_metric.error_message}]"
            report += "\n"
        
        if metrics.bottlenecks:
            report += "\nBottlenecks Detected:\n"
            for bottleneck in metrics.bottlenecks:
                report += f"  ⚠ {bottleneck}\n"
        
        if metrics.recommendations:
            report += "\nPerformance Recommendations:\n"
            for rec in metrics.recommendations:
                report += f"  💡 {rec}\n"
        
        report += f"\nReport Generated: {metrics.timestamp}\n"
        return report


# Example usage and configuration
PARALLELIZATION_CONFIG = {
    "strategy": ParallelizationStrategy.ADAPTIVE,
    "stages": [2, 3, 4, 5, 6],  # Stages to parallelize
    "sla_targets": {
        2: 30,  # Stage 2: max 30 seconds
        3: 30,
        4: 30,
        5: 30,
        6: 30,
    },
    "enable_profiling": True,
    "enable_monitoring": True,
    "metrics_output": "./.workflow_stats/parallelization_metrics.json",
}


if __name__ == "__main__":
    # Example: Run parallelization optimizer
    print("Parallelization Engine Optimizer")
    print("=" * 60)
    
    # Calculate optimal worker count
    for strategy in ParallelizationStrategy:
        if strategy != ParallelizationStrategy.SEQUENTIAL:
            optimal = WorkerPoolOptimizer.get_optimal_worker_count(strategy)
            print(f"\n{strategy.value.upper()}:")
            print(f"  Optimal workers: {optimal}")
    
    # Create adaptive pool
    print(f"\nCreating adaptive worker pool...")
    pool = AdaptiveWorkerPool(strategy=ParallelizationStrategy.ADAPTIVE)
    print(f"  Strategy: {pool.strategy.value}")
    print(f"  Pool size: {pool.size}")
    print(f"  Executor: {type(pool.executor).__name__}")
