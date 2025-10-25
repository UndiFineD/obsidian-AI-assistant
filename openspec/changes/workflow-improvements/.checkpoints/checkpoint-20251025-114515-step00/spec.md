# Specification: Workflow Improvements (Lanes, Parallelization, Validation)

---

## Document Overview

**Purpose**: Define the technical and functional specifications for implementing workflow improvements with lane selection, parallelization, and quality gates.

**Document Type**: Technical Specification Document

**Version**: 1.0

**Last Updated**: 2025-10-23

**Authors**: @kdejo

**Stakeholders**: @kdejo (owner), @UndiFineD (reviewer), all OpenSpec contributors

**Status**: In Progress

---

## Table of Contents

### Introduction (1-3)
1. [Project Overview](#1-project-overview)
2. [Project Target](#2-project-target)
3. [Acceptance Criteria](#3-acceptance-criteria)

### Technical Design (4-7)
4. [Technical Design](#4-technical-design)
5. [Functional Specifications](#5-functional-specifications)
6. [Technical Specifications](#6-technical-specifications)
7. [Data Models and Schemas](#7-data-models-and-schemas)

### Implementation Details (8-11)
8. [API Specifications](#8-api-specifications)
9. [Dependencies](#9-dependencies)
10. [Migration and Compatibility](#10-migration-and-compatibility)
11. [Security and Compliance](#11-security-and-compliance)

### Supporting Material (12-15)
12. [Performance Requirements](#12-performance-requirements)
13. [Testing and Quality Assurance](#13-testing-and-quality-assurance)
14. [References](#14-references)
15. [Glossary](#15-glossary)

---

## 1. Project Overview

**Project Name**: OpenSpec Workflow Improvements

**Project Vision**: Transform the OpenSpec 13-stage workflow into a flexible, efficient system that adapts to change complexity while maintaining governance standards.

**Project Summary**:

The OpenSpec Workflow Improvements project enhances the existing 13-stage workflow system by introducing intelligent lane selection that routes changes through appropriate validation stages based on complexity. Documentation-only changes can complete in under 5 minutes (67% faster) by skipping unnecessary stages, while maintaining full governance for code changes. The system includes automated quality gates that eliminate manual validation errors, parallel execution for documentation generation stages, and comprehensive status tracking for workflow observability.

This enhancement solves the current pain point where all changes—regardless of complexity—follow the same heavyweight process, causing frustration and wasted time. By implementing three lanes (docs, standard, heavy) with smart stage selection, we provide flexibility without compromising quality or governance.

**Background and Context**:

The current workflow, defined in `The_Workflow_Process.md`, executes all 13 stages sequentially for every change. This approach works well for complex changes but creates unnecessary overhead for simple documentation updates. Contributors have reported frustration with:
- Waiting ~15 minutes for docs-only changes that should take <5 minutes
- Manual interpretation of quality gate results (ruff, mypy, pytest, bandit)
- Repetitive environment validation (checking gh CLI, git state) at runtime
- No visibility into workflow progress when interrupted

The business driver for this change is developer productivity and satisfaction. With increasing contribution frequency, every minute saved per change compounds into significant time savings across the project lifecycle.

**Project Goals**:

1. **Primary Goal**: Reduce docs-only change cycle time by 67% (15 min → <5 min) while maintaining governance standards
2. **Secondary Goal**: Automate quality gate validation with 100% reliable PASS/FAIL determination
3. **Tertiary Goal**: Improve developer experience with clear error messages, progress tracking, and workflow resumption

**Success Metrics**:

| Metric | Target | Measurement Method | Baseline | Owner |
|--------|--------|--------------------|---------| ------|
| **Docs-only cycle time** | <5 minutes | Time from workflow start to PR creation | 15 minutes | @kdejo |
| **Lane adoption rate** | 80%+ within 1 month | Track --lane flag usage in status.json | 0% (N/A) | @kdejo |
| **Quality gate reliability** | 100% automated, 0% false positives | Audit quality_metrics.json results | Manual (variable) | @kdejo |
| **Workflow completion rate** | 95%+ | Track final status in status.json | ~85% | @kdejo |
| **User satisfaction** | 4.5/5 in post-release survey | User feedback survey | N/A | @kdejo |

**Measurement Frequency**: Daily for first 2 weeks, weekly thereafter
**Review Cadence**: Weekly review with @UndiFineD for first month

**Scope**:

**In Scope**:
- Lane selection logic (--lane flag for docs/standard/heavy)
- Lane-to-stage mapping with conditional execution
- Parallelization for documentation generation stages (2-6)
- Pre-step validation hooks (environment checks before dependent stages)
- Unified quality gates module (ruff, mypy, pytest, bandit)
- Status tracking system (status.json per change)
- Conventional Commits validation with interactive fixer
- Optional --use-agent flag for AI-assisted execution (with fallbacks)

**Out of Scope**:
- Replacing or fundamentally changing the 13-stage workflow model
- Changing test frameworks (pytest, Jest, etc.) or CI providers
- Altering repository branching strategies beyond lane-based conditions
- Building a standalone workflow orchestration platform
- GUI or web interface for workflow execution

**Key Deliverables**:

| Deliverable | Description | Acceptance Criteria | Due Date | Owner |
|-------------|-------------|---------------------|----------|-------|
| **Lane selection implementation** | Python and PowerShell scripts support --lane flag | All 3 lanes functional and tested | 2025-10-24 | @kdejo |
| **Quality gates module** | scripts/quality_gates.py emits PASS/FAIL | Thresholds enforced, JSON output validated | 2025-10-25 | @kdejo |
| **Parallelization engine** | Stages 2-6 run in parallel | Deterministic output, timing improvements verified | 2025-10-25 | @kdejo |
| **Status tracking system** | status.json written at each stage | Resume capability functional | 2025-10-26 | @kdejo |
| **Documentation** | The_Workflow_Process.md updated | All lanes documented with examples | 2025-10-29 | @kdejo |
| **Tests** | Unit + integration tests | 85%+ coverage, all lanes tested | 2025-10-28 | @kdejo |

**Project Phases**:

| Phase | Duration | Key Activities | Deliverables |
|-------|----------|----------------|--------------|
| **Phase 1: Planning** | 1 day (Oct 23) | Documentation (proposal, spec, tasks, test_plan), design | Complete OpenSpec artifacts |
| **Phase 2: Core Implementation** | 2 days (Oct 24-25) | Lane selection, parallelization, quality gates | Functional lane system |
| **Phase 3: Enhancement** | 2 days (Oct 26-27) | Hooks, status tracking, commit validation | Complete feature set |
| **Phase 4: Testing** | 1 day (Oct 28) | Unit tests, integration tests, manual validation | Test suite passing |
| **Phase 5: Documentation & Review** | 1 day (Oct 29) | Update docs, code review, feedback | Ready for merge |
| **Phase 6: Deployment** | 1 day (Oct 30) | Merge PR, monitor, gather feedback | Live and monitored |

**Assumptions and Dependencies**:

**System Assumptions**:
1. **Environmental**: Python 3.11+ is available in all development environments
2. **User**: Contributors are familiar with command-line workflow execution
3. **Technology**: pytest, ruff, mypy, bandit are installed and functional
4. **Data**: Existing workflow scripts (workflow.py, workflow.ps1) are maintainable
5. **Operational**: Changes are tested locally before PR creation

**Key Dependencies**:
- **Python 3.11+**: Required for type hints and modern syntax
- **pytest**: Test framework for validation (already installed)
- **ruff**: Linting tool for code quality (already installed)
- **mypy**: Type checker for Python code (already installed)
- **bandit**: Security scanner (already installed)
- **gh CLI**: Optional for PR creation (fallback to manual available)
- **git**: Version control (required, already installed)
- **@UndiFineD**: Code review and approval (blocking for merge)

**Constraints**:

**Technical Constraints**:
- **Platform**: Must support Windows (PowerShell) and Unix (bash/Python)
- **Backward Compatibility**: Default behavior must match current workflow
- **Python Version**: Must work with Python 3.11+ (no earlier versions)
- **No External Dependencies**: Cannot introduce new cloud services or paid tools

**Business Constraints**:
- **Budget**: Zero budget (volunteer open-source project)
- **Timeline**: 7-day implementation window (Oct 23-30)
- **Resources**: Single developer (@kdejo) with limited hours
- **Approval**: Requires @UndiFineD approval before merge

**Organizational Constraints**:
- **Coding Standards**: Must follow existing project conventions (PEP 8, 4-space indent)
- **Testing Standards**: 85%+ coverage for new code, all tests must pass
- **Documentation Standards**: All changes documented in relevant files

---

## 2. Project Target

**Target Audience**: All contributors to the obsidian-AI-assistant project using the OpenSpec workflow

### Primary Users

**User Persona 1: Documentation Writer**
- **Demographics**: Technical writers, developers contributing docs, ages 25-45, global
- **Job Role**: Documentation contributor, occasional developer
- **Technical Proficiency**: Comfortable with git, markdown, basic CLI
- **Goals**: 
    - Update documentation quickly without waiting for unnecessary validation
    - Ensure documentation quality without running full test suite
    - Contribute frequently with minimal friction
- **Pain Points**:
    - Current workflow takes ~15 minutes for docs-only changes
    - Forced to run test stages even when no code changes
    - No clear feedback on what stages are necessary
- **User Needs**: Fast, frictionless documentation updates with appropriate validation
- **Usage Context**: Updates README, docs/, OpenSpec templates 2-3 times per week

**User Persona 2: Feature Developer**
- **Demographics**: Software engineers, ages 25-50, global
- **Job Role**: Full-stack developer, backend/frontend specialist
- **Technical Proficiency**: Expert with Python, JavaScript, git, CI/CD, testing
- **Goals**:
    - Implement features with comprehensive quality validation
    - Get clear PASS/FAIL from quality gates
    - Understand workflow progress and resume if interrupted
- **Pain Points**:
    - Manual interpretation of quality gate results (which tool failed?)
    - No visibility into workflow progress
    - Cannot resume workflow after interruption
- **User Needs**: Automated quality validation, clear progress tracking, reliable workflow execution
- **Usage Context**: Implements features 1-2 times per week with full test suite

**User Persona 3: Hotfix Contributor**
- **Demographics**: Senior engineers, on-call responders, ages 30-55
- **Job Role**: Senior engineer, technical lead, DevOps
- **Technical Proficiency**: Expert in all project areas
- **Goals**:
    - Apply critical fixes quickly with maximum validation
    - Ensure no regressions in production systems
    - Have audit trail and comprehensive logging
- **Pain Points**:
    - Standard workflow not thorough enough for critical changes
    - Need more validation and logging for production fixes
    - Want stricter quality gates for high-risk changes
- **User Needs**: Heavy validation lane with enhanced logging and stricter gates
- **Usage Context**: Infrequent but critical changes, production hotfixes

### Secondary Users

**User Persona 4: Code Reviewer (@UndiFineD)**
- **Role**: Project maintainer, code reviewer
- **Needs**: 
  - Clear quality metrics in PR (PASS/FAIL from quality_metrics.json)
  - Understand which lane was used for the change
  - Verify appropriate validation was applied
- **Frequency of Use**: Reviews all PRs, multiple times per week

### Use Cases

**Use Case 1: Documentation-Only Update**
- **Actor**: Documentation Writer
- **Preconditions**: README.md needs updated examples
- **Flow**:
  1. Run `python scripts/workflow.py --lane docs --change-id update-readme --title "Update README examples"`
  2. Workflow detects docs-only change, executes stages: 0, 2, 3, 4, 9, 10, 11, 12
  3. Skips stages 1, 5, 6, 7, 8 (version bump, test plan, scripts, implementation, testing)
  4. Generates proposal.md, spec.md, tasks.md automatically
  5. Validates git state before commit
  6. Creates PR with gh CLI
  7. Total time: <5 minutes
- **Postconditions**: PR created with documentation changes, appropriate validation applied
- **Alternative Flows**: 
  - If code changes detected, warn user and offer to switch to standard lane
  - If gh CLI unavailable, provide manual PR instructions

**Use Case 2: Feature Implementation with Quality Gates**
- **Actor**: Feature Developer
- **Preconditions**: New feature requires backend changes and tests
- **Flow**:
  1. Run `python scripts/workflow.py --lane standard --change-id add-feature --title "Add feature X"`
  2. Workflow executes all 13 stages
  3. Stage 8 runs quality gates: ruff, mypy, pytest (coverage), bandit
  4. Quality gates emit quality_metrics.json with PASS/FAIL
  5. Console displays color-coded summary with links to detailed reports
  6. If PASS, workflow continues to git operations
  7. If FAIL, workflow stops with clear error messages and remediation steps
  8. Total time: ~12-20 minutes
- **Postconditions**: PR created with full validation, quality_metrics.json attached
- **Alternative Flows**:
  - If quality gates fail, developer fixes issues and reruns from last stage
  - If workflow interrupted, resume from last completed stage using status.json

**Use Case 3: Critical Hotfix with Heavy Validation**
- **Actor**: Hotfix Contributor
- **Preconditions**: Production issue requires immediate fix
- **Flow**:
  1. Run `python scripts/workflow.py --lane heavy --change-id hotfix-123 --title "Fix critical bug"`
  2. Workflow executes all 13 stages with verbose logging
  3. Quality gates use stricter thresholds (100% test pass rate, 0 security issues)
  4. All actions logged to assistant_logs/ with timestamps
  5. Status.json includes comprehensive audit trail
  6. Total time: ~15-25 minutes (thorough validation)
- **Postconditions**: PR created with comprehensive validation, full audit trail available
- **Alternative Flows**: If stricter gates fail, escalate to team for review

### User Journey Maps

**Journey 1: Documentation Contributor (Fast Lane)**

| Stage | User Actions | Touchpoints | Emotions | Pain Points | Opportunities | Our Solution |
|-------|--------------|-------------|----------|-------------|---------------|--------------|
| **Awareness** | Identifies docs that need updates | README.md, docs/ | Motivated to improve | Worries about workflow overhead | Reduce perceived complexity | Document --lane docs clearly |
| **Execution** | Runs workflow.py --lane docs | CLI, terminal | Hopeful, slightly anxious | Uncertainty about time required | Show progress and ETA | Progress spinners, status updates |
| **Validation** | Workflow skips unnecessary stages | Workflow orchestrator | Relieved, efficient | Would worry if skipped wrong stages | Build confidence with warnings | Auto-detect code changes, warn user |
| **Completion** | PR created in <5 minutes | GitHub | Satisfied, accomplished | N/A | Celebrate success | Success message with PR link |

**Journey Visualization**: [Mermaid diagram showing flow from start to PR creation]

### Target Market Characteristics

**Market Size**: 
- **Total Contributors**: 5-10 active contributors
- **Potential Contributors**: 50+ GitHub stargazers/watchers
- **Broader Market**: Thousands of open-source projects using OpenSpec-style workflows

**Geographic Target**: Global (English documentation)

**Market Segments**:
1. **Active Contributors**: Core team members contributing weekly
2. **Occasional Contributors**: External contributors contributing monthly
3. **Documentation-Only Contributors**: Technical writers, non-developers

**Adoption Strategy**: 
- Default to "standard" lane (no behavior change)
- Announce "docs" lane in CHANGELOG and README
- Provide examples in The_Workflow_Process.md

**User Acquisition Channels**:
1. **Internal Documentation**: README, CHANGELOG, workflow docs
2. **In-Line Help**: --help flag, error messages with suggestions
3. **Onboarding**: Update setup.ps1 to explain lanes

**Growth Metrics**:
- **Month 1**: 80%+ of docs-only changes use docs lane
- **Month 2-3**: <5% workflow interruptions/failures
- **Month 3-6**: User satisfaction 4.5/5 in survey

---

## 3. Acceptance Criteria

### Lane Selection
- [ ] `--lane [docs|standard|heavy]` flag exists in `scripts/workflow.py`
- [ ] `-Lane [docs|standard|heavy]` parameter exists in `scripts/workflow.ps1`
- [ ] Lane-to-stage mapping implemented and documented
- [ ] Auto-detection of code changes in docs lane warns user
- [ ] Default lane is "standard" (backward compatible)

### Parallelization
- [ ] Stages 2-6 run in parallel by default
- [ ] Max workers configurable (default: 3)
- [ ] Deterministic output ordering despite parallel execution
- [ ] `--no-parallel` flag disables parallelization for debugging

### Pre-Step Validation Hooks
- [ ] Hook registry system implemented
- [ ] Stage 0: Python environment, required tools validated
- [ ] Stage 10: Git state (clean, feature branch) validated
- [ ] Stage 12: gh CLI availability checked, fallback instructions provided
- [ ] Failed hooks display clear error messages with remediation steps

### Quality Gates (Stage 8)
- [ ] `scripts/quality_gates.py` module created
- [ ] Executes: ruff (lint), mypy (type), pytest (coverage), bandit (security)
- [ ] Emits `quality_metrics.json` with PASS/FAIL and detailed metrics
- [ ] Console summary is color-coded with links to detailed reports
- [ ] Thresholds enforced: ruff 0 errors, mypy 0 errors, pytest ≥80% pass ≥70% coverage, bandit 0 high-severity

### Status Tracking
- [ ] `status.json` written at each stage start and end
- [ ] Includes: step_id, start_time, end_time, result (success/failure), metrics
- [ ] Enables workflow resumption after interruption
- [ ] Atomic writes prevent corruption

### Conventional Commits Validation (Stage 10)
- [ ] Validates commit message format: `type(scope): subject`
- [ ] Interactive fixer prompts user for corrections
- [ ] `--no-verify` escape hatch available with warning
- [ ] Supports types: feat, fix, docs, style, refactor, test, chore

### Optional Agent Integration
- [ ] `--use-agent` flag implemented (Python and PowerShell)
- [ ] All agent actions logged to `<change-dir>/assistant_logs/`
- [ ] Manual fallbacks functional when agent unavailable
- [ ] status.json includes `agent_enabled: true` when used

### Documentation
- [ ] `docs/The_Workflow_Process.md` updated with lane guide, examples
- [ ] `openspec/PROJECT_WORKFLOW.md` updated with lane usage
- [ ] `README.md` mentions lane feature
- [ ] `CHANGELOG.md` documents changes
- [ ] Inline --help documentation complete

### Testing
- [ ] Unit tests: 85%+ coverage for new modules
- [ ] Integration tests: All 3 lanes tested end-to-end
- [ ] Manual validation: Real changes tested in each lane
- [ ] Regression tests: Standard lane behavior unchanged

---

## 4. Technical Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Workflow Orchestrator                        │
│                   (workflow.py / workflow.ps1)                      │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ├──► Parse CLI flags (--lane, --change-id, etc.)
                          │
                          ├──► Load lane-to-stage mapping
                          │
                          ├──► For each stage in mapping:
                          │    │
                          │    ├──► Execute pre-step hook (validation)
                          │    │
                          │    ├──► Execute stage logic
                          │    │    │
                          │    │    ├──► Stages 2-6: Parallel execution
                          │    │    │    (ThreadPoolExecutor, max_workers=3)
                          │    │    │
                          │    │    └──► Stage 8: Quality gates
                          │    │         (scripts/quality_gates.py)
                          │    │
                          │    └──► Write status.json update
                          │
                          └──► Generate summary report
                               Write final status.json
```

### Lane-to-Stage Mapping

```python
LANE_MAPPING = {
    "docs": {
        "stages": [0, 2, 3, 4, 9, 10, 11, 12],
        "description": "Documentation-only changes",
        "skip_reason": {
            1: "No version bump for docs-only",
            5: "No test plan needed for docs-only",
            6: "No scripts needed for docs-only",
            7: "No implementation for docs-only",
            8: "No quality gates for docs-only"
        }
    },
    "standard": {
        "stages": list(range(13)),  # 0-12
        "description": "Normal development workflow",
        "skip_reason": {}
    },
    "heavy": {
        "stages": list(range(13)),  # 0-12
        "description": "Critical changes with enhanced validation",
        "skip_reason": {},
        "options": {
            "verbose_logging": True,
            "strict_thresholds": True
        }
    }
}
```

### Parallelization Architecture (Stages 2-6)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_stages_parallel(stages, change_dir, max_workers=3):
    """Execute stages 2-6 in parallel with deterministic output."""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all stages
        future_to_stage = {
            executor.submit(execute_stage, stage, change_dir): stage
            for stage in stages
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_stage):
            stage = future_to_stage[future]
            try:
                result = future.result(timeout=300)  # 5 min timeout
                results[stage] = result
            except Exception as exc:
                results[stage] = {"error": str(exc), "status": "failed"}
    
    # Sort results by stage number for deterministic output
    return dict(sorted(results.items()))
```

### Quality Gates Architecture

```python
# scripts/quality_gates.py

def run_quality_gates(codebase_root, change_dir, strict=False):
    """
    Execute all quality gates and emit metrics.
    
    Args:
        codebase_root: Root directory of codebase
        change_dir: Change directory for output files
        strict: Use stricter thresholds for heavy lane
    
    Returns:
        dict: Quality metrics with PASS/FAIL decision
    """
    # Define thresholds
    thresholds = {
        "ruff_errors": 0,
        "mypy_errors": 0,
        "pytest_pass_rate": 1.0 if strict else 0.80,
        "pytest_coverage": 0.85 if strict else 0.70,
        "bandit_high_severity": 0
    }
    
    # Run tools
    ruff_result = run_ruff(codebase_root)
    mypy_result = run_mypy(codebase_root)
    pytest_result = run_pytest(codebase_root)
    bandit_result = run_bandit(codebase_root)
    
    # Evaluate against thresholds
    passed = (
        ruff_result["errors"] <= thresholds["ruff_errors"] and
        mypy_result["errors"] <= thresholds["mypy_errors"] and
        pytest_result["pass_rate"] >= thresholds["pytest_pass_rate"] and
        pytest_result["coverage"] >= thresholds["pytest_coverage"] and
        bandit_result["high_severity"] <= thresholds["bandit_high_severity"]
    )
    
    # Build metrics object
    metrics = {
        "overall_result": "PASS" if passed else "FAIL",
        "timestamp": datetime.now().isoformat(),
        "thresholds": thresholds,
        "results": {
            "ruff": ruff_result,
            "mypy": mypy_result,
            "pytest": pytest_result,
            "bandit": bandit_result
        }
    }
    
    # Write to file
    metrics_file = Path(change_dir) / "quality_metrics.json"
    write_json_atomic(metrics_file, metrics)
    
    # Print console summary
    print_quality_summary(metrics)
    
    return metrics
```

### Pre-Step Hook System

```python
# Centralized hook registry
PRE_STEP_HOOKS = {
    0: validate_environment,
    1: validate_version_files,
    10: validate_git_state,
    12: validate_gh_cli
}

def execute_pre_step_hooks(stage_num):
    """Execute pre-step validation hook if registered."""
    if stage_num in PRE_STEP_HOOKS:
        hook_func = PRE_STEP_HOOKS[stage_num]
        try:
            hook_func()
        except ValidationError as e:
            print_error(f"Pre-step validation failed for stage {stage_num}")
            print_error_hint(str(e), e.remediation)
            sys.exit(1)
```

---

## 5. Functional Specifications

### FR-1: Lane Selection

**Description**: Users can select workflow execution lane via `--lane` flag

**Inputs**:
- `--lane` parameter: `docs` | `standard` | `heavy` (default: `standard`)

**Processing**:
1. Parse CLI arguments
2. Validate lane name (must be one of 3 valid options)
3. Load lane-to-stage mapping from `LANE_MAPPING` dict
4. If docs lane, check for code changes with `detect_code_changes()`
5. If code detected in docs lane, warn user and offer to switch

**Outputs**:
- Selected lane configuration with list of stages to execute
- Warning message if code detected in docs lane

**Business Rules**:
- Default lane is `standard` for backward compatibility
- Docs lane only valid if no code changes detected
- Heavy lane uses stricter quality thresholds

**Error Handling**:
- Invalid lane name: Display error with valid options
- Code in docs lane: Warn but allow continuation with confirmation

### FR-2: Conditional Stage Execution

**Description**: Execute only stages mapped to selected lane

**Inputs**:
- Lane configuration (list of stage numbers)
- Change directory path

**Processing**:
1. Iterate through lane configuration stages
2. For each stage:
   - Execute pre-step hook (if registered)
   - Execute stage logic
   - Write status.json update
3. Skip stages not in lane configuration

**Outputs**:
- Executed stages complete successfully
- Skipped stages logged with skip reason
- status.json reflects execution state

**Business Rules**:
- Stages must execute in numerical order (dependencies)
- Skipped stages logged for audit trail
- Failed stage stops workflow execution

### FR-3: Parallel Documentation Generation (Stages 2-6)

**Description**: Generate documentation files (proposal, spec, tasks, test_plan, todo) in parallel

**Inputs**:
- Change directory path
- Template directory path
- Change metadata (id, title, owner)

**Processing**:
1. Create ThreadPoolExecutor with max_workers=3
2. Submit 5 generation tasks (stages 2-6) concurrently
3. Each task generates one OpenSpec document from template
4. Wait for all tasks to complete (with timeout)
5. Sort results by stage number for deterministic logging

**Outputs**:
- 5 OpenSpec documents created in change directory
- Parallel execution time logged (should be faster than serial)

**Business Rules**:
- Max 3 workers to avoid resource contention
- 5-minute timeout per task
- Deterministic output ordering for reproducibility
- Can be disabled with `--no-parallel` flag

**Error Handling**:
- Task timeout: Log error, continue with other tasks
- Task exception: Capture exception, include in results, continue

### FR-4: Quality Gates Execution (Stage 8)

**Description**: Run automated quality checks and emit PASS/FAIL decision

**Inputs**:
- Codebase root directory
- Change directory for output
- Strict mode flag (for heavy lane)

**Processing**:
1. Execute ruff (linting) and capture results
2. Execute mypy (type checking) and capture results
3. Execute pytest with coverage and capture results
4. Execute bandit (security) and capture results
5. Evaluate all results against thresholds
6. Determine overall PASS/FAIL
7. Write quality_metrics.json
8. Print color-coded console summary

**Outputs**:
- `quality_metrics.json` file with comprehensive metrics
- Console output with color-coded summary
- Links to detailed reports (htmlcov/, bandit_report.json)

**Business Rules**:
- Standard thresholds: ruff 0, mypy 0, pytest ≥80% pass ≥70% coverage, bandit 0 high
- Strict thresholds (heavy lane): pytest 100% pass, 85% coverage
- Overall PASS requires all individual gates to pass
- FAIL stops workflow with clear remediation steps

### FR-5: Status Tracking System

**Description**: Write workflow state to status.json at each stage for observability and resumption

**Inputs**:
- Stage number and name
- Start/end timestamps
- Result (success/failure)
- Optional metrics (quality gates, timing)

**Processing**:
1. Load existing status.json if present
2. Update with new stage information
3. Write atomically to prevent corruption
4. Include timestamp, result, metrics

**Outputs**:
- `<change-dir>/status.json` file updated
- Contains complete workflow execution history

**Business Rules**:
- Written at stage start and end
- Atomic writes prevent partial updates
- Enables resumption from last completed stage
- Includes agent_enabled flag if applicable

### FR-6: Conventional Commits Validation (Stage 10)

**Description**: Validate commit messages adhere to Conventional Commits format

**Inputs**:
- Commit message (from user input or --message flag)
- `--no-verify` flag (optional, bypasses validation)

**Processing**:
1. Check format: `type(scope): subject`
2. Validate type is one of: feat, fix, docs, style, refactor, test, chore
3. Validate subject length ≤72 characters
4. If invalid, launch interactive fixer
5. If --no-verify, warn but allow

**Outputs**:
- Valid commit message (potentially rewritten)
- Warning if --no-verify used

**Business Rules**:
- Valid types: feat, fix, docs, style, refactor, test, chore
- Scope is optional
- Subject must be present and ≤72 chars
- Interactive fixer guides user through corrections

**Error Handling**:
- Invalid format: Launch interactive fixer
- User cancels fixer: Abort commit
- --no-verify: Warn but allow commit

### FR-7: Pre-Step Validation Hooks

**Description**: Execute environment validation before dependent stages

**Inputs**:
- Stage number
- Change directory
- Environment variables

**Processing**:
1. Check if hook registered for stage
2. If registered, execute hook function
3. Hook performs environment checks
4. If check fails, raise ValidationError with remediation

**Outputs**:
- Validation passes silently
- Validation fails with error message and remediation steps

**Business Rules**:
- Stage 0: Python 3.11+, required tools (pytest, ruff, mypy, bandit, gh)
- Stage 1: pyproject.toml, package.json exist and parseable
- Stage 10: Clean git state, feature branch checked out
- Stage 12: gh CLI available (warn if missing, provide fallback)

**Error Handling**:
- Failed validation: Display error, remediation, stop workflow
- gh CLI missing: Warn but continue with manual PR instructions

---

## 6. Technical Specifications

### TS-1: Programming Languages & Frameworks

**Primary Language**: Python 3.11+
**Secondary Language**: PowerShell 7.0+ (for Windows compatibility)

**Key Libraries**:
- `concurrent.futures`: ThreadPoolExecutor for parallelization
- `subprocess`: Execute external tools (pytest, ruff, mypy, bandit)
- `json`: Read/write status.json, quality_metrics.json
- `pathlib`: Cross-platform file path handling
- `argparse`: CLI argument parsing
- `datetime`: Timestamps for status tracking

### TS-2: File System Structure

```
openspec/
├── changes/
│   └── <change-id>/
│       ├── proposal.md
│       ├── spec.md
│       ├── tasks.md
│       ├── test_plan.md
│       ├── todo.md
│       ├── status.json              # NEW: Workflow state tracking
│       ├── quality_metrics.json     # NEW: Quality gate results
│       └── assistant_logs/          # NEW: Agent execution logs (optional)
│           ├── 2025-10-23_10-30-15.log
│           └── 2025-10-23_11-45-22.log
└── templates/
    ├── proposal.md
    ├── spec.md
    ├── tasks.md
    ├── test_plan.md
    └── todo.md

scripts/
├── workflow.py                      # MODIFIED: Add --lane flag
├── workflow.ps1                     # MODIFIED: Add -Lane parameter
└── quality_gates.py                 # NEW: Unified quality gate module

docs/
└── The_Workflow_Process.md          # MODIFIED: Document lanes
```

### TS-3: Command-Line Interface

**Python (workflow.py)**:
```bash
python scripts/workflow.py \
  --lane [docs|standard|heavy] \
  --change-id <id> \
  --title "<title>" \
  --owner "@username" \
  [--step <stage-num>] \
  [--dry-run] \
  [--no-parallel] \
  [--use-agent] \
  [--no-verify]
```

**PowerShell (workflow.ps1)**:
```powershell
.\scripts\workflow.ps1 `
  -Lane [docs|standard|heavy] `
  -ChangeId <id> `
  -Title "<title>" `
  -Owner "@username" `
  [-Step <stage-num>] `
  [-DryRun] `
  [-NoParallel] `
  [-UseAgent] `
  [-NoVerify]
```

### TS-4: Configuration Files

**Lane Configuration** (embedded in workflow.py):
```python
LANE_MAPPING = {
    "docs": {
        "stages": [0, 2, 3, 4, 9, 10, 11, 12],
        "description": "Documentation-only changes"
    },
    "standard": {
        "stages": list(range(13)),
        "description": "Normal development workflow"
    },
    "heavy": {
        "stages": list(range(13)),
        "description": "Critical changes with enhanced validation",
        "options": {"verbose_logging": True, "strict_thresholds": True}
    }
}
```

**Quality Gate Thresholds** (embedded in quality_gates.py):
```python
STANDARD_THRESHOLDS = {
    "ruff_errors": 0,
    "mypy_errors": 0,
    "pytest_pass_rate": 0.80,
    "pytest_coverage": 0.70,
    "bandit_high_severity": 0
}

STRICT_THRESHOLDS = {
    "ruff_errors": 0,
    "mypy_errors": 0,
    "pytest_pass_rate": 1.0,
    "pytest_coverage": 0.85,
    "bandit_high_severity": 0
}
```

### TS-5: Parallelization Configuration

**Default Settings**:
- Max workers: 3
- Timeout per task: 5 minutes (300 seconds)
- Parallelized stages: 2, 3, 4, 5, 6 (documentation generation)

**Thread Safety**:
- Each stage writes to separate file (no shared state)
- status.json uses file locking for atomic writes
- Deterministic output ordering via sorted results

### TS-6: Error Codes

| Exit Code | Meaning | When Used |
|-----------|---------|-----------|
| 0 | Success | Workflow completed successfully |
| 1 | Validation Error | Pre-step hook failed, environment invalid |
| 2 | Quality Gate Failure | Quality gates returned FAIL |
| 3 | Stage Execution Error | Stage failed during execution |
| 4 | User Cancellation | User cancelled interactive prompt |
| 5 | Configuration Error | Invalid lane, missing config |

---

## 7. Data Models and Schemas

### status.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "change_id": {"type": "string"},
    "lane": {"type": "string", "enum": ["docs", "standard", "heavy"]},
    "started_at": {"type": "string", "format": "date-time"},
    "completed_at": {"type": ["string", "null"], "format": "date-time"},
    "overall_status": {"type": "string", "enum": ["in-progress", "completed", "failed"]},
    "agent_enabled": {"type": "boolean"},
    "stages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "stage_number": {"type": "integer", "minimum": 0, "maximum": 12},
          "stage_name": {"type": "string"},
          "status": {"type": "string", "enum": ["not-started", "in-progress", "completed", "failed", "skipped"]},
          "started_at": {"type": ["string", "null"], "format": "date-time"},
          "completed_at": {"type": ["string", "null"], "format": "date-time"},
          "duration_seconds": {"type": ["number", "null"]},
          "error": {"type": ["string", "null"]},
          "skip_reason": {"type": ["string", "null"]}
        },
        "required": ["stage_number", "stage_name", "status"]
      }
    }
  },
  "required": ["change_id", "lane", "started_at", "overall_status", "stages"]
}
```

**Example**:
```json
{
  "change_id": "workflow-improvements",
  "lane": "docs",
  "started_at": "2025-10-23T10:30:00Z",
  "completed_at": "2025-10-23T10:34:15Z",
  "overall_status": "completed",
  "agent_enabled": false,
  "stages": [
    {
      "stage_number": 0,
      "stage_name": "Setup & Initialization",
      "status": "completed",
      "started_at": "2025-10-23T10:30:00Z",
      "completed_at": "2025-10-23T10:30:30Z",
      "duration_seconds": 30
    },
    {
      "stage_number": 1,
      "stage_name": "Increment Version",
      "status": "skipped",
      "skip_reason": "Docs lane skips version increment"
    }
  ]
}
```

### quality_metrics.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "overall_result": {"type": "string", "enum": ["PASS", "FAIL"]},
    "timestamp": {"type": "string", "format": "date-time"},
    "strict_mode": {"type": "boolean"},
    "thresholds": {
      "type": "object",
      "properties": {
        "ruff_errors": {"type": "integer"},
        "mypy_errors": {"type": "integer"},
        "pytest_pass_rate": {"type": "number"},
        "pytest_coverage": {"type": "number"},
        "bandit_high_severity": {"type": "integer"}
      }
    },
    "results": {
      "type": "object",
      "properties": {
        "ruff": {
          "type": "object",
          "properties": {
            "errors": {"type": "integer"},
            "warnings": {"type": "integer"},
            "passed": {"type": "boolean"}
          }
        },
        "mypy": {
          "type": "object",
          "properties": {
            "errors": {"type": "integer"},
            "notes": {"type": "integer"},
            "passed": {"type": "boolean"}
          }
        },
        "pytest": {
          "type": "object",
          "properties": {
            "total_tests": {"type": "integer"},
            "passed": {"type": "integer"},
            "failed": {"type": "integer"},
            "pass_rate": {"type": "number"},
            "coverage": {"type": "number"},
            "passed": {"type": "boolean"}
          }
        },
        "bandit": {
          "type": "object",
          "properties": {
            "high_severity": {"type": "integer"},
            "medium_severity": {"type": "integer"},
            "low_severity": {"type": "integer"},
            "passed": {"type": "boolean"}
          }
        }
      }
    }
  },
  "required": ["overall_result", "timestamp", "thresholds", "results"]
}
```

---

## 8. API Specifications

### CLI API

**Function**: `execute_workflow()`

**Signature**:
```python
def execute_workflow(
    lane: str = "standard",
    change_id: str,
    title: str,
    owner: str,
    step: Optional[int] = None,
    dry_run: bool = False,
    no_parallel: bool = False,
    use_agent: bool = False,
    no_verify: bool = False
) -> int:
    """
    Execute OpenSpec workflow with lane selection.
    
    Args:
        lane: Workflow lane (docs|standard|heavy)
        change_id: Unique change identifier
        title: Change title
        owner: Change owner (@username)
        step: Optional specific stage to execute
        dry_run: Preview without executing
        no_parallel: Disable parallelization
        use_agent: Enable AI-assisted execution
        no_verify: Skip commit validation
    
    Returns:
        Exit code (0=success, >0=error)
    
    Raises:
        ValueError: Invalid lane or configuration
        ValidationError: Pre-step validation failed
    """
```

**Function**: `run_quality_gates()`

**Signature**:
```python
def run_quality_gates(
    codebase_root: Path,
    change_dir: Path,
    strict: bool = False
) -> dict:
    """
    Execute quality gates and return metrics.
    
    Args:
        codebase_root: Root directory of codebase
        change_dir: Change directory for output files
        strict: Use strict thresholds (heavy lane)
    
    Returns:
        dict: Quality metrics with overall_result (PASS/FAIL)
    
    Side Effects:
        - Writes quality_metrics.json
        - Prints console summary
        - Generates coverage reports (htmlcov/)
        - Generates security report (bandit_report.json)
    """
```

---

## 9. Dependencies

### External Dependencies

| Dependency | Version | Purpose | Required |
|------------|---------|---------|----------|
| Python | 3.11+ | Runtime environment | ✅ Yes |
| pytest | 7.4+ | Testing framework | ✅ Yes |
| pytest-cov | 4.1+ | Coverage reporting | ✅ Yes |
| ruff | 0.1+ | Linting | ✅ Yes |
| mypy | 1.5+ | Type checking | ✅ Yes |
| bandit | 1.7+ | Security scanning | ✅ Yes |
| gh CLI | 2.0+ | PR creation | ⚠️ Optional |
| git | 2.30+ | Version control | ✅ Yes |

### Internal Dependencies

| Module | Depends On | Purpose |
|--------|------------|---------|
| workflow.py | quality_gates.py | Quality gate execution |
| workflow.py | status.json | State tracking |
| quality_gates.py | pytest, ruff, mypy, bandit | Tool execution |
| Stage 2-6 | templates/*.md | Document generation |

---

## 10. Migration and Compatibility

### Backward Compatibility

**Guaranteed Compatibility**:
- Default lane is `standard` → Executes all 13 stages (current behavior)
- No changes to existing workflow.py arguments
- Existing changes in `openspec/changes/*` unaffected

**Non-Breaking Changes**:
- New `--lane` flag is optional
- New `quality_metrics.json` file doesn't impact existing processes
- `status.json` is additive (doesn't replace existing tracking)

### Migration Path

**No Migration Required**:
- Users can continue using workflow without `--lane` flag
- Existing documentation remains valid
- No breaking changes to file formats or structures

**Adoption Path**:
1. **Week 1**: Announce in CHANGELOG, README
2. **Week 2**: Add examples to The_Workflow_Process.md
3. **Week 3-4**: Encourage docs lane usage for docs-only changes
4. **Month 2+**: Monitor adoption via status.json logs

---

## 11. Security and Compliance

### Security Considerations

**Input Validation**:
- Lane parameter validated against allowed values
- Change ID sanitized (alphanumeric + hyphens only)
- File paths validated (no directory traversal)

**File System Security**:
- status.json written with atomic operations (prevent corruption)
- quality_metrics.json written with restricted permissions
- Agent logs stored in dedicated directory with clear naming

**Tool Execution Security**:
- External tools (pytest, ruff, mypy, bandit) executed with explicit paths
- No user input passed directly to shell commands
- Subprocess execution with explicit argument lists (no shell=True)

**Agent Integration Security** (if --use-agent enabled):
- All agent actions logged with timestamps
- Agent cannot execute arbitrary commands
- Fallback to manual mode if agent unavailable
- User retains control over final decisions

### Compliance

**Open Source Compliance**:
- MIT License maintained
- No new proprietary dependencies
- All code contributions follow project guidelines

**Data Privacy**:
- No personal data collected or transmitted
- status.json contains only workflow metadata
- quality_metrics.json contains only code metrics

---

## 12. Performance Requirements

### Response Time Requirements

| Operation | Target | Maximum | Notes |
|-----------|--------|---------|-------|
| **Docs lane (full workflow)** | <5 min | <8 min | 7 stages, parallel docs generation |
| **Standard lane (full workflow)** | <15 min | <20 min | 13 stages, includes testing |
| **Heavy lane (full workflow)** | <20 min | <25 min | 13 stages, strict validation, verbose logging |
| **Single stage execution** | <2 min | <5 min | Varies by stage complexity |
| **Quality gates (Stage 8)** | <3 min | <5 min | Includes test execution |
| **Parallel docs generation** | <2 min | <3 min | Stages 2-6 concurrent |

### Resource Requirements

**CPU**:
- Minimum: 2 cores
- Recommended: 4+ cores (for parallelization)
- Heavy lane: 4+ cores

**Memory**:
- Minimum: 2GB available RAM
- Recommended: 4GB+ available RAM
- Heavy lane: 4GB+ available RAM

**Disk**:
- Minimum: 100MB free space per change
- Recommended: 500MB+ free space
- I/O: SSD recommended for faster file operations

### Scalability

**Horizontal Scalability**:
- Each change is independent (no shared state)
- Multiple workflow instances can run concurrently
- CI/CD pipelines can run workflows in parallel

**Vertical Scalability**:
- Parallelization scales with CPU cores
- Memory usage scales with test suite size

---

## 13. Testing and Quality Assurance

See [test_plan.md](./test_plan.md) for comprehensive testing strategy.

**Testing Levels**:
- **Unit Tests**: 85%+ coverage for new modules (quality_gates.py, lane selection logic)
- **Integration Tests**: All 3 lanes tested end-to-end
- **Manual Tests**: Real changes tested in each lane
- **Regression Tests**: Standard lane behavior unchanged

**Quality Gates** (self-applied):
- ruff: 0 errors
- mypy: 0 errors
- pytest: 80%+ pass rate, 70%+ coverage
- bandit: 0 high-severity issues

---

## 14. References

- **Proposal**: [proposal.md](./proposal.md)
- **Tasks**: [tasks.md](./tasks.md)
- **Test Plan**: [test_plan.md](./test_plan.md)
- **TODO**: [todo.md](./todo.md)
- **Workflow Documentation**: `docs/The_Workflow_Process.md`
- **OpenSpec Overview**: `openspec/PROJECT_WORKFLOW.md`
- **Guidance Notes**: `workflow_improvements.txt`

---

## 15. Glossary

- **Lane**: A workflow execution path (docs, standard, heavy)
- **Stage**: One of the 13 discrete steps in the OpenSpec workflow (0-12)
- **Quality Gates**: Automated checks (ruff, mypy, pytest, bandit) enforcing quality standards
- **Pre-Step Hook**: Validation logic executed before a stage to ensure prerequisites met
- **Status Tracking**: Writing status.json at each stage for observability and resumption
- **Parallelization**: Executing multiple stages concurrently to reduce workflow time
- **Conventional Commits**: Standardized commit message format (`type(scope): subject`)
- **Agent-Assisted**: Optional AI integration for automated workflow tasks with audit trail
- **Deterministic Output**: Consistent, reproducible results regardless of execution order
- **Atomic Write**: File write operation that completes fully or not at all (no partial writes)
- **Dry-Run**: Execute workflow without making actual changes (validation only)
- **Heavy Lane**: Workflow path with enhanced validation, verbose logging, stricter thresholds
- **Standard Lane**: Default workflow path executing all 13 stages (current behavior)
- **Docs Lane**: Fast workflow path for documentation-only changes (skips testing/implementation)

---

**END OF SPECIFICATION**

## Technical Design

### Workflow Lanes

- Add `--lane` (default `standard`) to `workflow.py` and `workflow.ps1`.
- Define a mapping:
    - docs: run [0, 2, 3, 4, 9, 10, 11, 12]; skip 1, 5–8 unless code changes detected
    - standard: run all steps (0–12)
    - heavy: run all steps with additional verbose logging and stricter gates
- Auto-detect code changes; if present in docs lane, prompt to switch or
  continue with a warning.

### Parallelization of Stages 2–6

- Use ThreadPoolExecutor (Python) with `max_workers=3` by default.
- Serialize writes deterministically to avoid race conditions.
- Provide a config to disable parallelization if necessary.

### Pre-Step Validation Hooks

- Add hook registry to run checks before selected steps:
    - Stage 10: Ensure clean git state, feature branch exists.
    - Stage 12: Ensure `gh` CLI is installed and authenticated, else fallback to
      instructions.
- Hook failures print actionable remediation and block the step.

### Assistant Integration (Optional)

- Add `--use-agent` (and equivalent in PowerShell) to enable assistant
    helpers:
        - Documentation scaffolding and linking for OpenSpec artifacts
        - Codebase search to identify affected symbols/files
        - Quality automation wrapper (calls existing tools, aggregates output)
        - Commit message suggestions and PR body drafting
- All assistant activity writes audit logs under the change directory
    (e.g., `assistant_logs/`) and updates `status.json`.
- If the assistant is unavailable, steps proceed manually with guidance.

### Quality Gates (Stage 8)

- Create `scripts/quality_gates.py` to run:
    - ruff (lint)
    - mypy (type check)
    - pytest with coverage
    - bandit (security)
- Aggregate results and write `quality_metrics.json` with PASS/FAIL.
- Summarize to console with clear thresholds.

### Status Tracking

- Write `openspec/changes/<id>/status.json` at step start and end with:
    - current_step, start_time, end_time
    - result: success/failure
    - metrics: quality summary if available

### Conventional Commits Enforcement (Stage 10)

- Validate message against spec (type: subject; optional body/footer).
- Provide an interactive fixer to rewrite messages.
- Allow `--no-verify` escape hatch with a warning.

## Dependencies

- Python 3.11
- Existing project tools: pytest, ruff, mypy, bandit, gh CLI (optional)

## Migration and Compatibility

- Default lane is `standard`, so no change for existing flows.
- Docs lane is opt-in; warnings prevent accidental skipping of needed steps.
- All changes are additive and backward compatible.

## References

- Proposal: [proposal.md](./proposal.md)
- Tasks: [tasks.md](./tasks.md)
- Test Plan: [test_plan.md](./test_plan.md)
- Guidance Notes: [workflow_improvements.txt](./workflow_improvements.txt)

## Checklists and Best Practices (from guidance notes)

To reinforce quality and consistency, adopt the following checklists:

- Basic tests: file existence, comments where appropriate, key
    functions present, code indentation and bracket pairing validated.
- Security: input validation for APIs and scripts; avoid unsafe
    patterns found by bandit.
- Bulk operations: verify folder/file operations and content updates
    via idempotent functions.
- Operational steps: add/commit/push/PR sequence documented; commit
    messages follow Conventional Commits and lanes are recorded.
