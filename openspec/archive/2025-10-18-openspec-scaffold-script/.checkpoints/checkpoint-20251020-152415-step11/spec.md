# Specification: OpenSpec Scaffold Script

## Functional Requirements
- CLI command to create a new change directory under `openspec/changes/`
- Accept inputs: title (required), owner (optional), change-id (optional), date (optional)
- Auto-generate `change-id` as `YYYY-MM-DD-<slug>` when not provided
- Copy `openspec/templates/todo.md` and replace placeholders:
  - `<Change Title>` -> Title
  - `<change-id>` -> Change ID
  - `YYYY-MM-DD` -> Date
  - `@username` -> Owner (if provided)
- Create additional files with minimal content: `proposal.md`, `spec.md`, `tasks.md`, `test_plan.md`
- Dry-run mode to preview actions
- Force flag to overwrite existing directory

## Quality Requirements
- Standard library only (no new dependencies)
- Type hints for public functions
- Unit tests with pytest

## CLI
- Module: `scripts/openspec_new_change.py`
- Example:
  - `python scripts/openspec_new_change.py "Security headers audit" --owner @kdejo`
  - `python scripts/openspec_new_change.py --id 2025-10-18-security-audit --title "Security headers audit"`

## Acceptance Criteria
- Running the script creates the expected directory and files
- Placeholders in `todo.md` are correctly replaced
- Re-running without `--force` does not overwrite
- Tests pass

## Requirements

- **R-01**: ...
- **R-02**: ...

