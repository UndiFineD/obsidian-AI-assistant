# Performance Benchmarking Framework Guide

**Version**: 0.1.44  
**Status**: Production Ready  
**Last Updated**: October 24, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Running Benchmarks](#running-benchmarks)
4. [Analyzing Results](#analyzing-results)
5. [SLA Validation](#sla-validation)
6. [Optimization](#optimization)
7. [Reports & Dashboards](#reports--dashboards)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)

---

## Overview

### What is Performance Benchmarking?

The **Performance Benchmarking Framework** provides comprehensive capabilities to measure, analyze, and optimize workflow performance across lanes:

1. **Benchmark Execution** - Run workflows repeatedly with metrics collection
2. **Performance Analysis** - Statistical analysis of metrics
3. **SLA Validation** - Verify compliance with performance targets
4. **Optimization Recommendations** - AI-driven suggestions for improvements
5. **Reporting** - HTML dashboards and CSV exports

### Why It Matters

**Goals**:
- ✅ **SLA Compliance** - Meet performance targets for each lane
- ✅ **Regression Detection** - Catch performance degradation early
- ✅ **Optimization** - Identify and eliminate bottlenecks
- ✅ **Capacity Planning** - Plan for growth and scaling
- ✅ **Cost Optimization** - Run efficiently within resource constraints

### Performance Targets (SLA)

| Metric | DOCS Lane | STANDARD Lane | HEAVY Lane |
|--------|-----------|---------------|-----------|
| Target Time | 5 min | 15 min | 20 min |
| P95 Latency | 6:40 | 20 min | 25 min |
| P99 Latency | 8:20 | 25 min | 30 min |
| Memory Max | 512 MB | 1 GB | 2 GB |
| CPU Avg | 30% | 50% | 70% |

---

## Quick Start

### Run Single Benchmark

```bash
# Benchmark DOCS lane (5 iterations)
python scripts/performance_benchmark.py run --lane docs --iterations 5

# Benchmark STANDARD lane with timeout
python scripts/performance_benchmark.py run --lane standard --iterations 10 --timeout 1200

# Benchmark HEAVY lane (10 iterations, 30 min timeout)
python scripts/performance_benchmark.py run --lane heavy --iterations 10 --timeout 1800
```

### Analyze Results

```bash
# Quick analysis for all lanes
python scripts/performance_benchmark.py analyze

# Detailed analysis for specific lane
python scripts/performance_benchmark.py analyze --lane standard
```

### Validate SLA

```bash
# Check SLA compliance for lane
python scripts/performance_benchmark.py validate-sla --lane standard

# Check all lanes
for lane in docs standard heavy; do
    python scripts/performance_benchmark.py validate-sla --lane $lane
done
```

### Get Optimization Suggestions

```bash
# Get recommendations for lane
python scripts/performance_benchmark.py optimize --lane standard

# Get recommendations for all lanes
for lane in docs standard heavy; do
    python scripts/performance_benchmark.py optimize --lane $lane
done
```

### Generate Reports

```bash
# Generate HTML dashboard
python scripts/performance_benchmark.py report --output-format html

# Generate CSV export
python scripts/performance_benchmark.py report --output-format csv

# Generate both
python scripts/performance_benchmark.py report --output-format both
```

---

## Running Benchmarks

### Benchmark Execution

```bash
python scripts/performance_benchmark.py run \
    --lane standard \
    --iterations 10 \
    --timeout 1200
```

**What Happens**:
1. Workflow executes for specified lane
2. Metrics collected in real-time:
   - Execution time
   - CPU usage (%)
   - Memory usage (MB)
   - Disk I/O (bytes)
   - Network I/O (bytes)
3. Iteration repeated N times
4. Results saved to `.benchmark_results/metrics.json`
5. Summary displayed with mean/median/percentiles

### Benchmark Configuration

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| `--lane` | docs, standard, heavy | Required | Workflow lane |
| `--iterations` | 1-100 | 5 | Number of repetitions |
| `--timeout` | 60-3600 | Lane default | Execution timeout (seconds) |
| `--verbose` | flag | false | Detailed logging |

### Timeout Defaults (if not specified)

```
DOCS Lane:     300 seconds (5 minutes)
STANDARD Lane: 900 seconds (15 minutes)
HEAVY Lane:    1200 seconds (20 minutes)
```

### Example: Multi-Lane Benchmarking

```bash
#!/bin/bash
# Run benchmarks for all lanes

echo "Starting multi-lane benchmarking..."

for lane in docs standard heavy; do
    echo "Benchmarking $lane lane..."
    python scripts/performance_benchmark.py run \
        --lane $lane \
        --iterations 10 \
        --timeout 1800
    
    # Cool down between lanes
    sleep 60
done

echo "Benchmarking complete!"
```

---

## Analyzing Results

### Quick Analysis

```bash
python scripts/performance_benchmark.py analyze --lane docs
```

**Output**:
```json
{
  "lane": "docs",
  "total_runs": 5,
  "metrics_analysis": {
    "execution_time": {
      "mean": 285.5,
      "median": 280.2,
      "stdev": 15.3,
      "min": 270.1,
      "max": 310.5,
      "p95": 300.2,
      "p99": 308.5,
      "samples": 50
    },
    "memory_usage": {
      "mean": 256.3,
      "median": 250.1,
      ...
    },
    ...
  }
}
```

### Understanding Metrics

| Metric | Description | Usage |
|--------|-------------|-------|
| **mean** | Average value | Overall performance |
| **median** | Middle value | Typical case (robust) |
| **stdev** | Standard deviation | Performance variability |
| **p95** | 95th percentile | Worst 5% of cases |
| **p99** | 99th percentile | Worst 1% of cases |
| **min/max** | Range | Best/worst case |

### Comparative Analysis

```bash
# Compare all lanes side-by-side
python scripts/performance_benchmark.py analyze
```

**Analysis Questions**:
- Which lane is fastest?
- What's the variability in each lane?
- Are p95/p99 metrics within SLA?
- What's the memory/CPU footprint?

### Trend Analysis

```python
from scripts.performance_benchmark import PerformanceAnalyzer, LaneType

analyzer = PerformanceAnalyzer()

# Get last 10 benchmarks trend
trends = analyzer.get_trends(LaneType.STANDARD, "execution_time", window=10)

# Analyze trends
import statistics
trend_mean = statistics.mean(trends)
trend_stdev = statistics.stdev(trends)

print(f"Recent mean: {trend_mean:.2f}s")
print(f"Variability: {trend_stdev:.2f}s")

# Detect degradation
if len(trends) > 1:
    recent = trends[-1]
    previous = statistics.mean(trends[:-1])
    degradation = ((recent - previous) / previous) * 100
    
    if degradation > 10:
        print(f"⚠️  Performance degradation: {degradation:.1f}%")
```

---

## SLA Validation

### Check SLA Compliance

```bash
python scripts/performance_benchmark.py validate-sla --lane standard
```

**Output**:
```
✓ SLA Status: standard
  Compliant: True
```

Or if violations exist:

```
✗ SLA Status: standard
  Compliant: False
  Violations: 3
    - execution_time_mean: 920.50 > 900 (warning)
    - execution_time_p95: 1250.30 > 1200 (error)
    - memory_max: 1100.50 > 1024 (warning)
```

### SLA Thresholds

```python
SLA_CONFIG = {
    "docs": {
        "target_time": 300,    # 5 minutes
        "p95_time": 400,       # 95th percentile
        "p99_time": 500,       # 99th percentile
        "memory_max": 512,     # MB
        "cpu_avg": 30,         # Percent
    },
    "standard": {
        "target_time": 900,    # 15 minutes
        "p95_time": 1200,
        "p99_time": 1500,
        "memory_max": 1024,
        "cpu_avg": 50,
    },
    "heavy": {
        "target_time": 1200,   # 20 minutes
        "p95_time": 1500,
        "p99_time": 1800,
        "memory_max": 2048,
        "cpu_avg": 70,
    },
}
```

### Automated SLA Validation

```python
from scripts.performance_benchmark import (
    PerformanceAnalyzer, SLAValidator, LaneType
)

analyzer = PerformanceAnalyzer()
validator = SLAValidator(analyzer)

# Validate all lanes
results = {}
for lane in LaneType:
    is_compliant, violations = validator.validate_lane(lane)
    results[lane.value] = {
        "compliant": is_compliant,
        "violations": len(violations)
    }

# Report
for lane, result in results.items():
    status = "✓" if result["compliant"] else "✗"
    print(f"{status} {lane}: {result['violations']} violations")

# Fail CI/CD if not compliant
all_compliant = all(r["compliant"] for r in results.values())
if not all_compliant:
    exit(1)
```

---

## Optimization

### Get Optimization Recommendations

```bash
python scripts/performance_benchmark.py optimize --lane standard
```

**Output**:
```
📊 Optimization Suggestions for standard:

1. Reduce Execution Time (Priority: 5/5)
   Description: Execution time is approaching target. Consider parallelization.
   Estimated Improvement: 20%
   Effort Level: medium
   Steps:
     - Profile workflow execution with cProfile
     - Identify bottleneck operations
     - Parallelize independent tasks
     - Implement caching for expensive operations
     - Re-run benchmarks to verify improvement

2. Parallel Test Execution (Priority: 3/5)
   Description: Run tests in parallel to reduce execution time.
   Estimated Improvement: 60%
   Effort Level: medium
   Steps:
     - Install pytest-xdist
     - Mark independent tests
     - Configure parallel workers
     - Verify test isolation
     - Monitor resource usage
```

### Lane-Specific Optimization

#### DOCS Lane
- Markdown build optimization
- Documentation caching
- Incremental builds
- Parallel generation

#### STANDARD Lane
- Parallel test execution
- Test result caching
- Quality gate optimization
- Dependency caching

#### HEAVY Lane
- Distributed testing
- Advanced caching
- Load balancing
- Stress testing

### Implementing Optimization

**Example: Parallel Test Execution**

```bash
# Install xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -n 4

# Auto-detect optimal worker count
pytest tests/ -n auto
```

**Measure Impact**:

```bash
# Before optimization
python scripts/performance_benchmark.py run --lane standard --iterations 5

# After optimization
python scripts/performance_benchmark.py run --lane standard --iterations 5

# Compare
python scripts/performance_benchmark.py analyze --lane standard
```

---

## Reports & Dashboards

### HTML Dashboard

```bash
python scripts/performance_benchmark.py report --output-format html
```

**Output**: `.benchmark_results/performance_dashboard.html`

**Dashboard Features**:
- Executive summary with key metrics
- Lane-by-lane performance breakdown
- Statistical analysis (mean, median, p95, p99)
- Historical trends
- SLA compliance status
- Optimization opportunities

**View Dashboard**:
```bash
# Open in browser
open .benchmark_results/performance_dashboard.html  # macOS
xdg-open .benchmark_results/performance_dashboard.html  # Linux
start .benchmark_results/performance_dashboard.html  # Windows
```

### CSV Export

```bash
python scripts/performance_benchmark.py report --output-format csv
```

**Output**: `.benchmark_results/performance_metrics.csv`

**CSV Columns**:
- Benchmark ID
- Lane
- Start Time
- Duration
- Iterations
- Status
- Exec Time Mean
- Exec Time P95
- Memory Max
- CPU Mean

**Using CSV Data**:

```python
import pandas as pd

# Load metrics
df = pd.read_csv(".benchmark_results/performance_metrics.csv")

# Analyze by lane
for lane in ["docs", "standard", "heavy"]:
    lane_data = df[df["Lane"] == lane]
    print(f"{lane}:")
    print(f"  Avg Exec Time: {lane_data['Exec Time Mean'].mean():.2f}s")
    print(f"  Max Memory: {lane_data['Memory Max'].max():.2f}MB")
    print(f"  Success Rate: {(lane_data['Status'] == 'completed').sum() / len(lane_data) * 100:.1f}%")
```

---

## Best Practices

### 1. Regular Benchmarking Schedule

```bash
#!/bin/bash
# Weekly benchmark (cron job)
0 2 * * 0 python scripts/performance_benchmark.py run --lane docs --iterations 10
0 3 * * 0 python scripts/performance_benchmark.py run --lane standard --iterations 10
0 4 * * 0 python scripts/performance_benchmark.py run --lane heavy --iterations 10
```

### 2. Establish Baseline

```bash
# Initial baseline (3 runs to stabilize)
for i in 1 2 3; do
    echo "Baseline run $i..."
    python scripts/performance_benchmark.py run --lane standard --iterations 10
    sleep 120
done

# Review baseline
python scripts/performance_benchmark.py analyze --lane standard
```

### 3. Isolate Benchmarking Environment

```bash
# Stop background processes
killall chrome firefox node python  # Be careful!

# Reduce system noise
# Set CPU governor to performance mode
# Disable background updates
# Use consistent hardware/OS version
```

### 4. Compare Across Versions

```bash
# Benchmark version 1
git checkout v1.0.0
python scripts/performance_benchmark.py run --lane standard --iterations 5

# Benchmark version 2
git checkout v2.0.0
python scripts/performance_benchmark.py run --lane standard --iterations 5

# Compare
python scripts/performance_benchmark.py analyze --lane standard
```

### 5. Monitor for Regression

```python
from scripts.performance_benchmark import PerformanceAnalyzer, LaneType

analyzer = PerformanceAnalyzer()

# Get historical trend
trends = analyzer.get_trends(LaneType.STANDARD, "execution_time", window=20)

# Detect regression (>10% increase)
if len(trends) > 2:
    recent = trends[-1]
    baseline = sum(trends[:-1]) / len(trends[:-1])
    degradation = ((recent - baseline) / baseline) * 100
    
    if degradation > 10:
        print(f"🚨 REGRESSION DETECTED: {degradation:.1f}%")
        # Alert/escalate
```

---

## Troubleshooting

### Issue 1: Benchmark Timeout

**Symptom**: "Execution timeout after X seconds"

**Solution**:
```bash
# Increase timeout
python scripts/performance_benchmark.py run --lane heavy --timeout 2400

# Check what's slow
python scripts/workflow.py --lane heavy --change-id debug

# Profile execution
python -m cProfile -s cumulative scripts/workflow.py --lane heavy
```

### Issue 2: High Memory Usage

**Symptom**: Memory usage exceeds SLA limit

**Solution**:
```bash
# Profile memory usage
python -m memory_profiler scripts/workflow.py --lane heavy

# Identify memory leaks
import tracemalloc
tracemalloc.start()
# ... run workflow ...
tracemalloc.print_stats()
```

### Issue 3: High CPU Usage

**Symptom**: CPU usage exceeds SLA limit

**Solution**:
```bash
# Profile CPU usage
python -m py_spy record -o profile.svg -- python scripts/workflow.py --lane heavy

# Identify bottlenecks
python -c "import cProfile; cProfile.run('exec(open(\"scripts/workflow.py\").read())')"

# Optimize hot functions
# - Use faster algorithms
# - Cache results
# - Use compiled extensions (NumPy, etc.)
```

### Issue 4: Inconsistent Results

**Symptom**: Highly variable benchmark results

**Solution**:
```bash
# Increase sample size
python scripts/performance_benchmark.py run --lane standard --iterations 20

# Isolate environment
# - Close other applications
# - Disable background processes
# - Use consistent hardware

# Check for external factors
# - Network latency
# - Disk I/O contention
# - System load from cron jobs
```

---

## Advanced Usage

### Programmatic Benchmarking

```python
from scripts.performance_benchmark import (
    BenchmarkSuite, PerformanceAnalyzer, SLAValidator,
    OptimizationRecommender, ReportGenerator, LaneType
)

# Run benchmark
suite = BenchmarkSuite()
result = suite.run_benchmark(LaneType.STANDARD, iterations=10)

# Analyze results
analyzer = PerformanceAnalyzer()
analysis = analyzer.analyze_lane(LaneType.STANDARD)

# Validate SLA
validator = SLAValidator(analyzer)
is_compliant, violations = validator.validate_lane(LaneType.STANDARD)

# Get recommendations
recommender = OptimizationRecommender(analyzer)
suggestions = recommender.get_recommendations(LaneType.STANDARD)

# Generate reports
generator = ReportGenerator(analyzer)
generator.generate_html_report()
generator.generate_csv_report()
```

### Custom Metrics

```python
from scripts.performance_benchmark import MetricSnapshot, MetricsCollector
from datetime import datetime

collector = MetricsCollector()

# Add custom metric
custom_metric = MetricSnapshot(
    timestamp=datetime.now().isoformat(),
    metric_type="custom_operation_time",
    lane="standard",
    value=42.5,
    unit="seconds",
    context={"operation": "custom_task"}
)

collector.metrics.append(custom_metric)
```

### Continuous Performance Monitoring

```python
import schedule
import time
from scripts.performance_benchmark import BenchmarkSuite, LaneType

suite = BenchmarkSuite()

def daily_benchmark():
    """Daily benchmark job."""
    suite.run_benchmark(LaneType.STANDARD, iterations=5)

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(daily_benchmark)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Integration with CI/CD

### GitHub Actions Integration

```yaml
name: Performance Benchmark

on: [pull_request, push]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install psutil
      
      - name: Run benchmarks
        run: |
          python scripts/performance_benchmark.py run --lane standard --iterations 5
      
      - name: Validate SLA
        run: |
          python scripts/performance_benchmark.py validate-sla --lane standard
      
      - name: Generate report
        run: |
          python scripts/performance_benchmark.py report --output-format html
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: .benchmark_results/performance_dashboard.html
```

---

## Success Criteria

✅ **Benchmark Executed** - Workflow runs and metrics collected  
✅ **Analysis Complete** - Statistical metrics calculated  
✅ **SLA Validated** - Compliance verified  
✅ **Recommendations Generated** - Optimization suggestions provided  
✅ **Reports Generated** - HTML/CSV outputs available  
✅ **Trends Tracked** - Performance over time monitored  
✅ **Regressions Detected** - Degradation identified  
✅ **Optimizations Applied** - Improvements implemented  

---

## Related Documentation

- [Workflow Lanes Guide](WORKFLOW_LANES_GUIDE.md)
- [Interactive Lane Selector](INTERACTIVE_LANE_SELECTOR_GUIDE.md)
- [Analytics & Metrics](ANALYTICS_METRICS_FRAMEWORK.md)
- [Rollback & Recovery](ROLLBACK_PROCEDURES.md)

---

**Document Status**: Production Ready  
**Last Updated**: October 24, 2025  
**Version**: 0.1.44
