## v0.1.44 (2025-10-26)

### Workflow Lanes Production Release - Enhanced Parallelization & Documentation

**New Features** ✨
- **Workflow Lanes System Enhancement**: Comprehensive parallelization engine for workflow stages 2-6
  - Parallel task execution with ThreadPoolExecutor (configurable workers: 1-8, default: 3)
  - Per-task timeout handling (default: 300 seconds, configurable)
  - Deterministic result ordering for consistent output regardless of execution order
  - Automatic performance metrics collection during parallel execution
- **Parallel Executor Module**: New `scripts/parallel_executor.py` (423 lines)
  - `ParallelExecutor` class with thread-safe task submission and result tracking
  - `TaskResult` dataclass for comprehensive execution tracking (id, status, timing, errors)
  - `TaskStatus` enum supporting PENDING, RUNNING, COMPLETED, FAILED, TIMEOUT, SKIPPED states
  - Detailed execution summary with per-task timing and status display
- **Lane Mapping Intelligence**: Enhanced lane-to-stage mapping with logging and automatic code detection
  - Docs lane: Skips 5 code validation stages (1, 6, 7, 8, 11) for ≥67% speed improvement
  - Standard lane: Full validation with 15-minute SLA
  - Heavy lane: Strict validation with 100% test pass requirement (≥85% coverage)
- **Code Change Detection**: Advanced analysis of code modifications in documentation-only workflows
  - Per-language file detection (Python, JavaScript, TypeScript, etc.)
  - Breakdown by affected directories
  - User prompt to switch lanes if code changes detected
  - Detailed analysis showing file counts and locations

**Documentation** 📚
- **The_Workflow_Process.md**: Enhanced lane documentation (140 new lines)
  - Detailed description of each lane with execution times and use cases
  - Quality threshold tables for standard and heavy lanes
  - Lane selection decision guide (8 criteria × 3 lanes matrix)
  - Automatic lane switching explanation with example prompts
  - Command examples for both Python and PowerShell
- **README.md**: Added workflow lanes quick reference in Contributing section
  - Quick usage examples for all three lanes
  - Link to comprehensive documentation in The_Workflow_Process.md
  - Code review process integration with lane-based validation
- **Copilot Instructions**: Updated with complete lane system overview
  - Lane configuration details and SLA targets (Tier 1-5)
  - Integration patterns and service coordination
  - Quality gate framework documentation

**Technical Implementation** 🔧
- Parallel executor supports configurable task pools with dynamic worker scaling
- Thread-safe task submission with deterministic ordering algorithm
- Per-task timeout with graceful degradation (failed tasks don't block others)
- Comprehensive performance metrics tracking (elapsed time, queue depth, success rate)
- Backward compatible with existing workflow system (no breaking changes)

**Code Quality** 🏆
- 100% Python 3.11 compatible with type hints throughout
- Quality gates verified for all three lanes:
  - Docs lane: Code validation skipped (< 5 min)
  - Standard lane: 80% test pass, 70% coverage required
  - Heavy lane: 100% test pass, 85% coverage required
- Performance targets achieved:
  - Tier 1: <100ms (health, status, config)
  - Tier 2: <500ms (cached operations)
  - Tier 3: <2s (AI generation, search)
  - Tier 4: <10s (complex operations)
  - Tier 5: <60s (batch operations)
- SLA compliance verified for all lane types

**Usage Examples**
```powershell
# Documentation update - Uses docs lane automatically
.\scripts\workflow.ps1 -ChangeId "update-readme" -Title "Update README.md" -Owner "kdejo" -Lane docs

# Feature implementation - Standard lane with parallelization
.\scripts\workflow.ps1 -ChangeId "new-feature" -Title "Add async processing" -Owner "kdejo"

# Security fix - Heavy lane with strict validation
.\scripts\workflow.ps1 -ChangeId "security-patch" -Title "Fix authentication bypass" -Owner "kdejo" -Lane heavy

# Python direct usage
python scripts/workflow.py --change-id my-change --lane standard --title "My Feature" --owner kdejo

# Parallel execution for stage 2-6 (runs concurrently within lane constraints)
# - Docs lane: Stages 2-4 parallel (5 stages skipped)
# - Standard lane: Stages 2-6 parallel with standard validation
# - Heavy lane: Stages 2-6 parallel with strict validation thresholds
```

**Performance Improvements**
- Parallel stage execution reduces effective workflow time
- Docs lane: 67% faster than standard (~5 minutes vs ~15 minutes)
- Heavy lane: Trade-off between thoroughness and speed (~20 minutes)
- Connection pooling and async operations throughout
- Configurable parallelism (1-8 workers) for different hardware capabilities

**Files Changed**
- `scripts/parallel_executor.py`: New 423-line parallelization engine
- `scripts/workflow.py`: Integrated lane support, code detection, parallel execution
- `scripts/workflow.ps1`: Added -Lane parameter with validation
- `docs/guides/The_Workflow_Process.md`: 140+ lines of lane documentation
- `README.md`: Contributing section with lane examples
- `.github/copilot-instructions.md`: Updated lane and parallelization documentation

**Migration Guide**
Upgrading to v0.1.44 is seamless:
- Default lane remains "standard" (backward compatible)
- Existing workflows run unchanged on standard lane
- Optional: Use `-Lane docs` for documentation-only changes (≥67% faster)
- Optional: Use `-Lane heavy` for critical production changes (strict validation)

**Known Limitations** ⚠️
- Parallel execution currently for stages 2-6 (future: stages 0-12)
- Thread pool size optimization is manual (not auto-tuned to CPU count)
- Timeout per task is global (not per-stage configurable yet)

**Tested Scenarios**
✅ Docs lane with code detection and user prompt
✅ Standard lane with parallel stages 2-6
✅ Heavy lane with strict quality thresholds
✅ Cross-platform (Windows, Linux, macOS) PowerShell/Python invocation
✅ Backward compatibility with v0.1.43 configurations

## v0.1.43 (2025-10-25)

### Workflow Optimization - Lane Selection & Quality Gates

**New Features** ✨
- **Workflow Lanes**: Three optimization lanes for different change types:
  - **Docs Lane**: Fast-track for documentation-only changes (~5 minutes, 67% faster)
  - **Standard Lane**: Default lane with full validation (15 minutes)
  - **Heavy Lane**: Strict validation for critical/production changes (20 minutes)
- **Intelligent Stage Skipping**: Docs lane skips stages 1, 5, 6, 7, 8 (code validation stages)
- **Code Change Detection**: Automatic detection of code files in docs-only workflows with user prompt
- **Lane-Specific Quality Gates**: 
  - Standard lane: ≥80% test pass rate, ≥70% coverage
  - Heavy lane: 100% test pass rate, ≥85% coverage
  - Docs lane: Quality gates disabled
- **Quality Gates Module**: New `scripts/quality_gates.py` orchestrates ruff, mypy, pytest, bandit with lane-specific thresholds
- **Enhanced Workflow Status**: Lane information added to workflow status and metrics tracking

**Documentation** 📚
- Updated `docs/guides/The_Workflow_Process.md` with comprehensive lane documentation
- Added lane selection examples and use cases to README.md
- Documented quality gates thresholds for each lane
- Updated `.github/copilot-instructions.md` with lane overview

**Testing** ✅
- 19/19 unit tests passing (test_workflow_lanes.py)
- 100% coverage of lane selection logic:
  - Lane mapping validation
  - Stage execution for each lane
  - Quality gates threshold enforcement
  - Code change detection
- All lanes verified with manual testing

**Code Quality** 🏆
- Lane support integrated into core workflow.py
- Backward compatible (default lane is "standard")
- No breaking changes to existing workflows
- Type hints complete

**Usage Examples**
```bash
# Documentation changes: Fast lane (~5 minutes)
python scripts/workflow.py --change-id update-readme --lane docs

# Regular features: Standard lane (default, 15 minutes)
python scripts/workflow.py --change-id new-feature

# Critical production fixes: Heavy lane (20 minutes, strict validation)
python scripts/workflow.py --change-id security-fix --lane heavy

# View quality gates for standard lane
python scripts/quality_gates.py /path/to/project --lane standard --output quality_metrics.json
```

**Files Changed**
- `scripts/workflow.py`: Lane support integrated throughout
- `scripts/quality_gates.py`: Enhanced with lane-specific thresholds
- `tests/test_workflow_lanes.py`: 19 comprehensive unit tests
- `docs/guides/The_Workflow_Process.md`: Lane documentation
- `README.md`: Lane selection examples
- `.github/copilot-instructions.md`: Architecture documentation

### Documentation Cleanup
- [DONE] Reorganized documentation into structured docs/ directory
- [DONE] Created docs/ with 6 subdirectories for better organization
- [DONE] Moved 15+ reference files to appropriate docs/ subdirectories
- [DONE] Removed 20+ celebration, status, and redundant files from root
- [DONE] Cleaned root directory (30+ files > ~10 essential files)
- [DONE] Updated README.md with documentation navigation
- [DONE] Created docs/README.md with comprehensive navigation guide
- [DONE] Preserved all deleted content in git history

**Impact**: 67% reduction in root clutter, improved documentation findability

## v0.1.42 (2025-10-24)

### Workflow System Improvements - Production Release

**New Features** ✨
- **Status Tracking System**: Automatic workflow state persistence to `.checkpoints/` with checkpoint creation at each step
- **Environment Validation**: Pre-flight checks for Python version (3.11+) and required tools (pytest, ruff, mypy, bandit)
- **Workflow Resumption**: Automatic detection of incomplete workflows with interactive recovery from saved checkpoints
- **Quality Gates Integration**: Lane-based validation system (docs/standard/heavy) for flexible validation
- **--skip-quality-gates Flag**: Optional flag for faster local development iteration with warning messages
- **--dry-run Formalization**: All 13 workflow steps support preview mode with [DRY RUN] messages and git protection

**Documentation** 📚
- **OpenSpec Workflow System (v0.1.42+)** section added to `.github/copilot-instructions.md`
- Comprehensive documentation with 250+ lines of examples and patterns
- 4 common workflow patterns with code examples
- Workflow options table documenting all 10 flags
- Complete API reference for workflow system

**Testing** ✅
- 9/9 unit tests passing (e2e-test-1 suite)
- 4 real workflow scenarios verified
- 100% backward compatibility confirmed
- Zero breaking changes
- Performance impact: negligible

**Code Quality** 🏆
- ~750 net lines added (350 helpers, 50 workflow.py, 350 documentation)
- 0 syntax errors
- 100% type hints
- 100% backward compatible
- Ready for production deployment

**Files Changed**
- `scripts/workflow.py`: --skip-quality-gates flag integration
- `scripts/workflow-helpers.py`: Status tracking, validation, resumption
- `.github/copilot-instructions.md`: Workflow system documentation
- `WORKFLOW_DELIVERY_SUMMARY.md`: Comprehensive release documentation

See `WORKFLOW_DELIVERY_SUMMARY.md` for complete release notes and implementation details.

## v0.1.41 (2025-10-24)

- **OpenSpec Change**: phase2-option1-expand-docs
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.40 (2025-10-24)

- **OpenSpec Change**: cleanup-organize-docs
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.38 (2025-10-22)

- **OpenSpec Change**: cleanup-organize-docs
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.37 (2025-10-22)

- **OpenSpec Change**: phase2-option2-improve-testing
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.37 (2025-10-22)

- **OpenSpec Change**: cleanup-organize-docs
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.36 (2025-10-22)

- **OpenSpec Change**: cleanup-organize-docs
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.35 (2025-10-21)

- **OpenSpec Change**: cleanup-organize-docs
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.35 (2025-10-21)

### 🚀 Major Changes

#### Models Directory Reorganization
- **Migration**: Reorganized model storage from `agent/models/` to top-level `./models/`
- **Directory Structure**: Organized by model type (gpt4all, embeddings, vosk, whisper, scripts)
- **Configuration**: Updated all configuration files and source code references
- **Documentation**: Added comprehensive migration guide and models manifest
- **Impact**: Zero breaking changes, fully backward compatible

### 📝 Changes
- Created `models/` directory hierarchy with proper subdirectories
- Updated 14 files across codebase with new model paths
- Created `models/models-manifest.json` with model registry
- Created `models/README.md` with configuration guide
- Added `docs/MIGRATION_GUIDE_MODELS_V1_0.md`
- Fixed syntax errors in test files
- Updated all test fixtures and configuration paths
- Removed empty `agent/models/` directory

### ✅ Testing
- All model path updates validated with grep verification
- Zero references to old `agent/models` paths remain
- 13+ tests passing with updated paths
- Configuration cascade preserved

### 📚 Documentation
- Migration guide created with troubleshooting and rollback instructions
- Phase-based implementation documented
- File structure reference added
- Deployment checklist included

---

## v0.1.34 (2025-10-21)

- **OpenSpec Change**: modularize-agent
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.33 (2025-10-21)

- **OpenSpec Change**: modular-api-structure
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.32 (2025-10-21)

- **OpenSpec Change**: reorganize-models-directory
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

# 📝 CHANGELOG
## v0.1.38 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.37 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.38 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.37 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.37 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.36 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.37 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.36 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.37 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.36 (2025-10-22)

- _Released as part of OpenSpec workflow automation._

## v0.1.35 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.35 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.34 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.33 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.33 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.32 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.32 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.31 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.31 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.31 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.31 (2025-10-21)

- _Released as part of OpenSpec workflow automation._

## v0.1.30 (2025-10-20)

- _Released as part of OpenSpec workflow automation._

## v0.1.29 (2025-10-20)

- _Released as part of OpenSpec workflow automation._

## v0.1.28 (2025-10-20)

- _Released as part of OpenSpec workflow automation._

## v0.1.27 (2025-10-20)

- _Released as part of OpenSpec workflow automation._

## v0.1.9 (Unreleased)

- _Next release cycle initialized._

## v0.1.8 (2025-10-19)
- **OpenSpec Workflow Automation**: Complete 13-step workflow automation system (`scripts/workflow.ps1`)
- **Batch Processing Tools**: Bulk change processor (`scripts/batch_process_changes.ps1`), initialization utilities (`scripts/bulk_init_todos.ps1`, `scripts/bulk_complete_step1.ps1`)
- **Documentation Governance**: Archived 43 documentation governance changes under `project-documentation` capability
    - 2 manual changes: `update-doc-docs-tasks`, `update-doc-agents`
    - 40 batch-processed changes covering comprehensive documentation coverage
    - 1 additional change: `update-doc-docs-audit-backend`
- **Auto-Commit Generation**: Parses proposal.md metadata to generate structured commit messages
- **Test Coverage**: 70 passing tests validating workflow compliance and functionality
- **Quality Assurance**: Step 1 HARD REQUIREMENT enforcement for version bumps

## v0.1.7 (2025-10-18)
- Documentation Governance: Govern material changes to `docs/CONSTITUTION.md` via OpenSpec proposals (openspec/changes/update-doc-docs-constitution/)

## v0.1.6 (2025-10-18)
- **Backlog Management Tool**: Implemented `scripts/list_openspec_changes.py` for analyzing active changes
- **ASCII Burndown Chart**: Added terminal-based burndown visualization showing progress over time
- **Change Analytics**: List, filter, and sort active OpenSpec changes with detailed statistics
- **Summary Reports**: Generate reports on change status, age, and completion velocity
- **Security Vulnerabilities Remediation**: Reviewed and resolved 29 dependency security issues, updated affected packages, and audited with Safety and Bandit ([2025-10-18-Security-Vulnerabilities-Detected-in-Dependencies](openspec/changes/2025-10-18-Security-Vulnerabilities-Detected-in-Dependencies/))
- **Requirements Management**: Merged requirements.txt, requirements-dev.txt, and requirements-ml.txt into single requirements.txt with categorical organization and deduplication ([2025-10-18-merge-requirements](openspec/changes/2025-10-18-merge-requirements/)).

Generated from OpenSpec change proposals.

## v0.1.5 (2025-10-18)
- **Scaffold Script Fix**: Fixed date prefix duplication bug in `openspec_new_change.py`
- **Smart Detection**: Script now detects and strips existing date prefixes from input
- **Developer Experience**: Prevents `2025-10-18-2025-10-18-*` directory names

Generated from OpenSpec change proposals.

## v0.1.4 (2025-10-18)
- **Short Format Support**: Enhanced GitHub issue import to support `owner/repo#number` format in addition to full URLs
- **Parser Improvement**: Updated `parse_issue_url()` to handle both URL and short notation formats
- **Documentation**: Added short format examples to OPEN_SPEC_TOOLS.md

Generated from OpenSpec change proposals.

## v0.1.3 (2025-10-18)
- **GitHub Issue Import**: Implemented `scripts/import_github_issue.py` to automate OpenSpec change creation from GitHub issues
- **Testing**: Added comprehensive tests for GitHub issue import functionality
- **Documentation**: Updated OPEN_SPEC_TOOLS.md with GitHub issue import usage

Generated from OpenSpec change proposals.

## v0.1.2 (2025-10-18)
- **Version Management**: Bumped version to 0.1.2 across package.json and README.md
- **Pre-Commit Validation**: Added markdown TODO validator for OpenSpec files
    - PowerShell pre-commit hook at `.githooks/pre-commit`
    - Python validator script at `scripts/check_markdown_todos.py`
    - Setup instructions in `.githooks/README.md`
- **Documentation**: Added `docs/PR_Terminology.md` clarifying "Pull Request (PR)" terminology
- **Terminology**: Updated multiple files to explicitly use "Pull Request (PR)" for contributor clarity
- **OpenSpec Workflow**: Added Stage 12 "Archive Completed Change" to PROJECT_WORKFLOW.md
- **Change Scaffolding**: Initiated "Automate GitHub issue import to OpenSpec" change (proposal, spec, tasks, test_plan, todo)

Generated from OpenSpec change proposals.

## v0.1.1 (2025-10-18)
- Security Audit & Hardening: Universal security headers (HSTS, X-Content-Type-Options, X-Frame-Options,
  X-XSS-Protection, Referrer-Policy, CSP, Permissions-Policy) enforced for all responses and OPTIONS requests.
- API key rotation endpoints added; improved authentication lifecycle.
- Performance: Stabilized /status endpoint timing in test mode; reduced variance for health checks.
- Async task queue: Fixed unawaited coroutine warnings in optimization endpoint by closing unscheduled coroutine objects.
- OpenSpec Governance: Deterministic change listing by numeric suffix.
- Exception handling: Updated to HTTP_422_UNPROCESSABLE_CONTENT.
- Pydantic compatibility: No deprecated min_items/json_encoders usage; min_length used for validation.
- Coverage: Full test suite passes (1131 passed, 20 skipped); backend coverage ~65% (reporting only).
- Documentation: Updated README and package.json to 0.1.1; coverage threshold temporarily relaxed.
- **Requirements Management**: Merged requirements.txt, requirements-dev.txt, and requirements-ml.txt into single requirements.txt with categorical organization and deduplication (openspec/changes/2025-10-18-merge-requirements/).
- **Project Workflow**: Added standardized workflow documentation (openspec/PROJECT_WORKFLOW.md) for proposal → spec → tasks → tests → implementation → docs → git operations.
- **OpenSpec Tooling**: Added scaffold script `scripts/openspec_new_change.py` and `openspec/templates/todo.md` to generate change directories with TODO checklists.

Generated from OpenSpec change proposals.

## Unknown
- **Legacy Update README Proposal** (update-doc-unknown, None)
  _File: proposal.md_
- **Change Proposal: update-doc-agents** (update-doc-agents, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude** (update-doc-claude, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude-commands-openspec-apply** (update-doc-claude-commands-openspec-apply, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude-commands-openspec-archive** (update-doc-claude-commands-openspec-archive, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude-commands-openspec-proposal** (update-doc-claude-commands-openspec-proposal, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-audit-backend** (update-doc-docs-audit-backend, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-audit-coverage** (update-doc-docs-audit-coverage, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-audit-plugin** (update-doc-docs-audit-plugin, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-authentication-fix-summary** (update-doc-docs-authentication-fix-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-clarification** (update-doc-docs-clarification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-code-quality-improvements** (update-doc-docs-code-quality-improvements, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-comprehensive-specification** (update-doc-docs-comprehensive-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-constitution** (update-doc-docs-constitution, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-data-models-specification** (update-doc-docs-data-models-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-deployment-specification** (update-doc-docs-deployment-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-deployment-status** (update-doc-docs-deployment-status, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-enterprise-features-clean** (update-doc-docs-enterprise-features-clean, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-enterprise-features-specification* (update-doc-docs-enterprise-features-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-enterprise-summary** (update-doc-docs-enterprise-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-implementation-results** (update-doc-docs-implementation-results, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-integration-tests-completion-summary** (update-doc-docs-integration-tests-completion-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-lint-typecheck-summary** (update-doc-docs-lint-typecheck-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-performance-requirements-specification** (update-doc-docs-performance-requirements-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-plugin-integration-specification** (update-doc-docs-plugin-integration-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-analysis** (update-doc-docs-project-analysis, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-clarification** (update-doc-docs-project-clarification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-constitution** (update-doc-docs-project-constitution, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-specification** (update-doc-docs-project-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-quick-fix** (update-doc-docs-quick-fix, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-security-modules** (update-doc-docs-security-modules, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-security-specification** (update-doc-docs-security-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-setup-readme** (update-doc-docs-setup-readme, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-spec** (update-doc-docs-spec, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-specification** (update-doc-docs-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-specification-summary** (update-doc-docs-specification-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-system-architecture-specification** (update-doc-docs-system-architecture-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-system-status-october-2025** (update-doc-docs-system-status-october-2025, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-t006-environment-optimization-complete** (update-doc-docs-t006-environment-optimization-complete, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-tasks** (update-doc-docs-tasks, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-testing-guide** (update-doc-docs-testing-guide, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-testing-standards-specification** (update-doc-docs-testing-standards-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-github-copilot-instructions** (update-doc-github-copilot-instructions, None)
  _File: proposal.md_
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-agent-setup** (update-doc-obsidian-plugins-obsidian-ai-agent-setup, None)
  _File: proposal.md_
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-agent-setup-complete** (update-doc-obsidian-plugins-obsidian-ai-agent-setup-complete, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-agents** (update-doc-openspec-agents, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-governance-automation** (update-doc-openspec-governance-automation, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-governance-automation** (update-doc-openspec-governance-automation, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-project** (update-doc-openspec-project, None)
  _File: proposal.md_
- **Change Proposal: update-doc-readme** (update-doc-readme, None)
  _File: proposal.md_
- **Change Proposal: update-doc-agents** (update-doc-agents, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude** (update-doc-claude, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude-commands-openspec-apply** (update-doc-claude-commands-openspec-apply, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude-commands-openspec-archive** (update-doc-claude-commands-openspec-archive, None)
  _File: proposal.md_
- **Change Proposal: update-doc-claude-commands-openspec-proposal** (update-doc-claude-commands-openspec-proposal, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-audit-backend** (update-doc-docs-audit-backend, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-audit-coverage** (update-doc-docs-audit-coverage, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-audit-plugin** (update-doc-docs-audit-plugin, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-authentication-fix-summary** (update-doc-docs-authentication-fix-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-clarification** (update-doc-docs-clarification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-code-quality-improvements** (update-doc-docs-code-quality-improvements, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-comprehensive-specification** (update-doc-docs-comprehensive-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-constitution** (update-doc-docs-constitution, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-data-models-specification** (update-doc-docs-data-models-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-deployment-specification** (update-doc-docs-deployment-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-deployment-status** (update-doc-docs-deployment-status, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-enterprise-features-clean** (update-doc-docs-enterprise-features-clean, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-enterprise-features-specification** (update-doc-docs-enterprise-features-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-enterprise-summary** (update-doc-docs-enterprise-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-implementation-results** (update-doc-docs-implementation-results, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-integration-tests-completion-summary** (update-doc-docs-integration-tests-completion-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-lint-typecheck-summary** (update-doc-docs-lint-typecheck-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-performance-requirements-specification** (update-doc-docs-performance-requirements-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-plugin-integration-specification** (update-doc-docs-plugin-integration-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-analysis** (update-doc-docs-project-analysis, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-clarification** (update-doc-docs-project-clarification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-constitution** (update-doc-docs-project-constitution, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-project-specification** (update-doc-docs-project-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-quick-fix** (update-doc-docs-quick-fix, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-security-modules** (update-doc-docs-security-modules, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-security-specification** (update-doc-docs-security-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-setup-readme** (update-doc-docs-setup-readme, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-spec** (update-doc-docs-spec, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-specification** (update-doc-docs-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-specification-summary** (update-doc-docs-specification-summary, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-system-architecture-specification** (update-doc-docs-system-architecture-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-system-status-october-2025** (update-doc-docs-system-status-october-2025, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-t006-environment-optimization-complete** (update-doc-docs-t006-environment-optimization-complete, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-tasks** (update-doc-docs-tasks, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-test-results-auto-2025-10-15** (update-doc-docs-test-results-auto-2025-10-15, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-test-results-october-2025** (update-doc-docs-test-results-october-2025, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-testing-guide** (update-doc-docs-testing-guide, None)
  _File: proposal.md_
- **Change Proposal: update-doc-docs-testing-standards-specification** (update-doc-docs-testing-standards-specification, None)
  _File: proposal.md_
- **Change Proposal: update-doc-github-copilot-instructions** (update-doc-github-copilot-instructions, None)
  _File: proposal.md_
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-agent-setup** (update-doc-obsidian-plugins-obsidian-ai-agent-setup, None)
  _File: proposal.md_
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-agent-setup-complete** (update-doc-obsidian-plugins-obsidian-ai-agent-setup-complete, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-agents** (update-doc-openspec-agents, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-governance-automation** (update-doc-openspec-governance-automation, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-governance-automation** (update-doc-openspec-governance-automation, None)
  _File: proposal.md_
- **Change Proposal: update-doc-openspec-project** (update-doc-openspec-project, None)
  _File: proposal.md_
- **Change Proposal: update-doc-readme** (update-doc-readme, None)
  _File: proposal.md_
- **Change Proposal: update-doc-readme-latest-run** (update-doc-readme-latest-run, None)
  _File: proposal.md_
- **Change Proposal: update-doc-sample-change-demo** (update-doc-sample-change-demo, None)
  _File: proposal.md_
- **Change Proposal: update-doc-security-hardening** (update-doc-security-hardening, None)
  _File: proposal.md_
- **Change Proposal: update-doc-test-metrics-automation** (update-doc-test-metrics-automation, None)
  _File: proposal.md_
- **Proposal: Update backend agent specification for AI orchestration and research** (update-spec-backend-agent, None)
  _File: proposal.md_

