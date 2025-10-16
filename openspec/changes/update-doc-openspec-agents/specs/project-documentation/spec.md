# Spec Delta: project-documentation / update-doc-openspec-agents

## MODIFIED Requirements

### Requirement: Governance for AGENTS.md

The project SHALL govern material changes to `AGENTS.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change requires proposal

- **WHEN** a contributor plans a material update to `AGENTS.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Proposal content and validation requirements

- **WHEN** a contributor creates a change for updating `openspec/AGENTS.md`
- **THEN** the change SHALL include:
	- A `proposal.md` with a Why section and capability reference
	- A `tasks.md` with three or more actionable checklist items and a validation step
	- A delta spec at `changes/update-doc-openspec-agents/specs/project-documentation/spec.md` using valid ADDED/MODIFIED/REMOVED sections
	- A documented validation command: `openspec validate update-doc-openspec-agents --strict`
