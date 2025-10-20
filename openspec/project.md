# OpenSpec Governance Overview
## Purpose

This document explains how OpenSpec governs documentation changes in this
repository and how it integrates with our development workflow.
OpenSpec is used to ensure our critical project documentation stays accurate, consistent, and auditable over time.

## What is Governed?
Material changes to the following are governed by OpenSpec:
- Top-level docs: `README.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`
- Docs folder: Architecture, security, testing, performance, deployment, enterprise, and other files under `docs/`
- OpenSpec content: This directory (`openspec/`), including specs, changes, archive, docs, and scripts
See the authoritative baseline in `specs/project-documentation/spec.md`.

## Governance Lifecycle
1. Propose: Create a change under `openspec/changes/<id>/` with `proposal.md`, `tasks.md`, and deltas in `specs/<capability>/spec.md`
2. Validate: Run strict validation locally and in CI to ensure correctness
3. Review: Submit a pull request for peer review and approval
4. Apply: After merge, apply the change to the baseline spec (`openspec apply`
   or scripts)
5. Archive: Move the completed change to `openspec/archive/<id>/` with automated backup
Automation scripts in `openspec/scripts/` streamline each step (`create-change.ps1`,
`validate-all.ps1`, `apply-change.ps1`, `archive-change.ps1`).

## Success Metrics & SLAs
- Onboarding: < 1 hour for first contribution (target achieved: ~15–30 minutes)
- Validation: > 95% strict validation pass rate (current: 100%)
- Review: < 24 hours to first review on business days
- Availability: Docs remain accurate and consistent across files

## Integration with Development Workflow
- Governed docs must follow the OpenSpec process (proposal → validate → PR → apply → archive)
- CI validates `openspec/**` changes using strict mode
- Maintainers apply and archive changes post-merge (can be delegated using scripts)

## Roles & Responsibilities
- Contributors: Propose changes, ensure validation passes, respond to review
- Reviewers: Verify deltas, scenarios, and adherence to governance
- Maintainers: Apply to baseline, archive, and ensure overall quality

## Getting Started
- Read: `openspec/README.md`, `openspec/docs/contributor-guide.md`
- Use scripts: `openspec/scripts/create-change.ps1`, `validate-all.ps1`, `apply-change.ps1`, `archive-change.ps1`
- Follow patterns: `openspec/docs/change-patterns.md`
- Troubleshoot: `openspec/docs/troubleshooting.md`

## References
- Baseline spec: `openspec/specs/project-documentation/spec.md`
- Patterns: `openspec/docs/change-patterns.md`
- Onboarding: `openspec/docs/contributor-guide.md`
- Troubleshooting: `openspec/docs/troubleshooting.md`
- Scripts: `openspec/scripts/README.md`
