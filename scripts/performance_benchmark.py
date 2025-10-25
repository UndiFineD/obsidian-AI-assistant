"""
Performance Benchmarking Framework for v0.1.44

Comprehensive performance measurement, analysis, and optimization system for workflow lanes.

Components:
    - BenchmarkSuite: Execute performance tests across lanes
    - PerformanceAnalyzer: Analyze and compare performance metrics
    - SLAValidator: Validate SLA compliance for each lane
    - OptimizationRecommender: Generate optimization suggestions
    - MetricsCollector: Real-time metrics collection
    - ReportGenerator: HTML dashboard and CSV reports

Usage:
    python scripts/performance_benchmark.py run --lane standard --iterations 10
    python scripts/performance_benchmark.py analyze --output-format html
    python scripts/performance_benchmark.py validate-sla --lane heavy
    python scripts/performance_benchmark.py optimize --lane docs

Author: v0.1.44 Enhancement Cycle
Version: 1.0.0
"""

import argparse
import csv
import json
import logging
import statistics
import subprocess
import threading
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

# ============================================================================
# Configuration & Constants
# ============================================================================

RESULTS_DIR = Path(".benchmark_results")
METRICS_FILE = RESULTS_DIR / "metrics.json"
SLA_CONFIG = {
    "docs": {
        "target_time": 300,  # 5 minutes
        "p95_time": 400,  # 95th percentile
        "p99_time": 500,  # 99th percentile
        "memory_max": 512,  # MB
        "cpu_avg": 30,  # Percent
    },
    "standard": {
        "target_time": 900,  # 15 minutes
        "p95_time": 1200,
        "p99_time": 1500,
        "memory_max": 1024,
        "cpu_avg": 50,
    },
    "heavy": {
        "target_time": 1200,  # 20 minutes
        "p95_time": 1500,
        "p99_time": 1800,
        "memory_max": 2048,
        "cpu_avg": 70,
    },
}

# ============================================================================
# Enums
# ============================================================================


class LaneType(Enum):
    """Workflow lane types."""

    DOCS = "docs"
    STANDARD = "standard"
    HEAVY = "heavy"


class MetricType(Enum):
    """Performance metric types."""

    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CHECKPOINT_TIME = "checkpoint_time"
    RECOVERY_TIME = "recovery_time"


class BenchmarkStatus(Enum):
    """Benchmark execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class MetricSnapshot:
    """Single performance metric measurement."""

    timestamp: str
    metric_type: str
    lane: str
    value: float
    unit: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Complete benchmark execution result."""

    benchmark_id: str
    lane: str
    duration: float
    iterations: int
    start_time: str
    end_time: str
    metrics: Dict[str, List[float]]
    status: str
    error_message: Optional[str] = None
    system_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SLAViolation:
    """SLA compliance violation record."""

    lane: str
    metric: str
    threshold: float
    actual_value: float
    severity: str  # warning, error, critical
    timestamp: str


@dataclass
class OptimizationSuggestion:
    """Optimization recommendation."""

    title: str
    description: str
    affected_metric: str
    estimated_improvement: float  # Percentage
    effort_level: str  # low, medium, high
    priority: int  # 1-5, where 5 is highest
    implementation_steps: List[str]


# ============================================================================
# Metrics Collector
# ============================================================================


class MetricsCollector:
    """Real-time performance metrics collection."""

    def __init__(self):
        self.metrics: List[MetricSnapshot] = []
        self.process = psutil.Process()
        self.lock = threading.Lock()
        self.monitoring = False

    def start_monitoring(self):
        """Start background metrics collection."""
        self.monitoring = True
        thread = threading.Thread(target=self._collect_loop, daemon=True)
        thread.start()

    def stop_monitoring(self) -> Dict[str, List[float]]:
        """Stop monitoring and return aggregated metrics."""
        self.monitoring = False
        time.sleep(0.5)  # Brief pause to finish last collection
        return self.aggregate_metrics()

    def _collect_loop(self):
        """Background collection loop."""
        try:
            while self.monitoring:
                self._collect_snapshot()
                time.sleep(1)  # Collect every second
        except Exception as e:
            logging.error(f"Metrics collection error: {e}")

    def _collect_snapshot(self):
        """Collect single metrics snapshot."""
        try:
            with self.lock:
                # CPU usage
                cpu_percent = self.process.cpu_percent(interval=0.1)
                self.metrics.append(
                    MetricSnapshot(
                        timestamp=datetime.now().isoformat(),
                        metric_type=MetricType.CPU_USAGE.value,
                        lane="current",
                        value=cpu_percent,
                        unit="percent",
                    )
                )

                # Memory usage
                mem_info = self.process.memory_info()
                mem_mb = mem_info.rss / (1024 * 1024)
                self.metrics.append(
                    MetricSnapshot(
                        timestamp=datetime.now().isoformat(),
                        metric_type=MetricType.MEMORY_USAGE.value,
                        lane="current",
                        value=mem_mb,
                        unit="MB",
                    )
                )

                # I/O counters (disk operations)
                try:
                    io_counters = self.process.io_counters()
                    self.metrics.append(
                        MetricSnapshot(
                            timestamp=datetime.now().isoformat(),
                            metric_type=MetricType.DISK_IO.value,
                            lane="current",
                            value=io_counters.write_bytes + io_counters.read_bytes,
                            unit="bytes",
                        )
                    )
                except (AttributeError, OSError):
                    pass  # Not available on all systems
        except Exception as e:
            logging.debug(f"Snapshot collection error: {e}")

    def aggregate_metrics(self) -> Dict[str, List[float]]:
        """Aggregate collected metrics by type."""
        aggregated = defaultdict(list)

        with self.lock:
            for metric in self.metrics:
                key = metric.metric_type
                aggregated[key].append(metric.value)

        return dict(aggregated)


# ============================================================================
# Benchmark Suite
# ============================================================================


class BenchmarkSuite:
    """Execute performance benchmarks for workflow lanes."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.collector = MetricsCollector()
        RESULTS_DIR.mkdir(exist_ok=True)

    def run_benchmark(
        self, lane: LaneType, iterations: int = 5, timeout: Optional[int] = None
    ) -> BenchmarkResult:
        """Run benchmark for specified lane."""

        logging.info(f"Starting benchmark for lane: {lane.value}")
        benchmark_id = f"{lane.value}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        try:
            # Start metrics collection
            self.collector.start_monitoring()

            # Execute workflow iterations
            execution_times = []
            for i in range(iterations):
                logging.info(f"Iteration {i + 1}/{iterations}")
                exec_time = self._execute_workflow(lane, timeout)
                execution_times.append(exec_time)
                time.sleep(1)  # Cool down between iterations

            # Stop metrics collection
            metrics_dict = self.collector.stop_monitoring()

            # Add execution times
            metrics_dict[MetricType.EXECUTION_TIME.value] = execution_times

            # Create result
            result = BenchmarkResult(
                benchmark_id=benchmark_id,
                lane=lane.value,
                duration=float((datetime.now() - start_time).total_seconds()),
                iterations=iterations,
                start_time=start_time.isoformat(),
                end_time=datetime.now().isoformat(),
                metrics=metrics_dict,
                status=BenchmarkStatus.COMPLETED.value,
                system_info=self._get_system_info(),
            )

            self.results.append(result)
            self._save_result(result)

            logging.info(f"✓ Benchmark completed: {benchmark_id}")
            return result

        except Exception as e:
            logging.error(f"Benchmark failed: {e}", exc_info=True)
            return BenchmarkResult(
                benchmark_id=benchmark_id,
                lane=lane.value,
                duration=float((datetime.now() - start_time).total_seconds()),
                iterations=iterations,
                start_time=start_time.isoformat(),
                end_time=datetime.now().isoformat(),
                metrics={},
                status=BenchmarkStatus.FAILED.value,
                error_message=str(e),
            )

    def _execute_workflow(self, lane: LaneType, timeout: Optional[int]) -> float:
        """Execute workflow and measure execution time."""
        try:
            start = time.time()

            # Execute workflow with lane
            cmd = [
                "python",
                "scripts/workflow.py",
                "--lane",
                lane.value,
                "--change-id",
                f"benchmark-{lane.value}-{int(time.time())}",
            ]

            timeout_val = timeout or (
                300
                if lane == LaneType.DOCS
                else 900 if lane == LaneType.STANDARD else 1200
            )

            result = subprocess.run(
                cmd, timeout=timeout_val, capture_output=True, text=True
            )

            exec_time = time.time() - start

            if result.returncode != 0:
                logging.warning(f"Workflow failed: {result.stderr[:200]}")

            return exec_time

        except subprocess.TimeoutExpired:
            logging.warning(f"Workflow timeout after {timeout} seconds")
            return float(timeout or 1200)
        except Exception as e:
            logging.error(f"Workflow execution error: {e}")
            raise

    def _get_system_info(self) -> Dict[str, Any]:
        """Collect system information."""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total": psutil.virtual_memory().total / (1024**3),  # GB
            "memory_available": psutil.virtual_memory().available / (1024**3),
            "disk_total": psutil.disk_usage("/").total / (1024**3),
            "disk_free": psutil.disk_usage("/").free / (1024**3),
            "timestamp": datetime.now().isoformat(),
        }

    def _save_result(self, result: BenchmarkResult):
        """Save result to file."""
        try:
            results_list = []
            if METRICS_FILE.exists():
                with open(METRICS_FILE) as f:
                    results_list = json.load(f)

            results_list.append(
                {**asdict(result), "metrics": {k: v for k, v in result.metrics.items()}}
            )

            with open(METRICS_FILE, "w") as f:
                json.dump(results_list, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save result: {e}")


# ============================================================================
# Performance Analyzer
# ============================================================================


class PerformanceAnalyzer:
    """Analyze and compare performance metrics."""

    def __init__(self):
        self.results: List[BenchmarkResult] = self._load_results()

    def _load_results(self) -> List[BenchmarkResult]:
        """Load benchmark results from storage."""
        try:
            if METRICS_FILE.exists():
                with open(METRICS_FILE) as f:
                    data = json.load(f)
                    return [BenchmarkResult(**r) for r in data]
        except Exception as e:
            logging.error(f"Failed to load results: {e}")
        return []

    def analyze_lane(self, lane: LaneType) -> Dict[str, Any]:
        """Analyze performance metrics for a lane."""
        lane_results = [r for r in self.results if r.lane == lane.value]

        if not lane_results:
            return {}

        analysis = {
            "lane": lane.value,
            "total_runs": len(lane_results),
            "metrics_analysis": {},
        }

        # Analyze each metric type
        for metric_type in MetricType:
            metric_key = metric_type.value
            all_values = []

            for result in lane_results:
                if metric_key in result.metrics:
                    all_values.extend(result.metrics[metric_key])

            if all_values:
                analysis["metrics_analysis"][metric_key] = {
                    "mean": statistics.mean(all_values),
                    "median": statistics.median(all_values),
                    "stdev": statistics.stdev(all_values) if len(all_values) > 1 else 0,
                    "min": min(all_values),
                    "max": max(all_values),
                    "p95": self._percentile(all_values, 95),
                    "p99": self._percentile(all_values, 99),
                    "samples": len(all_values),
                }

        return analysis

    def compare_lanes(self) -> Dict[str, Any]:
        """Compare performance across all lanes."""
        comparison = {}

        for lane_type in LaneType:
            comparison[lane_type.value] = self.analyze_lane(lane_type)

        return comparison

    def get_trends(self, lane: LaneType, metric: str, window: int = 10) -> List[float]:
        """Get performance trend for metric."""
        lane_results = [r for r in self.results if r.lane == lane.value]
        lane_results.sort(key=lambda r: r.start_time)

        trends = []
        for result in lane_results[-window:]:
            if metric in result.metrics and result.metrics[metric]:
                trends.append(statistics.mean(result.metrics[metric]))

        return trends

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        sorted_data = sorted(data)
        index = (percentile / 100) * len(sorted_data)
        return sorted_data[int(index)]


# ============================================================================
# SLA Validator
# ============================================================================


class SLAValidator:
    """Validate SLA compliance for workflow lanes."""

    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer
        self.violations: List[SLAViolation] = []

    def validate_lane(self, lane: LaneType) -> Tuple[bool, List[SLAViolation]]:
        """Validate SLA compliance for lane."""
        self.violations = []
        analysis = self.analyzer.analyze_lane(lane)
        sla = SLA_CONFIG.get(lane.value, {})

        if not analysis or not sla:
            return True, []

        # Check execution time
        if MetricType.EXECUTION_TIME.value in analysis["metrics_analysis"]:
            exec_stats = analysis["metrics_analysis"][MetricType.EXECUTION_TIME.value]

            # Check mean vs target
            if exec_stats["mean"] > sla["target_time"]:
                self.violations.append(
                    SLAViolation(
                        lane=lane.value,
                        metric="execution_time_mean",
                        threshold=sla["target_time"],
                        actual_value=exec_stats["mean"],
                        severity="warning",
                        timestamp=datetime.now().isoformat(),
                    )
                )

            # Check p95
            if exec_stats["p95"] > sla["p95_time"]:
                self.violations.append(
                    SLAViolation(
                        lane=lane.value,
                        metric="execution_time_p95",
                        threshold=sla["p95_time"],
                        actual_value=exec_stats["p95"],
                        severity="error",
                        timestamp=datetime.now().isoformat(),
                    )
                )

            # Check p99
            if exec_stats["p99"] > sla["p99_time"]:
                self.violations.append(
                    SLAViolation(
                        lane=lane.value,
                        metric="execution_time_p99",
                        threshold=sla["p99_time"],
                        actual_value=exec_stats["p99"],
                        severity="critical",
                        timestamp=datetime.now().isoformat(),
                    )
                )

        # Check memory usage
        if MetricType.MEMORY_USAGE.value in analysis["metrics_analysis"]:
            mem_stats = analysis["metrics_analysis"][MetricType.MEMORY_USAGE.value]
            if mem_stats["max"] > sla["memory_max"]:
                self.violations.append(
                    SLAViolation(
                        lane=lane.value,
                        metric="memory_max",
                        threshold=sla["memory_max"],
                        actual_value=mem_stats["max"],
                        severity="warning",
                        timestamp=datetime.now().isoformat(),
                    )
                )

        # Check CPU usage
        if MetricType.CPU_USAGE.value in analysis["metrics_analysis"]:
            cpu_stats = analysis["metrics_analysis"][MetricType.CPU_USAGE.value]
            if cpu_stats["mean"] > sla["cpu_avg"]:
                self.violations.append(
                    SLAViolation(
                        lane=lane.value,
                        metric="cpu_avg",
                        threshold=sla["cpu_avg"],
                        actual_value=cpu_stats["mean"],
                        severity="warning",
                        timestamp=datetime.now().isoformat(),
                    )
                )

        is_compliant = len(self.violations) == 0
        return is_compliant, self.violations


# ============================================================================
# Optimization Recommender
# ============================================================================


class OptimizationRecommender:
    """Generate optimization suggestions based on performance analysis."""

    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer

    def get_recommendations(self, lane: LaneType) -> List[OptimizationSuggestion]:
        """Get optimization recommendations for lane."""
        suggestions = []
        analysis = self.analyzer.analyze_lane(lane)

        if not analysis:
            return []

        # High execution time
        if MetricType.EXECUTION_TIME.value in analysis["metrics_analysis"]:
            exec_stats = analysis["metrics_analysis"][MetricType.EXECUTION_TIME.value]
            if exec_stats["mean"] > SLA_CONFIG[lane.value]["target_time"] * 0.8:
                suggestions.append(
                    OptimizationSuggestion(
                        title="Reduce Execution Time",
                        description="Execution time is approaching or exceeding target. Consider parallelization or optimization.",
                        affected_metric="execution_time",
                        estimated_improvement=20,
                        effort_level="medium",
                        priority=5,
                        implementation_steps=[
                            "Profile workflow execution with cProfile",
                            "Identify bottleneck operations",
                            "Parallelize independent tasks",
                            "Implement caching for expensive operations",
                            "Re-run benchmarks to verify improvement",
                        ],
                    )
                )

        # High memory usage
        if MetricType.MEMORY_USAGE.value in analysis["metrics_analysis"]:
            mem_stats = analysis["metrics_analysis"][MetricType.MEMORY_USAGE.value]
            if mem_stats["max"] > SLA_CONFIG[lane.value]["memory_max"] * 0.7:
                suggestions.append(
                    OptimizationSuggestion(
                        title="Optimize Memory Usage",
                        description="Memory usage is high. Consider streaming data or reducing data retention.",
                        affected_metric="memory_usage",
                        estimated_improvement=30,
                        effort_level="high",
                        priority=4,
                        implementation_steps=[
                            "Use memory_profiler to identify memory leaks",
                            "Implement streaming for large datasets",
                            "Use generators instead of list comprehensions",
                            "Clear intermediate results after processing",
                            "Profile memory after changes",
                        ],
                    )
                )

        # High CPU usage
        if MetricType.CPU_USAGE.value in analysis["metrics_analysis"]:
            cpu_stats = analysis["metrics_analysis"][MetricType.CPU_USAGE.value]
            if cpu_stats["mean"] > SLA_CONFIG[lane.value]["cpu_avg"] * 0.8:
                suggestions.append(
                    OptimizationSuggestion(
                        title="Reduce CPU Utilization",
                        description="CPU usage is high. Consider optimizing algorithms or using compiled extensions.",
                        affected_metric="cpu_usage",
                        estimated_improvement=25,
                        effort_level="high",
                        priority=4,
                        implementation_steps=[
                            "Profile CPU usage with py-spy",
                            "Identify hot functions",
                            "Optimize algorithms (reduce complexity)",
                            "Consider using NumPy or compiled extensions",
                            "Implement async operations where applicable",
                        ],
                    )
                )

        # Variable performance
        if MetricType.EXECUTION_TIME.value in analysis["metrics_analysis"]:
            exec_stats = analysis["metrics_analysis"][MetricType.EXECUTION_TIME.value]
            if exec_stats["stdev"] > exec_stats["mean"] * 0.2:  # >20% variance
                suggestions.append(
                    OptimizationSuggestion(
                        title="Stabilize Performance",
                        description="Performance shows high variability. Identify and eliminate sources of variance.",
                        affected_metric="execution_time",
                        estimated_improvement=40,
                        effort_level="high",
                        priority=3,
                        implementation_steps=[
                            "Monitor system resources during runs",
                            "Identify external factors (I/O, network)",
                            "Isolate environment for testing",
                            "Implement consistent scheduling",
                            "Add checkpoints for recovery",
                        ],
                    )
                )

        # Add lane-specific suggestions
        if lane == LaneType.DOCS:
            suggestions.append(
                OptimizationSuggestion(
                    title="Optimize Documentation Build",
                    description="Consider caching documentation and incremental builds.",
                    affected_metric="execution_time",
                    estimated_improvement=50,
                    effort_level="low",
                    priority=2,
                    implementation_steps=[
                        "Implement doc cache system",
                        "Support incremental builds",
                        "Parallelize doc generation",
                        "Use static site generation",
                    ],
                )
            )
        elif lane == LaneType.STANDARD:
            suggestions.append(
                OptimizationSuggestion(
                    title="Parallel Test Execution",
                    description="Run tests in parallel to reduce execution time.",
                    affected_metric="execution_time",
                    estimated_improvement=60,
                    effort_level="medium",
                    priority=3,
                    implementation_steps=[
                        "Install pytest-xdist",
                        "Mark independent tests",
                        "Configure parallel workers",
                        "Verify test isolation",
                        "Monitor resource usage",
                    ],
                )
            )
        elif lane == LaneType.HEAVY:
            suggestions.append(
                OptimizationSuggestion(
                    title="Distributed Testing",
                    description="Distribute tests across multiple machines.",
                    affected_metric="execution_time",
                    estimated_improvement=70,
                    effort_level="high",
                    priority=2,
                    implementation_steps=[
                        "Set up distributed test infrastructure",
                        "Implement test distribution",
                        "Balance load across workers",
                        "Monitor distributed execution",
                        "Implement failure recovery",
                    ],
                )
            )

        return suggestions


# ============================================================================
# Report Generator
# ============================================================================


class ReportGenerator:
    """Generate performance reports and dashboards."""

    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer
        RESULTS_DIR.mkdir(exist_ok=True)

    def generate_html_report(self, output_path: Optional[Path] = None) -> str:
        """Generate HTML dashboard report."""
        output_path = output_path or RESULTS_DIR / "performance_dashboard.html"

        comparison = self.analyzer.compare_lanes()

        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Performance Benchmark Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .lane-section { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: inline-block; width: 30%; margin: 10px; padding: 10px; background: #f9f9f9; border-left: 4px solid #007bff; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric-label { font-size: 12px; color: #666; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f0f0f0; font-weight: bold; }
        .status-pass { color: green; }
        .status-fail { color: red; }
        .chart { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Benchmark Dashboard</h1>
        <p>Generated: {timestamp}</p>
"""

        for lane, analysis in comparison.items():
            if not analysis:
                continue

            html += f"""
    <div class="lane-section">
        <h2>{lane.upper()} Lane</h2>
        <p>Total Runs: {analysis.get("total_runs", 0)}</p>
"""

            # Metrics
            for metric_name, stats in analysis.get("metrics_analysis", {}).items():
                html += f"""
        <div class="metric">
            <div class="metric-value">{stats["mean"]:.2f}</div>
            <div class="metric-label">{metric_name}</div>
            <small>Min: {stats["min"]:.2f}, Max: {stats["max"]:.2f}, StDev: {stats["stdev"]:.2f}</small>
        </div>
"""

            # Detailed metrics table
            html += """
        <table>
            <tr>
                <th>Metric</th>
                <th>Mean</th>
                <th>Median</th>
                <th>P95</th>
                <th>P99</th>
                <th>Min</th>
                <th>Max</th>
                <th>StDev</th>
            </tr>
"""

            for metric_name, stats in analysis.get("metrics_analysis", {}).items():
                html += f"""
            <tr>
                <td>{metric_name}</td>
                <td>{stats["mean"]:.2f}</td>
                <td>{stats["median"]:.2f}</td>
                <td>{stats["p95"]:.2f}</td>
                <td>{stats["p99"]:.2f}</td>
                <td>{stats["min"]:.2f}</td>
                <td>{stats["max"]:.2f}</td>
                <td>{stats["stdev"]:.2f}</td>
            </tr>
"""

            html += """
        </table>
    </div>
"""

        html += """
    </div>
</body>
</html>
"""

        html = html.format(timestamp=datetime.now().isoformat())

        with open(output_path, "w") as f:
            f.write(html)

        logging.info(f"HTML report saved: {output_path}")
        return str(output_path)

    def generate_csv_report(self, output_path: Optional[Path] = None):
        """Generate CSV metrics export."""
        output_path = output_path or RESULTS_DIR / "performance_metrics.csv"

        try:
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "Benchmark ID",
                        "Lane",
                        "Start Time",
                        "Duration",
                        "Iterations",
                        "Status",
                        "Exec Time Mean",
                        "Exec Time P95",
                        "Memory Max",
                        "CPU Mean",
                    ]
                )

                for result in self.analyzer.results:
                    exec_times = result.metrics.get(MetricType.EXECUTION_TIME.value, [])
                    mem_usage = result.metrics.get(MetricType.MEMORY_USAGE.value, [])
                    cpu_usage = result.metrics.get(MetricType.CPU_USAGE.value, [])

                    exec_mean = statistics.mean(exec_times) if exec_times else 0
                    exec_p95 = self._percentile(exec_times, 95) if exec_times else 0
                    mem_max = max(mem_usage) if mem_usage else 0
                    cpu_mean = statistics.mean(cpu_usage) if cpu_usage else 0

                    writer.writerow(
                        [
                            result.benchmark_id,
                            result.lane,
                            result.start_time,
                            result.duration,
                            result.iterations,
                            result.status,
                            f"{exec_mean:.2f}",
                            f"{exec_p95:.2f}",
                            f"{mem_max:.2f}",
                            f"{cpu_mean:.2f}",
                        ]
                    )

            logging.info(f"CSV report saved: {output_path}")
        except Exception as e:
            logging.error(f"Failed to generate CSV: {e}")

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * len(sorted_data)
        return sorted_data[int(index)]


# ============================================================================
# Main CLI Interface
# ============================================================================


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    """Main entry point."""
    setup_logging()

    parser = argparse.ArgumentParser(description="Performance Benchmarking Framework")
    parser.add_argument(
        "action",
        choices=["run", "analyze", "validate-sla", "optimize", "report"],
        help="Action to perform",
    )
    parser.add_argument(
        "--lane", choices=["docs", "standard", "heavy"], help="Workflow lane"
    )
    parser.add_argument(
        "--iterations", type=int, default=5, help="Number of iterations"
    )
    parser.add_argument("--timeout", type=int, help="Execution timeout in seconds")
    parser.add_argument(
        "--output-format",
        choices=["html", "csv", "both"],
        default="html",
        help="Report output format",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.action == "run":
        if not args.lane:
            logging.error("--lane required for 'run' action")
            return

        suite = BenchmarkSuite()
        lane = LaneType[args.lane.upper()]
        result = suite.run_benchmark(lane, args.iterations, args.timeout)

        print("\n✓ Benchmark Result:")
        print(f"  Lane: {result.lane}")
        print(f"  Status: {result.status}")
        print(f"  Duration: {result.duration:.2f}s")
        print(f"  Iterations: {result.iterations}")

    elif args.action == "analyze":
        analyzer = PerformanceAnalyzer()

        if args.lane:
            lane = LaneType[args.lane.upper()]
            analysis = analyzer.analyze_lane(lane)
            print(json.dumps(analysis, indent=2))
        else:
            comparison = analyzer.compare_lanes()
            print(json.dumps(comparison, indent=2))

    elif args.action == "validate-sla":
        if not args.lane:
            logging.error("--lane required for 'validate-sla' action")
            return

        analyzer = PerformanceAnalyzer()
        validator = SLAValidator(analyzer)
        lane = LaneType[args.lane.upper()]

        is_compliant, violations = validator.validate_lane(lane)

        print(f"\n{'✓' if is_compliant else '✗'} SLA Status: {lane.value}")
        print(f"  Compliant: {is_compliant}")

        if violations:
            print(f"  Violations: {len(violations)}")
            for v in violations:
                print(
                    f"    - {v.metric}: {v.actual_value:.2f} > {v.threshold} ({v.severity})"
                )

    elif args.action == "optimize":
        if not args.lane:
            logging.error("--lane required for 'optimize' action")
            return

        analyzer = PerformanceAnalyzer()
        recommender = OptimizationRecommender(analyzer)
        lane = LaneType[args.lane.upper()]

        suggestions = recommender.get_recommendations(lane)

        print(f"\n📊 Optimization Suggestions for {lane.value}:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion.title} (Priority: {suggestion.priority}/5)")
            print(f"   Description: {suggestion.description}")
            print(f"   Estimated Improvement: {suggestion.estimated_improvement}%")
            print(f"   Effort Level: {suggestion.effort_level}")
            print("   Steps:")
            for step in suggestion.implementation_steps:
                print(f"     - {step}")

    elif args.action == "report":
        analyzer = PerformanceAnalyzer()
        generator = ReportGenerator(analyzer)

        if args.output_format in ["html", "both"]:
            html_path = generator.generate_html_report()
            print(f"✓ HTML report: {html_path}")

        if args.output_format in ["csv", "both"]:
            generator.generate_csv_report()
            print("✓ CSV report: .benchmark_results/performance_metrics.csv")


if __name__ == "__main__":
    main()
