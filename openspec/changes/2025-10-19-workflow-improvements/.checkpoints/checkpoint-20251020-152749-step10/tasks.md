# Tasks: 2025-10-19-workflow-improvements

## 1. Implementation
- [ ] 1.1 Step 1: auto-create/switch to release-x.y.z, store `$script:NewVersion`/`$script:VersionBranch`
- [ ] 1.2 Step 10: push to `$script:VersionBranch`; generate commit message from docs
- [ ] 1.3 Step 12: create PR from `$script:VersionBranch`; reuse doc metadata
- [ ] 1.4 Remove duplicate Update-TodoFile calls across steps
- [ ] 1.5 Integrate `Update-TasksFile` for steps 7/8/9
- [ ] 1.6 Auto-generate `test_plan.md` and align with proposal/spec/tasks

## 2. Testing
- [ ] 2.1 Write unit tests for version detection and branch naming logic (where feasible)
- [ ] 2.2 Validate CI workflow change doesn’t block PRs
- [ ] 2.3 Verify coverage contexts appear in coverage reports

## 3. Documentation
- [ ] 3.1 Update docs: WORKFLOW_IMPROVEMENTS_OCTOBER_2025.md
- [ ] 3.2 Summarize changes in CHANGELOG.md and README badges

## Validation
- [ ] Run: `./scripts/workflow.ps1 -ChangeId "2025-10-19-workflow-improvements" -Step 2..5`
- [ ] Confirm branch `release-0.1.19+` is created and PR uses it
