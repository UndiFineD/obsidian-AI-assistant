# Test Plan: Backlog Management CLI

## Scope
Validate the correctness of OpenSpec change scanning, stats generation, and ASCII burndown rendering across platforms.

## Unit Tests

- Parse change-id: valid/invalid, various slugs
- Compute age from id date and fallback to mtime
- Status inference: planned/in-progress/done heuristics
- Summary stats: counts and age metrics
- Burndown points: window boundaries and open counts
- Renderer: ASCII-only and fixed width lines

## Integration Tests

- Create temp `openspec/changes` tree with 5-8 entries across dates/statuses
- Run CLI with default text output and validate key lines
- Run CLI with `--format json` and validate schema and values

## Non-Functional Tests

- Windows console safety: no Unicode beyond ASCII
- Performance: scan completes in <200ms for 100 changes (local benchmark)

## Manual Validation

- Run in PowerShell on Windows and confirm chart alignment
- Verify README examples produce expected output

## Exit Criteria

- All unit/integration tests pass in CI
- Code coverage for the CLI module >= 90%
