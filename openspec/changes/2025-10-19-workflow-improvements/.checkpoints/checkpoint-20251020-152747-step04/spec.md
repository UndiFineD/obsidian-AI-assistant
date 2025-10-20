# Specification: Workflow Script Improvements

## Acceptance Criteria
- [ ] The workflow creates or switches to a versioned branch `release-x.y.z`
- [ ] If a PR exists for the current release branch, it auto-bumps patch and uses the next available version
- [ ] No duplicate updates to `todo.md` across steps
- [ ] `tasks.md` is updated for steps 7/8/9 where applicable
- [ ] Coverage warning “No contexts were measured” is resolved
- [ ] `test_plan.md` is auto-generated and aligned with proposal/spec/tasks
- [ ] OpenSpec validation in CI is disabled (non-blocking)

## Requirements
### Functional
1. Implement branch selection and patch auto-increment logic in Step 1 and reuse in Steps 10/12
2. Ensure a single `Update-TodoFile` call per step; add `Update-TasksFile` for steps 7/8/9
3. Update pytest/coverage config to enable test contexts
4. Synthesize `test_plan.md` from proposal/spec/tasks, with timestamp
5. Modify `.github/workflows/openspec-validate.yml` to disable blocking validation

### Non-Functional
- Script should run non-interactively and avoid halting exits on template placeholders
- Clear console output with minimal warnings

## Implementation
- PowerShell changes in `scripts/workflow.ps1` for versioning, tasks sync, and doc generation
- Additions to `pytest.ini` for coverage contexts
- CI workflow update in `.github/workflows/openspec-validate.yml`

## Design
- Centralize version/branch in `$script:NewVersion` and `$script:VersionBranch`
- Use `Get-ChangeDocInfo` to construct commit messages and PR bodies

## Architecture
- OpenSpec change docs under `openspec/changes/<id>/`
- CI workflows under `.github/workflows/`

## References
- Proposal: ./proposal.md
- Tasks: ./tasks.md
- Test Plan: ./test_plan.md
