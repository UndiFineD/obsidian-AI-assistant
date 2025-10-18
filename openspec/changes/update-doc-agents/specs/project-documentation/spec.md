# Spec Delta: project-documentation / update-doc-agents

## ADDED Requirements

### Requirement: Governance for AGENTS.md
The project SHALL govern material changes to `openspec/AGENTS.md` via OpenSpec change proposals.

#### Scenario: Material change requires proposal
- WHEN a contributor plans a material update to `openspec/AGENTS.md`
- THEN they MUST create or update an OpenSpec change under `project-documentation`
- AND include `proposal.md`, `tasks.md`, `test_plan.md`, and `retrospective.md`
- AND document a validation command: `openspec validate update-doc-agents --strict`
