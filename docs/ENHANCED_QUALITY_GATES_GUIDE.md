# Enhanced Quality Gates Configuration Guide

**Version:** v0.1.45  
**Date:** 2025-10-24  
**Module:** `scripts/enhanced_quality_gates.py`  

## Overview

The Enhanced Quality Gates System provides lane-specific quality thresholds, automatic remediation suggestions, and color-formatted output for comprehensive quality validation.

## Key Features

### 1. Lane-Specific Quality Thresholds

Different lanes enforce different quality standards:

**DOCS Lane (Fast)**
- Ruff: ✓ Enabled (warnings allowed)
- Mypy: ⊘ Skipped
- Pytest: ⊘ Skipped
- Bandit: ⊘ Skipped
- Coverage: ⊘ Skipped
- Focus: Quick validation, minimal gates

**STANDARD Lane (Balanced)**
- Ruff: ✓ Enabled (3 warnings allowed)
- Mypy: ✓ Enabled (5 warnings allowed)
- Pytest: ✓ Enabled (0 failures allowed)
- Bandit: ✓ Enabled (0 issues allowed)
- Coverage: ✓ Enabled (75%+ required)
- Focus: Complete validation

**HEAVY Lane (Thorough)**
- Ruff: ✓ Enabled (0 warnings allowed)
- Mypy: ✓ Enabled (0 warnings allowed)
- Pytest: ✓ Enabled (0 failures allowed)
- Bandit: ✓ Enabled (0 issues allowed)
- Coverage: ✓ Enabled (85%+ required)
- Focus: Strict validation, no compromises

### 2. Quality Gates

#### Ruff (Linting)
- **Command:** `ruff check agent/`
- **Purpose:** Python linting and code style
- **Lane Timeouts:**
  - DOCS: 30s
  - STANDARD: 45s
  - HEAVY: 60s
- **Severity:**
  - DOCS: WARNING
  - STANDARD: ERROR
  - HEAVY: CRITICAL

#### Mypy (Type Checking)
- **Command:** `mypy agent/ --ignore-missing-imports`
- **Purpose:** Static type checking
- **Lane Timeouts:**
  - DOCS: Skipped
  - STANDARD: 60s
  - HEAVY: 90s
- **Severity:**
  - STANDARD: ERROR
  - HEAVY: CRITICAL

#### Pytest (Testing)
- **Command:** `pytest tests/ -v --tb=short`
- **Purpose:** Unit and integration tests
- **Lane Timeouts:**
  - DOCS: Skipped
  - STANDARD: 120s
  - HEAVY: 180s
- **Severity:**
  - STANDARD: ERROR
  - HEAVY: CRITICAL

#### Bandit (Security)
- **Command:** `bandit -r agent/ -f json`
- **Purpose:** Security vulnerability scanning
- **Lane Timeouts:**
  - DOCS: Skipped
  - STANDARD: 60s
  - HEAVY: 90s
- **Severity:**
  - STANDARD: ERROR
  - HEAVY: CRITICAL

#### Coverage (Code Coverage)
- **Command:** `pytest --cov=agent --cov-report=term tests/`
- **Purpose:** Code coverage measurement
- **Lane Requirements:**
  - DOCS: Skipped
  - STANDARD: 75%+ required
  - HEAVY: 85%+ required
- **Severity:**
  - STANDARD: WARNING
  - HEAVY: CRITICAL

### 3. Automatic Remediation Suggestions

When a gate fails, the system provides specific remediation steps:

**Ruff Failures**
```
Fix formatting issues: Review the flagged lines
Run 'ruff check --fix agent/' to auto-fix issues
Review docs: https://docs.astral.sh/ruff/
```

**Mypy Failures**
```
Add type hints: def func(x: int) -> str:
Use typing module: from typing import List, Dict, Optional
Install type stubs: pip install types-<package>
Configure mypy: Check agent/mypy.ini settings
```

**Pytest Failures**
```
Review test output: pytest tests/ -v --tb=short
Check assertions: Verify expected vs actual
Run locally: pytest tests/backend/test_*.py -k 'test_name' -vv
Check fixtures: Ensure test setup is correct
```

**Bandit Failures**
```
Security issue detected: Review flagged code carefully
Check: Are you using secure functions (secrets vs random)?
Fix: Replace insecure patterns with secure alternatives
Test: Verify fix doesn't break functionality
```

### 4. Color-Formatted Output

Severity levels displayed with colors:

```
🟢 GREEN  - PASSED ✓
🟡 YELLOW - WARNING ⚠
🔴 RED    - ERROR ✗
🔴 RED    - CRITICAL !!!
```

Example output:
```
Quality Gates Execution
Lane: STANDARD
============================================================

✓ RUFF                    0.42s  [error]
✓ MYPY                    1.23s  [error]
✓ PYTEST                  5.67s  [error]
✓ BANDIT                  0.89s  [error]
✓ COVERAGE                2.34s  [warning]

============================================================
Quality Gates Summary
Total:   5
Passed:  ✓ 5
Failed:  ✗ 0
Duration: 10.55s
```

### 5. Severity Levels

| Level | Color | Behavior |
|-------|-------|----------|
| INFO | Blue | Informational, doesn't block |
| WARNING | Yellow | Non-blocking, should review |
| ERROR | Red | Blocks workflow (STANDARD/HEAVY) |
| CRITICAL | Red | Blocks workflow (HEAVY only) |

## Configuration

### Basic Setup

```python
from scripts.enhanced_quality_gates import (
    EnhancedQualityGateExecutor,
    LaneType,
)

# Create executor for STANDARD lane
executor = EnhancedQualityGateExecutor(lane=LaneType.STANDARD)

# Execute all gates
all_passed, metrics = await executor.execute_all_gates()

# Export metrics
await executor.export_metrics(".workflow_stats/quality_gates.json")
```

### Custom Thresholds

```python
from scripts.enhanced_quality_gates import (
    LaneQualityConfig,
    QualityThreshold,
    QualityGateName,
    GateSeverity,
)

# Customize specific threshold
custom_threshold = QualityThreshold(
    gate=QualityGateName.COVERAGE,
    lane=LaneType.STANDARD,
    enabled=True,
    pass_threshold=80.0,  # Raise from 75% to 80%
    fail_threshold=95.0,
    severity=GateSeverity.ERROR,  # Raise from WARNING
)

# Update configuration
LaneQualityConfig.LANE_CONFIGS[LaneType.STANDARD][QualityGateName.COVERAGE] = custom_threshold
```

### Lane-Specific Execution

```python
# DOCS Lane - Fast validation
docs_executor = EnhancedQualityGateExecutor(lane=LaneType.DOCS)
passed, metrics = await docs_executor.execute_all_gates()

# STANDARD Lane - Complete validation
std_executor = EnhancedQualityGateExecutor(lane=LaneType.STANDARD)
passed, metrics = await std_executor.execute_all_gates()

# HEAVY Lane - Strict validation
heavy_executor = EnhancedQualityGateExecutor(lane=LaneType.HEAVY)
passed, metrics = await heavy_executor.execute_all_gates()
```

## Usage Patterns

### Pattern 1: Lane-Specific Validation

```python
from scripts.enhanced_quality_gates import EnhancedQualityGateExecutor, LaneType

async def validate_for_lane(lane: LaneType) -> bool:
    executor = EnhancedQualityGateExecutor(lane=lane)
    passed, metrics = await executor.execute_all_gates()
    
    if not passed:
        print(f"Validation failed for {lane.value} lane")
        for gate, result in executor.failed_gates:
            print(f"  {gate.value}: {result.error_output}")
        return False
    
    return True
```

### Pattern 2: With Parallelization Integration

```python
from scripts.enhanced_quality_gates import EnhancedQualityGateExecutor, LaneType
from scripts.parallelization_optimizer import AdaptiveWorkerPool

# Get lane from detection
lane = detect_lane_from_changes()  # Returns LaneType

# Create parallel pool for this lane
pool = AdaptiveWorkerPool(strategy=get_strategy_for_lane(lane))

# Execute quality gates
executor = EnhancedQualityGateExecutor(lane=lane)
gates_passed, gates_metrics = await executor.execute_all_gates()

# Export metrics
await executor.export_metrics(f".workflow_stats/quality_gates_{lane.value}.json")
```

### Pattern 3: Metrics Reporting

```python
from scripts.enhanced_quality_gates import QualityGateDashboard

# After execution
executor = EnhancedQualityGateExecutor(lane=LaneType.STANDARD)
passed, metrics = await executor.execute_all_gates()

# Display dashboard report
report = QualityGateDashboard.format_metrics_report(metrics)
print(report)

# Export for trend analysis
await executor.export_metrics(".workflow_stats/quality_gates.json")
```

### Pattern 4: Remediation Workflow

```python
from scripts.enhanced_quality_gates import EnhancedQualityGateExecutor, RemediationSuggestions

executor = EnhancedQualityGateExecutor(lane=LaneType.STANDARD)
passed, metrics = await executor.execute_all_gates()

if not passed:
    for gate, result in executor.failed_gates:
        print(f"\n❌ {gate.value.upper()} FAILED")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Errors: {result.errors_count}")
        
        if result.remediation_steps:
            print("Remediation:")
            for step in result.remediation_steps:
                print(f"  → {step}")
```

## Quality Gate Thresholds by Lane

### DOCS Lane
```
Ruff:     ✓ 30s  timeout, 5 warnings allowed      [WARNING]
Mypy:     ⊘ Skipped
Pytest:   ⊘ Skipped
Bandit:   ⊘ Skipped
Coverage: ⊘ Skipped
```

### STANDARD Lane
```
Ruff:     ✓ 45s  timeout, 3 warnings allowed      [ERROR]
Mypy:     ✓ 60s  timeout, 5 warnings allowed      [ERROR]
Pytest:   ✓ 120s timeout, 0 failures allowed      [ERROR]
Bandit:   ✓ 60s  timeout, 0 issues allowed        [ERROR]
Coverage: ✓ 75%  minimum required                 [WARNING]
```

### HEAVY Lane
```
Ruff:     ✓ 60s  timeout, 0 warnings allowed      [CRITICAL]
Mypy:     ✓ 90s  timeout, 0 warnings allowed      [CRITICAL]
Pytest:   ✓ 180s timeout, 0 failures allowed      [CRITICAL]
Bandit:   ✓ 90s  timeout, 0 issues allowed        [CRITICAL]
Coverage: ✓ 85%  minimum required                 [CRITICAL]
```

## Remediation Command Reference

### Quick Fixes

```bash
# Auto-fix ruff issues
ruff check --fix agent/

# Run tests locally
pytest tests/backend/ -v

# Check coverage
pytest --cov=agent --cov-report=html tests/

# Security scan
bandit -r agent/

# Type check
mypy agent/ --ignore-missing-imports
```

### Detailed Debugging

```bash
# Pytest verbose with traceback
pytest tests/ -vv --tb=long -k 'test_name'

# Ruff specific checks
ruff check --extend-select=E,W,F agent/

# Mypy with config
mypy agent/ --show-error-codes --no-implicit-optional

# Bandit detailed
bandit -r agent/ -ll  # Low severity threshold
```

## Monitoring

### Real-Time Monitoring

```python
# Print progress during execution
executor = EnhancedQualityGateExecutor(lane=LaneType.STANDARD)
passed, metrics = await executor.execute_all_gates()

# Check individual gate results
for result in metrics.gate_results:
    if result.passed:
        print(f"✓ {result.gate.value}: {result.duration_seconds:.2f}s")
    else:
        print(f"✗ {result.gate.value}: {result.errors_count} errors")
```

### Historical Analysis

```python
import json

# Load metrics from JSON
with open(".workflow_stats/quality_gates.json") as f:
    metrics = json.load(f)

# Analyze trends
total_failures = metrics['failed_gates']
avg_duration = metrics['avg_gate_duration_seconds']

print(f"Avg Duration: {avg_duration:.2f}s")
print(f"Failures: {total_failures}")
```

## Troubleshooting

### Issue: "HEAVY lane gates keep failing"

**Solution:** Review the strict thresholds
```python
# Check if requirements are realistic
# Consider if you really need 0 warnings for production
# Can use ERROR severity in STANDARD instead of CRITICAL
```

### Issue: "Coverage reports show low percentage"

**Solution:** Add missing tests
```bash
# Generate coverage report
pytest --cov=agent --cov-report=html tests/

# Open report
open htmlcov/index.html  # Review gaps

# Add tests for uncovered code
```

### Issue: "Ruff keeps failing on style issues"

**Solution:** Auto-fix or suppress
```bash
# Auto-fix all style issues
ruff check --fix agent/

# Or suppress specific violations
# At line level: # noqa: E501
# At file level: # ruff: noqa
```

### Issue: "Tests timeout on HEAVY lane"

**Solution:** Increase timeout or optimize tests
```python
# Increase timeout
custom_threshold = QualityThreshold(
    gate=QualityGateName.PYTEST,
    lane=LaneType.HEAVY,
    timeout_seconds=300,  # 5 minutes
)

# Or optimize slow tests
pytest tests/ --durations=10  # Find slowest tests
```

## Integration with Workflow

### Update workflow.py to use enhanced gates

```python
# In scripts/workflow.py

from scripts.enhanced_quality_gates import EnhancedQualityGateExecutor
from scripts.lane_selection_enhancements import LaneAutoDetector

async def execute_quality_gates(lane: LaneType):
    """Execute quality gates with lane-specific thresholds."""
    executor = EnhancedQualityGateExecutor(lane=lane)
    
    passed, metrics = await executor.execute_all_gates()
    
    # Export metrics
    metrics_file = f".workflow_stats/quality_gates_{lane.value}.json"
    await executor.export_metrics(metrics_file)
    
    # Check for critical failures
    if executor.failed_gates and any(
        result.severity == GateSeverity.CRITICAL 
        for _, result in executor.failed_gates
    ):
        raise QualityGateException(f"Critical quality gate failures in {lane.value} lane")
    
    return metrics
```

## Best Practices

1. **Match Lane to Workflow Requirements**
   - DOCS: Quick validation for documentation
   - STANDARD: Complete validation for features
   - HEAVY: Strict validation for production

2. **Review Remediation Suggestions**
   - Always read the suggested fixes
   - Understand why the gate failed
   - Apply best practices

3. **Iterate on Thresholds**
   - Start conservative (higher thresholds)
   - Tighten gradually as code improves
   - Document custom threshold changes

4. **Monitor Trends**
   - Track metrics over time
   - Identify patterns in failures
   - Optimize based on data

5. **Use Color Output**
   - Terminal output helps developers
   - Makes failures/warnings obvious
   - Improves workflow comprehension

## Performance Targets

| Lane | Gate Count | Total Time | Avg/Gate |
|------|-----------|-----------|----------|
| DOCS | 1 | <1m | <30s |
| STANDARD | 5 | ~10m | ~2m |
| HEAVY | 5 | ~12m | ~2.4m |

## References

- `scripts/enhanced_quality_gates.py` - Implementation
- `scripts/lane_selection_enhancements.py` - Lane detection
- `scripts/parallelization_optimizer.py` - Parallelization
- `scripts/workflow.py` - Workflow orchestrator
- `docs/The_Workflow_Process.md` - Complete guide

---

**Last Updated:** 2025-10-24  
**Maintained By:** @kdejo
