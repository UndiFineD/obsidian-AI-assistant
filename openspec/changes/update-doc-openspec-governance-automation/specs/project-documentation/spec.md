
# Spec Delta: project-documentation / update-doc-openspec-governance-automation

## ADDED Requirements

### Requirement: OpenSpec Governance Automation

The system SHALL provide comprehensive OpenSpec change management capabilities including automated validation, application, and archiving of specification changes.

#### Scenario: Material change requires proposal

- **WHEN** a contributor plans a material update to `openspec/governance-automation.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Proposal content and validation requirements

- **WHEN** a contributor creates a change for updating `openspec/governance-automation.md`
- **THEN** the change SHALL include:
	- A `proposal.md` with a Why section and capability reference
	- A `tasks.md` with three or more actionable checklist items and a validation step
	- A delta spec at `changes/update-doc-openspec-governance-automation/specs/project-documentation/spec.md` using valid ADDED/MODIFIED/REMOVED sections
	- A documented validation command: `openspec validate update-doc-openspec-governance-automation --strict`
