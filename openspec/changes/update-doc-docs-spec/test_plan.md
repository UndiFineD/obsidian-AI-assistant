# Test Plan: update-doc-docs-spec

## Objective
Validate that governance for `docs/spec.md` is enforced via OpenSpec proposals and that all workflow steps are followed.

## Tests
- [ ] Confirm that any material change to `docs/spec.md` triggers an OpenSpec proposal and spec delta.
- [ ] Validate that all workflow artifacts (proposal, spec, tasks, todo, test_plan, retrospective) are present and complete.
- [ ] Run `openspec validate update-doc-docs-spec --strict` and confirm no errors.
- [ ] Confirm PR references the change and links to the archived directory after archiving.
