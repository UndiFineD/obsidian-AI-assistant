# OpenSpec: Project Workflow Specification

## Overview
This OpenSpec defines the standardized workflow for all major changes and contributions to the Obsidian AI Assistant project. It ensures traceability, quality, and repeatability for every feature, fix, or refactor.

---

## Workflow Stages

### 1. Proposal
- **Purpose:** Capture the motivation, context, and high-level goals for a change.
- **Artifacts:** `openspec/changes/<change-id>/proposal.md`
- **Contents:** Problem statement, rationale, alternatives, impact analysis.

### 2. Specification
- **Purpose:** Define the technical and functional requirements for the change.
- **Artifacts:** `openspec/changes/<change-id>/spec.md`
- **Contents:** Acceptance criteria, data models, API changes, diagrams, security/privacy notes.

### 3. Task Breakdown
- **Purpose:** Decompose the specification into actionable tasks.
- **Artifacts:** `openspec/changes/<change-id>/tasks.md`
- **Contents:** Task list, dependencies, test plan, assignment.

### 4. Test Definition
- **Purpose:** Define and implement tests before or alongside code changes.
- **Artifacts:** `tests/`, `docs/TESTING_GUIDE.md`, `openspec/changes/<change-id>/test_plan.md`
- **Contents:** Unit, integration, performance, and security tests.

### 5. Script & Tooling
- **Purpose:** Add or update scripts for setup, validation, and automation.
- **Artifacts:** `scripts/`, `setup.ps1`, `setup.sh`, `Makefile`, etc.
- **Contents:** Reusable scripts, automation, and developer tools.

### 6. Implementation
- **Purpose:** Make code changes as defined in the spec and tasks.
- **Artifacts:** `backend/`, `plugin/`, `tests/`, etc.
- **Contents:** Code, refactors, documentation updates.

### 7. Test Run & Validation
- **Purpose:** Run all tests and validate acceptance criteria.
- **Artifacts:** `docs/TEST_RESULTS_*.md`, `htmlcov/`, `bandit_report.json`, etc.
- **Contents:** Test results, coverage, security scan outputs.

### 8. Documentation Update
- **Purpose:** Update documentation to reflect changes.
- **Artifacts:** `README.md`, `docs/`, `openspec/`, `CHANGELOG.md`
- **Contents:** Usage, architecture, API, and workflow docs.

### 9. Git Operations
- **Purpose:** Commit, tag, and push changes with traceable metadata.
- **Artifacts:** Git commits, tags, PRs.
- **Contents:** `git add`, `git commit`, `git tag`, `git push`, PR description linking to OpenSpec.

### 10. Workflow Improvement
- **Purpose:** Capture lessons learned and propose improvements to the workflow.
- **Artifacts:** `openspec/changes/<change-id>/retrospective.md` (optional)
- **Contents:** What worked, what didn’t, improvement proposals.

---

## Directory Structure Example

```
openspec/
  changes/
    2025-10-18-merge-requirements/
      proposal.md
      spec.md
      tasks.md
      test_plan.md
      retrospective.md
```

## Governance
- All changes must follow this workflow.
- Exceptions require explicit approval and documentation.
- See `AGENTS.md` and `CONSTITUTION.md` for governance details.

---

## References
- `docs/COMPREHENSIVE_SPECIFICATION.md`
- `docs/TESTING_GUIDE.md`
- `docs/PROJECT_SPECIFICATION.md`
- `openspec/AGENTS.md`
- `openspec/CONSTITUTION.md`
