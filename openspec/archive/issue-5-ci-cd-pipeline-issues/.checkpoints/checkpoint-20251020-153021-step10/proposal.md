# Proposal: CI/CD pipeline issues

**Source**: GitHub Issue #5

## Overview

GitHub Copilot Chat Assistant

I can create the issues for you, but I cannot open GitHub issues directly with the available tools. Please confirm whether you want me to:

A) Create these issues in the repository for you (I will prepare the issue content and the exact gh CLI commands you can run), or
B) Open a PR that fixes the pipeline errors (I can create a branch + PR to fix the artifact actions automatically if you want).
Which would you like? If A, I’ll prepare the exact issue bodies and gh commands now. If B, say “open PR” and I’ll create the patch and open a PR.

Below are the issue drafts I will create (one per distinct CI/CD error or actionable problem). Each includes the title, body, files/locations (using the referenced workflow ref 4065eb0de821a7a6be1a23a89f522494cdab5fa6), and a ready-to-run gh CLI command.

Title Replace deprecated actions/upload-artifact@v3 and actions/download-artifact@v3 with v4
Body Observed failure:

Job 53064452115 failed with: "This request has been automatically failed because it uses a deprecated version of actions/upload-artifact: v3."
Workflow: .github/workflows/security-scan.yml at ref 4065eb0de821a7a6be1a23a89f522494cdab5fa6
What to change:

Replace all uses of actions/upload-artifact@v3 -> actions/upload-artifact@v4
Replace all uses of actions/download-artifact@v3 -> actions/download-artifact@v4
Files/locations

.github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6)
Suggested patch snippet

Change: uses: actions/upload-artifact@v3 uses: actions/download-artifact@v3
To: uses: actions/upload-artifact@v4 uses: actions/download-artifact@v4
Why

v3 of the artifact actions was deprecated (April 2024) and using it causes workflow failures.
gh CLI to create gh issue create --title "Replace deprecated actions/upload-artifact@v3 and actions/download-artifact@v3 with v4" --body "$(cat <<'EOF' Observed failure:

Job 53064452115 failed with: "This request has been automatically failed because it uses a deprecated version of actions/upload-artifact: v3."
Workflow: .github/workflows/security-scan.yml at ref 4065eb0de821a7a6be1a23a89f522494cdab5fa6
What to change:

Replace actions/upload-artifact@v3 -> actions/upload-artifact@v4
Replace actions/download-artifact@v3 -> actions/download-artifact@v4
Files:

.github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6)
Suggested patch:

Update usages to @v4 as shown above.
EOF )" --label "ci" --label "bug"

Title Pin third-party actions to fixed releases (avoid tracking master)
Body Observed risk:

Workflow uses snyk/actions/python@master (and actions/github-script@v6 is used which is OK but consider pinning to exact tags). Tracking master can introduce breaking changes into CI.
What to change:

Replace snyk/actions/python@master with a released tag (e.g., snyk/actions/python@v1.x — pick the latest stable tag from the action repo).
Where practical, prefer anchored tags or commit SHAs for critical workflows so unexpected breaks are minimized.
Files/locations

.github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6), lines referencing snyk/actions/python@master
Why

Pinning prevents upstream breaking changes from suddenly breaking CI.
gh CLI to create gh issue create --title "Pin third-party actions to fixed releases (avoid tracking master)" --body "$(cat <<'EOF' Observed risk:

Workflow uses snyk/actions/python@master in .github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6).
Tracking master risks unexpected CI breakage.
What to change:

Replace master with the latest stable release tag for snyk/actions/python.
Consider pinning other critical actions to tags or SHAs.
EOF )" --label "ci" --label "maintenance"

Title Stop masking security scan failures with "|| true" so CI reflects actual failures
Body Observed issue:

Several scan commands end with || true (safety, bandit, semgrep, npm audit). This forces steps to succeed even when scans find problems or the scanner errors out, making detection and enforcement harder.
What to change:

Decide per-scan whether failures should block the job. If you want scans to fail the job on errors/severe findings, remove || true and handle reporting/return codes explicitly.
Alternatively, capture scan exit codes to a file and use an explicit summary step that fails if thresholds are exceeded.
Files/locations

.github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6) — search for "|| true" in scan steps.
Why

Masking failures hides real issues and makes CI less actionable.
Suggested change example

Replace: semgrep --config=auto backend/ --json --output=semgrep-report.json || true
With: semgrep --config=auto backend/ --json --output=semgrep-report.json || true # or better: capture exit code and optionally fail
Or implement: semgrep --config=auto backend/ --json --output=semgrep-report.json || echo "SEMgrep_FAILED=true" >> $GITHUB_ENV

gh CLI to create gh issue create --title "Stop masking security scan failures with '|| true' so CI reflects actual failures" --body "$(cat <<'EOF' Observed issue:

Scan commands in .github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6) use "|| true", masking failures.
What to change:

Remove "|| true" where you want CI to fail on scanner errors/findings, or capture exit codes and fail conditionally based on thresholds.
EOF )" --label "ci" --label "enhancement"

Title Ensure SNYK_TOKEN secret is configured (Snyk report generation may be skipped)
Body Observed behavior:

Snyk step writes a note in the summary if snyk-report.json is missing; Snyk requires SNYK_TOKEN for authenticated scans. If the secret is missing, Snyk may not run or produce a report.
What to change:

Add SNYK_TOKEN as a repository secret if you intend to run authenticated Snyk scans.
Alternatively document that Snyk scan is optional and make the step conditional on SNYK_TOKEN presence.
Files/locations

.github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6)
gh CLI to create gh issue create --title "Ensure SNYK_TOKEN secret is configured for Snyk scans" --body "$(cat <<'EOF' Observed:

The Snyk step references SNYK_TOKEN in .github/workflows/security-scan.yml (ref: 4065eb0de821a7a6be1a23a89f522494cdab5fa6).
If SNYK_TOKEN is not set, the report may not be produced.
Suggested:

Add SNYK_TOKEN as a repository secret or make the step conditional on the token.
EOF )" --label "ci" --label "ops"

## Labels

None

## Proposed Changes

<!-- Fill in specific implementation details -->

## Tasks

See `todo.md` for detailed task breakdown.

## Testing

<!-- Describe how changes will be tested -->

## Impact Analysis

<!-- Describe potential impacts and risks -->

## Context

Describe the background and motivation.


## What Changes

List the proposed changes at a high level.


## Goals

- Goal 1: ...
- Goal 2: ...


## Stakeholders

- Owner: [owner]
- Reviewers: [reviewers]

