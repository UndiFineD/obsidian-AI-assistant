# Workflow Visualization Guide

Visual representation of OpenSpec workflow state to help understand progress and identify issues quickly.

## Overview

The workflow visualization system provides multiple views of your workflow state, including:
- Completed steps with checkmarks
- Current step highlighted
- Remaining steps shown as pending
- Checkpoint markers on steps with snapshots
- Progress percentage and statistics

## Display Formats

### Tree View (Default)

Hierarchical view showing all steps with status icons:

```
Workflow: my-feature
────────────────────────────────────────────────────────────

Progress: 6/13 steps (46.2%)

├─ ✓ Step  0: GitHub Issue Sync
├─ ✓ Step  1: Change Setup
├─ ✓ Step  2: Proposal Review ⚑ 1
├─ ✓ Step  3: Capability Spec ⚑ 1
├─ ✓ Step  4: Dependency Spec
├─ ✓ Step  5: Risk Assessment
├─ ▶ Step  6: Script Generation
├─ ○ Step  7: Implementation
├─ ○ Step  8: Testing
├─ ○ Step  9: Documentation
├─ ○ Step 10: Review
├─ ○ Step 11: Merge
└─ ○ Step 12: Archive

────────────────────────────────────────────────────────────
Total Checkpoints: 2
Last Checkpoint: 2025-10-20 09:05:42
```

**Symbols:**
- `✓` Completed step
- `▶` Current step
- `○` Pending step
- `✗` Failed step
- `⊝` Skipped step
- `⚑` Checkpoint marker (with count)

### Timeline View

Linear progress view showing workflow as a timeline:

```
Workflow Timeline: my-feature

✓ ── ✓ ── ✓ ── ✓ ── ✓ ── ✓ ── ▶ ── ○ ── ○ ── ○ ── ○ ── ○ ── ○
 0    1    2    3    4    5    6    7    8    9   10   11   12

[=======================                           ] 46.2%
6/13 steps complete
```

**Best for:** Quick glance at overall progress

### Compact View

Single-line status for integration with other tools:

```
my-feature [6/13 - 46%] | Current: Script Generation | ⚑ 2
```

**Best for:** Scripts, dashboards, CI/CD output

### Detailed View

Comprehensive report with all information:

```
======================================================================
Workflow Detailed Report
======================================================================

Change ID: my-feature
Total Steps: 13

Progress:
  Completed: 6/13 (46.2%)
  Current: 6
  Failed: 0
  Skipped: 0

Completed Steps:
  ✓  0: GitHub Issue Sync
  ✓  1: Change Setup
  ✓  2: Proposal Review ⚑ 1
  ✓  3: Capability Spec ⚑ 1
  ✓  4: Dependency Spec
  ✓  5: Risk Assessment

Current Step:
  ▶  6: Script Generation

Pending Steps:
  ○  7: Implementation
  ○  8: Testing
  ○  9: Documentation
  ○ 10: Review
  ○ 11: Merge
  ○ 12: Archive

Checkpoint Summary:
  Total: 2
  Last: 2025-10-20 09:05:42

======================================================================
```

**Best for:** Detailed analysis, debugging, reports

## Usage

### Command Line

```bash
# Show status with default (tree) format
python scripts/workflow.py --status --change-id my-feature

# Show timeline format
python scripts/workflow.py --status --change-id my-feature --format timeline

# Show compact format
python scripts/workflow.py --status --change-id my-feature --format compact

# Show detailed report
python scripts/workflow.py --status --change-id my-feature --format detailed
```

### Direct Script Usage

```bash
# Using the visualizer script directly
python scripts/workflow_visualizer.py openspec/changes/my-feature

# With specific format
python scripts/workflow_visualizer.py openspec/changes/my-feature --format detailed
```

### Python API

```python
from pathlib import Path
from workflow_visualizer import WorkflowVisualizer

# Create visualizer
visualizer = WorkflowVisualizer(Path("openspec/changes/my-feature"))

# Analyze current state
state = visualizer.analyze_state()

# Render different views
tree_view = visualizer.render_tree(state)
timeline_view = visualizer.render_timeline(state)
compact_view = visualizer.render_compact(state)
detailed_view = visualizer.render_detailed(state)

print(tree_view)
```

## Step Status Indicators

| Symbol | Status | Meaning |
|--------|--------|---------|
| ✓ | Completed | Step finished successfully |
| ▶ | Current | Step currently in progress |
| ○ | Pending | Step not yet started |
| ✗ | Failed | Step failed (requires attention) |
| ⊝ | Skipped | Step was skipped |
| ⚑ | Checkpoint | Step has checkpoint snapshot(s) |

## State Detection

The visualizer automatically detects workflow state by:

1. **File presence**: Checking for step output files (proposal.md, spec.md, etc.)
2. **Checkpoint data**: Reading checkpoint state for completed/failed steps
3. **Git commits**: Tracking which checkpoints correspond to git commits

### Completion Detection

Steps are marked complete based on:
- **Step 1 (Change Setup)**: `proposal.md` exists
- **Step 2 (Proposal Review)**: `proposal.md` validated
- **Step 3 (Capability Spec)**: `spec.md` created
- **Step 6 (Script Generation)**: `test.sh` and `implement.sh` exist
- **Step 9 (Documentation)**: `README.md` exists
- **Other steps**: Detected via checkpoint success markers

## Integration with Checkpoints

The visualization system integrates seamlessly with the checkpoint system:

### Checkpoint Markers

Checkpoints are shown inline with step status:
```
├─ ✓ Step  2: Proposal Review ⚑ 1
├─ ✓ Step  3: Capability Spec ⚑ 1
```

The number after `⚑` indicates how many checkpoints exist for that step.

### Checkpoint Summary

Tree and detailed views include a checkpoint summary:
```
────────────────────────────────────────────────────────────
Total Checkpoints: 2
Last Checkpoint: 2025-10-20 09:05:42
```

### Combined Workflow

```bash
# 1. Run workflow step
python scripts/workflow.py --change-id my-feature --step 3

# 2. Check status
python scripts/workflow.py --status --change-id my-feature

# 3. List checkpoints
python scripts/workflow.py --list-checkpoints --change-id my-feature

# 4. Rollback if needed
python scripts/workflow.py --rollback checkpoint-20251020-090542-step03 --change-id my-feature

# 5. Verify state after rollback
python scripts/workflow.py --status --change-id my-feature
```

## Common Workflows

### Monitoring Long Workflows

```bash
# Start workflow in one terminal
python scripts/workflow.py --change-id my-feature

# Monitor progress in another terminal
watch -n 5 "python scripts/workflow.py --status --change-id my-feature --format compact"
```

### CI/CD Integration

```bash
# In GitHub Actions or Jenkins
- name: Show workflow status
  run: |
    python scripts/workflow.py --status --change-id $CHANGE_ID --format compact
    
- name: Verify progress
  run: |
    STATUS=$(python scripts/workflow.py --status --change-id $CHANGE_ID --format compact)
    echo "Workflow Status: $STATUS"
```

### Debugging Failed Steps

```bash
# 1. Check detailed status
python scripts/workflow.py --status --change-id my-feature --format detailed

# 2. Identify failed steps (shown with ✗)

# 3. Check checkpoints before failure
python scripts/workflow.py --list-checkpoints --change-id my-feature

# 4. Rollback to last good state
python scripts/workflow.py --rollback checkpoint-before-failure --change-id my-feature

# 5. Verify rollback success
python scripts/workflow.py --status --change-id my-feature
```

### Comparing Multiple Changes

```bash
# List all changes
python scripts/workflow.py --list

# Check status of each
for change in feature-a feature-b bugfix-c; do
  echo "=== $change ==="
  python scripts/workflow.py --status --change-id $change --format compact
  echo ""
done
```

## Automatic Visualization

The visualization is automatically shown:

1. **After workflow completion**: Tree view displayed at end
2. **During interactive workflow**: Progress updates shown between steps
3. **On status query**: Via `--status` command

### Disable Automatic Display

If you want to suppress automatic visualization:
- Not currently supported (visualization is always available)
- Use `--format compact` for minimal output

## Troubleshooting

### No Checkpoints Shown

**Symptom**: Checkpoint markers (⚑) not appearing even though checkpoints exist.

**Solutions:**
- Verify checkpoints exist: `--list-checkpoints`
- Check `.checkpoints/` directory exists in change folder
- Ensure checkpoint_manager.py is available
- Verify state.json is not corrupted

### Incorrect Step Status

**Symptom**: Steps shown as complete/pending incorrectly.

**Solutions:**
- Verify required files exist (proposal.md, spec.md, etc.)
- Check checkpoint state: `--list-checkpoints`
- Run validation: `python scripts/workflow.py --validate --change-id <id>`
- Manually inspect `.checkpoints/state.json`

### Visualization Not Available

**Symptom**: `Workflow visualizer not available` error.

**Solutions:**
- Verify `workflow_visualizer.py` exists in `scripts/`
- Check Python path includes scripts directory
- Ensure all dependencies installed
- Try: `python scripts/workflow_visualizer.py --help`

### Colors Not Showing

**Symptom**: Visualization shows escape codes instead of colors.

**Solutions:**
- Enable ANSI colors in terminal
- Windows: Use Windows Terminal or enable VT100 mode
- Set environment: `export TERM=xterm-256color`
- Some CI systems don't support colors (use `--format compact`)

## Advanced Usage

### Custom Status Detection

The visualizer can be extended to detect custom step completion:

```python
# Add to workflow_visualizer.py
step_markers = {
    # ... existing markers ...
    7: ["src/implemented.txt"],  # Custom implementation marker
    8: ["tests/results.json"],    # Custom test results marker
}
```

### Integration with Git

The visualizer tracks git commits with checkpoints:

```python
# Check which git commit a checkpoint corresponds to
visualizer = WorkflowVisualizer(Path("openspec/changes/my-feature"))
state = visualizer.analyze_state()

# Checkpoints include git_commit field
for step_num, count in state.checkpoints.items():
    step_info = visualizer.get_step_info(step_num, state)
    if step_info.has_checkpoint:
        print(f"Step {step_num}: {step_info.checkpoint_count} checkpoints")
```

### Scripting with Compact Format

```bash
#!/bin/bash
# Check if workflow is complete
STATUS=$(python scripts/workflow.py --status --change-id my-feature --format compact)

if [[ $STATUS == *"[13/13"* ]]; then
  echo "Workflow complete!"
  exit 0
else
  echo "Workflow in progress: $STATUS"
  exit 1
fi
```

## Performance

### Overhead

- **Tree/Timeline**: <50ms for typical workflow
- **Compact**: <20ms (fastest format)
- **Detailed**: <100ms (includes all analysis)

### Caching

State detection is performed on-demand (not cached):
- Reads filesystem each time
- Loads checkpoint state from JSON
- No persistent cache needed

For high-frequency monitoring, consider:
- Using compact format (fastest)
- Caching results externally
- Polling less frequently

## See Also

- [Error Recovery](ERROR_RECOVERY.md) - Checkpoint/rollback system
- [Workflow Templates](WORKFLOW_TEMPLATES.md) - Pre-structured proposals
- [API Reference](API_REFERENCE.md) - Workflow automation
- [Comprehensive Specification](COMPREHENSIVE_SPECIFICATION.md) - System architecture
