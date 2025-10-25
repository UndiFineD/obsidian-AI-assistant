# Implementation Guide: Workflow-Improvements

**Status**: Comprehensive Implementation Plan Ready  
**Date**: 2025-10-23  
**Version**: 1.0  
**Owner**: @kdejo  
**Reviewer**: @UndiFineD (pending)

---

## Overview

This guide documents all implementation requirements for the workflow-improvements change extracted from:
- **tasks.md**: 187 tasks across 7 implementation categories
- **spec.md**: Technical specifications, data models, APIs
- **test_plan.md**: Complete testing strategy
- **test.py**: 54 comprehensive tests validating all requirements

**Total Scope**: 39 implementation tasks + 6 test suites + 7 documentation tasks

---

## Quick Start

### List All Tasks
```bash
python openspec/changes/workflow-improvements/implement.py --list
```

### View Summary
```bash
python openspec/changes/workflow-improvements/implement.py --summary
```

### Run Single Task (Dry-Run)
```bash
python openspec/changes/workflow-improvements/implement.py --task IMPL-1 --what-if
```

### Run Category
```bash
python openspec/changes/workflow-improvements/implement.py --category "Lane Selection" --what-if
```

---

## File Operations Summary

### Total File Operations: 47

| Operation | Count | Examples |
|-----------|-------|----------|
| **create** | 8 | `scripts/quality_gates.py`, `tests/backend/test_*.py`, docs |
| **modify** | 38 | `scripts/workflow.py`, `scripts/workflow.ps1`, documentation |
| **create_dir** | 1 | `assistant_logs/` (for AI-assisted execution) |

### Files to Create (8 total)

1. **scripts/quality_gates.py** (NEW)
   - Purpose: Execute ruff, mypy, pytest, bandit and emit PASS/FAIL
   - Size: ~300-400 lines
   - Dependencies: None (runs existing tools)
   - Tests: TEST-3 (90%+ coverage)
   - Related Tasks: IMPL-8, IMPL-9, IMPL-10, IMPL-11

2. **tests/backend/test_lane_selection.py** (NEW)
   - Purpose: Unit tests for lane selection logic
   - Coverage: 90%+
   - Test Cases: 8-10 test functions
   - Related Task: TEST-1

3. **tests/backend/test_parallelization.py** (NEW)
   - Purpose: Unit tests for ThreadPoolExecutor implementation
   - Coverage: 85%+
   - Test Cases: 6-8 test functions
   - Related Task: TEST-2

4. **tests/backend/test_quality_gates.py** (NEW)
   - Purpose: Unit tests for quality gates module
   - Coverage: 90%+
   - Test Cases: 10-12 test functions
   - Related Task: TEST-3

5. **tests/backend/test_status_tracking.py** (NEW)
   - Purpose: Unit tests for status.json operations
   - Coverage: 85%+
   - Test Cases: 6-8 test functions
   - Related Task: TEST-4

6. **tests/backend/test_pre_step_hooks.py** (NEW)
   - Purpose: Unit tests for hook registry and validators
   - Coverage: 85%+
   - Test Cases: 6-8 test functions
   - Related Task: TEST-5

7. **tests/backend/test_conventional_commits.py** (NEW)
   - Purpose: Unit tests for Conventional Commits validation
   - Coverage: 90%+
   - Test Cases: 6-8 test functions
   - Related Task: TEST-6

8. **docs/WORKFLOW_IMPLEMENTATION_GUIDE.md** (NEW)
   - Purpose: Implementation guide for future contributors
   - Size: ~1000-1500 lines
   - Sections: Architecture, extension points, examples
   - Related Task: DOC-7

### Files to Modify (38 total)

#### Core Workflow Scripts (6 files)

| File | Tasks | Changes |
|------|-------|---------|
| **scripts/workflow.py** | IMPL-1, 3, 4, 5, 6, 7, 12, 13, 14, 15, 16, 17, 18, 19, 20-26 | Add lane selection, parallelization, quality gates, status tracking, hooks, commits validation, helpers (~2000+ new lines) |
| **scripts/workflow.ps1** | IMPL-2, 3, 5, 11 | Add -Lane parameter, pass-through to Python (~50-100 new lines) |

#### Quality Gates (1 file - already covered in "create" section)

#### Documentation (12 files)

| File | Tasks | Changes |
|------|-------|---------|
| **The_Workflow_Process.md** | DOC-3 | Add sections for 3 lanes with examples, quality gates, pre-step hooks (~400-600 new lines) |
| **README.md** | DOC-4 | Add lane feature to quick start section (~30-50 new lines) |
| **CHANGELOG.md** | DOC-5 | Add v0.1.40 section with all changes (~50-100 new lines) |
| **docs/AGENTS.md** | DOC-1 (indirect) | Add --use-agent documentation |
| **docs/API_REFERENCE.md** | DOC-6 | Add lane and quality gate APIs (~100-200 new lines) |
| **docs/CONFIGURATION_API.md** | DOC-6 | Document lane configuration options (~50-100 new lines) |

#### Helper Functions (via workflow.py modifications)

**New Classes to Implement**:
1. **Colors** - ANSI color constants
2. **OutputHelpers** - write_step, write_info, write_success, write_error, write_warning
3. **FileOperations** - set_content_atomic for atomic writes
4. **StatusTracker** - Progress tracking with spinners
5. **DocumentValidator** - Validate OpenSpec documents
6. **TemplateManager** - Load and manage templates
7. **DocumentGenerator** - Generate spec/tasks/test_plan

**Core Functions to Add**:
- Lane selection logic (get_lane_stages, is_docs_only_change)
- Parallelization (run_stages_parallel, run_stages_serial)
- Quality gates integration (run_quality_gates, parse_quality_results)
- Status tracking (write_status, read_status, resume_workflow)
- Hook registry and execution (register_hooks, run_pre_step_hooks)
- Conventional Commits validation (validate_commit_msg, fix_commit_interactively)

#### Directory Creation

| Directory | Purpose | Tasks |
|-----------|---------|-------|
| **assistant_logs/** | Optional AI-assisted execution logging | IMPL-5 |
| **openspec/changes/{change_id}/** | Change artifacts (proposal, spec, tasks, test_plan) | Generated by workflow |

---

## Implementation Tasks by Priority

### P0 Tasks (Critical Path - Must Do First)

**Lane Selection Foundation** (6 hours)
- [ ] IMPL-1: Add --lane flag to workflow.py
- [ ] IMPL-2: Add -Lane parameter to workflow.ps1
- [ ] IMPL-3: Implement lane-to-stage mapping

**Quality Gates** (11 hours)
- [ ] IMPL-8: Create quality_gates.py module
- [ ] IMPL-9: Define standard thresholds
- [ ] IMPL-11: Integrate into Stage 8

**Status Tracking** (5 hours)
- [ ] IMPL-12: Implement status.json writing

**Pre-Step Hooks** (2 hours)
- [ ] IMPL-15: Stage 0 environment validation

**Documentation** (8 hours)
- [ ] DOC-3: Update The_Workflow_Process.md
- [ ] DOC-4: Update README.md
- [ ] DOC-5: Update CHANGELOG.md

**Testing** (11 hours)
- [ ] TEST-1: Lane selection unit tests
- [ ] TEST-3: Quality gates unit tests
- [ ] TEST-4: Status tracking unit tests

**Total P0 Effort**: ~43 hours

### P1 Tasks (High Priority)

**Lane Enhancement** (3 hours)
- [ ] IMPL-4: Auto-detect code changes

**Parallelization** (5 hours)
- [ ] IMPL-6: ThreadPoolExecutor implementation

**Status Tracking** (6 hours)
- [ ] IMPL-13: Workflow resumption logic

**Pre-Step Hooks** (4 hours)
- [ ] IMPL-16: Git state validation
- [ ] IMPL-14: Hook registry system

**Conventional Commits** (6 hours)
- [ ] IMPL-18: Commit message validator
- [ ] IMPL-19: Interactive fixer

**Helpers** (16 hours)
- [ ] IMPL-21: Console output helpers
- [ ] IMPL-22: Atomic file writes
- [ ] IMPL-24: DocumentValidator class
- [ ] IMPL-25: TemplateManager class

**Documentation** (3 hours)
- [ ] DOC-1: Add docstrings
- [ ] DOC-6: Update CLI help

**Testing** (11 hours)
- [ ] TEST-2: Parallelization unit tests
- [ ] TEST-5: Pre-step hooks unit tests
- [ ] TEST-6: Commit validation unit tests

**Total P1 Effort**: ~54 hours

### P2 Tasks (Nice-to-Have)

**Lane Enhancement** (4 hours)
- [ ] IMPL-5: --use-agent flag

**Parallelization** (1 hour)
- [ ] IMPL-7: --no-parallel flag

**Pre-Step Hooks** (2 hours)
- [ ] IMPL-17: gh CLI validation

**Helpers** (9 hours)
- [ ] IMPL-20: Colors class
- [ ] IMPL-23: StatusTracker class

**Documentation** (6 hours)
- [ ] DOC-2: Inline comments
- [ ] DOC-7: Implementation guide

**Total P2 Effort**: ~22 hours

---

## Data Models

### status.json Schema

```json
{
  "change_id": "feature-xyz",
  "workflow_version": "0.1.39",
  "lane": "standard",
  "agent_enabled": false,
  "created_at": "2025-10-23T14:30:00Z",
  "started_at": "2025-10-23T14:30:05Z",
  "completed_at": null,
  "status": "in-progress",
  "stages": [
    {
      "stage_id": 0,
      "stage_name": "Setup & Initialization",
      "started_at": "2025-10-23T14:30:05Z",
      "completed_at": "2025-10-23T14:30:10Z",
      "result": "success",
      "error": null,
      "metrics": {
        "duration_seconds": 5,
        "memory_usage_mb": 45
      }
    }
  ],
  "current_stage": 0,
  "resumable_from": 0,
  "error_count": 0,
  "warnings": []
}
```

### quality_metrics.json Schema

```json
{
  "workflow_version": "0.1.39",
  "change_id": "feature-xyz",
  "lane": "standard",
  "generated_at": "2025-10-23T14:45:30Z",
  "overall_result": "PASS",
  "tools": {
    "ruff": {
      "result": "PASS",
      "errors": 0,
      "warnings": 0,
      "score": 100
    },
    "mypy": {
      "result": "PASS",
      "errors": 0,
      "score": 100
    },
    "pytest": {
      "result": "PASS",
      "total_tests": 1042,
      "passed": 1042,
      "failed": 0,
      "coverage_percent": 88.5,
      "coverage_threshold": 70
    },
    "bandit": {
      "result": "PASS",
      "high_severity": 0,
      "medium_severity": 2,
      "low_severity": 5
    }
  },
  "thresholds": {
    "ruff_errors_max": 0,
    "mypy_errors_max": 0,
    "pytest_pass_rate_min": 80,
    "pytest_coverage_min": 70,
    "bandit_high_severity_max": 0
  },
  "lane_applied": "standard"
}
```

### Lane-to-Stage Mapping

```python
LANE_MAPPING = {
    "docs": [0, 2, 3, 4, 9, 10, 11, 12],      # Skip: 1, 5, 6, 7, 8
    "standard": list(range(0, 13)),            # All stages 0-12
    "heavy": list(range(0, 13)),               # All stages with strict validation
}

SKIP_REASONS = {
    "docs": {
        1: "Version bumping skipped for docs-only changes",
        5: "Test plan generation skipped for docs-only changes",
        6: "Implementation scripts skipped for docs-only changes",
        7: "Implementation execution skipped for docs-only changes",
        8: "Quality gates skipped for docs-only changes"
    }
}
```

---

## Implementation Dependencies

### Dependency Graph (Critical Path)

```
IMPL-1 (--lane flag)
  ├─> IMPL-2 (PowerShell)
  │     └─> IMPL-3 (lane mapping) ◄─── Core Foundation
  │           ├─> IMPL-4 (code detection)
  │           ├─> IMPL-6 (parallelization)
  │           └─> TEST-1 (tests)
  │
  ├─> IMPL-8 (quality_gates.py)
  │     ├─> IMPL-9 (standard thresholds)
  │     │     ├─> IMPL-10 (heavy thresholds)
  │     │     └─> IMPL-11 (Stage 8 integration)
  │     │           └─> TEST-3
  │     └─> TEST-3
  │
  └─> IMPL-12 (status.json)
        ├─> IMPL-13 (resumption)
        └─> TEST-4

IMPL-14 (hook registry)
  ├─> IMPL-15 (Stage 0 env check)
  ├─> IMPL-16 (Stage 10 git check)
  ├─> IMPL-17 (Stage 12 gh check)
  └─> TEST-5

IMPL-18 (commit validator)
  └─> IMPL-19 (interactive fixer)
        └─> TEST-6

DOC-3, DOC-4, DOC-5 (Documentation)
  └─> REVIEW-1 (Code Review)
        └─> REVIEW-2 (Final Approval)
```

### Parallel Execution Opportunities

**Can Execute in Parallel After IMPL-1,2,3**:
- IMPL-4 (Code detection)
- IMPL-5 (Agent flag)
- IMPL-6 (Parallelization)
- IMPL-12 (Status tracking)
- IMPL-14 (Hook registry)
- IMPL-18 (Commit validator)
- DOC-1, DOC-2, DOC-3, DOC-4, DOC-5, DOC-6

**Total Parallel Time**: ~40 hours (vs 119 hours sequential)

---

## Testing Strategy

### Test Coverage Requirements

| Module | Target Coverage | Current | Tasks |
|--------|-----------------|---------|-------|
| Lane selection | 90%+ | 0% | TEST-1 |
| Parallelization | 85%+ | 0% | TEST-2 |
| Quality gates | 90%+ | 0% | TEST-3 |
| Status tracking | 85%+ | 0% | TEST-4 |
| Pre-step hooks | 85%+ | 0% | TEST-5 |
| Conventional commits | 90%+ | 0% | TEST-6 |

### Test Commands

```bash
# Run all tests for workflow-improvements
pytest tests/backend/test_lane_selection.py -v --cov=scripts/workflow
pytest tests/backend/test_parallelization.py -v --cov=scripts/workflow
pytest tests/backend/test_quality_gates.py -v --cov=scripts/quality_gates
pytest tests/backend/test_status_tracking.py -v --cov=scripts/workflow
pytest tests/backend/test_pre_step_hooks.py -v --cov=scripts/workflow
pytest tests/backend/test_conventional_commits.py -v --cov=scripts/workflow

# Combined coverage report
pytest tests/backend/test_*.py --cov=scripts --cov-report=html --cov-report=term

# Validate with comprehensive test suite
python openspec/changes/workflow-improvements/test.py
```

### Expected Test Results

- **test.py**: ✅ 54/54 PASSED (100%)
- **Unit Tests**: ≥80 tests total, ≥85% coverage
- **Integration Tests**: ✅ All lanes functional, parallel execution verified
- **Manual Tests**: ✅ Real workflows tested and validated

---

## Quality Gates

### Standard Lane Thresholds

| Tool | Criteria |
|------|----------|
| ruff | 0 errors |
| mypy | 0 errors |
| pytest | ≥80% pass rate, ≥70% coverage |
| bandit | 0 high-severity issues |

### Heavy Lane Thresholds

| Tool | Criteria |
|------|----------|
| ruff | 0 errors |
| mypy | 0 errors |
| pytest | **100% pass rate**, **≥85% coverage** |
| bandit | 0 high-severity issues |

### PASS/FAIL Logic

```
OVERALL_RESULT = PASS if:
  AND ruff_result == PASS
  AND mypy_result == PASS
  AND pytest_result == PASS (meeting lane thresholds)
  AND bandit_result == PASS (0 high-severity)
  
else:
  OVERALL_RESULT = FAIL
  Workflow stops with remediation steps
```

---

## File Operations Checklist

### Create Operations

- [ ] scripts/quality_gates.py (IMPL-8)
- [ ] tests/backend/test_lane_selection.py (TEST-1)
- [ ] tests/backend/test_parallelization.py (TEST-2)
- [ ] tests/backend/test_quality_gates.py (TEST-3)
- [ ] tests/backend/test_status_tracking.py (TEST-4)
- [ ] tests/backend/test_pre_step_hooks.py (TEST-5)
- [ ] tests/backend/test_conventional_commits.py (TEST-6)
- [ ] docs/WORKFLOW_IMPLEMENTATION_GUIDE.md (DOC-7)
- [ ] assistant_logs/ directory (IMPL-5)

### Modify Operations (scripts/workflow.py)

- [ ] Add --lane flag with docs/standard/heavy values (IMPL-1)
- [ ] Add lane-to-stage mapping dictionary (IMPL-3)
- [ ] Add code change detection for docs lane (IMPL-4)
- [ ] Add --use-agent flag support (IMPL-5)
- [ ] Add ThreadPoolExecutor parallelization (IMPL-6)
- [ ] Add --no-parallel flag (IMPL-7)
- [ ] Add status.json writing (IMPL-12)
- [ ] Add workflow resumption logic (IMPL-13)
- [ ] Add hook registry system (IMPL-14)
- [ ] Add Stage 0 environment validation hook (IMPL-15)
- [ ] Add Stage 10 git validation hook (IMPL-16)
- [ ] Add Stage 12 gh CLI validation hook (IMPL-17)
- [ ] Add commit message validator (IMPL-18)
- [ ] Add interactive commit fixer (IMPL-19)
- [ ] Add Colors class (IMPL-20)
- [ ] Add console output helpers (IMPL-21)
- [ ] Add atomic file write function (IMPL-22)
- [ ] Add StatusTracker class (IMPL-23)
- [ ] Add DocumentValidator class (IMPL-24)
- [ ] Add TemplateManager class (IMPL-25)
- [ ] Add DocumentGenerator class (IMPL-26)

### Modify Operations (scripts/workflow.ps1)

- [ ] Add -Lane parameter (IMPL-2)
- [ ] Pass lane to Python workflow (IMPL-3)
- [ ] Add --use-agent flag pass-through (IMPL-5)
- [ ] Add --no-parallel flag pass-through (IMPL-7)
- [ ] Add stage skip logic (IMPL-3)

### Documentation Updates

- [ ] The_Workflow_Process.md - Add lane sections (DOC-3)
- [ ] README.md - Add quick start lane section (DOC-4)
- [ ] CHANGELOG.md - Add v0.1.40 changes (DOC-5)
- [ ] All new functions - Add docstrings (DOC-1)
- [ ] Complex logic - Add inline comments (DOC-2)
- [ ] workflow.py --help - Document all flags (DOC-6)
- [ ] docs/WORKFLOW_IMPLEMENTATION_GUIDE.md - Create guide (DOC-7)

---

## Success Criteria

### Project Acceptance Criteria

- [ ] All P0 and P1 tasks completed
- [ ] All tests passing with ≥85% coverage for new code
- [ ] No critical or high-severity bugs
- [ ] Docs-only lane completes in <5 minutes (67% faster than current 15 min)
- [ ] Quality gates emit reliable PASS/FAIL decisions
- [ ] Security review passed (bandit 0 high-severity)
- [ ] Documentation complete and reviewed
- [ ] @UndiFineD approval obtained

### Quality Gates for This Change

| Gate | Criteria | Status |
|------|----------|--------|
| Code Quality | ruff 0 errors, complexity reasonable | [Pending] |
| Type Safety | mypy 0 errors | [Pending] |
| Test Coverage | Unit: ≥85%, Integration: ≥70% | [Pending] |
| Test Pass Rate | ≥80% pass rate | [Pending] |
| Security | bandit 0 high-severity issues | [Pending] |
| Documentation | All sections complete, reviewed | [Pending] |

---

## Next Steps

### Phase 1: Foundation (Days 1-2)
1. Execute IMPL-1, IMPL-2, IMPL-3 (lane selection)
2. Execute IMPL-8, IMPL-9 (quality gates basics)
3. Execute IMPL-12 (status tracking)
4. Execute TEST-1 (lane selection tests)

### Phase 2: Enhancement (Days 3-4)
1. Execute IMPL-4, IMPL-5, IMPL-6, IMPL-7 (lane enhancements)
2. Execute IMPL-10, IMPL-11 (quality gates integration)
3. Execute IMPL-13 (workflow resumption)
4. Execute remaining IMPL-14 through IMPL-26 tasks
5. Execute TEST-2 through TEST-6

### Phase 3: Documentation & Review (Days 5-6)
1. Execute DOC-1 through DOC-7
2. Code review with @UndiFineD
3. Address feedback and iterate

### Phase 4: Deployment (Day 7)
1. Merge PR to main
2. Monitor for issues
3. Gather user feedback
4. Post-release retrospective

---

## Usage Examples

### Run Docs Lane

```bash
python scripts/workflow.py --lane docs \
  --change-id update-readme \
  --title "Update README examples"
```

Expected behavior:
- Workflow execution: Stages 0, 2, 3, 4, 9, 10, 11, 12 (skip 1, 5, 6, 7, 8)
- Execution time: <5 minutes
- Output: status.json with stage-by-stage tracking

### Run Standard Lane with Quality Gates

```bash
python scripts/workflow.py --lane standard \
  --change-id feature-xyz \
  --title "Implement feature X"
```

Expected behavior:
- Workflow execution: All stages 0-12
- Stage 8: Quality gates validate ruff, mypy, pytest (80%+ pass, 70%+ coverage), bandit
- Output: quality_metrics.json with PASS/FAIL, status.json with full tracking

### Run Heavy Lane (Strict Validation)

```bash
python scripts/workflow.py --lane heavy \
  --change-id hotfix-critical \
  --title "Fix critical bug"
```

Expected behavior:
- Workflow execution: All stages 0-12 with verbose logging
- Stage 8: Quality gates use strict thresholds (100% pass, 85%+ coverage)
- Output: Comprehensive status.json and quality_metrics.json with audit trail

### Resume Interrupted Workflow

```bash
python scripts/workflow.py --lane standard --change-id feature-xyz --resume
```

Expected behavior:
- Detects incomplete workflow in status.json
- Prompts user to resume or start fresh
- Resumes from last completed stage
- Continues to completion

---

## References

- **proposal.md**: Business case and user requirements
- **spec.md**: Technical specifications and data models  
- **tasks.md**: Complete task breakdown with 187 identified tasks
- **test_plan.md**: Comprehensive testing strategy with pytest patterns
- **test.py**: 54 validation tests for all requirements
- **implement.py**: Comprehensive implementation execution script

---

## Questions & Support

For questions or issues during implementation:

1. **Review spec.md**: Technical details and acceptance criteria
2. **Check test.py**: Validation tests showing expected behavior
3. **Run implement.py --list**: See all available tasks
4. **Check existing code**: Reference implementation patterns in workflow.py

---

**Ready to implement? Start with Phase 1 tasks!** 🚀
