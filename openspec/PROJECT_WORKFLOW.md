# OpenSpec: Project Workflow Specification

## Overview
This OpenSpec defines the standardized workflow for all major changes and contributions to the Obsidian AI Assistant project. It ensures traceability, quality, and repeatability for every feature, fix, or refactor.

---

## Workflow Stages

### 0. Create TODOs
**Purpose:** Make it visible what we are going to do and track our progress through the workflow.

**Best Practices:**
- Create TODO list at the start of every change proposal
- Use checkbox format for easy tracking
- Update status as each stage completes
- Link to artifacts as they're created

**Artifacts:** `openspec/changes/<change-id>/todo.md`

**Example Template:**
```markdown
# TODO: <Change Title>

## Workflow Progress
- [ ] 0. Create TODOs
- [ ] 1. Increment Release Version
- [ ] 2. Proposal
- [ ] 3. Specification
- [ ] 4. Task Breakdown
- [ ] 5. Test Definition
- [ ] 6. Script & Tooling
- [ ] 7. Implementation
- [ ] 8. Test Run & Validation
- [ ] 9. Documentation Update
- [ ] 10. Git Operations
- [ ] 11. Workflow Improvement

## Artifacts Created
- [ ] `proposal.md`
- [ ] `specs/spec.md`
- [ ] `tasks.md`
- [ ] `test_plan.md`
- [ ] `retrospective.md`
```

### 1. Increment Release Version (+0.0.1)
**Purpose:** Prepare the next development cycle by incrementing the release version (e.g., 0.1.1 → 0.1.2), ensuring all new work is tracked on a future version branch while the current release remains stable.
**Best Practices:**
- Create a new branch for the next release (e.g., `release-0.1.2`) after tagging the current release.
- Update version numbers in `CHANGELOG.md`, `README.md`, and config files.
- Automate version bumping with a script or CI workflow.
- Document the version increment in the OpenSpec change log.
**Artifacts:** Updated branch, versioned files, OpenSpec log entry.

### 2. Proposal
**Purpose:** Capture the motivation, context, and high-level goals for a change (feature, fix, refactor, or issue).
**Artifacts:** `openspec/changes/<change-id>/proposal.md`
**Contents:** Problem statement, rationale, alternatives, impact analysis, links to related issues or PRs.

### 3. Specification
**Purpose:** Define the technical and functional requirements for the change.
**Artifacts:** `openspec/changes/<change-id>/spec.md`
**Contents:** Acceptance criteria, data models, API changes, diagrams, security/privacy notes, performance requirements.

### 4. Task Breakdown
**Purpose:** Decompose the specification into actionable tasks and dependencies.
**Artifacts:** `openspec/changes/<change-id>/tasks.md`
**Contents:** Task list, dependencies, test plan, assignment, estimated effort.

### 5. Test Definition
**Purpose:** Define and implement tests before or alongside code changes.
**Artifacts:** `tests/`, `docs/TESTING_GUIDE.md`, `openspec/changes/<change-id>/test_plan.md`
**Contents:** Unit, integration, performance, and security tests; coverage goals; validation steps.
    - markdownlint all created .md files in `openspec/changes/<change-id>/`

### 6. Script & Tooling
**Purpose:** Add or update scripts for setup, validation, automation, and developer experience.
**Artifacts:** `scripts/`, `setup.ps1`, `setup.sh`, `Makefile`, etc.
**Contents:** Reusable scripts, automation, developer tools, CI/CD updates.

Tip: Use the scaffold tool to generate a new change directory quickly:

```bash
# Preview (no files created)
python scripts/openspec_new_change.py "My New Change" --dry-run

# Create with defaults (id: YYYY-MM-DD-my-new-change)
python scripts/openspec_new_change.py "My New Change" --owner @yourhandle

# Explicit id
python scripts/openspec_new_change.py --id 2025-10-18-my-new-change --title "My New Change"
```

### 7. Implementation
**Purpose:** Make code changes as defined in the spec and tasks.
**Artifacts:** `backend/`, `plugin/`, `tests/`, etc.
**Contents:** Code, refactors, documentation updates, commit messages.

### 8. Test Run & Validation
**Purpose:** Run all tests and validate acceptance criteria and quality gates.
**Artifacts:** `docs/TEST_RESULTS_*.md`, `htmlcov/`, `bandit_report.json`, CI/CD logs.
**Contents:** Test results, coverage, security scan outputs, performance benchmarks.

### 9. Documentation Update
**Purpose:** Update documentation to reflect changes and ensure maintainability.
**Artifacts:** `README.md`, `docs/`, `openspec/`, `CHANGELOG.md`, API docs.
**Contents:** Usage, architecture, API, workflow docs, changelog entries.

### 10. Git Operations
**Purpose:** Commit, tag, and push changes with traceable metadata and OpenSpec references.
**Artifacts:** Git commits, tags, branch updates.
**Contents:**
- Stage and commit your changes:
  ```bash
  git add .
  git commit -m "feat: implement <change-title> (<change-id>) [OpenSpec]"
  ```
- Tag the release (if applicable):
  ```bash
  git tag v<new-version>
  ```
- Push your branch and tags:
  ```bash
  git push origin <branch-name>
  git push origin --tags
  ```
- Move completed change to archive after merge:
  ```bash
  git mv openspec/changes/<change-id> openspec/changes/archive/<change-id>
  git commit -m "chore: archive completed change <change-id>"
  git push origin <branch-name>
  ```

### 11. Create Pull Request (PR)
**Purpose:** Open a Pull Request on GitHub to review and merge the change.
**Artifacts:** Pull Request on GitHub, linked to the change directory.
**Contents:**
- Reference the OpenSpec change directory in the PR description (e.g., `Implements openspec/changes/<change-id>`)
- Link to proposal/spec/tasks as needed
- Use a clear merge strategy (e.g., squash, rebase, or merge commit)
- Ensure all checks pass before merging

### 12. Archive Completed Change
**Purpose:** Move completed and merged changes to the archive to keep the active changes directory clean and focused.
**Best Practices:**
- Only archive changes after the Pull Request (PR) has been merged to main
- Preserve all artifacts (proposal, spec, tasks, tests, retrospective)
- Maintain the same directory structure in the archive
- Update any references in documentation to point to archived location
**Artifacts:** All change files moved to `openspec/changes/archive/<change-id>/`

---

## Directory Structure Example

```text
openspec/
  templates/
    todo.md                    # TODO template for new changes
  changes/
    2025-10-18-merge-requirements/
      todo.md                  # Progress tracking
      proposal.md
      spec.md
      tasks.md
      test_plan.md
      retrospective.md
    1-github-issue/
      todo.md                  # Progress tracking
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
