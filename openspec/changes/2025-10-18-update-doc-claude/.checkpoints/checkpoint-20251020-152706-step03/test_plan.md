# Test Plan: update-doc-claude

## Goals
- Validate that `docs/CLAUDE.md` meets OpenSpec governance requirements.
- Ensure proposal, tasks, and delta spec exist and are valid.

## Checks
[x] Lint markdown files under this change directory
[x] Run validation: `openspec validate update-doc-claude --strict`
[x] Confirm CI passes for PR

## Exit Criteria
- All checks above are green and PR is merged.
