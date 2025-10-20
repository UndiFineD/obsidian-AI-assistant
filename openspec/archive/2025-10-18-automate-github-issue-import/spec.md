# Specification: Automate GitHub Issue Import to OpenSpec

## Overview
Provide a CLI that takes a GitHub issue URL or number and scaffolds a new OpenSpec change directory using the issue metadata.

## Requirements
- Input: `--issue <url-or-number>`, `--owner`, optional `--id`
- Output: create `openspec/changes/<id>/` with: proposal.md, spec.md, tasks.md, test_plan.md, todo.md
- Populate proposal.md with issue title, link, and body
- Update todo.md placeholders: owner, created date, change-id
- Robust to missing labels/body

## Acceptance Criteria
- Given an issue URL, the CLI creates the directory and files without errors
- proposal.md contains the issue title and a link
- todo.md shows updated owner and date

## Security
- Read-only GitHub calls using env var token `GITHUB_TOKEN` if provided
- Fallback to unauthenticated requests (low rate limits)
