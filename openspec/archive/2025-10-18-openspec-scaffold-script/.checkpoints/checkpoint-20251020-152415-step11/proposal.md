# Proposal: OpenSpec Scaffold Script

## Problem Statement
Creating OpenSpec change directories and files (todo.md, proposal.md, spec.md, tasks.md, test_plan.md) is repetitive and error-prone when done manually.

## Goal
Provide a simple, repeatable CLI tool to scaffold a new change with correct structure, naming, and placeholder replacement.

## Scope
- Generate `openspec/changes/<change-id>/` directory
- Create files: `todo.md` (from template), `proposal.md`, `spec.md`, `tasks.md`, `test_plan.md`
- Replace placeholders in `todo.md` with title, id, date, and owner
- Safe-by-default: do not overwrite existing changes unless `--force`

## Non-Goals
- No network calls or GitHub API integration
- No CI wiring (documented usage only)

## Rationale
- Reduces friction and ensures consistency across changes
- Aligns with Stage 0: Create TODOs

## Alternatives
- Manual copy-paste of templates (error-prone)
- Complex project generators (overkill)

## Impact
- Developer productivity improvement
- Consistent artifact naming and content

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

