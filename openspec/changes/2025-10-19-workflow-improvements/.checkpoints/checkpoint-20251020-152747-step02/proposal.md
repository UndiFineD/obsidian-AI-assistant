# Change Proposal: 2025-10-19-workflow-improvements

## Why

We need a fully non-interactive OpenSpec workflow that always progresses when invoked, creates versioned release branches automatically, avoids duplicate updates to docs, fixes coverage warnings, and ensures CI doesn’t block on OpenSpec validation. This reduces manual effort and makes releases predictable.

**Change Type**: New functionality or capability

## What Changes

- Automate versioned release branch creation and use it for push/PR
- Auto-bump patch if a PR already exists for the current release branch
- Remove duplicate todo.md updates; sync tasks.md where relevant
- Fix coverage configuration warning and enable test contexts
- Auto-generate test_plan.md from proposal/spec/tasks
- Disable OpenSpec validation in CI to avoid blocking documentation-only PRs

## Impact

- **Affected specs**: openspec/specs/project-documentation, openspec/specs/ci-cd
- **Affected files**: .github/workflows/openspec-validate.yml, package.json, pytest.ini, scripts/workflow.ps1
- **Users impacted**: Contributors and maintainers running the workflow
- **Review priority**: Medium

## Alternatives Considered

- Keep semi-interactive flow: rejected to meet “always yes” requirement
- Only adjust CI without automating workflow: rejected; would leave manual steps

## Related

- **GitHub Issue**: #0
- **Related Changes**: 2025-10-18-openspec-scaffold-script
