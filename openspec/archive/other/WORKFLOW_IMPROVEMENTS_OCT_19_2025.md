# Workflow Script Improvements - October 19, 2025

## Summary

Improved `scripts/workflow.ps1` to reduce excessive warnings and fix version handling issues.

## Changes Made

### 1. **Version Storage Improvements**
- **Before**: Stored new version in `_new_version.txt` file in change directory
- **After**: Store version in script-level variable `$script:NewVersion`
- **Benefits**:
  - Cleaner - no temporary files left in change directories
  - More reliable - version persists across steps in same script execution
  - Simpler - no file I/O for version passing between steps

### 2. **Fixed "todo.md not found" Warnings**
- **Issue**: After Step 11 (Archive), todo.md is moved to archive, but Step 12 tried to update it
- **Fix**: Modified `Update-TodoFile` function to silently skip if todo.md doesn't exist
- **Result**: No more warnings about missing todo.md after archiving

### 3. **Reduced Excessive Validation Warnings**

#### Test Plan Validation (Step 5)
- **Before**: Showed ALL missing items from todo.md (50+ warnings including workflow template items)
- **After**: 
  - Skip todo.md validation (it's workflow template, not test requirements)
  - Show max 5 alignment issues, then summary
  - Focus on actual requirements from proposal.md, spec.md, tasks.md
- **Example Output**:
  ```
  WARNING: test_plan.md review found 3 alignment issue(s):
    - Missing requirement from proposal.md: 'xyz'
    - Missing acceptance criteria from spec.md: 'abc'
    - Missing test case from tasks.md: 'def'
  Please edit test_plan.md to ensure alignment with proposal.md, spec.md, and tasks.md.
  ```

#### Proposal Validation (Step 2)
- **Before**: Listed all quality issues as warnings
- **After**: Simple info message
- **Example Output**:
  ```
  Proposal has 2 quality suggestion(s) - proceeding anyway
  ✓ proposal.md validated
  ```

#### Spec Validation (Step 3)
- **Before**: Listed all quality issues as warnings
- **After**: Simple info message
- **Example Output**:
  ```
  Specification has 1 quality suggestion(s) - proceeding anyway
  ✓ spec.md validated
  ```

## Impact

### Before
```
WARNING: Specification validation found quality issues:
WARNING:   - No standard specification sections found
WARNING:   - Specification lacks structured lists
WARNING: test_plan.md review found alignment issues:
WARNING:   - Missing actionable item from todo.md: 'Create new release branch'
WARNING:   - Missing actionable item from todo.md: 'Update version in CHANGELOG.md'
WARNING:   - Missing actionable item from todo.md: 'Update version in README.md'
... (50+ more lines of warnings) ...
WARNING: todo.md not found at C:\...\openspec\changes\2025-10-14-update-doc-claude\todo.md
```

### After
```
Specification has 2 quality suggestion(s) - proceeding anyway
✓ spec.md validated
test_plan.md review found 2 alignment issue(s):
  - Missing requirement from proposal.md: 'governance requirement'
  - Missing requirement from proposal.md: 'documentation tracking'
Please edit test_plan.md to ensure alignment with proposal.md, spec.md, and tasks.md.
```

## Benefits

1. **Cleaner Output**: Workflow execution is much easier to read and follow
2. **Actionable Warnings**: Only show warnings that require action, not informational suggestions
3. **No False Positives**: Eliminated warnings about normal workflow behavior (archiving)
4. **Better Version Handling**: Version information reliably passes from Step 1 to Step 12
5. **Improved PR Creation**: PR titles now correctly include version (e.g., "chore(openspec): Update docs [v0.1.15]")

## Technical Details

### Code Changes

**File**: `scripts/workflow.ps1`

1. Added script-level variable (line ~111):
   ```powershell
   $script:NewVersion = $null  # Shared version variable set in Step 1
   ```

1. Modified Step 1 (lines ~365-369):
   ```powershell
   # Store version in script-level variable for use in later steps
   $script:NewVersion = $newVersion
   Write-Info "New version $newVersion stored for PR creation in Step 12"
   ```

1. Modified Step 12 (lines ~1892-1895):
   ```powershell
   # Use version from Step 1 (stored in script variable)
   $newVersion = $script:NewVersion
   ```

1. Modified `Update-TodoFile` function (lines ~2008-2011):
   ```powershell
   if (!(Test-Path $todoPath)) {
       # Silently skip if todo.md doesn't exist (e.g., after archiving)
       return
   }
   ```

1. Modified Step 5 validation (lines ~1103-1106):
   ```powershell
   # Skip todo.md checking - it contains workflow templates, not test requirements
   # Test plan should focus on actual test cases from tasks.md and spec.md
   ```

1. Modified validation warnings to show concise summaries instead of full lists

## Testing

✅ Script loads without syntax errors  
✅ Version correctly stored in script variable  
✅ No warnings about missing todo.md after archiving  
✅ Validation warnings are concise and actionable  

## Future Improvements

- Consider adding `-Verbose` flag to show detailed validation issues on demand
- Add `-Quiet` flag to suppress all non-error output for CI/CD
- Create validation report file that can be reviewed separately

---

**Author**: Copilot  
**Date**: October 19, 2025  
**Related**: `scripts/workflow.ps1`, OpenSpec workflow automation
