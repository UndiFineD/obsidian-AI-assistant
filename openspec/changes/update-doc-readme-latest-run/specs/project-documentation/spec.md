# Spec Delta: project-documentation / update-doc-readme-latest-run

## ADDED Requirements

### Requirement: Keep README test status current

- Capability: project-documentation
- Artifact: README.md

#### Scenario: README reflects latest test run

- **GIVEN** a new full-suite test run completes
- **WHEN** counts or timing change
- **THEN** README.md MUST be updated to match the latest status (e.g., 691 passed, 2 skipped on Oct 15, 2025)

This change is governed by OpenSpec documentation governance. Material changes to README require a proposal, tasks checklist, and spec delta in openspec/changes.
