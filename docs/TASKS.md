# Tasks: Add Unit Tests (002-add-unit-tests)

> Governance: Material updates to this document are governed by OpenSpec
> change proposals under the `project-documentation` capability. See
> `openspec/PROJECT_WORKFLOW.md` and related archived changes for reference.

**IMPORTANT:** All test scaffolding, execution, and reporting must use the './tests/' folder. Never create or reference
'./test/'.

**Input**: Design documents from `docs/`
**Date:** 2025-10-05
**Branch:** 002-add-unit-tests
**Spec:** docs/spec.md

---

## Task Generation Principles

- Follow TDD: Write failing tests before implementation

- Minimum 90% coverage for backend (Python) and plugin (TypeScript)

- Console + Markdown reporting for all test runs

- Security-focused tests for sensitive modules

- Legacy code coverage must improve over time

- Mark [P] for parallelizable tasks

---

## Actionable, Dependency-Ordered Tasks

### Phase 1: Setup & Audit

- [ ] T001 Audit backend modules in `agent/` and list all major files/classes/functions in `docs/audit-backend.md`

- [ ] T002 Audit plugin modules in `plugin/` and list all major files/classes/functions in `docs/audit-plugin.md`

- [ ] T003 Audit existing tests and coverage reports (if any) in `tests/` and document in `docs/audit-coverage.md`

- [ ] T004 Document sensitive modules requiring security-focused tests in `docs/security-modules.md`

### Phase 2: Test Scaffolding [P]

- [ ] T005 [P] For each backend module, create `tests/test_<module>.py` (one per file)

- [ ] T006 [P] For each plugin module, create `tests/<module>.test.ts` (one per file)

- [ ] T007 [P] For each sensitive module, create security-focused test stubs in corresponding test files

### Phase 3: Write Failing Tests (TDD) [P]

- [ ] T008 [P] For each backend module, write at least one failing pytest test per major function/class in
`tests/test_<module>.py`

- [ ] T009 [P] For each plugin module, write at least one failing Jest test per major function/class in `tests/<module>
.test.ts`

- [ ] T010 [P] For each contract, write at least one failing contract test in `tests/contract/`

### Phase 4: Implement Tests & Coverage [P]

- [ ] T011 [P] Implement passing tests for backend modules, targeting >=90% coverage in `tests/test_<module>.py`

- [ ] T012 [P] Implement passing tests for plugin modules, targeting >=90% coverage in `tests/<module>.test.ts`

- [ ] T013 [P] Implement security-focused tests for sensitive modules in their respective test files

- [ ] T014 [P] For legacy modules, incrementally add tests and document coverage improvement in `docs/legacy-coverage
.md`

### Phase 5: Reporting & Validation

- [ ] T015 Run `pytest --cov agent/` and output Markdown report to `docs/backend-test-report.md`

- [ ] T016 Run `jest --coverage plugin/` and output Markdown report to `docs/plugin-test-report.md`

- [ ] T017 Review Markdown reports for coverage and failures

- [ ] T018 Refactor code or add tests to meet coverage threshold

- [ ] T019 Document test results and coverage in project documentation

- [ ] T020 Validate full test suite (backend + plugin) completes in <5 minutes per NFR-001

### Phase 6: CI Integration & Finalization

- [ ] T021 Integrate coverage checks into CI pipeline (e.g., GitHub Actions)

- [ ] T022 Validate that all new code meets coverage and reporting requirements

- [ ] T023 Final review: Ensure all constitutional and spec requirements are met

---

## Parallelization Guide

- Tasks marked [P] can be executed in parallel (e.g., per module)

- Sequential tasks (T001-T004) must be completed before dependent tasks begin

- Example: Launch T005-T007 together for all modules

---

## Dependency Notes

- T001-T004 (setup/audit) must be completed before scaffolding and test writing

- T005-T007 (scaffolding) before T008-T010 (failing tests)

- T008-T010 (failing tests) before T011-T014 (implementation)

- Reporting/validation (T015-T019) after implementation

- CI/finalization (T020-T022) last

---

## Validation Checklist

- [ ] All contracts have corresponding tests

- [ ] All entities have model tasks

- [ ] All tests come before implementation

- [ ] Parallel tasks truly independent

- [ ] Each task specifies exact file path

- [ ] No task modifies same file as another [P] task

---

## Notes

- Refer to quickstart.md for step-by-step test integration

- Use data-model.md and contracts/unit-test-contract.md for entity and test conventions

- Document any deviations or blockers in project documentation
