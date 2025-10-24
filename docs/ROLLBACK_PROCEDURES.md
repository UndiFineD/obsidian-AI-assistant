# Rollback and Recovery Procedures Guide

**Version**: 0.1.44  
**Status**: Production Ready  
**Last Updated**: October 24, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Checkpoint Management](#checkpoint-management)
4. [Recovery Procedures](#recovery-procedures)
5. [Failure Types & Recovery](#failure-types--recovery)
6. [Lane-Specific Recovery](#lane-specific-recovery)
7. [Advanced Procedures](#advanced-procedures)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Integration Examples](#integration-examples)

---

## Overview

### What is Rollback and Recovery?

The **Rollback and Recovery Framework** provides comprehensive capabilities to recover from workflow failures:

1. **Checkpoint Management** - Save workflow state at each step
2. **Recovery Procedures** - Specific procedures for different failure types
3. **Partial Execution Resume** - Continue from last successful checkpoint
4. **State Cleanup** - Clean up failed execution state
5. **Rollback Support** - Revert to previous state
6. **Recovery Planning** - Smart recommendations for recovery

### Why It Matters

**Before Recovery Framework**:
```
Workflow fails → Manual investigation → Manual fix → Retry entire workflow
Time: 30+ minutes
Risk: Loss of progress, manual errors
```

**After Recovery Framework**:
```
Workflow fails → Automatic checkpoint saved → Smart recovery plan → Resume from checkpoint
Time: 2-5 minutes
Risk: Minimal, automated and tested
```

### Key Benefits

- ✅ **Fault Tolerance** - Recover from failures automatically
- ✅ **Time Savings** - Resume from checkpoint instead of restarting
- ✅ **Progress Preservation** - No loss of previous work
- ✅ **Smart Recovery** - Different strategies for different failures
- ✅ **Lane-Aware** - Recovery tailored to workflow lane
- ✅ **State Validation** - Verify system integrity before recovery

---

## Quick Start

### Create a Checkpoint

```bash
python scripts/rollback_recovery.py checkpoint \
  --lane standard \
  --step-number 3 \
  --step-name "Running tests"
```

### List Checkpoints

```bash
python scripts/rollback_recovery.py list
```

### Restore from Checkpoint

```bash
python scripts/rollback_recovery.py restore \
  --checkpoint-id standard-step3-20251024_143045
```

### Validate State

```bash
python scripts/rollback_recovery.py validate
```

### Cleanup Failed State

```bash
python scripts/rollback_recovery.py cleanup
```

### Get Recovery Plan

```bash
python scripts/rollback_recovery.py plan \
  --failure-type test_failure \
  --lane standard
```

---

## Checkpoint Management

### What are Checkpoints?

Checkpoints are snapshots of workflow state saved at each step:

```
Checkpoint Data:
├── Checkpoint ID (unique identifier)
├── Lane (docs/standard/heavy)
├── Step number and name
├── Timestamp
├── Git commit & branch
├── State hash (for validation)
├── Files snapshot (backed up)
├── Metrics (timing, resource usage)
└── Success status & error message
```

### Creating Checkpoints

**Automatic Creation**:
```python
from scripts.rollback_recovery import RollbackRecoverySystem

system = RollbackRecoverySystem()

# Create checkpoint after each step
result = system.run(
    'checkpoint',
    lane='standard',
    step_number=1,
    step_name='Quality gates'
)

print(f"Checkpoint: {result.checkpoint_id}")
```

**Manual Creation**:
```bash
python scripts/rollback_recovery.py checkpoint \
  --lane standard \
  --step-number 2 \
  --step-name "Running tests"
```

### Checkpoint Storage

Checkpoints are stored in `.checkpoints/` directory:

```
.checkpoints/
├── state.json (checkpoint metadata)
├── standard-step1-20251024_143000/
│   ├── scripts/workflow.py
│   ├── agent/backend.py
│   └── ...
├── standard-step2-20251024_143200/
│   └── ...
└── ...
```

**Storage Requirements**:
- ~50MB per full workflow checkpoint
- Automatic cleanup of old checkpoints (older than 7 days)
- Compressed backups available for long-term storage

### Listing Checkpoints

**Command Line**:
```bash
python scripts/rollback_recovery.py list

# Output:
# standard-step3-20251024_143045: Running tests (standard)
# standard-step2-20251024_143000: Quality gates (standard)
# standard-step1-20251024_142900: Building (standard)
```

**Programmatic**:
```python
system = RollbackRecoverySystem()
checkpoints = system.checkpoint_manager.list_checkpoints()

for cp in checkpoints:
    print(f"{cp.checkpoint_id}: {cp.step_name}")
```

---

## Recovery Procedures

### Recovery Workflow

```
Failure Detected
    ↓
Identify Failure Type
    ↓
Get Recovery Plan
    ↓
Execute Recovery Strategy
    ↓
Validate Recovery
    ↓
Resume Workflow
```

### Available Strategies

| Strategy | Description | When to Use | Time Impact |
|----------|-------------|------------|------------|
| **RETRY** | Retry the failed step | Transient errors | +5-60 min |
| **RESUME** | Continue from checkpoint | After cleanup | +2-10 min |
| **SKIP** | Skip failed step | For optional tests | -time saved |
| **ROLLBACK** | Revert to previous state | Serious issues | +10-30 min |
| **MANUAL** | Manual intervention | Complex failures | +varies |

### State Validation

Before recovery, validate the state:

```bash
python scripts/rollback_recovery.py validate
```

**Validation Checks**:
- ✓ Critical files exist (workflow.py, backend.py, etc.)
- ✓ Git repository is accessible
- ✓ Working directory is clean
- ✓ Dependencies are installed
- ✓ Configuration is valid

---

## Failure Types & Recovery

### 1. Timeout Failure

**Symptoms**:
- Execution exceeds time limit
- Process killed or hangs indefinitely
- "Timeout exceeded" error message

**Recovery Plan**:

| Step | Action | Command | Time |
|------|--------|---------|------|
| 1 | Check resources | `free -h; df -h` | 30s |
| 2 | Resume checkpoint | `rollback_recovery.py restore` | 60s |
| 3 | Try heavier lane | Retry with HEAVY | 1200s |

**Example**:
```bash
# Check resource usage
free -h
df -h

# Clean up and retry
python scripts/rollback_recovery.py cleanup

# Restore checkpoint
python scripts/rollback_recovery.py restore \
  --checkpoint-id standard-step2-20251024_143000

# Or try heavier lane
python scripts/workflow.py --lane heavy --change-id my-change
```

### 2. Test Failure

**Symptoms**:
- Tests fail with error messages
- AssertionError or exception raised
- Specific test or test suite fails

**Recovery Plan**:

| Step | Action | Command | Time |
|------|--------|---------|------|
| 1 | Re-run failed tests | `pytest tests/ -v -x` | 180s |
| 2 | Run with detailed output | `pytest -v --tb=short` | 180s |
| 3 | Skip and continue | `pytest --ignore=tests/broken` | 120s |
| 4 | Manual review | Fix failing tests | varies |

**Example**:
```bash
# Re-run with stop on first failure
pytest tests/ -v -x

# Get detailed traceback
pytest tests/ -v --tb=long

# Skip specific test file
pytest tests/ --ignore=tests/broken -v

# Run with coverage
pytest tests/ --cov=agent --cov-report=html
```

### 3. Quality Gate Failure

**Symptoms**:
- Lint errors (ruff)
- Type errors (mypy)
- Security issues (bandit)
- Code style violations

**Recovery Plan**:

| Step | Action | Command | Time |
|------|--------|---------|------|
| 1 | Run gates individually | See commands below | 120s |
| 2 | Fix issues automatically | `ruff check --fix` | 60s |
| 3 | Re-run gates | Verify fixes | 60s |

**Example**:
```bash
# Run individual quality gates
ruff check agent/
mypy agent/ --ignore-missing-imports
bandit -r agent/

# Auto-fix linting issues
ruff check --fix agent/

# Type check with strict mode
mypy agent/ --strict

# Generate security report
bandit -r agent/ -f json -o bandit_report.json
```

### 4. Resource Exhaustion

**Symptoms**:
- "Out of memory" error
- "No space left on device"
- Slow performance or hangs
- Process killed by system

**Recovery Plan**:

| Step | Action | Command | Time |
|------|--------|---------|------|
| 1 | Clean up temp files | `git clean -fd` | 30s |
| 2 | Clear caches | `rm -rf __pycache__` | 20s |
| 3 | Clear pytest cache | `pytest --cache-clear` | 30s |
| 4 | Downgrade lane | Try lighter lane | varies |

**Example**:
```bash
# Clean up all temporary files
git clean -fd
find . -type d -name __pycache__ -exec rm -r {} +
rm -rf .pytest_cache

# Clear Python bytecode
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# Retry workflow
python scripts/rollback_recovery.py cleanup
python scripts/workflow.py --lane docs --change-id my-change
```

### 5. Network Error

**Symptoms**:
- "Connection refused" or "Connection timeout"
- "Failed to resolve host"
- External API/service unreachable
- Git push/pull fails

**Recovery Plan**:

| Step | Action | Command | Time |
|------|--------|---------|------|
| 1 | Check connectivity | `ping 8.8.8.8; nc -zv github.com 22` | 30s |
| 2 | Wait and retry | Wait 60s then retry | 60s |
| 3 | Use checkpoint | Resume from checkpoint | 120s |

**Example**:
```bash
# Check network connectivity
ping 8.8.8.8
curl -I https://github.com

# Check git connectivity
ssh -T git@github.com
git fetch origin

# Retry after wait
sleep 60
python scripts/rollback_recovery.py restore --checkpoint-id standard-step2-20251024_143000
```

### 6. Git Error

**Symptoms**:
- "Git command failed"
- "Cannot read object"
- "Merge conflict"
- "Authentication failed"

**Recovery Plan**:

| Step | Action | Command | Time |
|------|--------|---------|------|
| 1 | Check status | `git status; git log` | 30s |
| 2 | Fetch latest | `git fetch origin` | 60s |
| 3 | Reset changes | `git reset --hard` | 20s |
| 4 | Manual recovery | Restore from checkpoint | varies |

**Example**:
```bash
# Check repository status
git status
git log -5 --oneline

# Fetch latest from origin
git fetch origin
git pull origin release-0.1.44

# If conflicts, reset
git reset --hard HEAD
git clean -fd

# Or restore from checkpoint
python scripts/rollback_recovery.py restore --checkpoint-id standard-step1-20251024_142900
```

---

## Lane-Specific Recovery

### DOCS Lane Recovery

**Characteristics**: Lightweight, fast (<5 min)

**Typical Issues**:
- Markdown formatting errors
- Documentation build failures
- Link validation failures

**Recovery Strategy**:
```bash
# Validate documentation
mdl docs/*.md

# Fix markdown issues
# Rebuild documentation
python scripts/rollback_recovery.py cleanup

# Retry
python scripts/workflow.py --lane docs --change-id my-change
```

### STANDARD Lane Recovery

**Characteristics**: Balanced, moderate (<15 min)

**Typical Issues**:
- Test failures
- Quality gate violations
- Resource contention

**Recovery Strategy**:
```bash
# Run quality gates
ruff check agent/
mypy agent/ --ignore-missing-imports

# Run tests
pytest tests/ -v

# If timeout, retry with checkpoint
python scripts/rollback_recovery.py restore --checkpoint-id standard-step2-...
```

### HEAVY Lane Recovery

**Characteristics**: Comprehensive, thorough (<20 min)

**Typical Issues**:
- Complex test failures
- Performance issues
- Integration problems

**Recovery Strategy**:
```bash
# Full validation
python scripts/post_deployment_validation_enhanced.py

# Stress testing
python -m locust -f tests/load_test.py

# If still failing, collect metrics
python -c "from agent.analytics import MetricsReporter; \
           MetricsReporter().generate_summary_report()"
```

---

## Advanced Procedures

### Partial Execution Resume

Resume workflow from specific checkpoint:

```bash
# 1. List available checkpoints
python scripts/rollback_recovery.py list

# 2. Choose checkpoint to restore from
CHECKPOINT="standard-step2-20251024_143000"

# 3. Restore state
python scripts/rollback_recovery.py restore --checkpoint-id $CHECKPOINT

# 4. Continue workflow
python scripts/workflow.py --lane standard --change-id my-change
```

### Multi-Step Recovery

Handle multiple failures in sequence:

```python
from scripts.rollback_recovery import RollbackRecoverySystem

system = RollbackRecoverySystem()

# Attempt 1: Try again
print("Attempt 1: Retry")
# ... run workflow ...

# Attempt 2: Validate and cleanup
if workflow_failed:
    system.run('validate')
    system.run('cleanup')
    
    # Try again
    print("Attempt 2: After cleanup")
    # ... run workflow ...

# Attempt 3: Restore from checkpoint
if workflow_failed_again:
    checkpoints = system.checkpoint_manager.list_checkpoints()
    if checkpoints:
        latest = checkpoints[0]
        system.run('restore', checkpoint_id=latest.checkpoint_id)
        
        print(f"Attempt 3: Restored from {latest.checkpoint_id}")
        # ... run workflow ...
```

### Automated Recovery Loop

Implement automatic recovery with exponential backoff:

```python
import time
from scripts.rollback_recovery import RollbackRecoverySystem, FailureType

system = RollbackRecoverySystem()
max_attempts = 3
retry_delay = 30  # seconds

for attempt in range(1, max_attempts + 1):
    try:
        # Run workflow
        result = run_workflow()
        
        if result.success:
            break
        
        # Get recovery plan
        recovery_plan = system.recovery_planner.get_recovery_plan(
            FailureType.UNKNOWN,
            lane='standard'
        )
        
        # Execute recovery
        for action in recovery_plan[:attempt]:  # Escalate actions
            execute_action(action)
        
        # Wait before retry
        wait_time = retry_delay * (2 ** (attempt - 1))
        time.sleep(wait_time)
        
    except Exception as e:
        print(f"Attempt {attempt} failed: {e}")
        if attempt >= max_attempts:
            raise
```

---

## Troubleshooting

### Issue 1: Checkpoint Not Found

**Symptom**: "Checkpoint not found: standard-step2-..."

**Solution**:
```bash
# List all available checkpoints
python scripts/rollback_recovery.py list

# Use correct checkpoint ID from list
python scripts/rollback_recovery.py restore --checkpoint-id <ID>
```

### Issue 2: Restore Failed

**Symptom**: "Error restoring checkpoint: Permission denied"

**Solution**:
```bash
# Check file permissions
ls -la .checkpoints/

# Fix permissions
chmod -R 755 .checkpoints/

# Try restore again
python scripts/rollback_recovery.py restore --checkpoint-id standard-step2-...
```

### Issue 3: State Validation Failed

**Symptom**: "State validation passed" but workflow still fails

**Solution**:
```bash
# Deep validation
python scripts/rollback_recovery.py validate --verbose

# Full cleanup
python scripts/rollback_recovery.py cleanup

# Check system resources
free -h
df -h
ps aux | grep python

# Verify git status
git status
git log -1
```

### Issue 4: Checkpoint Disk Space

**Symptom**: "No space left on device" when creating checkpoint

**Solution**:
```bash
# Clean old checkpoints (>7 days)
find .checkpoints -name "*.tar.gz" -mtime +7 -delete

# Compress old checkpoints
tar -czf backup-checkpoints-$(date +%Y%m%d).tar.gz .checkpoints/
rm -rf .checkpoints

# Or increase disk space on system
# Move checkpoints to external storage
mv .checkpoints /mnt/external/checkpoints
ln -s /mnt/external/checkpoints .checkpoints
```

---

## Best Practices

### 1. Create Checkpoints at Key Steps

```python
# Good: Checkpoints at strategic points
system.run('checkpoint', lane='standard', step_number=1, step_name='Start')
run_quality_gates()

system.run('checkpoint', lane='standard', step_number=2, step_name='After QA')
run_tests()

system.run('checkpoint', lane='standard', step_number=3, step_name='After Tests')
run_deployment()
```

### 2. Validate State Before Recovery

```bash
# Always validate first
python scripts/rollback_recovery.py validate

# If validation fails, cleanup
python scripts/rollback_recovery.py cleanup

# Then restore
python scripts/rollback_recovery.py restore --checkpoint-id standard-step2-...
```

### 3. Document Failure Causes

```python
# Capture detailed error info
try:
    run_workflow()
except Exception as e:
    logger.error(f"Workflow failed: {e}", exc_info=True)
    
    # Create checkpoint for debugging
    system.run('checkpoint', 
               lane='standard',
               step_number=5, 
               step_name=f'Failed: {str(e)[:50]}')
```

### 4. Clean Up Old Checkpoints

```bash
# Automated cleanup in cron (weekly)
0 0 * * 0 find /path/to/project/.checkpoints -mtime +7 -delete

# Or manually
find .checkpoints -mtime +7 -delete  # Older than 7 days
find .checkpoints -mtime +1 -delete  # Older than 1 day (during testing)
```

### 5. Monitor Checkpoint Usage

```bash
# Check checkpoint size
du -sh .checkpoints/

# List by size
du -sh .checkpoints/*/ | sort -h

# Archive old checkpoints
tar -czf backup-$(date +%Y%m%d).tar.gz .checkpoints/
rm -rf .checkpoints
```

---

## Integration Examples

### Example 1: GitHub Actions with Recovery

```yaml
name: Workflow with Recovery

on: [push, pull_request]

jobs:
  workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Create checkpoint
        run: |
          python scripts/rollback_recovery.py checkpoint \
            --lane standard --step-number 1 --step-name "Start"
      
      - name: Run quality gates
        run: ruff check agent/ && mypy agent/
      
      - name: Create QA checkpoint
        if: success()
        run: |
          python scripts/rollback_recovery.py checkpoint \
            --lane standard --step-number 2 --step-name "After QA"
      
      - name: Run tests
        run: pytest tests/ -v
      
      - name: Recovery on failure
        if: failure()
        run: |
          python scripts/rollback_recovery.py plan \
            --failure-type test_failure --lane standard
```

### Example 2: Pre-commit with Checkpoint

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Creating checkpoint before commit..."
python scripts/rollback_recovery.py checkpoint \
  --lane standard \
  --step-number 1 \
  --step-name "pre-commit"

# Run checks
if ! pytest tests/ -q; then
    echo "Tests failed. Restoring checkpoint..."
    python scripts/rollback_recovery.py restore \
      --checkpoint-id standard-step1-...
    exit 1
fi

exit 0
```

### Example 3: Development Workflow

```bash
#!/bin/bash
# scripts/dev-with-recovery.sh

set -e

LANE=${1:-standard}
CHANGE_ID=${2:-dev-change}

echo "Starting workflow with recovery..."

# Step 1: Create initial checkpoint
python scripts/rollback_recovery.py checkpoint \
  --lane "$LANE" --step-number 1 --step-name "Initial"

# Step 2: Run workflow
if python scripts/workflow.py --lane "$LANE" --change-id "$CHANGE_ID"; then
    echo "✓ Workflow succeeded"
else
    echo "✗ Workflow failed, attempting recovery..."
    
    # Get recovery plan
    python scripts/rollback_recovery.py plan \
      --failure-type unknown --lane "$LANE"
    
    # Cleanup and retry
    python scripts/rollback_recovery.py cleanup
    python scripts/rollback_recovery.py restore \
      --checkpoint-id standard-step1-...
fi
```

---

## Success Criteria

✅ **Checkpoint Created** - State successfully saved  
✅ **Checkpoint Restored** - State successfully recovered  
✅ **Recovery Planned** - Appropriate strategy identified  
✅ **State Validated** - System integrity verified  
✅ **Execution Resumed** - Workflow continues successfully  
✅ **Time Saved** - Significant speedup vs restarting  

---

## Related Documentation

- [Workflow Lanes Guide](WORKFLOW_LANES_GUIDE.md)
- [POST Deployment Validation](POST_DEPLOYMENT_VALIDATION_GUIDE.md)
- [Analytics & Metrics](ANALYTICS_METRICS_FRAMEWORK.md)
- [Interactive Lane Selector](INTERACTIVE_LANE_SELECTOR_GUIDE.md)

---

**Document Status**: Production Ready  
**Last Updated**: October 24, 2025  
**Version**: 0.1.44
