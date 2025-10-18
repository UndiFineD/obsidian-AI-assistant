# project-documentation Specification
## Governed Files and Change History (Summary)
| File/Artifact                              | Governance Requirement | Last Change Delta Example |
|--------------------------------------------|------------------------|--------------------------|
| docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md  | Yes                    | update-doc-docs-system-architecture-specification |
| docs/SECURITY_SPECIFICATION.md             | Yes                    | update-doc-docs-security-specification           |
| README.md                                  | Yes                    | update-doc-readme                                 |
| AGENTS.md                                  | Yes                    | update-doc-agents                                 |
| .github/copilot-instructions.md            | Yes                    | update-doc-copilot-instructions                   |
| ... (see below for full list)              | Yes                    | ...                                              |

## Purpose
Provide authoritative, governed documentation for the Obsidian AI Assistant. This capability ensures all project knowledge (architecture, backend agent orchestration, offline/connected modes, API and enterprise features, testing, performance, security, deployment, and plugin integration) is accurate, consistent, and easy to navigate.

Scope and artifacts:
- Core docs under `docs/` (architecture, security, testing, performance, deployment, enterprise, specs)
- Top-level files: `README.md`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`
- OpenSpec governance content under `openspec/` (baseline specs and change deltas)

Governance model:
- All material documentation changes are proposed, reviewed, and tracked via OpenSpec change directories with `proposal.md`, `tasks.md`, and compliant delta specs (ADDED/MODIFIED/REMOVED)
- Strict validation enforces completeness, formatting, and cross-document consistency

Success criteria:
- Documentation enables contributor onboarding in under 1 hour
- Cross-document consistency for status and metrics (README, system status, test results)
- All OpenSpec validations pass in strict mode

## References

For end-to-end governance workflow, examples, and troubleshooting, see:

- OpenSpec overview: [openspec/README.md](../../README.md)
- Governance workflow (for humans/agents): [openspec/AGENTS.md](../../AGENTS.md)
- Delta patterns and examples: [openspec/docs/change-patterns.md](../../docs/change-patterns.md)
- Contributor onboarding: [openspec/docs/contributor-guide.md](../../docs/contributor-guide.md)
- Troubleshooting validation: [openspec/docs/troubleshooting.md](../../docs/troubleshooting.md)
- Automation scripts guide: [openspec/scripts/README.md](../../scripts/README.md)
## Requirements
### Requirement: Backend agent orchestration and extensibility

The backend SHALL act as a modular AI agent, exposing a REST API capable of:
**See also:** [System Architecture Specification](docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md) for architectural context and orchestration patterns.
- Answering questions using local compute AI models (offline/private)
- Indexing, searching, and analyzing Obsidian notes
- Using web hooks and internet access (if enabled) for external research
- Routing requests to other AI agents/models for multi-agent workflows
- Integrating enterprise features and extensible orchestration

#### Scenario: Local compute AI answering
- WHEN a user asks a question via the API
- THEN the backend SHALL answer using local models if available

#### Scenario: Web-enabled research
- WHEN internet access is enabled and a user requests external research
- THEN the backend SHALL use web hooks or external models to fetch and summarize content

#### Scenario: Multi-agent orchestration
- WHEN a request requires broader research or model access
- THEN the backend SHALL route or delegate to other agents/models as configured
- **Note:** See system architecture documentation for orchestration flows and extensibility patterns.

#### Scenario: Enterprise integration
- WHEN enterprise features are enabled
- THEN the backend SHALL support SSO, RBAC, compliance, and extensible service orchestration

#### Scenario: Offline mode enforcement
- WHEN the system is operating in offline/local mode
- THEN the backend SHALL restrict operations to local models and local data sources only, with no outbound network calls

#### Scenario: Connected mode behavior
- WHEN the system is operating in connected/internet-enabled mode and external research is permitted
- THEN the backend MAY perform outbound requests via approved web hooks or external models as configured

### Requirement: Documentation clarity
The OpenSpec documentation SHALL describe backend agent architecture, API capabilities, and extensibility for both offline and connected modes.

#### Scenario: Contributor onboarding
- WHEN a new contributor reviews AGENTS.md or project-documentation/spec.md
- THEN they SHALL understand backend agent roles, orchestration, and extensibility

#### Scenario: Architecture modes documented
- WHEN agent capabilities or modes (offline/connected) are modified
- THEN the documentation SHALL be updated to reflect mode-specific behavior, constraints, and examples

### Requirement: Governance for README.md
The project SHALL govern material changes to key documentation files via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to README.md requires proposal
- **WHEN** a contributor plans a material update to `README.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to copilot-instructions.md requires proposal
- **WHEN** a contributor plans a material update to `.github/copilot-instructions.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to AGENTS.md requires proposal
- **WHEN** a contributor plans a material update to `AGENTS.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to SYSTEM_ARCHITECTURE_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to TESTING_STANDARDS_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/TESTING_STANDARDS_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to SECURITY_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/SECURITY_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to ENTERPRISE_FEATURES_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/ENTERPRISE_FEATURES_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to PERFORMANCE_REQUIREMENTS_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/PERFORMANCE_REQUIREMENTS_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to DEPLOYMENT_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/DEPLOYMENT_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to TESTING_GUIDE.md requires proposal
- **WHEN** a contributor plans a material update to `docs/TESTING_GUIDE.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to PLUGIN_INTEGRATION_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/PLUGIN_INTEGRATION_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to DATA_MODELS_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/DATA_MODELS_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Material change to COMPREHENSIVE_SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/COMPREHENSIVE_SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: OpenSpec Governance Automation

The project SHALL provide automated tools for tracking, validating, applying, and archiving OpenSpec changes, including support for importing GitHub issues with flexible reference formats.

#### Scenario: Import GitHub issue using full URL format

- **WHEN** a contributor runs python scripts/import_github_issue.py with a full GitHub URL
- **THEN** the tool SHALL parse the URL and import the issue successfully

#### Scenario: Import GitHub issue using short format

- **WHEN** a contributor runs python scripts/import_github_issue.py with owner/repo#number format
- **THEN** the tool SHALL parse the short format reference and import the issue successfully

#### Scenario: Short format with repository containing dashes

- **WHEN** a contributor provides a reference like microsoft/vscode-docs#456
- **THEN** the parser SHALL correctly extract owner repository name with dashes and issue number

#### Scenario: Invalid format provides helpful error message

- **WHEN** a contributor provides an invalid format like microsoft/vscode without issue number
- **THEN** the tool SHALL display an error message explaining both valid formats

#### Scenario: Backward compatibility maintained

- **WHEN** existing automation scripts use full GitHub URLs
- **THEN** all existing URLs SHALL continue to work without modification

### Requirement: Governance for CLAUDE.md
The project SHALL govern material changes to `docs/CLAUDE.md` via OpenSpec
change proposals to maintain consistency, review, and auditability. In
addition, such changes SHALL document proposal content, tasks, a delta spec,
and a validation command.

#### Scenario: Proposal content and validation requirements

- **WHEN** a contributor creates a change for updating `CLAUDE.md`
- **THEN** the change SHALL include:
    - A `proposal.md` with a Why section and capability reference
    - A `tasks.md` with three or more actionable checklist items and a validation step
        - A delta spec at
            `changes/update-doc-claude/specs/project-documentation/spec.md` using valid
            ADDED/MODIFIED/REMOVED sections
    - A documented validation command: `openspec validate update-doc-claude --strict`

### Requirement: Governance for SPECIFICATION_SUMMARY.md
The project SHALL govern material changes to `docs/SPECIFICATION_SUMMARY.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to SPECIFICATION_SUMMARY.md requires proposal
- **WHEN** a contributor plans a material update to `docs/SPECIFICATION_SUMMARY.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for IMPLEMENTATION_RESULTS.md
The project SHALL govern material changes to `docs/IMPLEMENTATION_RESULTS.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to IMPLEMENTATION_RESULTS.md requires proposal
- **WHEN** a contributor plans a material update to `docs/IMPLEMENTATION_RESULTS.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for apply.md
The project SHALL govern material changes to `.claude/commands/openspec/apply.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to apply.md requires proposal
- **WHEN** a contributor plans a material update to `.claude/commands/openspec/apply.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for archive.md
The project SHALL govern material changes to `.claude/commands/openspec/archive.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to archive.md requires proposal
- **WHEN** a contributor plans a material update to `.claude/commands/openspec/archive.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for proposal.md
The project SHALL govern material changes to `.claude/commands/openspec/proposal.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to proposal.md requires proposal
- **WHEN** a contributor plans a material update to `.claude/commands/openspec/proposal.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for audit-backend.md
The project SHALL govern material changes to `docs/audit-backend.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to audit-backend.md requires proposal
- **WHEN** a contributor plans a material update to `docs/audit-backend.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for audit-coverage.md
The project SHALL govern material changes to `docs/audit-coverage.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to audit-coverage.md requires proposal
- **WHEN** a contributor plans a material update to `docs/audit-coverage.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for audit-plugin.md
The project SHALL govern material changes to `docs/audit-plugin.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to audit-plugin.md requires proposal
- **WHEN** a contributor plans a material update to `docs/audit-plugin.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for INTEGRATION_TESTS_COMPLETION_SUMMARY.md
The project SHALL govern material changes to `docs/INTEGRATION_TESTS_COMPLETION_SUMMARY.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to INTEGRATION_TESTS_COMPLETION_SUMMARY.md requires proposal
- **WHEN** a contributor plans a material update to `docs/INTEGRATION_TESTS_COMPLETION_SUMMARY.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for LINT_TYPECHECK_SUMMARY.md
The project SHALL govern material changes to `docs/LINT_TYPECHECK_SUMMARY.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to LINT_TYPECHECK_SUMMARY.md requires proposal
- **WHEN** a contributor plans a material update to `docs/LINT_TYPECHECK_SUMMARY.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for PROJECT_ANALYSIS.md
The project SHALL govern material changes to `docs/PROJECT_ANALYSIS.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to PROJECT_ANALYSIS.md requires proposal
- **WHEN** a contributor plans a material update to `docs/PROJECT_ANALYSIS.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for AUTHENTICATION_FIX_SUMMARY.md
The project SHALL govern material changes to `docs/AUTHENTICATION_FIX_SUMMARY.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to AUTHENTICATION_FIX_SUMMARY.md requires proposal
- **WHEN** a contributor plans a material update to `docs/AUTHENTICATION_FIX_SUMMARY.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for security-modules.md
The project SHALL govern material changes to `docs/security-modules.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to security-modules.md requires proposal
- **WHEN** a contributor plans a material update to `docs/security-modules.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for T006_ENVIRONMENT_OPTIMIZATION_COMPLETE.md
The project SHALL govern material changes to `docs/T006_ENVIRONMENT_OPTIMIZATION_COMPLETE.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to T006_ENVIRONMENT_OPTIMIZATION_COMPLETE.md requires proposal
- **WHEN** a contributor plans a material update to `docs/T006_ENVIRONMENT_OPTIMIZATION_COMPLETE.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for CLARIFICATION.md
The project SHALL govern material changes to `docs/CLARIFICATION.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to CLARIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/CLARIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for CONSTITUTION.md

The project SHALL govern material changes to `docs/CONSTITUTION.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change requires proposal

- **WHEN** a contributor plans a material update to `docs/CONSTITUTION.md`

- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for PROJECT_CLARIFICATION.md
The project SHALL govern material changes to `docs/PROJECT_CLARIFICATION.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to PROJECT_CLARIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/PROJECT_CLARIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for PROJECT_CONSTITUTION.md
The project SHALL govern material changes to `docs/PROJECT_CONSTITUTION.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to PROJECT_CONSTITUTION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/PROJECT_CONSTITUTION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for spec.md
The project SHALL govern material changes to `docs/spec.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to spec.md requires proposal
- **WHEN** a contributor plans a material update to `docs/spec.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for SPECIFICATION.md
The project SHALL govern material changes to `docs/SPECIFICATION.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to SPECIFICATION.md requires proposal
- **WHEN** a contributor plans a material update to `docs/SPECIFICATION.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for ENTERPRISE_FEATURES_CLEAN.md
The project SHALL govern material changes to `docs/ENTERPRISE_FEATURES_CLEAN.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to ENTERPRISE_FEATURES_CLEAN.md requires proposal
- **WHEN** a contributor plans a material update to `docs/ENTERPRISE_FEATURES_CLEAN.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for ENTERPRISE_SUMMARY.md
The project SHALL govern material changes to `docs/ENTERPRISE_SUMMARY.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to ENTERPRISE_SUMMARY.md requires proposal
- **WHEN** a contributor plans a material update to `docs/ENTERPRISE_SUMMARY.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for DEPLOYMENT_STATUS.md
The project SHALL govern material changes to `docs/DEPLOYMENT_STATUS.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to DEPLOYMENT_STATUS.md requires proposal
- **WHEN** a contributor plans a material update to `docs/DEPLOYMENT_STATUS.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for QUICK_FIX.md
The project SHALL govern material changes to `docs/QUICK_FIX.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to QUICK_FIX.md requires proposal
- **WHEN** a contributor plans a material update to `docs/QUICK_FIX.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for SETUP.md
The project SHALL govern material changes to `.obsidian/plugins/obsidian-ai-assistant/SETUP.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to SETUP.md requires proposal

- **WHEN** a contributor plans a material update to `.obsidian/plugins/obsidian-ai-assistant/SETUP.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for SETUP_COMPLETE.md

The project SHALL govern material changes to `.obsidian/plugins/obsidian-ai-assistant/SETUP_COMPLETE.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to SETUP_COMPLETE.md requires proposal

- **WHEN** a contributor plans a material update to `.obsidian/plugins/obsidian-ai-assistant/SETUP_COMPLETE.md`

- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for project.md

The project SHALL govern material changes to `openspec/project.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to project.md requires proposal

- **WHEN** a contributor plans a material update to `openspec/project.md`

- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: Governance for TASKS.md

The project SHALL govern material changes to `docs/TASKS.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change to TASKS.md requires proposal

- **WHEN** a contributor plans a material update to `docs/TASKS.md`

- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

### Requirement: OpenSpec Change Scaffolding CLI

The project SHALL provide a CLI tool to scaffold a new OpenSpec change directory with the correct structure and placeholders.

#### Scenario: Scaffold with title only
- WHEN a contributor runs `python scripts/openspec_new_change.py "My New Change"`
- THEN the tool SHALL create `openspec/changes/YYYY-MM-DD-my-new-change/` with required files

#### Scenario: Scaffold with explicit change ID
- WHEN a contributor runs `python scripts/openspec_new_change.py --id 2025-10-18-my-new-change --title "My New Change"`
- THEN the tool SHALL use the provided ID and create the directory and files accordingly

#### Scenario: Dry run does not create files
- WHEN a contributor runs `python scripts/openspec_new_change.py "My New Change" --dry-run`
- THEN the tool SHALL print the intended actions and SHALL NOT create any files

#### Scenario: Placeholder replacement in todo.md
- WHEN a change is scaffolded
- THEN the tool SHALL replace placeholders in `todo.md` with title, change-id, date, and owner (if provided)

#### Scenario: Force overwrite existing directory
- WHEN a target change directory already exists and the user provides `--force`
- THEN the tool SHALL overwrite the directory contents safely

#### Scenario: Prevent overwrite by default
- WHEN a target change directory already exists and no `--force` flag is provided
- THEN the tool SHALL abort with a clear error message

### Requirement: Review and address all 29 reported security vulnerabilities in dependencies
The project SHALL review and address all 29 reported security vulnerabilities in dependencies.

#### Scenario: Security Scan Review
- **WHEN** a security scan (Safety, Bandit) is run on project dependencies
- **THEN** all 29 reported vulnerabilities are listed and reviewed by a maintainer

### Requirement: Update or replace affected packages to resolve critical vulnerabilities
The project SHALL update or replace affected packages to resolve all critical vulnerabilities.

#### Scenario: Critical Vulnerability Remediation
- **WHEN** a list of critical vulnerabilities is identified
- **THEN** the affected packages are updated or replaced and the vulnerabilities are no longer reported by security tools

### Requirement: Document mitigation plans for non-critical vulnerabilities
The project SHALL document mitigation plans for all non-critical vulnerabilities that cannot be immediately resolved.

#### Scenario: Mitigation Documentation
- **WHEN** non-critical vulnerabilities are found that cannot be immediately resolved
- **THEN** a mitigation plan is created and documented in project documentation and referenced in the security report

### Requirement: Audit all dependencies using Safety and Bandit
The project SHALL audit all dependencies using Safety and Bandit.

#### Scenario: Dependency Audit
- **WHEN** Safety and Bandit are run on the full list of project dependencies
- **THEN** the audit results are reviewed and any issues are addressed or documented

### Requirement: Ensure no new vulnerabilities are introduced
The project SHALL ensure no new vulnerabilities are introduced after updates.

#### Scenario: Regression Prevention
- **WHEN** a new security scan is run after dependency updates
- **THEN** no new vulnerabilities are reported compared to the previous baseline

### Requirement: Update documentation to reflect changes
The project SHALL update documentation to reflect all changes to dependencies or mitigations.

#### Scenario: Documentation Update
- **WHEN** changes to dependencies or mitigations occur
- **THEN** all relevant changes are documented in CHANGELOG.md and security notes

### Requirement: Merge all requirements files into one
The project SHALL merge requirements.txt, requirements-dev.txt, and requirements-ml.txt into a single requirements.txt file.

#### Scenario: Successful merge
- **WHEN** the merge script is run
- **THEN** all packages from the three files are present in the new requirements.txt

### Requirement: Deduplicate and categorize packages
The project SHALL deduplicate all package entries and organize them by category with clear comments.

#### Scenario: Deduplication and categorization
- **WHEN** the merged requirements.txt is generated
- **THEN** no duplicate packages exist, all version pins are preserved, and packages are grouped by category

### Requirement: Remove obsolete requirements files
The project SHALL remove requirements-dev.txt and requirements-ml.txt after merging.

#### Scenario: Obsolete file removal
- **WHEN** the merge is complete
- **THEN** requirements-dev.txt and requirements-ml.txt no longer exist in the repository

### Requirement: Governance for AGENTS.md

The project SHALL govern material changes to `AGENTS.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change requires proposal

- **WHEN** a contributor plans a material update to `AGENTS.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Proposal content and validation requirements

- **WHEN** a contributor creates a change for updating `AGENTS.md`
- **THEN** the change SHALL include:
	- A `proposal.md` with a Why section and capability reference
	- A `tasks.md` with three or more actionable checklist items and a validation step
	- A delta spec at `changes/update-doc-agents/specs/project-documentation/spec.md` using valid ADDED/MODIFIED/REMOVED sections
	- A documented validation command: `openspec validate update-doc-agents --strict`

