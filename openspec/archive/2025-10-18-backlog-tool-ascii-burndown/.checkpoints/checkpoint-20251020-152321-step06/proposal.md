# Proposal: Backlog Management Tool with ASCII Burndown

## Problem Statement

Maintainers need a quick, offline-friendly way to visualize and manage OpenSpec change backlog health directly from the repository. Existing solutions are either manual or require external services. We need a simple CLI that scans `openspec/changes/` and surfaces actionable insights, including an ASCII burndown chart that renders cleanly in any terminal (including Windows), plus summary stats to help prioritize work.

## Goals and Non-Goals

- Goals
	- Provide a Python CLI that scans OpenSpec changes and prints:
		- Active changes list with age, status, and owner when available
		- Summary metrics (counts per status, average/median age)
		- ASCII burndown chart over a selectable window
	- Ensure outputs are ASCII-only and stable on Windows terminals
	- Include basic filtering by date/status and support JSON output for automation
	- Add tests that validate parsing, stats, and chart rendering

- Non-Goals
	- No external dashboard or web UI
	- No dependency on network access or external APIs

## Rationale

An offline-first CLI aligns with the project’s constraints and improves day-to-day visibility without adding operational overhead. ASCII visualization avoids encoding issues and works in CI logs and PowerShell consoles.

## Solution Overview

Implement `scripts/list_openspec_changes.py` with:
	- Directory scan and change-id parsing (YYYY-MM-DD-slug)
	- Age computation based on change-id date and/or file timestamps
	- Summary stats aggregation and optional filters
	- Burndown data generation (daily open count) and fixed-width ASCII chart rendering
	- CLI options for format, window, filters, and output redirection

## Alternatives Considered

- Markdown images via external charting libraries: introduces rendering and dependency complexity
- Rich/Unicode plotting: fails on Windows legacy code pages; harder to read in CI
- GitHub Projects integration: requires network and credentials, non-offline

## Impact Analysis

- Code: Adds a standalone script plus tests; no breaking API changes
- Performance: O(number of changes) file system scan; negligible impact
- Security/Privacy: No external calls; reads repository files only
- Maintenance: Low; tests cover core functionality

## Acceptance Criteria

- Running the CLI with no args prints a readable summary and ASCII burndown without errors on Windows
- Provides JSON output with `--format json` that includes stats and burndown data
- Handles empty or missing `openspec/changes/` gracefully
- Unit tests cover parsing, stats, and rendering with 90%+ module coverage

## Validation

- Pytest tests pass locally and in CI on Windows/Linux
- Manual runs show correct chart spacing and labels in PowerShell

## Rollout Plan

- Merge behind v0.1.6 release branch, document in CHANGELOG, and include short how-to in README

## Risks and Mitigations

- Terminal width differences: default to sane width and wrap labels; provide `--width` option
- Encoding issues on Windows: enforce ASCII-only output and avoid emojis

## Context

Describe the background and motivation.


## What Changes

List the proposed changes at a high level.


## Stakeholders

- Owner: [owner]
- Reviewers: [reviewers]

