# Test Plan: update-doc-agents

## Scope
- Validate that AGENTS.md is updated for OpenSpec compliance
- Ensure all required artifacts (proposal.md, tasks.md, spec.md) exist and are valid

## Test Cases
- [ ] AGENTS.md contains OPENSPEC:START/END managed block
- [ ] AGENTS.md documents proposal, tasks, and capability spec requirements
- [ ] AGENTS.md references project-documentation capability
- [ ] All checklist items in tasks.md are actionable and include a validation step
- [ ] Delta spec exists at specs/project-documentation/spec.md and uses valid ADDED/MODIFIED/REMOVED sections
- [ ] Running `openspec validate update-doc-agents --strict` passes with no errors

## Manual Validation
- [ ] Review AGENTS.md for clarity and completeness
- [ ] Confirm all links and references are correct
