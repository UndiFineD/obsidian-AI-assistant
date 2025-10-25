# Test Plan: Workflow Improvements

---

## Document Overview

**Purpose**: Define comprehensive testing strategy, test cases, and validation criteria for workflow improvements (lanes, parallelization, quality gates).

**Change ID**: `workflow-improvements`

**Related Documents**:
- **Proposal**: [proposal.md](./proposal.md)
- **Specification**: [spec.md](./spec.md)
- **Tasks**: [tasks.md](./tasks.md)
- **TODO**: [todo.md](./todo.md)

**Owner**: @kdejo

**QA Lead**: @kdejo

**Status**: In Progress

**Last Updated**: 2025-10-23

---

## Table of Contents

### Planning & Strategy (1-5)
01. [Test Strategy](#1-test-strategy)
02. [Test Scope](#2-test-scope)
03. [Test Objectives](#3-test-objectives)
04. [Test Automation Strategy](#4-test-automation-strategy)
05. [Test Types & Coverage](#5-test-types--coverage)

### Test Implementation (6-14)
06. [Unit Testing](#6-unit-testing)
07. [Integration Testing](#7-integration-testing)
08. [End-to-End Testing](#8-end-to-end-testing)
09. [Performance Testing](#9-performance-testing)
10. [Security Testing](#10-security-testing)
11. [Compatibility Testing](#11-compatibility-testing)
12. [Regression Testing](#12-regression-testing)
13. [Manual Testing](#13-manual-testing)
14. [User Acceptance Testing (UAT)](#14-user-acceptance-testing-uat)

### Test Infrastructure (15-16)
15. [Test Environment](#15-test-environment)
16. [Test Data Management](#16-test-data-management)

### Test Execution & Management (17-20)
17. [Test Execution Schedule](#17-test-execution-schedule)
18. [Defect Management](#18-defect-management)
19. [Test Metrics & Reporting](#19-test-metrics--reporting)
20. [Risk Assessment](#20-risk-assessment)

### Test Completion & Best Practices (21-25)
21. [Test Deliverables](#21-test-deliverables)
22. [Entry & Exit Criteria](#22-entry--exit-criteria)
23. [Validation Checklist](#23-validation-checklist)
24. [Pytest Best Practices & Patterns](#24-pytest-best-practices--patterns)
25. [Document Metadata](#25-document-metadata)

---

## 1. Test Strategy

**Testing Approach**: Risk-Based Testing with Shift-Left principles

**Testing Principles**:
- **Early Testing**: Testing activities begin during design phase
- **Continuous Testing**: Automated tests run on every commit
- **Risk-Based**: Focus testing efforts on high-risk areas (lane selection, parallelization, quality gates)
- **Defect Prevention**: Identify and fix issues early through unit tests
- **Comprehensive Coverage**: All code paths, edge cases, and failure scenarios tested

**Testing Pyramid**:
```
        /\
       /  \  E2E Tests (15%)
      /    \
     /------\  Integration Tests (25%)
    /        \
   /----------\  Unit Tests (60%)
  /            \
```

**Test Level Distribution**:
- **Unit Tests**: 60% - Fast, isolated, developer-owned (lane logic, quality gates, status tracking)
- **Integration Tests**: 25% - Component interactions (full lane execution, quality gate integration)
- **End-to-End Tests**: 15% - Critical user workflows (docs lane end-to-end, standard lane, heavy lane)

**Quality Gates**:
- All unit tests must pass before code review
- Integration tests must pass before merge to main
- E2E tests must pass in manual validation
- Test coverage ≥85% for new code before merge
- Security scans must pass (bandit 0 high-severity)

---

## 2. Test Scope

**In Scope**:
- **Lane Selection**: All 3 lanes (docs, standard, heavy) with correct stage mapping
- **Parallelization**: Stages 2-6 parallel execution with deterministic output
- **Quality Gates**: ruff, mypy, pytest, bandit execution and threshold enforcement
- **Status Tracking**: status.json writing, resumption logic
- **Pre-Step Hooks**: Environment validation, git state checks, gh CLI validation
- **Conventional Commits**: Commit message validation, interactive fixer
- **Code Quality**: All new Python code in scripts/ directory
- **Regression Testing**: Ensure standard lane maintains current behavior

**Out of Scope**:
- **Existing Workflow Logic**: No changes to stages 1-12 internal logic (already tested)
- **External Tools**: pytest, ruff, mypy, bandit functionality (third-party, assumed working)
- **GUI Interface**: No web or GUI testing (CLI only)
- **Performance Optimization**: Beyond parallelization (out of current scope)

**Testing Boundaries**:
- **Start**: After implementation of each feature complete
- **End**: After production validation (PR merged, feature live)
- **Inclusions**: All new code in scripts/workflow.py, scripts/quality_gates.py, helper modules
- **Exclusions**: Existing agent/ backend code (not modified)

---

## 3. Test Objectives

**Primary Objectives**:
1. **Functional Correctness**: Verify all lanes execute correct stages
2. **Quality Assurance**: Ensure quality gates reliably detect failures
3. **Risk Mitigation**: Prevent workflow corruption, data loss, race conditions
4. **Performance Validation**: Confirm docs lane <5 minutes, parallelization faster than serial
5. **Security Assurance**: Validate input validation, file operations security

**Success Criteria**:
- ✅ All critical (P0) and high-priority (P1) test cases pass
- ✅ Test coverage ≥85% for new code (scripts/workflow.py, scripts/quality_gates.py)
- ✅ Test coverage ≥70% for integration tests (full lane execution)
- ✅ No open P0 or P1 defects
- ✅ All 3 lanes pass manual validation
- ✅ Performance benchmarks met (docs lane <5 min, parallelization faster)
- ✅ Security scan passes (bandit 0 high-severity)
- ✅ @UndiFineD acceptance obtained

---

## 4. Test Automation Strategy

**Automation Coverage**: 85% (unit + integration)

**Automation Framework**:
- **Language**: Python 3.11+
- **Framework**: pytest 7.4+
- **Coverage**: pytest-cov 4.1+
- **Mocking**: pytest-mock, unittest.mock

**Automation Approach**:
- **Unit Tests**: 100% automated - All new functions tested
- **Integration Tests**: 100% automated - All 3 lanes tested end-to-end
- **E2E Tests**: 50% automated - Critical paths automated, edge cases manual
- **Performance Tests**: 100% automated - Timing measurements in tests
- **Security Tests**: 100% automated - bandit, input validation tests

**CI/CD Integration**:
- Tests run on every commit via pytest
- Coverage reports generated and uploaded
- Failed tests block merge

---

## 5. Test Types & Coverage

**Test Type Coverage Matrix**:

| Test Type | Coverage Target | Automation | Owner | Tools |
|-----------|----------------|------------|-------|-------|
| Unit Tests | ≥85% code coverage | 100% automated | @kdejo | pytest, pytest-cov |
| Integration Tests | ≥70% workflow coverage | 100% automated | @kdejo | pytest |
| E2E Tests | 3 critical paths | 50% automated | @kdejo | pytest + manual |
| Performance Tests | Timing benchmarks | 100% automated | @kdejo | pytest + time.time() |
| Security Tests | Input validation, file ops | 100% automated | @kdejo | bandit, pytest |
| Compatibility Tests | Windows PowerShell | Manual | @kdejo | Manual execution |
| Regression Tests | Standard lane unchanged | 100% automated | @kdejo | pytest |

**Estimated Effort**:

| Test Type | Estimated Hours | Actual Hours | Variance |
|-----------|----------------|--------------|----------|
| Unit Test Creation | 12 hours | [TBD] | [TBD] |
| Integration Test Creation | 8 hours | [TBD] | [TBD] |
| E2E Test Creation | 4 hours | [TBD] | [TBD] |
| Performance Testing | 2 hours | [TBD] | [TBD] |
| Security Testing | 2 hours | [TBD] | [TBD] |
| Manual Testing | 4 hours | [TBD] | [TBD] |
| **Total** | **32 hours (4 days)** | **[TBD]** | **[TBD]** |

---

## 6. Unit Testing

**Unit Test Strategy**: Test individual functions, methods, and classes in isolation with mocked dependencies.

**Coverage Targets**:
- **Overall Coverage**: ≥85% for new code
- **Critical Modules**: ≥90% (lane selection, quality gates)
- **Branch Coverage**: ≥75%

**Testing Framework**: pytest 7.4+

**Test Organization**:
```
tests/
├── unit/
│   ├── test_lane_selection.py
│   ├── test_parallelization.py
│   ├── test_quality_gates.py
│   ├── test_status_tracking.py
│   ├── test_pre_step_hooks.py
│   ├── test_commit_validation.py
│   └── test_helpers.py
└── conftest.py
```

**Unit Test Cases**:

### Module 1: Lane Selection (scripts/workflow.py)

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UT-001 | Test docs lane mapping returns stages [0,2,3,4,9,10,11,12] | P0 | not-started | @kdejo |
| UT-002 | Test standard lane mapping returns stages [0-12] | P0 | not-started | @kdejo |
| UT-003 | Test heavy lane mapping returns stages [0-12] with strict=True | P0 | not-started | @kdejo |
| UT-004 | Test invalid lane name raises ValueError | P1 | not-started | @kdejo |
| UT-005 | Test default lane is standard when --lane not provided | P1 | not-started | @kdejo |
| UT-006 | Test detect_code_changes() returns True for .py files | P1 | not-started | @kdejo |
| UT-007 | Test detect_code_changes() returns False for .md files | P1 | not-started | @kdejo |

### Module 2: Parallelization (scripts/workflow.py)

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UT-101 | Test execute_stages_parallel() runs 5 stages concurrently | P0 | not-started | @kdejo |
| UT-102 | Test results dict sorted by stage number (deterministic) | P0 | not-started | @kdejo |
| UT-103 | Test timeout handling (5 min timeout per task) | P1 | not-started | @kdejo |
| UT-104 | Test exception in one task doesn't stop others | P1 | not-started | @kdejo |
| UT-105 | Test --no-parallel flag disables parallelization | P1 | not-started | @kdejo |
| UT-106 | Test max_workers=3 configuration | P2 | not-started | @kdejo |

### Module 3: Quality Gates (scripts/quality_gates.py)

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UT-201 | Test run_quality_gates() executes all 4 tools | P0 | not-started | @kdejo |
| UT-202 | Test PASS determination when all thresholds met | P0 | not-started | @kdejo |
| UT-203 | Test FAIL determination when any threshold fails | P0 | not-started | @kdejo |
| UT-204 | Test quality_metrics.json written with correct schema | P0 | not-started | @kdejo |
| UT-205 | Test strict thresholds for heavy lane | P1 | not-started | @kdejo |
| UT-206 | Test console summary includes color codes | P2 | not-started | @kdejo |
| UT-207 | Test error handling when tool execution fails | P1 | not-started | @kdejo |

### Module 4: Status Tracking

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UT-301 | Test status.json written with correct schema | P0 | not-started | @kdejo |
| UT-302 | Test atomic write prevents partial updates | P0 | not-started | @kdejo |
| UT-303 | Test resumption detects incomplete workflow | P1 | not-started | @kdejo |
| UT-304 | Test resumption prompts user correctly | P1 | not-started | @kdejo |
| UT-305 | Test state validation before resume | P1 | not-started | @kdejo |

### Module 5: Pre-Step Hooks

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UT-401 | Test validate_environment() checks Python 3.11+ | P0 | not-started | @kdejo |
| UT-402 | Test validate_environment() checks tool availability | P0 | not-started | @kdejo |
| UT-403 | Test validate_git_state() detects dirty working directory | P1 | not-started | @kdejo |
| UT-404 | Test validate_git_state() detects non-feature branch | P1 | not-started | @kdejo |
| UT-405 | Test validate_gh_cli() warns but doesn't block | P1 | not-started | @kdejo |
| UT-406 | Test hook registry executes correct hook for stage | P1 | not-started | @kdejo |

### Module 6: Conventional Commits

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UT-501 | Test valid commit message accepted | P1 | not-started | @kdejo |
| UT-502 | Test invalid format rejected | P1 | not-started | @kdejo |
| UT-503 | Test interactive fixer prompts user | P1 | not-started | @kdejo |
| UT-504 | Test --no-verify bypasses validation with warning | P1 | not-started | @kdejo |
| UT-505 | Test subject length validation (≤72 chars) | P2 | not-started | @kdejo |

**Test Execution**:
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=scripts --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_lane_selection.py -v

# Run tests matching pattern
pytest tests/unit/ -k "quality_gates" -v

# Run with coverage threshold enforcement
pytest tests/unit/ --cov=scripts --cov-fail-under=85
```

**Coverage Requirements by Module**:

| Module | Current Coverage | Target Coverage | Gap | Actions |
|--------|-----------------|-----------------|-----|---------|
| lane_selection | 0% | 90% | 90% | Create UT-001 through UT-007 |
| parallelization | 0% | 85% | 85% | Create UT-101 through UT-106 |
| quality_gates | 0% | 90% | 90% | Create UT-201 through UT-207 |
| status_tracking | 0% | 85% | 85% | Create UT-301 through UT-305 |
| pre_step_hooks | 0% | 85% | 85% | Create UT-401 through UT-406 |
| commit_validation | 0% | 85% | 85% | Create UT-501 through UT-505 |

---

## 7. Integration Testing

**Integration Test Strategy**: Test full lane execution from start to finish with minimal mocking.

**Integration Test Cases**:

### Scenario 1: Docs Lane End-to-End

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| IT-001 | Execute docs lane with README.md change | P0 | not-started | @kdejo |
| IT-002 | Verify stages 1,5,6,7,8 skipped | P0 | not-started | @kdejo |
| IT-003 | Verify status.json reflects correct execution | P0 | not-started | @kdejo |
| IT-004 | Verify completion time <5 minutes | P0 | not-started | @kdejo |
| IT-005 | Verify warning when code changes detected | P1 | not-started | @kdejo |

### Scenario 2: Standard Lane End-to-End

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| IT-101 | Execute standard lane with backend changes | P0 | not-started | @kdejo |
| IT-102 | Verify all 13 stages execute | P0 | not-started | @kdejo |
| IT-103 | Verify quality gates execute and emit metrics | P0 | not-started | @kdejo |
| IT-104 | Verify PASS case allows workflow continuation | P0 | not-started | @kdejo |
| IT-105 | Verify FAIL case stops workflow | P0 | not-started | @kdejo |

### Scenario 3: Heavy Lane End-to-End

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| IT-201 | Execute heavy lane with critical changes | P1 | not-started | @kdejo |
| IT-202 | Verify all 13 stages execute | P1 | not-started | @kdejo |
| IT-203 | Verify strict thresholds enforced | P1 | not-started | @kdejo |
| IT-204 | Verify verbose logging enabled | P1 | not-started | @kdejo |

### Scenario 4: Parallelization Integration

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| IT-301 | Execute workflow with parallelization enabled | P1 | not-started | @kdejo |
| IT-302 | Verify stages 2-6 run concurrently | P1 | not-started | @kdejo |
| IT-303 | Verify output deterministic across runs | P0 | not-started | @kdejo |
| IT-304 | Verify timing improvement vs serial | P1 | not-started | @kdejo |

### Scenario 5: Workflow Resumption

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| IT-401 | Interrupt workflow at stage 5 | P1 | not-started | @kdejo |
| IT-402 | Resume workflow from stage 5 | P1 | not-started | @kdejo |
| IT-403 | Verify completion successful | P1 | not-started | @kdejo |
| IT-404 | Verify state integrity maintained | P1 | not-started | @kdejo |

**Test Execution**:
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific scenario
pytest tests/integration/test_docs_lane_e2e.py -v

# Run with timing
pytest tests/integration/ -v --durations=10
```

---

## 8. End-to-End Testing

**E2E Test Strategy**: Test critical user workflows in real environment with minimal automation.

**E2E Test Scenarios**:

### Scenario 1: Documentation Contributor Workflow

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| E2E-001 | User updates README.md | P0 | not-started | @kdejo |
| E2E-002 | User runs `python scripts/workflow.py --lane docs --change-id update-readme --title "Update README"` | P0 | not-started | @kdejo |
| E2E-003 | Workflow completes in <5 minutes | P0 | not-started | @kdejo |
| E2E-004 | PR created successfully | P0 | not-started | @kdejo |
| E2E-005 | User reviews quality_metrics.json (should not exist for docs lane) | P1 | not-started | @kdejo |

### Scenario 2: Feature Developer Workflow

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| E2E-101 | User implements new feature in agent/backend.py | P0 | not-started | @kdejo |
| E2E-102 | User runs `python scripts/workflow.py --lane standard --change-id add-feature --title "Add feature X"` | P0 | not-started | @kdejo |
| E2E-103 | Quality gates execute and display results | P0 | not-started | @kdejo |
| E2E-104 | Workflow completes successfully if tests pass | P0 | not-started | @kdejo |
| E2E-105 | PR created with quality_metrics.json | P0 | not-started | @kdejo |

### Scenario 3: Hotfix Contributor Workflow

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| E2E-201 | User applies critical fix to production code | P1 | not-started | @kdejo |
| E2E-202 | User runs `python scripts/workflow.py --lane heavy --change-id hotfix-123 --title "Fix critical bug"` | P1 | not-started | @kdejo |
| E2E-203 | Strict thresholds enforced (100% pass rate) | P1 | not-started | @kdejo |
| E2E-204 | Verbose logging captures all actions | P1 | not-started | @kdejo |
| E2E-205 | PR created with comprehensive audit trail | P1 | not-started | @kdejo |

**Manual Test Procedure**:
1. Set up clean environment (fresh git clone)
2. Execute workflow command with specific lane
3. Observe console output for correct behavior
4. Verify timing with stopwatch
5. Inspect generated files (status.json, quality_metrics.json)
6. Verify PR creation (manual or with gh CLI)

---

## 9. Performance Testing

**Performance Test Strategy**: Measure timing and resource usage for key operations.

**Performance Benchmarks**:

| Metric | Target | Measurement Method | Priority |
|--------|--------|--------------------|----------|
| Docs lane full workflow | <5 minutes | time.time() in test | P0 |
| Standard lane full workflow | <15 minutes | time.time() in test | P1 |
| Heavy lane full workflow | <20 minutes | time.time() in test | P1 |
| Parallelization speedup | 30%+ faster than serial | Compare timing | P1 |
| Quality gates execution | <3 minutes | time.time() in test | P1 |
| status.json write | <100ms | time.time() in test | P2 |

**Performance Test Cases**:

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| PT-001 | Measure docs lane timing | P0 | not-started | @kdejo |
| PT-002 | Measure standard lane timing | P1 | not-started | @kdejo |
| PT-003 | Measure heavy lane timing | P1 | not-started | @kdejo |
| PT-004 | Compare parallel vs serial execution | P1 | not-started | @kdejo |
| PT-005 | Measure quality gates execution time | P1 | not-started | @kdejo |

**Test Execution**:
```bash
# Run performance tests
pytest tests/performance/ -v --durations=10

# Measure specific operation
python -m timeit -s "from scripts.workflow import execute_docs_lane" "execute_docs_lane()"
```

---

## 10. Security Testing

**Security Test Strategy**: Validate input validation, file operations, and prevent common vulnerabilities.

**Security Test Cases**:

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| SEC-001 | Test lane parameter rejects malicious input | P0 | not-started | @kdejo |
| SEC-002 | Test change-id sanitized (no path traversal) | P0 | not-started | @kdejo |
| SEC-003 | Test file writes use absolute paths | P0 | not-started | @kdejo |
| SEC-004 | Test subprocess calls don't use shell=True | P0 | not-started | @kdejo |
| SEC-005 | Test commit message escapes special characters | P1 | not-started | @kdejo |
| SEC-006 | Run bandit on new code (0 high-severity) | P0 | not-started | @kdejo |

**Test Execution**:
```bash
# Run security tests
pytest tests/security/ -v

# Run bandit scan
bandit -r scripts/ -f json -o tests/bandit_report.json
```

---

## 11. Compatibility Testing

**Compatibility Test Strategy**: Validate cross-platform functionality (Windows PowerShell, Linux bash).

**Compatibility Test Cases**:

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| COMPAT-001 | Test workflow.py on Windows | P0 | not-started | @kdejo |
| COMPAT-002 | Test workflow.ps1 on Windows PowerShell | P0 | not-started | @kdejo |
| COMPAT-003 | Test workflow.py on Linux (if applicable) | P2 | not-started | @kdejo |
| COMPAT-004 | Test file path handling cross-platform | P1 | not-started | @kdejo |

---

## 12. Regression Testing

**Regression Test Strategy**: Ensure standard lane behavior unchanged.

**Regression Test Cases**:

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| REG-001 | Test standard lane executes all 13 stages | P0 | not-started | @kdejo |
| REG-002 | Test standard lane timing unchanged (within 10%) | P1 | not-started | @kdejo |
| REG-003 | Test existing workflow.py arguments still work | P0 | not-started | @kdejo |
| REG-004 | Test existing OpenSpec files generated correctly | P0 | not-started | @kdejo |

---

## 13. Manual Testing

**Manual Test Strategy**: Exploratory testing, usability testing, edge cases.

**Manual Test Cases**:

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| MAN-001 | Test docs lane with real documentation change | P0 | not-started | @kdejo |
| MAN-002 | Test standard lane with real feature change | P0 | not-started | @kdejo |
| MAN-003 | Test heavy lane with real critical fix | P1 | not-started | @kdejo |
| MAN-004 | Test interactive commit fixer UX | P1 | not-started | @kdejo |
| MAN-005 | Test error messages clarity | P1 | not-started | @kdejo |
| MAN-006 | Test --help documentation accuracy | P1 | not-started | @kdejo |

---

## 14. User Acceptance Testing (UAT)

**UAT Strategy**: @UndiFineD validates feature meets requirements.

**UAT Test Cases**:

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UAT-001 | @UndiFineD tests docs lane with docs change | P0 | not-started | @UndiFineD |
| UAT-002 | @UndiFineD validates quality gate reliability | P0 | not-started | @UndiFineD |
| UAT-003 | @UndiFineD reviews documentation completeness | P1 | not-started | @UndiFineD |
| UAT-004 | @UndiFineD approves feature for merge | P0 | not-started | @UndiFineD |

---

## 15. Test Environment

**Test Environment Configuration**:

| Environment | OS | Python Version | Tools | Purpose |
|-------------|-----|----------------|-------|---------|
| Local Dev | Windows 11 | 3.11.5 | pytest, ruff, mypy, bandit, gh | Unit + Integration tests |
| CI/CD | GitHub Actions | 3.11+ | pytest, coverage | Automated tests on PR |
| Manual Test | Windows 11 | 3.11.5 | Full workflow tools | Manual validation |

**Environment Setup**:
```powershell
# Windows setup
.\setup.ps1
.\setup-venv311.ps1
.\.venv\Scripts\Activate.ps1

# Verify tools
python --version  # 3.11+
pytest --version  # 7.4+
ruff --version    # 0.1+
mypy --version    # 1.5+
bandit --version  # 1.7+
gh --version      # 2.0+ (optional)
```

---

## 16. Test Data Management

**Test Data Strategy**: Use fixtures and sample data for repeatable tests.

**Test Data Types**:
- Sample change directories with OpenSpec files
- Sample code files for quality gate testing
- Sample git repositories for git state testing
- Sample commit messages for validation testing

**Test Data Location**: `tests/fixtures/`

---

## 17. Test Execution Schedule

**Test Schedule**:

| Phase | Timeline | Tests | Owner |
|-------|----------|-------|-------|
| Phase 1: Unit Tests | Day 1-2 (Oct 24-25) | UT-001 through UT-505 | @kdejo |
| Phase 2: Integration Tests | Day 3 (Oct 26) | IT-001 through IT-404 | @kdejo |
| Phase 3: E2E Tests | Day 4 (Oct 27) | E2E-001 through E2E-205 | @kdejo |
| Phase 4: Performance + Security | Day 5 (Oct 28) | PT-001 through SEC-006 | @kdejo |
| Phase 5: Manual + UAT | Day 6 (Oct 29) | MAN-001 through UAT-004 | @kdejo + @UndiFineD |

---

## 18. Defect Management

**Defect Tracking**: GitHub Issues

**Defect Severity**:
- **P0 (Critical)**: Workflow broken, data loss, security vulnerability
- **P1 (High)**: Feature doesn't work, incorrect behavior
- **P2 (Medium)**: Minor bug, UX issue
- **P3 (Low)**: Cosmetic issue, documentation typo

**Defect Workflow**: Open → Assigned → In Progress → Fixed → Verified → Closed

---

## 19. Test Metrics & Reporting

**Key Metrics**:
- Test pass rate: Target 100%
- Code coverage: Target ≥85% for new code
- Defect density: Target <1 defect per 100 LOC
- Test execution time: Target <5 minutes for unit tests
- Mean time to resolution (MTTR): Target <1 day for P1 defects

**Reporting**:
- Daily: Update test execution status in this document
- Weekly: Report to @UndiFineD via GitHub PR comments
- Final: Test summary report attached to PR

---

## 20. Risk Assessment

**Test Risks**:

| Risk ID | Risk Description | Probability | Impact | Mitigation |
|---------|------------------|-------------|--------|------------|
| TEST-RISK-1 | Parallelization race conditions hard to reproduce | Medium | High | Stress testing with high concurrency |
| TEST-RISK-2 | Quality gate false positives | Medium | High | Extensive threshold tuning and validation |
| TEST-RISK-3 | Edge cases not covered | Medium | Medium | Comprehensive edge case brainstorming |
| TEST-RISK-4 | Platform-specific issues (Windows vs Linux) | Low | Medium | Test on both platforms if possible |

---

## 21. Test Deliverables

**Test Artifacts**:
- [ ] Test plan document (this file)
- [ ] Unit test suite (`tests/unit/`)
- [ ] Integration test suite (`tests/integration/`)
- [ ] E2E test suite (`tests/e2e/`)
- [ ] Coverage reports (`htmlcov/`, `coverage.xml`)
- [ ] Security scan report (`bandit_report.json`)
- [ ] Test execution summary (section 24)
- [ ] Defect log (GitHub Issues)

---

## 22. Entry & Exit Criteria

**Entry Criteria** (testing can begin when):
- [ ] All implementation tasks complete
- [ ] Code compiles/runs without errors
- [ ] Test environment set up
- [ ] Test data prepared

**Exit Criteria** (testing complete when):
- [ ] All P0 and P1 test cases pass
- [ ] Code coverage ≥85% for new code
- [ ] No open P0 or P1 defects
- [ ] Performance benchmarks met
- [ ] Security scan passes
- [ ] UAT approval obtained

---

## 23. Validation Checklist

### Pre-Testing Validation
- [x] Proposal approved
- [x] Specification complete
- [x] Tasks defined
- [ ] Implementation complete
- [ ] Test environment ready

### Testing Validation
- [ ] All unit tests pass (≥85% coverage)
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Performance benchmarks met
- [ ] Security scan passes (bandit 0 high-severity)
- [ ] Regression tests pass (standard lane unchanged)

### Final Validation
- [ ] UAT approval obtained from @UndiFineD
- [ ] All test deliverables complete
- [ ] Test summary report written
- [ ] Ready for merge

---

## 24. Pytest Best Practices & Patterns

### Pytest Configuration (pytest.ini)

```ini
[pytest]
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

testpaths = tests

minversion = 3.11

addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=scripts
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=85

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests requiring full workflow
    e2e: End-to-end tests
    slow: Tests that take more than 5 seconds
    security: Security-related tests
    performance: Performance benchmarks
```

### Conftest.py (Shared Fixtures)

```python
"""
Shared pytest fixtures for workflow tests.
Location: tests/conftest.py
"""
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_config():
    """Test configuration for workflow testing."""
    return {
        "models_dir": "./models",
        "vault_path": "./test_vault",
        "timeout": 300
    }

@pytest.fixture
def temp_change_dir():
    """Create temporary change directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_change_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_git_state(monkeypatch):
    """Mock git state for testing."""
    def mock_check_output(cmd, *args, **kwargs):
        if "status" in cmd:
            return b"On branch feature/test\nnothing to commit"
        return b""
    
    monkeypatch.setattr("subprocess.check_output", mock_check_output)

@pytest.fixture
def sample_proposal(temp_change_dir):
    """Create sample proposal.md for testing."""
    proposal_file = temp_change_dir / "proposal.md"
    proposal_file.write_text("# Proposal: Test Change\n\n## Context\nTest context")
    return proposal_file
```

### Test Example: Lane Selection

```python
"""
Unit tests for lane selection logic.
Location: tests/unit/test_lane_selection.py
"""
import pytest
from scripts.workflow import get_lane_mapping, detect_code_changes

def test_docs_lane_mapping():
    """Test docs lane returns correct stages."""
    # Arrange
    lane = "docs"
    
    # Act
    result = get_lane_mapping(lane)
    
    # Assert
    assert result["stages"] == [0, 2, 3, 4, 9, 10, 11, 12]
    assert 1 not in result["stages"]  # Version bump skipped
    assert 8 not in result["stages"]  # Quality gates skipped

def test_invalid_lane_raises_error():
    """Test invalid lane name raises ValueError."""
    # Arrange
    lane = "invalid"
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid lane"):
        get_lane_mapping(lane)

@pytest.mark.parametrize("lane,expected_count", [
    ("docs", 8),
    ("standard", 13),
    ("heavy", 13)
])
def test_lane_stage_count(lane, expected_count):
    """Test lane stage count using parametrization."""
    # Act
    result = get_lane_mapping(lane)
    
    # Assert
    assert len(result["stages"]) == expected_count
```

### Test Example: Quality Gates

```python
"""
Unit tests for quality gates module.
Location: tests/unit/test_quality_gates.py
"""
import pytest
from unittest.mock import patch, MagicMock
from scripts.quality_gates import run_quality_gates

@pytest.fixture
def mock_tool_success():
    """Mock all tools returning success."""
    return {
        "ruff": {"errors": 0, "passed": True},
        "mypy": {"errors": 0, "passed": True},
        "pytest": {"pass_rate": 1.0, "coverage": 0.85, "passed": True},
        "bandit": {"high_severity": 0, "passed": True}
    }

def test_quality_gates_pass(temp_change_dir, mock_tool_success):
    """Test quality gates return PASS when all thresholds met."""
    # Arrange
    with patch("scripts.quality_gates.run_ruff", return_value=mock_tool_success["ruff"]), \
         patch("scripts.quality_gates.run_mypy", return_value=mock_tool_success["mypy"]), \
         patch("scripts.quality_gates.run_pytest", return_value=mock_tool_success["pytest"]), \
         patch("scripts.quality_gates.run_bandit", return_value=mock_tool_success["bandit"]):
        
        # Act
        result = run_quality_gates(Path("."), temp_change_dir, strict=False)
        
        # Assert
        assert result["overall_result"] == "PASS"
        assert result["results"]["ruff"]["passed"] is True
        assert result["results"]["pytest"]["coverage"] >= 0.70

def test_quality_gates_fail_on_low_coverage(temp_change_dir):
    """Test quality gates return FAIL when coverage below threshold."""
    # Arrange
    mock_results = {
        "ruff": {"errors": 0, "passed": True},
        "mypy": {"errors": 0, "passed": True},
        "pytest": {"pass_rate": 1.0, "coverage": 0.50, "passed": False},  # Below 70%
        "bandit": {"high_severity": 0, "passed": True}
    }
    
    with patch("scripts.quality_gates.run_ruff", return_value=mock_results["ruff"]), \
         patch("scripts.quality_gates.run_mypy", return_value=mock_results["mypy"]), \
         patch("scripts.quality_gates.run_pytest", return_value=mock_results["pytest"]), \
         patch("scripts.quality_gates.run_bandit", return_value=mock_results["bandit"]):
        
        # Act
        result = run_quality_gates(Path("."), temp_change_dir, strict=False)
        
        # Assert
        assert result["overall_result"] == "FAIL"
        assert result["results"]["pytest"]["coverage"] < 0.70
```

### Running Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/unit/test_lane_selection.py -v

# Run tests with coverage
pytest --cov=scripts --cov-report=html --cov-report=term

# Run tests matching pattern
pytest -k "lane_selection" -v

# Run with markers
pytest -m unit -v
pytest -m integration -v

# Run with coverage threshold
pytest --cov=scripts --cov-fail-under=85

# Run specific test function
pytest tests/unit/test_lane_selection.py::test_docs_lane_mapping -v
```

---

## 25. Document Metadata

- **Created**: 2025-10-23
- **Last Updated**: 2025-10-23
- **Version**: v1.0
- **Authors**: @kdejo
- **Status**: In Progress
- **Approvers**: @UndiFineD (pending)


