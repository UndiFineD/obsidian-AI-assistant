## v0.1.33 (2025-10-21)

- **OpenSpec Change**: modular-api-structure
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

## v0.1.32 (2025-10-21)

- **OpenSpec Change**: reorganize-models-directory
- **Git Status**: Changes staged, committed, and pushed
- _Released as part of OpenSpec workflow automation._

# 📝 CHANGELOG
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

