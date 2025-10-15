# Spec Delta: project-documentation / update-doc-openspec-agents

This change updates `openspec/AGENTS.md` to comply with OpenSpec documentation governance. All agent documentation changes are tracked via proposals, tasks, and capability specs.

## ADDED Requirements

### Requirement: proposal.md present with Why section and capability reference

### Requirement: tasks.md present with ≥3 checklist items and validation command

### Requirement: specs/project-documentation/spec.md present with proper structure

### Requirement: Validation command: `openspec validate update-doc-openspec-agents --strict`

#### Scenario: Update openspec/AGENTS.md with OpenSpec compliance

- **WHEN** a contributor updates openspec/AGENTS.md for OpenSpec compliance

- **THEN** the change is tracked via proposal.md, tasks.md, and spec.md, and validated using the OpenSpec command above. All requirements are met for OpenSpec compliance.
