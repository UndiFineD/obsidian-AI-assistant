# Proposal: Automate GitHub Issue Import to OpenSpec

- Change ID: 2025-10-18-automate-github-issue-import
- Owner: @UndiFineD
- Status: Draft

## Problem Statement
Contributors often open GitHub issues first. We want a simple way to import an issue into an OpenSpec change directory so it can be governed (proposal → spec → tasks → tests → implementation → docs).

## Goals
- One command to scaffold an OpenSpec change from a GitHub issue
- Preserve issue title, body, labels, and links
- Insert references into `proposal.md` and pre-populate `todo.md`

## Non-Goals
- Two-way sync of comments
- Full GitHub project management

## Alternatives Considered
- Manual copy/paste (slow, error-prone)
- GitHub actions that mirror issues to files (less control, PR-only)

## Impact and Risks
- Low risk; local tooling with simple GitHub API calls

## References
- openspec/PROJECT_WORKFLOW.md

## Context

Describe the background and motivation.


## What Changes

List the proposed changes at a high level.


## Stakeholders

- Owner: [owner]
- Reviewers: [reviewers]

