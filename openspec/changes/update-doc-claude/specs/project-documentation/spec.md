# Spec Delta: project-documentation / update-doc-claude

## MODIFIED Requirements

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
