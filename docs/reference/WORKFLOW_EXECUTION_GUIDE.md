# OpenSpec Workflow Execution Guide

## Quick Reference

### Option 1: Run Complete Workflow (Recommended)

```powershell
cd c:\Users\kdejo\DEV\obsidian-llm-assistant\obsidian-AI-assistant
.\scripts\workflow.ps1 -ChangeId "cleanup-organize-docs"
```

**Expected Duration**: ~2 minutes  
**Expected Result**: v0.1.37 created with all scripts and documentation

---

### Option 2: Test Individual Components

#### Test the Comprehensive Test Suite

```powershell
cd openspec\changes\cleanup-organize-docs
python test.py
```

**Expected Output**:
```
[1/8] Directory Structure Validation [PASS]
[2/8] Celebration Files Deletion [PASS]
[3/8] Reference Docs Move [PASS]
[4/8] Root Directory Cleanup [PASS]
[5/8] README.md Updates [PASS]
[6/8] Link Validation [PASS]
[7/8] OpenSpec Separation [PASS]
[8/8] CHANGELOG Updates [PASS]

✅ RESULT: PASSED
```

#### Preview Implementation (What-If Mode)

```powershell
cd openspec\changes\cleanup-organize-docs
python implement.py --what-if
```

**Expected Output**: Lists all operations that will be performed without executing them

#### Execute Implementation

```powershell
cd openspec\changes\cleanup-organize-docs
python implement.py --force
```

**Expected Output**: 
```
Creating directory structure...
Moving reference documentation...
Deleting celebration files...
Updating README.md...
Updating CHANGELOG.md...
Validating implementation...
✅ Implementation complete!
```

#### Verify After Implementation

```powershell
cd openspec\changes\cleanup-organize-docs
python test.py
```

**Expected**: All tests should PASS with actual files in place

---

## What Each Script Does

### workflow-step05.py - Generate Planning Documents

**Inputs**: 
- `proposal.md` - Change proposal with requirements
- `tasks.md` - Task breakdown
- `spec.md` - Current specification

**Outputs**:
- `spec.md` - **Enhanced** with comprehensive acceptance criteria
- `test_plan.md` - **Enhanced** with 8 test suites and 40+ test cases

**Key Extraction**:
- Success criteria (12+ items from proposal)
- File operations (KEEP/MOVE/DELETE lists)
- Implementation phases (5 phases)

---

### workflow-step06.py - Generate Executable Scripts

**Inputs**:
- `proposal.md` - Change proposal
- `tasks.md` - Task breakdown
- `spec.md` - Specification

**Outputs**:
- `test.py` - **Rewritten** with 8 comprehensive test suites
- `implement.py` - **Rewritten** with 25+ file operations

**Intelligent Selection**:
- For cleanup-organize-docs: Uses specialized comprehensive templates
- For other changes: Uses generic extensible templates

---

### test.py - Validate Implementation

**8 Test Suites**:

1. **Directory Structure Validation**
   - Checks docs/ created with 6 subdirectories
   - Validates docs/README.md exists

2. **Celebration Files Deletion**
   - Verifies 20-30 celebration files deleted from root
   - Tests patterns: 🎉_*, COMPLETION_*, SESSION_*, etc.

3. **Reference Docs Move**
   - Validates reference files in docs/ subdirectories
   - Tests: GIT_WORKFLOW_REFERENCE.md, PRODUCTION_READINESS.md, etc.

4. **Root Directory Cleanup**
   - Ensures ≤20 files in root (down from 30+)
   - Validates essential files still present

5. **README.md Updates**
   - Checks README has docs/ navigation section
   - Validates sufficient documentation content

6. **Link Validation**
   - Tests README.md for broken internal links
   - Tests docs/README.md for broken links

7. **OpenSpec Separation**
   - Validates openspec/ directory isolated
   - Checks no OpenSpec files in root

8. **CHANGELOG Updates**
   - Verifies CHANGELOG documents cleanup changes
   - Checks for cleanup-related keywords

---

### implement.py - Perform Actual Work

**6 Implementation Phases**:

1. **Create Directory Structure** (7 operations)
   - Creates docs/ with 6 subdirectories
   - Creates docs/README.md with navigation

2. **Move Reference Docs** (11+ operations)
   - Moves 11+ reference files to appropriate docs/ locations
   - Examples: GIT_*.md → docs/guides/, PRODUCTION_* → docs/production/

3. **Delete Celebration Files** (20+ operations)
   - Deletes 20-30 celebration/status files from root
   - Patterns: 🎉_*, COMPLETION_*, SESSION_*, READY_*, etc.

4. **Update README.md** (1 operation)
   - Adds documentation section with links to docs/ subdirectories

5. **Update CHANGELOG.md** (1 operation)
   - Documents cleanup changes with full details

6. **Validate Implementation** (6+ tests)
   - Runs internal validation
   - Confirms success

---

## Workflow Architecture

```
Step 1: Run Workflow
  └─→ .\scripts\workflow.ps1 -ChangeId "cleanup-organize-docs"

Step 2: workflow-step05.py Executes
  ├─→ Extracts success criteria from proposal.md
  ├─→ Extracts file lists from proposal scope
  ├─→ Extracts 5 implementation phases
  ├─→ Generates comprehensive spec.md
  └─→ Generates detailed test_plan.md with 8 suites

Step 3: workflow-step06.py Executes
  ├─→ Detects change_id = "cleanup-organize-docs"
  ├─→ Generates specialized test.py (320+ lines, 8 suites)
  └─→ Generates specialized implement.py (450+ lines, 25+ ops)

Step 4: Create Release Branch & PR
  ├─→ Branch: release-0.1.37
  ├─→ PR: #70 (with all improvements)
  └─→ Ready for merge after testing

Step 5: Manual Test Execution (Optional)
  ├─→ Run: python test.py  (Should PASS)
  └─→ Result: Validates test structure is comprehensive

Step 6: Manual Implementation (Optional)
  ├─→ Preview: python implement.py --what-if
  ├─→ Execute: python implement.py --force
  └─→ Result: Performs 25+ file operations

Step 7: Verify Implementation
  ├─→ Run: python test.py
  ├─→ Result: All tests PASS with actual changes
  └─→ Result: Validates implement.py works correctly

Step 8: Merge Changes
  ├─→ Commit: git add -A && git commit
  ├─→ Merge: git checkout main && git merge release-0.1.37
  └─→ Result: Changes deployed to main branch
```

---

## Success Criteria

### Workflow Execution Success ✅
- [ ] All steps 0-12 pass without errors
- [ ] v0.1.37 branch created
- [ ] PR #70 created with all changes
- [ ] spec.md has comprehensive content (not empty)
- [ ] test_plan.md has 8 test suites with 40+ tests
- [ ] test.py has 8 test functions (320+ lines)
- [ ] implement.py has 6 operational phases (450+ lines)

### Test Suite Success ✅
- [ ] Run `python test.py` before implementation
  - Expected: All 8 test suites PASS
- [ ] Run `python test.py` after implementation
  - Expected: All 8 test suites PASS with actual changes

### Implementation Success ✅
- [ ] Run `python implement.py --what-if`
  - Expected: Lists 25+ operations without executing
- [ ] Run `python implement.py --force`
  - Expected: 6 phases complete, 25+ operations performed
- [ ] Root directory reduced from 30+ to ~10 files
- [ ] docs/ directory created with 6 subdirectories
- [ ] Reference files moved to docs/ locations
- [ ] Celebration files deleted from root
- [ ] README.md updated with docs/ navigation
- [ ] CHANGELOG.md documents cleanup changes

---

## Troubleshooting

### Issue: Tests fail with "docs/ not found"

**Cause**: implement.py hasn't been executed yet  
**Solution**: Run `python implement.py --force` first, then run tests again

### Issue: PowerShell script not found

**Solution**: Make sure you're in the workspace root directory
```powershell
cd c:\Users\kdejo\DEV\obsidian-llm-assistant\obsidian-AI-assistant
```

### Issue: Python script execution fails

**Solution**: Ensure Python 3.11+ is installed and in PATH
```powershell
python --version  # Should show 3.11+
```

### Issue: test.py shows "broken links"

**Cause**: Reference files haven't been moved yet  
**Solution**: Run implement.py before running tests on actual repository

---

## Key Improvements in This Workflow

### Previously (v0.1.36)
- ❌ test.py only checked file existence (8 basic tests)
- ❌ implement.py was just a template scaffold
- ❌ workflow-step05.py generated placeholder documents
- ❌ workflow-step06.py used generic templates for all changes
- ❌ No validation of actual implementation requirements

### Now (v0.1.37)
- ✅ test.py validates actual implementation (8 suites, 40+ tests)
- ✅ implement.py performs real file operations (25+ operations)
- ✅ workflow-step05.py intelligently extracts proposal requirements
- ✅ workflow-step06.py generates context-aware scripts
- ✅ Tests and implementation are logically coupled through proposal

---

## Documentation

- **[WORKFLOW_IMPROVEMENTS_SUMMARY_OCT22.md](WORKFLOW_IMPROVEMENTS_SUMMARY_OCT22.md)** - Detailed improvement summary
- **[openspec/changes/cleanup-organize-docs/proposal.md](openspec/changes/cleanup-organize-docs/proposal.md)** - Change proposal
- **[openspec/changes/cleanup-organize-docs/tasks.md](openspec/changes/cleanup-organize-docs/tasks.md)** - Task breakdown
- **[openspec/changes/cleanup-organize-docs/spec.md](openspec/changes/cleanup-organize-docs/spec.md)** - Specification (will be enhanced)
- **[openspec/changes/cleanup-organize-docs/test_plan.md](openspec/changes/cleanup-organize-docs/test_plan.md)** - Test plan (will be enhanced)

---

## Next Steps

1. **Run the workflow**: `.\scripts\workflow.ps1 -ChangeId "cleanup-organize-docs"`
2. **Test the implementation**: `python openspec/changes/cleanup-organize-docs/test.py`
3. **Execute the changes**: `python openspec/changes/cleanup-organize-docs/implement.py --force`
4. **Verify success**: `python openspec/changes/cleanup-organize-docs/test.py`
5. **Merge to main**: `git merge release-0.1.37`

**Expected Result**: v0.1.37 with comprehensive documentation reorganization and fully functional workflow scripts.

---

**Last Updated**: October 22, 2025  
**Status**: Ready for Execution
