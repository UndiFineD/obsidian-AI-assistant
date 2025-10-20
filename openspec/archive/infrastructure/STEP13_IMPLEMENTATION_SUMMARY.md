# Step 13 Implementation: Pull Request Creation

## Summary

Successfully implemented Step 13 for automatic GitHub Pull Request creation,
extending the OpenSpec workflow from 13 steps (0-12) to 14 steps (0-13).

## Implementation Date

October 17, 2025

## Changes Made

### 1. Created `scripts/workflow-step13.py` (New File - 359 lines)

**Purpose**: Create GitHub Pull Requests for completed changes using GitHub CLI (`gh`)

**Key Features**:
- Extract metadata from `proposal.md` (title, why, affected specs/files/code)
- Build comprehensive PR title with optional version number
- Generate detailed PR body with:
    - Change summary
    - Version information
    - Documentation links (proposal.md, spec.md, tasks.md, test_plan.md)
    - Affected specs/files/code
    - Completion checklist
    - OpenSpec workflow reference
- Check for existing PRs to avoid duplicates
- Support dry-run mode for previewing PR content
- Handle archived changes (in `openspec/archive/`)
- Graceful fallback when `gh` CLI not available (manual PR instructions)
- Progress indicators during PR creation
- Support for passing version from Step 1

**Functions**:
- `get_change_doc_info(change_path)` - Extract metadata from proposal.md
- `get_current_branch()` - Get current git branch name
- `check_gh_cli_available()` - Check if GitHub CLI is installed
- `check_existing_pr(branch)` - Check for existing PR on branch
- `create_pr_with_gh(title, body, branch, base)` - Create PR using `gh` CLI
- `invoke_step13(change_path, dry_run, new_version)` - Main step function

**Reference Implementation**: Ported from PowerShell (`scripts/workflow2.ps1` Step 12: lines 2388-2546)

### 2. Updated `scripts/workflow.py` (2 changes)

**Line 679**: Updated `--step` argument choices
```python
# Before
choices=range(0, 13),  # Steps 0-12
help='Execute specific step (0-12)'

# After
choices=range(0, 14),  # Steps 0-13
help='Execute specific step (0-13)'
```

**Line 533**: Updated total steps calculation
```python
# Before
total_steps = 13 - start_step

# After
total_steps = 14 - start_step
```

### 3. Updated `scripts/workflow_visualizer.py` (3 changes)

**Lines 80-94**: Added Step 13 to STEPS dictionary
```python
STEPS = {
    0: "GitHub Issue Sync",
    1: "Change Setup",
    2: "Proposal Review",
    3: "Capability Spec",
    4: "Dependency Spec",
    5: "Risk Assessment",
    6: "Script Generation",
    7: "Implementation",
    8: "Testing",
    9: "Documentation",
    10: "Review",
    11: "Merge",
    12: "Archive",
    13: "Pull Request",  # NEW
}
```

**Line 198**: Updated current step detection logic
```python
# Before
current = max(completed) + 1 if max(completed) < 12 else None

# After
current = max(completed) + 1 if max(completed) < 13 else None
```

**Line 202**: Updated total_steps from 13 to 14
```python
# Before
total_steps=13,

# After
total_steps=14,
```

## Verification

### Module Loading Test
```bash
python -c "import sys; sys.path.insert(0, 'scripts'); ..."
# Result: Module loaded: True
```

### Help Text Verification
```bash
python scripts/workflow.py --help
# Output: --step N              Execute specific step (0-13)
```

## Usage Examples

### Execute Step 13 for a change
```bash
python scripts/workflow.py --change-id my-feature --step 13
```

### Dry-run Step 13 (preview PR)
```bash
python scripts/workflow.py --change-id my-feature --step 13 --dry-run
```

### Full workflow including PR creation
```bash
python scripts/workflow.py --change-id my-feature
# Will execute all steps 0-13 automatically
```

### Standalone execution with version
```bash
python scripts/workflow-step13.py openspec/changes/my-feature --version=1.2.3
```

## PR Body Example

When Step 13 creates a PR, it generates content like:

```markdown
# OpenSpec Change: my-feature

## Version
- New version: 1.2.3

## Summary
Brief description of the change from proposal.md "Why" section

## Documentation
- **Proposal**: [openspec/changes/my-feature/proposal.md](...)
- **Specification**: [openspec/changes/my-feature/spec.md](...)
- **Tasks**: [openspec/changes/my-feature/tasks.md](...)
- **Test Plan**: [openspec/changes/my-feature/test_plan.md](...)

## Changes
- **Affected specs**: [list from proposal]
- **Affected files**: [list from proposal]
- **Affected code**: [list from proposal]

## Checklist
- [x] All workflow steps completed (0-12)
- [x] Change archived to openspec/archive/my-feature/
- [x] Documentation complete and validated
- [x] Tests passing
- [x] Ready for review

## Reference
- OpenSpec Workflow: [openspec/PROJECT_WORKFLOW.md](...)
```

## Benefits

1. **Complete Automation**: End-to-end workflow from change creation to PR
2. **Comprehensive Documentation**: PR body includes all relevant links and metadata
3. **Version Tracking**: Integrates with Step 1 version bumping
4. **Duplicate Prevention**: Checks for existing PRs before creating new ones
5. **Graceful Degradation**: Provides manual instructions if `gh` CLI unavailable
6. **Dry-Run Support**: Preview PR content before creation
7. **Archive Support**: Works with both active and archived changes

## Testing

### Manual Test Plan

1. **Test PR Creation**:
```bash
python scripts/workflow.py --change-id test-pr-creation --step 13
```

2. **Test Dry-Run**:
```bash
python scripts/workflow.py --change-id test-pr-creation --step 13 --dry-run
```

3. **Test Without gh CLI**:
   - Temporarily rename `gh.exe` and verify fallback instructions

4. **Test With Archived Change**:
   - Run Step 13 on change that was archived in Step 11

5. **Test Duplicate Detection**:
   - Run Step 13 twice on same branch, verify it detects existing PR

## Integration Points

### Receives from Previous Steps:
- **Step 1**: `new_version` (optional, stored in script variable)
- **Step 2-9**: Documentation files (proposal.md, spec.md, tasks.md, test_plan.md)
- **Step 10**: Git branch and commits
- **Step 11**: Archive location (if archived)
- **Step 12**: Validation completion

### Provides:
- GitHub Pull Request with comprehensive documentation
- PR URL for tracking
- Integration with GitHub workflows (CI/CD triggers)

## Dependencies

### Required:
- Python 3.7+
- Git (for branch detection)

### Optional
- GitHub CLI (`gh`) - for automated PR creation
    - Without `gh`: Provides manual PR creation instructions
    - Install: https://cli.github.com/

### Python Modules:
- Standard library only: `os`, `subprocess`, `sys`, `tempfile`, `pathlib`, `re`, `json`
- Custom: `progress_indicators` (from scripts/)

## Future Enhancements

Potential improvements for future versions:

1. **Auto-assign Reviewers**: Parse `proposal.md` for suggested reviewers
2. **Label Management**: Auto-apply labels based on change type
3. **Milestone Integration**: Link PR to active milestone
4. **Draft PRs**: Option to create draft PRs for work-in-progress
5. **PR Template Support**: Use custom PR templates from `.github/`
6. **Multi-repo Support**: Create PRs across related repositories
7. **Slack/Teams Integration**: Post PR notifications to team channels

## Documentation Updates Needed

The following documentation should be updated to reflect Step 13:

1. **openspec/PROJECT_WORKFLOW.md** - Update workflow diagram (12→13 steps)
2. **docs/WORKFLOW_MODULARIZATION.md** - Add Step 13 section
3. **docs/WORKFLOW_MODULARIZATION_SUMMARY.md** - Update step count
4. **README.md** - Update workflow overview
5. **.github/copilot-instructions.md** - Update workflow step list
6. **Phase 4 Documentation** - Add Step 13 to feature list

## Backward Compatibility

✅ **Fully backward compatible**:
- Existing workflows (Steps 0-12) continue to work unchanged
- Step 13 is optional - workflow can complete at Step 12
- No breaking changes to existing step interfaces
- Old documentation references Steps 0-12 remain valid (subset)

## Alignment with OpenSpec Goals

This implementation aligns with OpenSpec's core principles:

1. **Automation**: Reduces manual PR creation effort
2. **Documentation**: Ensures PRs link to complete change documentation
3. **Traceability**: Links PRs back to proposals, specs, and tasks
4. **Consistency**: Standardizes PR format across all changes
5. **Governance**: Enforces checklist before PR creation

## Success Criteria

- [x] workflow-step13.py created and functional
- [x] workflow.py updated to support Step 13
- [x] workflow_visualizer.py updated with Step 13
- [x] Module loads successfully
- [x] Help text shows Steps 0-13
- [x] Ported logic from PowerShell reference implementation
- [x] Dry-run mode supported
- [x] Graceful fallback without `gh` CLI
- [x] Progress indicators integrated
- [x] Version parameter supported
- [ ] Manual testing completed (pending)
- [ ] Documentation updated (pending)
- [ ] Integration test added (pending)

## Related Files

- **Primary**: `scripts/workflow-step13.py` (new)
- **Updated**: `scripts/workflow.py`, `scripts/workflow_visualizer.py`
- **Reference**: `scripts/workflow2.ps1` (PowerShell implementation)
- **Dependencies**: `scripts/progress_indicators.py`, `scripts/workflow_helpers.py`

## Commit Message (Suggested)

```
feat(openspec): Add Step 13 - Pull Request Creation

Extends OpenSpec workflow from 13 to 14 steps (0-13) with automatic GitHub PR creation.

Features:
- Create PRs using GitHub CLI (gh)
- Comprehensive PR body with documentation links
- Version integration from Step 1
- Duplicate PR detection
- Graceful fallback without gh CLI
- Dry-run preview support
- Archive change support

Changes:
- New: scripts/workflow-step13.py (359 lines)
- Updated: scripts/workflow.py (2 changes)
- Updated: scripts/workflow_visualizer.py (3 changes)

Reference: Ported from scripts/workflow2.ps1 Step 12

OpenSpec-Change: add-step-13-pull-request
Docs: openspec/changes/add-step-13-pull-request/
```

## Timeline

- **Request**: October 17, 2025 (user: "Add Step 13 for Pull Request creation")
- **Reference Provided**: scripts/workflow2.ps1 (PowerShell implementation)
- **Implementation**: October 17, 2025
- **Files Created**: 1 (workflow-step13.py)
- **Files Updated**: 2 (workflow.py, workflow_visualizer.py)
- **Total Lines Added**: 359 (workflow-step13.py)
- **Total Lines Modified**: 5 (workflow.py + workflow_visualizer.py)
- **Status**: ✅ Implementation Complete, Testing Pending

---

**Implementation by**: GitHub Copilot
**Session**: October 17, 2025
**Context**: Continuation of Phase 4 completion and template auto-selection enhancement
