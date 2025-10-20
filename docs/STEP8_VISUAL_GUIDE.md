# Step 8 Three-Phase Process - Visual Guide

## Process Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    Step 8: Testing Phase                       │
│        Verify Implementation & Test Results                    │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Start Step 8      │
                    └─────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                    ▼                    ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  Get Project     │  │  Initialize      │
          │  Root Path       │  │  Results File    │
          └──────────────────┘  └──────────────────┘
                    │                    │
                    └─────────┬──────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  PHASE 1: Verify Implementation       │
         │           Changes                     │
         └────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
           ┌────────┐  ┌──────────┐  ┌───────────────┐
           │ Check  │  │ Read     │  │ Run Git       │
           │ impl   │  │ impl_    │  │ Commands:     │
           │ notes  │  │ notes.md │  │ • git diff    │
           │ for    │  │ for      │  │ • git ls-     │
           │ success│  │ success  │  │   files       │
           │ keyword│  │ keywords │  │               │
           └────────┘  └──────────┘  └───────────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │ Report:                               │
         │ • Files Modified: N                   │
         │ • Files Created: N                    │
         │ • Total Changes: N                    │
         │ • Status: SUCCESS/DETECTED/FAILED     │
         └────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                No  ▼                    ▼  Yes
             changes                 changes
                │                      │
         ┌──────▼─────┐         ┌──────▼─────────┐
         │ ⚠ Warning  │         │ ✓ Implementation
         │ No changes │         │ Verified
         └────────────┘         └─────────────────┘
                │                      │
                └─────────────┬────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  PHASE 2: Run Verification Tests      │
         └────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                   Yes                  No
                    │                    │
                    ▼                    ▼
           ┌──────────────────┐  ┌──────────────┐
           │ test.py Exists?  │  │ ℹ No test.py │
           └──────────────────┘  │ Skip tests   │
                    │             └──────────────┘
                   Yes                    │
                    │                     │
                    ▼                     │
           ┌──────────────────┐           │
           │ Execute test.py  │           │
           │ • Capture output │           │
           │ • 300s timeout   │           │
           │ • Parse returncd │           │
           └──────────────────┘           │
                    │                     │
            ┌───────┴────────┐            │
            │                │            │
        Exit 0           Exit 1           │
            │                │            │
            ▼                ▼            │
      ┌─────────┐      ┌──────────┐     │
      │ ✓ PASS  │      │ ✗ FAILED │     │
      └─────────┘      └──────────┘     │
            │                │            │
            └───────┬────────┘            │
                    │                     │
                    └──────────┬──────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  PHASE 3: Record Results               │
         │           in test_results.md           │
         └────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                    ▼                    ▼
           ┌──────────────────┐  ┌──────────────┐
           │ Read existing    │  │ Build results│
           │ test_results.md  │  │ block with:  │
           │ (if exists)      │  │ • Status     │
           └──────────────────┘  │ • Files list │
                    │             │ • Tests      │
                    └─────────────┤ • Output     │
                                  └──────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │ Append to test_results.md│
                          │ Atomically write         │
                          └──────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │ Mark Step 8 Complete     │
                          │ in todo.md               │
                          └──────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │ Return (impl_success AND │
                          │ test_success)            │
                          │                          │
                          │ True  = ✅ Safe to merge │
                          │ False = ❌ Needs review  │
                          └──────────────────────────┘
```

---

## Phase 1: Implementation Detection

```
Phase 1: Verify Implementation Changes
├─ Call _check_file_changes()
│  ├─ Check implementation_notes.md
│  │  └─ Look for: SUCCESS, PASSED, COMPLETED
│  │
│  └─ Call _check_git_changes()
│     ├─ Run: git diff --name-only
│     │  └─ Get: [list of modified files]
│     │
│     └─ Run: git ls-files --others --exclude-standard
│        └─ Get: [list of untracked files]
│
├─ Return:
│  {
│    "files_modified": [...],
│    "files_created": [...],
│    "total_changes": N,
│    "implementation_successful": bool,
│  }
│
└─ Output:
   ├─ If successful: ✓ Implementation verified: 3 modified, 2 created
   └─ If failed:     ⚠ No implementation changes detected
```

---

## Phase 2: Test Execution

```
Phase 2: Run Verification Tests
├─ Check if test.py exists
│
├─ If YES:
│  ├─ Run: subprocess.run([sys.executable, "test.py"])
│  ├─ Capture: stdout + stderr
│  ├─ Timeout: 300 seconds
│  └─ Result:
│     ├─ returncode == 0 → success = True
│     └─ returncode != 0 → success = False
│
├─ If NO:
│  ├─ write_info("ℹ No test.py found")
│  └─ success = True (don't fail without tests)
│
├─ Exception Handling:
│  ├─ TimeoutExpired → return (False, "Timed out")
│  ├─ FileNotFound → return (False, "Not found")
│  └─ Other Error → return (False, "Error message")
│
└─ Output:
   ├─ If success: ✓ Verification tests passed
   └─ If failed:  ⚠ Some verification tests failed
```

---

## Phase 3: Result Recording

```
Phase 3: Record Results in test_results.md
├─ Read existing content (if exists)
├─ Build result block:
│  ├─ Implementation Status
│  │  ├─ Status: SUCCESS/DETECTED
│  │  ├─ Files Modified: N
│  │  ├─ Files Created: N
│  │  └─ Total Changes: N
│  │
│  ├─ Modified Files List (first 10)
│  ├─ Created Files List (first 10)
│  │
│  ├─ Test Execution Status
│  │  ├─ Status: PASSED/FAILED
│  │  └─ Output: (truncated to 1000 chars)
│  │
│  └─ Overall Result
│     ├─ ✅ PASS   (impl_success AND test_success)
│     └─ ⚠️ VERIFY (impl_success OR test_success but not both)
│
├─ Atomically write: existing + new block
└─ Output:
   Updated: openspec/changes/test-id/test_results.md
```

---

## Decision Tree

```
                    Start invoke_step8()
                            │
                            ▼
                ┌─────────────────────────┐
                │ Check implementation    │
                │ changes via git         │
                └─────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
            YES │                       │ NO
                │                       │
                ▼                       ▼
         ┌────────────┐         ┌──────────────┐
         │Files       │         │impl_notes.md │
         │changed?    │         │has success?  │
         └────────────┘         └──────────────┘
                │                       │
            YES │                   YES │
                │                       │
                └───────────┬───────────┘
                            │
                    impl_success = True
                            │
                            ▼
                ┌─────────────────────────┐
                │ Run test.py if exists   │
                └─────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                Exists           Doesn't
                    │               Exist
                    ▼               │
            ┌─────────────┐        │
            │Execute &    │        │
            │capture      │        │
            └─────────────┘        │
                    │              │
            ┌───────┴──────┐       │
            │              │       │
        Pass          Fail │       │
            │              │       │
            │              │       │
    test_   │      test_   │   test_
    success │      success │   success
      =True │       =False │    =True
            │              │       │
            └───────┬──────┴───────┘
                    │
                    ▼
         ┌────────────────────────┐
         │ Record results         │
         │ to test_results.md     │
         └────────────────────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │ return (impl_success   │
         │   AND test_success)    │
         └────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
       True                   False
        │                       │
        ▼                       ▼
    ✅ PASS               ❌ NEEDS REVIEW
    Safe to Merge         Fix or Retry
```

---

## Function Call Sequence

```
invoke_step8()
│
├─ helpers.write_step(8, "Testing - Verify Implementation Changes")
│
├─ PHASE 1
│  └─ change_results = _check_file_changes(change_path, project_root)
│     ├─ impl_notes = change_path / "implementation_notes.md"
│     ├─ git_changes = _check_git_changes(project_root)
│     │  ├─ subprocess.run(["git", "diff", "--name-only"])
│     │  └─ subprocess.run(["git", "ls-files", "--others"])
│     └─ Returns: {files_modified, files_created, total_changes, ...}
│
├─ Write Phase 1 results to console
│
├─ PHASE 2
│  ├─ if test_script.exists():
│  │  └─ test_success, test_output = _run_test_script(test_script, dry_run)
│  │     ├─ subprocess.run([sys.executable, str(test_script)])
│  │     ├─ Capture stdout + stderr
│  │     ├─ Return: (returncode == 0, output)
│  │     └─ Exception handling (timeout, etc)
│  │
│  └─ else:
│     └─ test_success = True, test_output = "No test script"
│
├─ Write Phase 2 results to console
│
├─ PHASE 3
│  └─ _record_test_results(results, change_results, test_success, test_output)
│     ├─ Build markdown block with:
│     │  ├─ Implementation status
│     │  ├─ Files modified/created
│     │  └─ Test results
│     └─ Atomically write to test_results.md
│
├─ _mark_complete(change_path)
│
└─ return (impl_success AND test_success)
   └─ If True:  ✅ Safe to merge
   └─ If False: ❌ Needs review
```

---

## File State Transitions

```
Before Step 8:
├─ implementation_notes.md (from step 7)
│  └─ Contains: Implementation details
├─ test.py (generated in step 6)
│  └─ Contains: Test script
└─ test_results.md (empty)
   └─ Status: Not yet tested

During Step 8:
├─ Phase 1: Read implementation_notes.md + git diff
├─ Phase 2: Execute test.py (no file changes)
└─ Phase 3: Generate markdown results

After Step 8:
├─ implementation_notes.md (unchanged)
├─ test.py (unchanged)
└─ test_results.md (UPDATED)
   ├─ Implementation Status section
   ├─ Files Modified list
   ├─ Files Created list
   ├─ Test Execution section
   └─ Overall Result (✅ PASS or ⚠️ VERIFY)
```

---

## Console Output Timeline

```
Time  Event                          Output
────  ─────────────────────────────  ──────────────────────────────
T=0   Start Step 8                   "Step 8: Testing - Verify Implementation Changes"
      
T=1   Begin Phase 1                  "Phase 1: Verifying implementation changes..."
T=2   Detect git changes             "✓ Implementation verified: 3 modified, 2 created"
      
T=3   Begin Phase 2                  "Phase 2: Running verification tests..."
T=4   Locate test.py                 [found]
T=5   Execute test.py                [spinner: "Running verification tests"]
T=10  Test completes                 "✓ Verification tests passed"
      
T=11  Begin Phase 3                  "Phase 3: Recording test results..."
T=12  Read test_results.md           [found existing content]
T=13  Append results                 [spinner: "Recording results"]
T=14  Write complete                 "Updated: openspec/changes/test-id/test_results.md"
      
T=15  Mark complete                  [todo.md updated]
T=16  Return status                  "Step 8 completed"
      Workflow continues with True
```

---

## Error Paths

```
Path 1: Git not available
│
├─ _check_git_changes() raises Exception
├─ Caught: helpers.write_warning("Could not check git changes: {e}")
├─ Fallback: Use implementation_notes.md success keywords
└─ Continue normally

Path 2: test.py not found
│
├─ test_script.exists() = False
├─ Write: "ℹ No test.py found"
├─ Set: test_success = True (don't fail)
└─ Continue normally

Path 3: test.py times out
│
├─ subprocess.run() raises TimeoutExpired
├─ Caught: return (False, "Test execution timed out")
├─ Set: test_success = False
└─ Record as FAILED

Path 4: test.py fails
│
├─ subprocess.run() returns returncode = 1
├─ Logic: returncode != 0 → success = False
├─ Set: test_success = False
└─ Record as FAILED
```

---

## State Diagram: invoke_step8() Return Values

```
                    invoke_step8()
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
    impl_success =                 test_success =
    (files_changed OR              (test.py passed
     impl_notes_success)           OR no test.py)
            │                           │
    ┌───────┴───────┐           ┌───────┴───────┐
    │               │           │               │
   True          False         True           False
    │               │           │               │
    ├───────────────┴───────────┼───────────────┤
    │                           │
    ├─── True AND True ─────────┤
    │       ↓                    │
    │  ✅ RETURN: True           │
    │  Safe to Merge             │
    │                            │
    ├─── True AND False ────────┼────────┐
    │       ↓                    │        │
    │  ❌ RETURN: False          │        │
    │  Needs Review              │        │
    │                            │        │
    ├─── False AND True ────────┼────────┤
    │       ↓                    │
    │  ❌ RETURN: False          │
    │  No Changes Detected       │
    │                            │
    └─── False AND False ───────┤
            ↓                    │
        ❌ RETURN: False         │
        Complete Failure         │
                                 │
                                 └──────┘
```

---

**Visual Guide Created:** October 20, 2025  
**Status:** ✅ Complete  
**Use Cases:** Understanding Step 8 flow and decision logic
