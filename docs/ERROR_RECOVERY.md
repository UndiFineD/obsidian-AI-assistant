# Error Recovery & Checkpoint System

The OpenSpec workflow includes a comprehensive checkpoint and rollback system to protect
against failures and enable safe experimentation.

## Overview

The checkpoint system automatically creates snapshots of your work before each workflow step executes.
If a step fails or produces unexpected results, you can easily roll back to any previous checkpoint.

### Key Features

- **Automatic Checkpoints**: Created before each step execution
- **Safe Rollback**: Restore to any previous checkpoint with confirmation
- **Storage Management**: Cleanup old checkpoints to save disk space
- **Git Integration**: Tracks git commit hash with each checkpoint
- **Minimal Overhead**: Only snapshots files that exist in change directory

## How It Works

### Automatic Checkpoint Creation

When you run a workflow step, the system automatically:

1. Creates a checkpoint ID: `checkpoint-YYYYMMDD-HHMMSS-step{N}`
2. Snapshots all files in the change directory (except `.checkpoints/` itself)
3. Records metadata: timestamp, step number, git commit, file list
4. Saves the snapshot to `.checkpoints/` subdirectory

**Example:**
```bash
# Running step 3 creates a checkpoint automatically
python scripts/workflow.py --change-id my-feature --step 3

# Creates: openspec/changes/my-feature/.checkpoints/checkpoint-20251020-143025-step03/
```

### Checkpoint Storage

Checkpoints are stored in the change directory:

```
openspec/changes/my-feature/
├── proposal.md
├── todo.md
├── tasks.md
└── .checkpoints/
    ├── state.json                          # Checkpoint metadata
    ├── checkpoint-20251020-143025-step02/  # Step 2 snapshot
    │   ├── proposal.md
    │   └── todo.md
    └── checkpoint-20251020-143156-step03/  # Step 3 snapshot
        ├── proposal.md
        ├── todo.md
        └── tasks.md
```

## Usage Guide

### Listing Checkpoints

View all checkpoints for a change:

```bash
python scripts/workflow.py --list-checkpoints my-feature
```

**Output:**
```
Available checkpoints for 'my-feature':

checkpoint-20251020-143025-step02
  Step: 2 (Create Proposal)
  Created: 2025-10-20 14:30:25
  Status: ✓ Success
  Files: proposal.md, todo.md
  Git: abc123def

checkpoint-20251020-143156-step03
  Step: 3 (Create Capability Specs)
  Created: 2025-10-20 14:31:56
  Status: ✗ Failed
  Files: proposal.md, todo.md, tasks.md
  Git: abc123def
```

### Rolling Back to a Checkpoint

If a step fails or produces bad results, roll back:

```bash
python scripts/workflow.py --rollback checkpoint-20251020-143025-step02
```

**Interactive Confirmation:**
```
Rollback to checkpoint 'checkpoint-20251020-143025-step02'?
  Step: 2 (Create Proposal)
  Created: 2025-10-20 14:30:25
  Files: proposal.md, todo.md

This will:
  1. Create backup of current state
  2. Restore all files from checkpoint
  3. You can rollback to the backup if needed

Continue? [y/N]: y

✓ Created backup: checkpoint-20251020-144500-backup
✓ Restored 2 files
✓ Rollback complete!

You can now:
  - Review restored files
  - Re-run step 3 with fixes
  - Rollback to backup if needed
```

### Cleaning Up Old Checkpoints

Remove old checkpoints to save disk space:

```bash
# Keep only 10 most recent checkpoints (default)
python scripts/workflow.py --cleanup-checkpoints my-feature

# Keep only 5 most recent checkpoints
python scripts/workflow.py --cleanup-checkpoints my-feature 5
```

**Output:**
```
Keeping 5 most recent checkpoints for 'my-feature'

Removing old checkpoints:
  - checkpoint-20251019-101523-step01
  - checkpoint-20251019-102645-step02
  - checkpoint-20251019-103412-step03

✓ Removed 3 old checkpoints
✓ Kept 5 recent checkpoints
```

### Disabling Checkpoints

If you don't want automatic checkpoints (e.g., for testing):

```bash
python scripts/workflow.py --change-id my-feature --step 3 --no-checkpoints
```

## Common Workflows

### Recovering from a Failed Step

**Scenario**: Step 5 failed and created corrupted files.

```bash
# 1. List checkpoints to find the last good state
python scripts/workflow.py --list-checkpoints my-feature

# 2. Roll back to the checkpoint before step 5
python scripts/workflow.py --rollback checkpoint-20251020-143412-step04

# 3. Fix the issue (update code, adjust settings, etc.)

# 4. Re-run step 5
python scripts/workflow.py --change-id my-feature --step 5
```

### Experimenting Safely

**Scenario**: Want to try a risky change without losing current state.

```bash
# 1. Current state is automatically checkpointed before step
python scripts/workflow.py --change-id my-feature --step 6

# 2. If experiment fails, rollback
python scripts/workflow.py --list-checkpoints my-feature
python scripts/workflow.py --rollback checkpoint-20251020-150000-step05

# 3. Try a different approach
python scripts/workflow.py --change-id my-feature --step 6
```

### Managing Storage

**Scenario**: After many workflow runs, too many checkpoints.

```bash
# 1. Check how many checkpoints exist
python scripts/workflow.py --list-checkpoints my-feature

# 2. Clean up, keep only recent ones
python scripts/workflow.py --cleanup-checkpoints my-feature 5

# 3. Verify cleanup
python scripts/workflow.py --list-checkpoints my-feature
```

## Best Practices

### When to Use Checkpoints

✅ **DO use checkpoints for:**
- Production changes that will be merged
- Complex multi-step workflows
- Experimenting with risky changes
- Long-running workflow sessions

❌ **DON'T use checkpoints for:**
- Quick test changes (use `--no-checkpoints`)
- Throwaway experiments
- CI/CD automated runs (unless needed)

### Checkpoint Management

1. **Regular Cleanup**: Run cleanup monthly to prevent disk bloat
2. **Keep Critical Points**: Don't cleanup too aggressively - keep at least 5-10 checkpoints
3. **Document Experiments**: Add notes when creating important checkpoints
4. **Review Before Rollback**: Always list checkpoints to verify target state

### Recovery Strategies

**For Minor Issues:**
- Fix files manually without rollback
- Only rollback if too complex to fix

**For Major Failures:**
- Rollback immediately to last known good state
- Investigate issue before retrying
- Consider using `--dry-run` first

**For Corruption:**
- Rollback to earliest uncorrupted checkpoint
- May need to redo multiple steps
- Review git diff to understand what changed

## Troubleshooting

### Checkpoint Not Created

**Symptom**: No checkpoint created before step execution.

**Solutions:**
- Check that `checkpoint_manager.py` is installed
- Verify no `--no-checkpoints` flag used
- Check disk space available
- Review logs for errors during checkpoint creation

### Rollback Failed

**Symptom**: Error during rollback operation.

**Solutions:**
- Check that checkpoint ID is correct (use `--list-checkpoints`)
- Verify checkpoint directory exists in `.checkpoints/`
- Ensure no file permission issues
- Review backup created before rollback

### Too Many Checkpoints

**Symptom**: Disk space running low.

**Solutions:**
- Run `--cleanup-checkpoints` with low keep count (e.g., 5)
- Manually delete `.checkpoints/` directory for old changes
- Consider using `--no-checkpoints` for test workflows

### Checkpoint Metadata Corrupted

**Symptom**: `state.json` file is corrupted or missing.

**Solutions:**
- If snapshots still exist, manually restore files from `.checkpoints/checkpoint-*/`
- Delete corrupted `state.json` - system will recreate on next checkpoint
- Consider git history as backup if checkpoints lost

## Technical Details

### Checkpoint Metadata

Each checkpoint includes:
- **checkpoint_id**: Unique identifier (timestamp-based)
- **step_number**: Which workflow step created it
- **step_name**: Human-readable step description
- **timestamp**: When checkpoint was created
- **files**: List of files included in snapshot
- **git_commit**: Current git commit hash (if in git repo)
- **success**: Whether step completed successfully
- **notes**: Optional description (for future enhancement)

### State Persistence

Checkpoint state is stored in JSON format:

```json
{
  "change_id": "my-feature",
  "checkpoints": [
    {
      "checkpoint_id": "checkpoint-20251020-143025-step02",
      "step_number": 2,
      "step_name": "Create Proposal",
      "timestamp": "2025-10-20T14:30:25",
      "files": ["proposal.md", "todo.md"],
      "git_commit": "abc123def456",
      "success": true,
      "notes": null
    }
  ]
}
```

### Rollback Process

1. **Validation**: Verify checkpoint exists and is valid
2. **Confirmation**: Prompt user to confirm rollback
3. **Backup**: Create backup checkpoint of current state
4. **Restore**: Copy all files from checkpoint snapshot
5. **Verification**: Confirm all files restored successfully

### Storage Overhead

- **Metadata**: ~1 KB per checkpoint (state.json)
- **Snapshots**: Size depends on files in change directory
- **Typical**: 10-50 KB per checkpoint for documentation changes
- **Large**: 100-500 KB per checkpoint if including generated code

## Advanced Usage

### Programmatic Access

```python
from scripts.checkpoint_manager import CheckpointManager

# Initialize manager
manager = CheckpointManager("openspec/changes/my-feature")

# Create checkpoint
manager.create_checkpoint(
    step_num=3,
    step_name="Create Capability Specs",
    notes="Before major refactor"
)

# List checkpoints
checkpoints = manager.list_checkpoints()
for cp in checkpoints:
    print(f"{cp.checkpoint_id}: Step {cp.step_number}")

# Rollback
manager.rollback_to_checkpoint("checkpoint-20251020-143025-step02")

# Cleanup
manager.cleanup_old_checkpoints(keep_count=5)
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Run workflow with checkpoints
  run: |
    python scripts/workflow.py --change-id ${{ github.event.issue.number }} --step 0
    
- name: Cleanup old checkpoints on success
  if: success()
  run: |
    python scripts/workflow.py --cleanup-checkpoints ${{ github.event.issue.number }} 5
    
- name: Show checkpoint info on failure
  if: failure()
  run: |
    python scripts/workflow.py --list-checkpoints ${{ github.event.issue.number }}
```

## FAQ

**Q: Are checkpoints stored in git?**

A: No, `.checkpoints/` directories are gitignored by default. Checkpoints are local-only for safety.

**Q: Can I share checkpoints with team members?**

A: No, checkpoints are designed for local use only. Use git for sharing state.

**Q: What happens if I delete a checkpoint manually?**

A: The system will update `state.json` on next checkpoint operation. Safe to delete old checkpoints manually.

**Q: Can I checkpoint in the middle of a step?**

A: Not automatically. Checkpoints are created before step execution.
You can manually create checkpoints via programmatic API if needed.

**Q: Do checkpoints include generated code?**

A: Yes, all files in the change directory are included (except `.checkpoints/` itself).

**Q: How do checkpoints interact with git?**

A: Checkpoints track git commit hash for reference but don't modify git state. They're independent of git operations.

## See Also

- [Workflow Templates](WORKFLOW_TEMPLATES.md) - Pre-structured proposals
- [API Reference](API_REFERENCE.md) - Workflow automation
- [Comprehensive Specification](COMPREHENSIVE_SPECIFICATION.md) - System architecture
