# Spec Delta: project-documentation / update-doc-docs-constitution

## MODIFIED Requirements

### Requirement: Governance for CONSTITUTION.md
The project SHALL govern material changes to `docs/CONSTITUTION.md` via OpenSpec
change proposals to maintain consistency and review. Changes SHALL also
document proposal content, tasks, delta spec, and validation.

#### Scenario: Proposal content and validation requirements
- **WHEN** a contributor creates a change for updating `docs/CONSTITUTION.md`
- **THEN** the change SHALL include:
    - A `proposal.md` with a Why section and capability reference
    - A `tasks.md` with three or more actionable checklist items and a validation step
    - A delta spec at
      `changes/update-doc-docs-constitution/specs/project-documentation/spec.md`
      using valid ADDED/MODIFIED/REMOVED sections
    - A documented validation command:
      `openspec validate update-doc-docs-constitution --strict`
