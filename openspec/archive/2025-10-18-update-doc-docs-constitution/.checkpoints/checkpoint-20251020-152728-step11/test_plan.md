# Test Plan: update-doc-docs-constitution

## Goals
- Validate that `docs/CONSTITUTION.md` governance is documented and compliant with OpenSpec.
- Ensure the change directory contains proposal, tasks, and delta spec.

## Checks
- [ ] Lint markdown files under this change directory
- [ ] Run validation: `openspec validate update-doc-docs-constitution --strict`
- [ ] Confirm CI passes for PR

## Exit Criteria
- All checks above are green and PR is merged.
