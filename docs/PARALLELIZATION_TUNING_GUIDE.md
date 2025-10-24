# Parallelization Tuning Guide

**Version:** v0.1.45  
**Date:** 2025-10-24  
**Module:** `scripts/parallelization_optimizer.py`  

## Overview

The Parallelization Engine Optimizer provides adaptive worker pool management, SLA enforcement, and performance tuning for workflow stages 2-6. This guide explains how to configure, monitor, and optimize parallelization for your environment.

## Key Features

### 1. Adaptive Worker Pool Sizing

Automatically adjusts worker pool size based on:
- CPU core count
- Available memory
- Selected parallelization strategy
- Historical performance data

**Strategies:**
- **THREAD_POOL**: Best for I/O-bound tasks (SQL, file ops, network)
- **PROCESS_POOL**: Best for CPU-bound tasks (calculations, transformations)
- **HYBRID**: Mix of thread and process pools
- **ADAPTIVE**: Automatically choose based on system resources and task characteristics
- **SEQUENTIAL**: No parallelization (debugging, troubleshooting)

### 2. Per-Stage Metrics Collection

Automatically captures:
- Execution duration (wall clock time)
- CPU usage percentage
- Memory consumption
- Worker assignment
- Success/failure status
- Detailed error messages

### 3. SLA Management

Define and enforce Service Level Agreement targets:
- Per-stage maximum duration (default: 30s per stage)
- Warning thresholds (default: 80% of maximum)
- Critical violation detection (blocks workflow)
- Automatic reporting and remediation

### 4. Bottleneck Detection

Identifies:
- Slowest stages (>1.5x average duration)
- Uneven task distribution (>3x variance)
- Suboptimal strategy selection
- Worker pool under/over-utilization

### 5. Performance Dashboard

Real-time visualization showing:
- Pool configuration and utilization
- Per-stage execution timelines
- Throughput (tasks/second)
- Success rates
- Detected bottlenecks
- Optimization recommendations

## Configuration

### Basic Setup

```python
from scripts.parallelization_optimizer import (
    AdaptiveWorkerPool,
    ParallelizationStrategy,
    ParallelizationSLAManager,
    ParallelizationDashboard,
)

# Create adaptive pool (automatically sizes workers)
pool = AdaptiveWorkerPool(
    strategy=ParallelizationStrategy.ADAPTIVE,
    initial_size=None  # Let it auto-detect
)

# Create SLA manager
sla_manager = ParallelizationSLAManager()
```

### Custom Configuration

```python
# Define custom SLA targets (in seconds)
custom_slas = {
    2: SLATarget(stage_number=2, max_duration_seconds=45, critical=False),
    3: SLATarget(stage_number=3, max_duration_seconds=45, critical=False),
    4: SLATarget(stage_number=4, max_duration_seconds=60, critical=True),  # Critical
    5: SLATarget(stage_number=5, max_duration_seconds=60, critical=True),
    6: SLATarget(stage_number=6, max_duration_seconds=60, critical=False),
}

sla_manager = ParallelizationSLAManager(slas=custom_slas)

# Create pool with explicit size
pool = AdaptiveWorkerPool(
    strategy=ParallelizationStrategy.THREAD_POOL,
    initial_size=6
)
```

### Lane-Specific Configuration

```python
from scripts.lane_selection_enhancements import LaneType

# Configure different parallelization for each lane
LANE_PARALLELIZATION = {
    LaneType.DOCS: {
        "strategy": ParallelizationStrategy.THREAD_POOL,
        "workers": 2,
        "sla_seconds": 15,
    },
    LaneType.STANDARD: {
        "strategy": ParallelizationStrategy.ADAPTIVE,
        "workers": None,  # Auto-detect
        "sla_seconds": 30,
    },
    LaneType.HEAVY: {
        "strategy": ParallelizationStrategy.PROCESS_POOL,
        "workers": 8,
        "sla_seconds": 60,
    },
}

# Use in workflow
def get_pool_for_lane(lane: LaneType) -> AdaptiveWorkerPool:
    config = LANE_PARALLELIZATION[lane]
    return AdaptiveWorkerPool(
        strategy=config["strategy"],
        initial_size=config["workers"]
    )
```

## Usage Patterns

### Pattern 1: Simple Parallel Execution

```python
# Create pool
pool = AdaptiveWorkerPool(strategy=ParallelizationStrategy.ADAPTIVE)

# Submit stages
def stage_2_task():
    # Run quality gates
    subprocess.run(["ruff", "check", "agent/"], check=True)

def stage_3_task():
    # Run type checking
    subprocess.run(["mypy", "agent/"], check=True)

pool.submit_stage(2, "quality_gates", stage_2_task)
pool.submit_stage(3, "type_checking", stage_3_task)
pool.submit_stage(4, "unit_tests", lambda: subprocess.run(["pytest", "tests/backend/"], check=True))
pool.submit_stage(5, "integration_tests", lambda: subprocess.run(["pytest", "tests/integration/"], check=True))
pool.submit_stage(6, "security_scan", lambda: subprocess.run(["bandit", "-r", "agent/"], check=True))

# Wait for completion
success, errors = pool.wait_all()

if not success:
    for error in errors:
        logger.error(error)
    sys.exit(1)

# Display results
report = ParallelizationDashboard.format_metrics_report(pool.metrics)
print(report)
```

### Pattern 2: With SLA Enforcement

```python
pool = AdaptiveWorkerPool(strategy=ParallelizationStrategy.ADAPTIVE)
sla_manager = ParallelizationSLAManager()

# Submit stages
pool.submit_stage(2, "linting", run_linting)
pool.submit_stage(3, "type_check", run_type_check)
pool.submit_stage(4, "tests", run_tests)

# Wait and check SLAs
success, errors = pool.wait_all()

# Validate SLA compliance
sla_met = sla_manager.check_all_stages(pool.metrics)

if not sla_met:
    print("\n⚠️  SLA VIOLATIONS DETECTED:")
    for violation in sla_manager.violations:
        print(f"  {violation}")
    for warning in sla_manager.warnings:
        print(f"  {warning}")
    
    if sla_manager.violations:  # Critical violations
        sys.exit(1)
```

### Pattern 3: Performance Profiling

```python
from scripts.parallelization_optimizer import ParallelizationProfiler

profiler = ParallelizationProfiler(num_iterations=3)

# Profile each stage
profile_2 = profiler.profile_stage(2, "quality_gates", run_linting)
profile_3 = profiler.profile_stage(3, "type_check", run_type_check)
profile_4 = profiler.profile_stage(4, "tests", run_tests)

# Get recommendations
print("Stage Profiles:")
for stage_num, profile in profiler.profile_results.items():
    print(f"\nStage {stage_num}: {profile['stage_name']}")
    print(f"  Avg Duration: {profile['avg_duration_seconds']:.2f}s")
    print(f"  Variability: {profile['variability_seconds']:.2f}s")
    print(f"  CPU Usage: {profile['avg_cpu_percent']:.1f}%")
    print(f"  Recommended Strategy: {profile['recommended_strategy']}")
    print(f"  Parallelizable: {profile['parallelizable']}")
```

### Pattern 4: Monitoring and Metrics Export

```python
import json

pool = AdaptiveWorkerPool(strategy=ParallelizationStrategy.ADAPTIVE)

# ... execute stages ...

success, errors = pool.wait_all()

# Export metrics to JSON
metrics_dict = pool.metrics.to_dict()

output_file = ".workflow_stats/parallelization_metrics.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w') as f:
    json.dump(metrics_dict, f, indent=2, default=str)

print(f"Metrics saved to {output_file}")

# Analyze metrics
print(f"\n📊 Performance Summary:")
print(f"  Total Duration: {pool.metrics.total_duration_seconds:.2f}s")
print(f"  Throughput: {pool.metrics.throughput_tasks_per_second:.2f} tasks/sec")
print(f"  Worker Utilization: {pool.metrics.worker_utilization:.1f}%")
print(f"  Success Rate: {(pool.metrics.completed_tasks/pool.metrics.total_tasks*100):.1f}%")
```

## Performance Tuning

### Diagnosing Bottlenecks

**Symptom: Very slow overall workflow**
```
Check pool.metrics.max_task_duration_seconds vs avg
If max >> avg: Focus on slowest stage
If all stages slow: Try increasing workers or changing strategy
```

**Symptom: High CPU usage (thread pool)**
```
pool.metrics.bottlenecks contains "High CPU usage"
Solution: Switch from THREAD_POOL to PROCESS_POOL
```

**Symptom: Low worker utilization**
```
pool.metrics.worker_utilization < 50%
Solution: Reduce pool size, or add more parallelizable tasks
```

### Optimization Checklist

- [ ] Profile stages to understand CPU vs I/O characteristics
- [ ] Choose appropriate strategy (THREAD_POOL vs PROCESS_POOL)
- [ ] Verify optimal worker count for your system
- [ ] Set realistic SLA targets based on profiling
- [ ] Monitor for bottlenecks in high-cost stages
- [ ] Implement lane-specific configurations
- [ ] Track metrics over time (trend analysis)
- [ ] Document any custom SLA tuning

### Lane-Specific Tuning

**DOCS Lane (Fast):**
```python
LANE_DOCS_CONFIG = {
    "strategy": ParallelizationStrategy.THREAD_POOL,
    "workers": 2,
    "sla_targets": {2: 10, 3: 10, 4: 10, 5: 10, 6: 10},
}
# Focus: Minimal parallelization, fast fail-fast
```

**STANDARD Lane (Balanced):**
```python
LANE_STANDARD_CONFIG = {
    "strategy": ParallelizationStrategy.ADAPTIVE,
    "workers": None,  # Auto-detect
    "sla_targets": {2: 30, 3: 30, 4: 30, 5: 30, 6: 30},
}
# Focus: Balanced resource usage, complete validation
```

**HEAVY Lane (Thorough):**
```python
LANE_HEAVY_CONFIG = {
    "strategy": ParallelizationStrategy.PROCESS_POOL,
    "workers": 8,
    "sla_targets": {2: 60, 3: 60, 4: 60, 5: 60, 6: 60},
}
# Focus: Maximum thoroughness, full resource utilization
```

## Monitoring & Maintenance

### Real-Time Monitoring

Monitor active workflow pool:
```python
# Print dashboard during execution
print(ParallelizationDashboard.format_metrics_report(pool.metrics))

# Check SLA status
for violation in sla_manager.violations:
    logger.error(f"SLA VIOLATION: {violation}")
for warning in sla_manager.warnings:
    logger.warning(f"SLA WARNING: {warning}")
```

### Historical Analysis

Track trends over time:
```python
# Load historical metrics
with open(".workflow_stats/parallelization_metrics.json") as f:
    historical = json.load(f)

# Identify trends
avg_throughput = sum(m["throughput_tasks_per_second"] for m in historical) / len(historical)
print(f"Average throughput: {avg_throughput:.2f} tasks/sec")

# Detect degradation
latest_throughput = historical[-1]["throughput_tasks_per_second"]
if latest_throughput < avg_throughput * 0.8:
    print("⚠️  PERFORMANCE DEGRADATION DETECTED")
```

### Resource Cleanup

Always shutdown pools properly:
```python
try:
    # ... execute tasks ...
finally:
    pool.shutdown()
```

## Troubleshooting

### Issue: "Thread pool uses 100% CPU"

**Cause:** CPU-bound tasks on thread pool  
**Solution:** Use PROCESS_POOL or HYBRID strategy
```python
pool = AdaptiveWorkerPool(strategy=ParallelizationStrategy.PROCESS_POOL)
```

### Issue: "SLA violations in HEAVY lane"

**Cause:** Stages taking longer than configured targets  
**Solution:** Increase SLA targets or reduce tasks in stages
```python
custom_slas = {6: SLATarget(stage_number=6, max_duration_seconds=90)}
sla_manager = ParallelizationSLAManager(slas=custom_slas)
```

### Issue: "Worker pool under-utilized"

**Cause:** Stages complete too quickly relative to pool size  
**Solution:** Reduce workers or add more tasks
```python
pool = AdaptiveWorkerPool(strategy=ParallelizationStrategy.THREAD_POOL, initial_size=2)
```

### Issue: "Memory usage spikes"

**Cause:** Process pool with many workers  
**Solution:** Reduce worker count or use THREAD_POOL
```python
pool = AdaptiveWorkerPool(strategy=ParallelizationStrategy.THREAD_POOL, initial_size=4)
```

## Integration with workflow.py

### Update workflow.py to use optimizer

```python
# In scripts/workflow.py

from scripts.parallelization_optimizer import (
    AdaptiveWorkerPool,
    ParallelizationStrategy,
    ParallelizationSLAManager,
)

class WorkflowOrchestrator:
    def __init__(self, lane: LaneType):
        self.lane = lane
        
        # Initialize parallelization based on lane
        if lane == LaneType.DOCS:
            strategy = ParallelizationStrategy.THREAD_POOL
        elif lane == LaneType.HEAVY:
            strategy = ParallelizationStrategy.PROCESS_POOL
        else:
            strategy = ParallelizationStrategy.ADAPTIVE
        
        self.pool = AdaptiveWorkerPool(strategy=strategy)
        self.sla_manager = ParallelizationSLAManager()
    
    async def execute_parallel_stages(self):
        """Execute stages 2-6 in parallel with monitoring."""
        # Submit stages to pool
        self.pool.submit_stage(2, "quality_gates", self.run_stage_2)
        self.pool.submit_stage(3, "type_checking", self.run_stage_3)
        self.pool.submit_stage(4, "unit_tests", self.run_stage_4)
        self.pool.submit_stage(5, "integration_tests", self.run_stage_5)
        self.pool.submit_stage(6, "security_scan", self.run_stage_6)
        
        # Wait for completion
        success, errors = self.pool.wait_all()
        
        # Check SLAs
        sla_met = self.sla_manager.check_all_stages(self.pool.metrics)
        
        return success and sla_met, errors
```

## Best Practices

1. **Profile Before Tuning:** Use `ParallelizationProfiler` to understand task characteristics
2. **Start Conservative:** Begin with fewer workers, increase as needed
3. **Monitor Continuously:** Track metrics over time to detect issues
4. **Set Realistic SLAs:** Base on profiled durations, not wishful thinking
5. **Lane-Specific Config:** Different lanes need different parallelization
6. **Clean Shutdown:** Always call `pool.shutdown()` in finally blocks
7. **Document Changes:** Record any custom tuning in configuration
8. **Test Changes:** Validate changes don't break workflow reliability

## Performance Targets (by Lane)

| Lane | Strategy | Workers | Total Time | SLA/Stage |
|------|----------|---------|-----------|-----------|
| DOCS | thread | 2 | <5m | 10s |
| STANDARD | adaptive | auto | ~15m | 30s |
| HEAVY | process | 8 | ~20m | 60s |

## References

- `scripts/parallelization_optimizer.py` - Main module
- `scripts/lane_selection_enhancements.py` - Lane detection
- `scripts/workflow.py` - Workflow orchestrator
- `docs/The_Workflow_Process.md` - Complete workflow guide

---

**Last Updated:** 2025-10-24  
**Maintained By:** @kdejo
