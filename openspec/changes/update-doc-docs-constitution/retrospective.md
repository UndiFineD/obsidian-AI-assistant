# Retrospective: update-doc-docs-constitution

## Summary
- Established OpenSpec governance for material changes to `docs/CONSTITUTION.md`.
- Ensures future updates follow proposal → spec → tasks → validation → docs → PR flow.

## What Went Well
- Clean separation of documentation governance from code changes.
- Clear requirements added under `project-documentation` capability.

## What Could Improve
- Automate validation with a dedicated OpenSpec CLI.
- Add pre-commit hook to detect material CONSTITUTION.md changes and require a proposal reference.

## Follow-ups
- Integrate `scripts/generate_changelog.py` into release workflow to include OpenSpec changes.
- Consider adding a GitHub Action to run `scripts/openspec-validate.ps1` on PRs touching docs/CONSTITUTION.md.
