# Specification: Backlog Management CLI and ASCII Burndown

## Overview

CLI: `python scripts/list_openspec_changes.py [options]`

## CLI Options

- --base-dir PATH: Root directory (default: repo root)
- --format [text|json]: Output format (default: text)
- --window DAYS: Number of days to include in burndown (default: 30)
- --status STATUS[,STATUS...]: Filter by status inferred from todo/spec
- --since YYYY-MM-DD: Only include changes on/after this date
- --width N: Chart width (default: 60)

## Data Model

- ChangeId: yyyy-mm-dd-slug
- ChangeRecord
	- id: str
	- date: date
	- title: str | None
	- status: enum{'planned','in-progress','done','unknown'}
	- owner: str | None
	- age_days: int

## Behavior

- Detect changes by directories under `openspec/changes/*`
- Parse date from change id; fallback to directory mtime
- Determine status heuristically:
	- done if retrospective.md exists and todo has all major stages checked
	- in-progress if any stage 3-8 checked, else planned
- Generate burndown: For each day in window, count open (not done) changes whose date <= day
- Render chart with ASCII only; axes and labels stay within width

## Acceptance Criteria

- Text output includes:
	- header summary of counts and age stats
	- table/list of top N oldest changes
	- burndown chart block
- JSON output includes keys: changes[], summary{}, burndown{points[], window}
- Windows-safe: no Unicode outside ASCII; no encoding errors

## Examples

Text:

Summary: 12 active, 5 planned, 6 in-progress, 1 done
Oldest: 2025-08-02-foo (77d), 2025-09-14-bar (34d)
Burndown (last 14 days):
	10 | #######
	 8 | #####
	 6 | ####
	 4 | ###
	 2 | ##
		 +-------------->

JSON (abridged):
{
	"summary": {"active": 12, "planned": 5, "in_progress": 6, "done": 1},
	"burndown": {"window": 14, "points": [{"date":"2025-10-05","open":10}]}
}

## Testability

- Unit tests simulate a temp changes tree with known dates and statuses
- Rendering tests assert ASCII-only and fixed width lines
