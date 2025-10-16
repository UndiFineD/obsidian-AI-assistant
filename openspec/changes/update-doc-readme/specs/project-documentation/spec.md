# Spec Delta: project-documentation / update-doc-readme

## MODIFIED Requirements

### Requirement: Governance for README.md

The project SHALL govern material changes to `README.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change requires proposal

- **WHEN** a contributor plans a material update to `README.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Proposal content and validation requirements

- **WHEN** a contributor creates a change for updating `README.md`
- **THEN** the change SHALL include:
	- A `proposal.md` with a Why section and capability reference
	- A `tasks.md` with three or more actionable checklist items and a validation step
	- A delta spec at `changes/update-doc-readme/specs/project-documentation/spec.md` using valid ADDED/MODIFIED/REMOVED sections
	- A documented validation command: `openspec validate update-doc-readme --strict`
