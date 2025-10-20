# Spec Delta: project-documentation / update-doc-test-metrics-automation

## ADDED Requirements

### Requirement: Documentation clarity

The OpenSpec documentation SHALL describe backend agent architecture, API capabilities, and extensibility for both offline and connected modes.

#### Scenario: Contributor onboarding for automation

- **WHEN** a contributor adds or updates test metrics automation documentation (e.g., scripts or CI workflows)
- **THEN** they SHALL ensure docs (e.g., `docs/TESTING_GUIDE.md`) clearly document usage, flags, CI integration, and troubleshooting

### Requirement: Governance for TESTING_GUIDE.md

The project SHALL govern material changes to `docs/TESTING_GUIDE.md` via OpenSpec change proposals to maintain consistency and review.

#### Scenario: Material change requires proposal

- **WHEN** a contributor plans a material update to `docs/TESTING_GUIDE.md`
- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`

#### Scenario: Proposal content and validation requirements

- **WHEN** a contributor creates a change for updating automation documentation
- **THEN** the change SHALL include:
	- A `proposal.md` with a Why section and capability reference
	- A `tasks.md` with three or more actionable checklist items and a validation step
	- A delta spec at `changes/update-doc-test-metrics-automation/specs/project-documentation/spec.md` using valid ADDED/MODIFIED/REMOVED sections
	- A documented validation command: `openspec validate update-doc-test-metrics-automation --strict`

## Requirements

- **R-01**: ...
- **R-02**: ...


## Acceptance Criteria

- [ ] AC-01: ...
- [ ] AC-02: ...

