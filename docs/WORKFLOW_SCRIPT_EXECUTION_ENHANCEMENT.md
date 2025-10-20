# Workflow Script Execution Enhancement
## Automatic test.py and implement.py Execution in OpenSpec Workflow

**Date:** October 20, 2025  
**Status:** ✅ Implementation Complete  
**Changes:** workflow-step07.py and workflow-step08.py  

---

## Summary of Changes

The OpenSpec workflow has been enhanced to **automatically execute generated test and implementation scripts** instead of just generating them passively.

### ✅ What Was Changed

#### **workflow-step07.py (Implementation Step)**
- **Before:** Only created/updated implementation_notes.md
- **After:** 
  - ✅ Executes test.py to validate the change
  - ✅ Executes implement.py to run implementation tasks
  - ✅ Captures execution results and logs them
  - ✅ Updates implementation_notes.md with results

#### **workflow-step08.py (Testing Step)**
- **Before:** Only created placeholder test_results.md
- **After:**
  - ✅ Verifies implementation changes (files modified/created)
  - ✅ Checks git diff for actual project changes
  - ✅ Executes test.py script for verification
  - ✅ Records comprehensive results in test_results.md
  - ✅ Documents files affected and test outcomes

---

## New Functionality

### Step 7: Implementation (workflow-step07.py)

**Three-Phase Execution:**

```
Phase 1: Run Tests
  └─ Execute test.py
  └─ Capture results (PASS/FAIL)
  └─ Report status

Phase 2: Run Implementation
  └─ Execute implement.py
  └─ Capture output
  └─ Report status

Phase 3: Update Documentation
  └─ Record all results in implementation_notes.md
  └─ Include test output (first 500 chars)
  └─ Include implementation output (first 500 chars)
```

**New Helper Function:**
```python
def _execute_script(script_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Execute a generated script and return (success, output)."""
```

**Features:**
- ✅ Executes scripts via subprocess with timeout (300 seconds)
- ✅ Captures both stdout and stderr
- ✅ Returns success status and output
- ✅ Handles errors gracefully
- ✅ Supports dry-run mode
- ✅ Works on Windows and Unix

### Step 8: Testing (workflow-step08.py)

**Three-Phase Verification Process:**

```
Phase 1: Verify Implementation Changes
  └─ Check git diff for modified files
  └─ Check for newly created files
  └─ Verify implementation_notes.md for success indicators
  └─ Report files affected and total changes

Phase 2: Run Verification Tests
  └─ Execute test.py if available
  └─ Capture test output
  └─ Determine pass/fail status

Phase 3: Record Results
  └─ Document implementation status
  └─ List files affected
  └─ Record test results
  └─ Overall pass/fail determination
```

**New Helper Functions:**
```python
def _check_git_changes(project_root: Path) -> Dict:
    """Check for git changes (modified and new files)."""
    # Returns: {modified: [...], added: [...]}

def _check_file_changes(change_path: Path, project_root: Path) -> Dict:
    """Verify what files were changed by the implementation."""
    # Returns: {files_modified: [...], files_created: [...], total_changes: N}

def _record_test_results(results_file: Path, change_results: Dict, ...):
    """Record comprehensive implementation and test results."""
    # Updates test_results.md with:
    # - Implementation status
    # - Files modified/created
    # - Test execution results
```

**Features:**
- ✅ **Git Change Detection:** Automatically detects modified and new files
- ✅ **Implementation Verification:** Confirms changes were actually made
- ✅ **Test Execution:** Runs test.py for further validation
- ✅ **Comprehensive Logging:** Documents all changes and results
- ✅ **Three-Phase Process:** Sequential verification steps
- ✅ **Graceful Fallbacks:** Works even if git or test.py unavailable

---

## Implementation Details

### Execution Flow

**Before Changes:**
```
Step 6 (Script Generation)  → Generate test.py, implement.py
Step 7 (Implementation)     → Create implementation_notes.md (no script execution)
Step 8 (Testing)           → Create test_results.md (no actual testing)
Result: Scripts generated but never executed
```

**After Changes:**
```
Step 6 (Script Generation)  → Generate test.py, implement.py
Step 7 (Implementation)     → Execute implement.py, run tests, log results
Step 8 (Testing)           → Execute test.py, capture results, update test_results.md
Result: Scripts generated AND executed automatically
```

### Script Execution Details

**workflow-step07.py Execution Order:**

1. **Test Phase:**
   ```python
   test_script = change_path / "test.py"
   test_success, test_output = _execute_script(test_script, dry_run)
   ```
   - Executes with subprocess.run()
   - Captures stdout and stderr
   - Returns (success: bool, output: str)
   - Logs results to helpers

2. **Implementation Phase:**
   ```python
   implement_script = change_path / "implement.py"
   implement_success, implement_output = _execute_script(implement_script, dry_run)
   ```
   - Executes implementation tasks
   - Captures output
   - Returns status and results

3. **Documentation Phase:**
   - Reads existing implementation_notes.md
   - Appends results block with:
     - Script execution status (PASSED/FAILED)
     - Test output (truncated to 500 chars)
     - Implementation output (truncated to 500 chars)
   - Updates file atomically

**workflow-step08.py Execution:**

```python
test_script = change_path / "test.py"
test_success, test_output = _run_test_script(test_script, dry_run)

# Record results
existing = results.read_text() if results.exists() else ""
summary = "PASSED" if test_success else "FAILED"

block = f"\n## Test Results\n\n- **Status**: {summary}\n..."
helpers.set_content_atomic(results, existing + block)
```

---

## Error Handling

### Timeout Protection
```python
result = subprocess.run(
    [sys.executable, str(script_path)],
    capture_output=True,
    text=True,
    timeout=300,  # 5 minute timeout per script
)
```

### Exception Handling
```python
except subprocess.TimeoutExpired:
    return False, f"Script execution timed out: {script_path}"
except Exception as e:
    return False, f"Error executing script: {e}"
```

### File Not Found Handling
```python
if not script_path.exists():
    return False, f"Script not found: {script_path}"
```

---

## Output Examples

### implementation_notes.md Output

```markdown
## Implementation Details

- Modules changed:
- Rationale:
- Alternatives considered:

## Script Execution Results

- Test script: PASSED
- Implementation script: PASSED

### Test Output
```
Testing: Proposal document exists [PASS]
Testing: Tasks has checkboxes [PASS]
Testing: Specification document exists [PASS]

Test Summary
Passed: 9
Failed: 0
RESULT: PASSED
```

### Implementation Output
```
Implementation: update-doc-project-improvement

Analyzing tasks.md...
Task: Document update-doc-project-improvement
  [COMPLETED]

Implementation Summary
Completed: 5
Failed: 0
RESULT: SUCCESS
```
```

### test_results.md Output

```markdown
## Test Results - Implementation Verification

### Implementation Status
- **Status**: SUCCESS
- **Files Modified**: 3
- **Files Created**: 2
- **Total Changes**: 5

**Modified Files:**
- `docs/API_REFERENCE.md`
- `backend/settings.py`
- `plugin/manifest.json`

**Created Files:**
- `openspec/changes/update-doc-project-improvement/proposal.md`
- `openspec/changes/update-doc-project-improvement/spec.md`

### Test Execution
- **Status**: PASSED
- **Tests Run**: Yes

**Test Output:**
```
Testing: Proposal document exists [PASS]
Testing: Proposal has 'Why' section [PASS]
Testing: Specification exists [PASS]
...
Test Summary
Passed: 9
Failed: 0
RESULT: PASSED
```

### Overall Result
- ✅ PASS
```

---

## Dry-Run Mode

Both steps support `--dry-run` mode:

```powershell
# Test without executing
python scripts/workflow.py --change-id "test-change" --dry-run

# Output:
# [DRY RUN] Would execute: test.py
# [DRY RUN] Would execute: implement.py
```

---

## Benefits

### 1. **Automatic Validation**
- ✅ Tests run automatically without manual intervention
- ✅ Implementation tasks verified before merge
- ✅ Early error detection

### 2. **Comprehensive Logging**
- ✅ Full execution output captured
- ✅ Results stored in implementation_notes.md
- ✅ Test results in test_results.md

### 3. **Safety & Control**
- ✅ Timeout protection (300 seconds per script)
- ✅ Error handling and reporting
- ✅ Dry-run preview capability
- ✅ Graceful failure handling

### 4. **Better Auditability**
- ✅ Clear record of what was executed
- ✅ Test results documented in change
- ✅ Full traceability of implementation

### 5. **Workflow Integration**
- ✅ Scripts execute in proper sequence
- ✅ Results inform workflow decisions
- ✅ Failure stops further processing

---

## Backward Compatibility

✅ **Fully Backward Compatible:**

- If test.py or implement.py don't exist → Script skips execution gracefully
- Existing implementation_notes.md preserved → Results appended
- All existing functionality maintained
- No breaking changes to workflow API

---

## Testing the Changes

### Test Case 1: Execute with Generated Scripts

```powershell
cd openspec/archive/update-doc-project-improvement

# Run workflow
python ../../scripts/workflow.py --change-id "update-doc-project-improvement"

# Expected:
# Step 7: Execute test.py ✅
# Step 7: Execute implement.py ✅
# Step 8: Execute test.py ✅
# Results recorded in implementation_notes.md and test_results.md
```

### Test Case 2: Dry-Run Mode

```powershell
python scripts/workflow.py --change-id "test-change" --dry-run

# Expected:
# [DRY RUN] Would execute: test.py
# [DRY RUN] Would execute: implement.py
# [DRY RUN] Would record test results
```

### Test Case 3: Missing Scripts

```powershell
# When test.py or implement.py don't exist
python scripts/workflow.py --change-id "test-change"

# Expected:
# ℹ No test.py found
# Step continues gracefully
# Workflow completes successfully
```

---

## Files Modified

### 1. **scripts/workflow-step07.py**
- Added import for subprocess
- Added `_execute_script()` helper function
- Enhanced `invoke_step7()` to execute scripts
- Added three-phase execution (test, implement, document)
- Return value now reflects success of script execution

**Changes:**
- ➕ 60 lines added (script execution logic)
- ➖ ~20 lines removed (old placeholder logic)
- 📝 Updated docstring

### 2. **scripts/workflow-step08.py**
- Added import for subprocess
- Added `_run_test_script()` helper function
- Enhanced `invoke_step8()` to execute and parse tests
- Records test results with status and output

**Changes:**
- ➕ 65 lines added (test execution logic)
- ➖ ~15 lines removed (old placeholder logic)
- 📝 Updated docstring

---

## Future Enhancements

Potential improvements for future iterations:

1. **Test Result Parsing**
   - Parse test output for coverage metrics
   - Extract pass/fail counts automatically
   - Generate visual reports

2. **Implementation Confirmation**
   - Require manual confirmation before running implement.py
   - Implement --auto-confirm flag
   - Show preview first

3. **Metrics Collection**
   - Track test execution time
   - Measure implementation duration
   - Generate performance trends

4. **Integration with CI/CD**
   - Export results in CI format
   - Generate test reports for GitHub Actions
   - Link to external test systems

5. **Script Customization**
   - Allow custom test frameworks
   - Support different implementation strategies
   - Plugin system for script generation

---

## Migration Guide

### For Existing Workflows

No migration needed! The changes are backward compatible:

1. **Existing changes continue to work** - If no test.py/implement.py exist, workflow continues
2. **New changes get automatic execution** - test.py and implement.py are executed automatically
3. **Results are captured** - Output saved in implementation_notes.md and test_results.md

### For New Changes

New OpenSpec changes will automatically benefit from:
- ✅ Automatic test execution
- ✅ Implementation task execution
- ✅ Comprehensive result logging
- ✅ Workflow integration

---

## Troubleshooting

### Script Execution Timeout
**Problem:** Script takes longer than 5 minutes  
**Solution:** Increase timeout in workflow-step07.py or workflow-step08.py (line with `timeout=300`)

### Script Not Found Error
**Problem:** test.py or implement.py not generated  
**Solution:** Check workflow-step06.py executed successfully, verify files in change directory

### Execution Permission Error (Unix)
**Problem:** "Permission denied" when running script  
**Solution:** workflow-step06.py chmod 755 applied automatically, check file permissions manually if needed

### Subprocess Output Capture Issue
**Problem:** Output not captured properly  
**Solution:** Verify scripts use print() or logging that writes to stdout, not file-based logging

---

## Summary

The OpenSpec workflow now automatically executes generated test and implementation scripts, providing:

✅ **Automatic Validation** - Tests run without manual intervention  
✅ **Better Auditability** - Full execution logs recorded  
✅ **Safety Features** - Timeout protection and error handling  
✅ **Backward Compatible** - Works with existing changes  
✅ **Future Ready** - Foundation for enhanced CI/CD integration

**The workflow is now more intelligent, safer, and provides complete traceability of all generated script execution.**

---

**Implementation Date:** October 20, 2025  
**Status:** ✅ Complete and Ready  
**Testing:** Recommended before merge to main
