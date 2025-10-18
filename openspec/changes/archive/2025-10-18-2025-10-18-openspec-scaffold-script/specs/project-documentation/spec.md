# project-documentation Delta Spec

## ADDED Requirements

### Requirement: OpenSpec Change Scaffolding CLI

The project SHALL provide a CLI tool to scaffold a new OpenSpec change directory with the correct structure and placeholders.

#### Scenario: Scaffold with title only
- WHEN a contributor runs `python scripts/openspec_new_change.py "My New Change"`
- THEN the tool SHALL create `openspec/changes/YYYY-MM-DD-my-new-change/` with required files

#### Scenario: Scaffold with explicit change ID
- WHEN a contributor runs `python scripts/openspec_new_change.py --id 2025-10-18-my-new-change --title "My New Change"`
- THEN the tool SHALL use the provided ID and create the directory and files accordingly

#### Scenario: Dry run does not create files
- WHEN a contributor runs `python scripts/openspec_new_change.py "My New Change" --dry-run`
- THEN the tool SHALL print the intended actions and SHALL NOT create any files

#### Scenario: Placeholder replacement in todo.md
- WHEN a change is scaffolded
- THEN the tool SHALL replace placeholders in `todo.md` with title, change-id, date, and owner (if provided)

#### Scenario: Force overwrite existing directory
- WHEN a target change directory already exists and the user provides `--force`
- THEN the tool SHALL overwrite the directory contents safely

#### Scenario: Prevent overwrite by default
- WHEN a target change directory already exists and no `--force` flag is provided
- THEN the tool SHALL abort with a clear error message
