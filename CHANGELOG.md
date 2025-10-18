# 📝 CHANGELOG
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
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-assistant-setup** (update-doc-obsidian-plugins-obsidian-ai-assistant-setup, None)
  _File: proposal.md_
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-assistant-setup-complete** (update-doc-obsidian-plugins-obsidian-ai-assistant-setup-complete, None)
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
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-assistant-setup** (update-doc-obsidian-plugins-obsidian-ai-assistant-setup, None)
  _File: proposal.md_
- **Change Proposal: update-doc-obsidian-plugins-obsidian-ai-assistant-setup-complete** (update-doc-obsidian-plugins-obsidian-ai-assistant-setup-complete, None)
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
