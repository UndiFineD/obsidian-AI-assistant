# Python Workflow Usage Guide

## Quick Start

The Python workflow system provides a clean, maintainable alternative to the PowerShell version with better encoding
handling and easier debugging.

### Basic Commands

```bash
# List all active changes with completion percentages
python scripts\workflow.py --list

# Create a new change and run step 0
python scripts\workflow.py --change-id my-feature --step 0

# Run step 0 in dry-run mode (preview only)
python scripts\workflow.py --change-id my-feature --step 0 --dry-run

# Validate change directory structure
python scripts\workflow.py --change-id my-feature --validate

# Run complete interactive workflow (all steps)
python scripts\workflow.py --change-id my-feature

# Resume workflow from where it left off
python scripts\workflow.py --change-id my-feature  # Checks todo.md for completed steps

# Archive a completed change
python scripts\workflow.py --change-id my-feature --archive
```

### Command-Line Options

**Mode Selection** (mutually exclusive):
- `--list` - List all active changes
- `--validate` - Validate change directory structure
- `--archive` - Archive a completed change
- (default) - Run workflow (interactive or single step)

**Change Identification**:
- `--change-id CHANGE_ID` - Change identifier (kebab-case, e.g., "update-readme")

**Change Metadata**:
- `--title TITLE` - Human-readable title (auto-derived from change-id if not provided)
- `--owner OWNER` - GitHub handle (e.g., "@username", auto-detected from git if not provided)

**Execution Control**:
- `--step N` - Execute specific step (0-12)
- `--dry-run` - Preview actions without making changes
- `--release-type {patch|minor|major}` - Optional version bump for Step 1 (e.g., 0.1.26 → 0.1.27)

## Workflow Steps

The workflow consists of 13 steps (0-12):

| Step | Description | Module Status |
|------|-------------|---------------|
| 0 | Create TODOs | ✅ Complete (`workflow-step00.py`) |
| 1 | Version Snapshot & Bump (optional) | ✅ Complete (`workflow-step01.py`) |
| 2 | Proposal | ✅ Complete (`workflow-step02.py`) |
| 3 | Specification | ✅ Complete (`workflow-step03.py`) |
| 4 | Task Breakdown | ✅ Complete (`workflow-step04.py`) |
| 5 | Test Definition | ✅ Complete (`workflow-step05.py`) |
| 6 | Script Changes | ✅ Complete (`workflow-step06.py`) |
| 7 | Implementation | ✅ Complete (`workflow-step07.py`) |
| 8 | Testing | ✅ Complete (`workflow-step08.py`) |
| 9 | Documentation & Review | ✅ Complete (`workflow-step09.py`) |
| 10 | Git Commit | ✅ Complete (`workflow-step10.py`) |
| 11 | Archive | ✅ Complete (`workflow-step11.py`) |
| 12 | Pull Request | ✅ Complete (`workflow-step12.py`) |

## Architecture

### File Structure

```
scripts/
├── workflow.py             # Main CLI orchestrator (350+ lines)
├── workflow-helpers.py     # Shared utilities (400+ lines)
└── workflow-stepXX.py      # Individual step modules (13 files)
    ├── workflow-step00.py  # ✅ Create TODOs
    ├── workflow-step01.py  # ✅ Version Snapshot
    ├── workflow-step02.py  # ✅ Proposal
    ├── workflow-step03.py  # ✅ Specification
    ├── workflow-step04.py  # ✅ Task Breakdown
    ├── workflow-step05.py  # ✅ Test Definition
    ├── workflow-step06.py  # ✅ Script Changes
    ├── workflow-step07.py  # ✅ Implementation
    ├── workflow-step08.py  # ✅ Testing
    ├── workflow-step09.py  # ✅ Documentation
    ├── workflow-step10.py  # ✅ Git Commit
    ├── workflow-step11.py  # ✅ Archive
    └── workflow-step12.py  # ✅ Pull Request
```

### Module Design

Each step module follows this pattern:

```python
#!/usr/bin/env python3
"""Step N: [Description]"""

import sys
import importlib.util
from pathlib import Path

# Import helpers
SCRIPT_DIR = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "workflow_helpers",
    SCRIPT_DIR / "workflow-helpers.py"
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def invoke_stepN(change_path, **kwargs):
    """
    Execute Step N of the workflow.
    
    Args:
        change_path: Path to change directory
        **kwargs: Step-specific arguments
        
    Returns:
        True if successful, False otherwise
    """
    helpers.write_step(N, "Step Description")
    
    # Step logic here
    
    # Mark step complete in todo.md
    todo_path = change_path / "todo.md"
    if todo_path.exists():
        content = todo_path.read_text(encoding='utf-8')
        content = content.replace(
            f'[ ] **{N}. Step Name',
            f'[x] **{N}. Step Name'
        )
        helpers.set_content_atomic(todo_path, content)
    
    helpers.write_success(f"Step {N} completed")
    return True


if __name__ == '__main__':
    # Self-test code
    test_path = Path("openspec/changes/test-change")
    test_path.mkdir(parents=True, exist_ok=True)
    
    success = invoke_stepN(test_path, dry_run=True)
    sys.exit(0 if success else 1)
```

## Interactive Workflow Mode

When you run without `--step`, the workflow enters interactive mode:

1. **Auto-resume**: Checks `todo.md` for completed steps and resumes from next uncompleted step
2. **Sequential execution**: Runs steps in order (0 → 12)
3. **Error handling**: Stops on first failure, provides recovery instructions
4. **Progress tracking**: Updates `todo.md` checkboxes as each step completes

Example:

```bash
# Start new change
python scripts\workflow.py --change-id my-feature

# Workflow runs steps 0-12 sequentially
# If step 5 fails, it stops and tells you how to resume

# After fixing the issue
python scripts\workflow.py --change-id my-feature --step 5

# Continue from where you left off
python scripts\workflow.py --change-id my-feature
```

## Features

### 1. List Changes

Shows all active changes with completion percentages calculated from `todo.md`:

```bash
$ python scripts\workflow.py --list

Active Changes:
  [69%] 2025-10-18-automate-github-issue-import
  [100%] 2025-10-18-merge-requirements
  [47%] 2025-10-18-openspec-scaffold-script
  [0%] issue-15
  [???] test-change  # No todo.md found
```

### 2. Structure Validation

Validates that all required OpenSpec files exist:

```bash
$ python scripts\workflow.py --change-id my-feature --validate

Validating change: my-feature

Checking required files:
  ✓ todo.md exists
  ✓ proposal.md exists
  ✓ spec.md exists
  ✓ tasks.md exists
  ✓ test_plan.md exists

✓ Change structure is valid
```

### 3. Dry-Run Mode

Preview what would happen without making changes:

```bash
$ python scripts\workflow.py --change-id test --step 0 --dry-run

Executing Step 0...

═════════  STEP 0: Create TODOs ═════════
[DRY RUN] Would create: openspec\changes\test\todo.md
  Template: openspec\templates\todo.md
  Title: Test
  Owner: @username

✓ Step 0 completed successfully
```

### 4. Documentation Review (Step 9)

Displays a concise summary of key documentation files and writes `review_summary.md`:

```bash
$ python scripts\workflow.py --change-id my-feature --step 9

═════════  STEP 9: Documentation ═════════
Documentation review summary:
  - proposal: 45 lines, title: My Feature Proposal
  - spec: 120 lines, title: Technical Specification
  - tasks: 67 lines, title: Implementation Tasks
  - test_plan: 89 lines, title: Test Plan

Updated: openspec\changes\my-feature\doc_changes.md
Wrote: openspec\changes\my-feature\review_summary.md

✓ Step 9 completed successfully
```

The `review_summary.md` includes quick links and line counts for proposal, spec, tasks, and test_plan documents to
facilitate review.

### 5. Comprehensive Script Generation (Step 6)

Automatically generates test and implementation scripts based on change documentation:

```bash
$ python scripts\workflow.py --change-id my-feature --step 6

═════════  STEP 6: Script Generation & Tooling ═════════
Analyzing documentation for script requirements...
Found automation requirements in spec.md

Detected Script Requirements:
  Purpose: testing/validation
  Script Types: Python
  Affected Files: backend/test.py, frontend/app.js

Generating test script: test.py
Generated: test.py
Generating implementation script: implement.py
Generated: implement.py
```

**Generated Scripts:**

- **test.py** (~160 lines): Comprehensive test harness with validation functions
    - Tests proposal, spec, tasks documents
    - Validates affected files exist
    - Pattern matching for required sections
    - Results tracking and summary

- **implement.py** (~140 lines): Implementation framework with task execution
    - Parses tasks.md for implementation steps
    - Verifies affected files
    - Supports `--what-if` dry-run mode
    - Results tracking and error handling

**Features:**
- Intelligent requirement detection from proposal and spec
- Detects script types (Python, PowerShell, Bash)
- Identifies affected files automatically
- Generates executable scripts with proper permissions
- Skips generation if no requirements detected

### 6. GitHub Issue Sync (Step 10)

Automatically syncs open GitHub issues to create change folders with pre-filled proposal and todo files:

```bash
$ python scripts\workflow.py --change-id my-feature --step 10

═════════  STEP 10: Git Operations & GitHub Issue Sync ═════════
Fetching open GitHub issues...
Found 3 open issue(s)
  [DRY-RUN] Would create: issue-15-testopenspecintegration-test-generated-changes-exi
    Title: testOpenSpecIntegration.test_generated_changes_exist
  [DRY-RUN] Would create: issue-6-ci-cd-pipline-issue-1
    Title: CI/CD pipline issue 1
  [DRY-RUN] Would create: issue-5-ci-cd-pipeline-issues
    Title: CI/CD pipeline issues
Synced 3 issue(s) to change folders
[DRY-RUN] Would write git_notes.md:
## Git Context

- Branch: release-0.1.26
- Suggested commit message: chore(openspec): my-feature
```

**Requirements:**
- GitHub CLI (`gh`) must be installed and authenticated
- Install: [https://cli.github.com/](https://cli.github.com/)

**Features:**
- Fetches open GitHub issues from the repository
- Creates change folders named `issue-{number}-{sanitized-title}`
- Generates `proposal.md` from issue title, body, and labels
- Pre-populates `todo.md` with all workflow steps
- Skips issues that already have change folders
- Creates git notes for the current change

### 7. Cross-Validation (Step 12)

Performs 5-way documentation validation:

1. **Proposal → Tasks**: Ensures all "What Changes" are reflected in tasks.md
2. **Spec → Test Plan**: Verifies acceptance criteria have test coverage
3. **Tasks → Spec**: Checks implementation tasks match specifications
4. **Orphaned References**: Detects broken markdown links
5. **Affected Files**: Validates consistency across documents

## Migration from PowerShell

### Key Differences

| Aspect | PowerShell | Python |
|--------|------------|--------|
| Encoding | Smart quote issues | UTF-8 works perfectly |
| Syntax | Verbose | Clean and readable |
| Debugging | Poor error messages | Stack traces, line numbers |
| Shell Integration | Native | subprocess module |
| Maintenance | Complex | Standard patterns |

### Migration Steps

1. **Immediate**: Use Python workflow for new changes
2. **Gradual**: Continue PowerShell for in-progress changes
3. **Complete**: Archive PowerShell version once all changes processed

### Compatibility

Both workflows work with the same OpenSpec directory structure:
- No changes needed to `openspec/` directory
- Templates remain the same
- Git integration unchanged
- Documentation formats identical

## Troubleshooting

### Import Errors

If you see module import errors:

```bash
# Check Python version (3.8+ required)
python --version

# Verify files exist
Test-Path scripts\workflow.py
Test-Path scripts\workflow-helpers.py
```

### Step Module Not Found

```
Step 5 module not found
Expected: scripts/workflow-step05.py
```

**Solution**: All 13 step modules (00-12) are now implemented. If you see this error, verify:
- You're running from the project root directory
- The `scripts/workflow-step05.py` file exists and is readable
- The Python environment has proper permissions

### Template Not Found

```
Template not found: openspec\templates\todo.md
```

**Solution**: Ensure you're running from the project root directory.

### Git User Not Detected

If `--owner` shows `@unknown`:

```bash
# Set git user.name
git config --global user.name "Your Name"

# Or provide explicitly
python scripts\workflow.py --change-id my-feature --owner "@username"
```

## Development

### Adding a New Step Module

1. **Copy template** from `workflow-step00.py`
2. **Update function name**: `invoke_step0` → `invoke_stepN`
3. **Implement step logic** specific to that step
4. **Update step number** in `write_step(N, "Description")`
5. **Update checkbox pattern** in todo.md marking logic
6. **Add self-test** in `__main__` block
7. **Test in dry-run mode**

### Testing

```bash
# Unit test a single step module
python scripts\workflow-step00.py

# Integration test with dry-run
python scripts\workflow.py --change-id test-step --step 0 --dry-run

# Full workflow test
python scripts\workflow.py --change-id full-test --dry-run
```

### Code Quality

Follow these conventions:

- **UTF-8 encoding**: All files use `encoding='utf-8'`
- **Type hints**: Optional but recommended for complex functions
- **Docstrings**: Required for all public functions
- **Error handling**: Return `True`/`False`, don't raise exceptions
- **Logging**: Use `helpers.write_*()` functions for output
- **Atomic writes**: Use `helpers.set_content_atomic()` for file operations

## Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| `--list` | ~100ms | Scans all change directories |
| `--validate` | ~50ms | Checks 5 files |
| `--step 0` | ~200ms | Template copy + placeholder replacement |
| Interactive workflow | Variable | Depends on step implementations |

### Optimization Tips

1. **Use specific steps** instead of full workflow when iterating
2. **Use dry-run mode** to preview without I/O overhead
3. **Run validation** before long-running steps
4. **Cache git user** detection by providing `--owner` explicitly

## Future Enhancements

### Planned Features

- [ ] Parallel step execution (where dependencies allow)
- [ ] Step progress indicators (spinners, progress bars)
- [ ] Undo/rollback capability
- [ ] Workflow templates (feature, bugfix, docs)
- [ ] Integration with GitHub CLI for PR creation
- [ ] VS Code tasks integration
- [ ] Slack/Discord notifications

### Contribution Guidelines

When adding features:

1. **Maintain backward compatibility** with OpenSpec structure
2. **Follow existing patterns** from workflow-step00.py
3. **Add dry-run support** for all destructive operations
4. **Update this guide** with new features
5. **Test thoroughly** with various change states

## Support

- **Issues**: Report in GitHub issues with `workflow` label
- **Questions**: See `WORKFLOW_MODULARIZATION_QUICKSTART.md`
- **Architecture**: See `WORKFLOW_MODULARIZATION.md`
- **Changes**: See `WORKFLOW_MODULARIZATION_SUMMARY.md`
