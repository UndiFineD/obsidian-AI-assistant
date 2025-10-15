#!/usr/bin/env python3
"""Generate OpenSpec change directories for documentation governance."""
import sys
from pathlib import Path
from datetime import datetime

# Repository root detection
REPO_ROOT = Path(__file__).parent.parent

# Paths to exclude from OpenSpec change generation
EXCLUDED_PATHS = {
    '__pycache__',
    '.git',
    'node_modules',
    '.venv',
    '.pytest_cache',
    'htmlcov',
    'dist',
    'build',
    '.mypy_cache',
    '.ruff_cache',
}


def to_change_id(file_path):
    """Convert a file path to an OpenSpec change ID.
    
    Args:
        file_path: Path object or string representing the file
        
    Returns:
        String change ID in format: update-doc-{path-parts}
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # Get relative path from repo root
    try:
        rel_path = file_path.relative_to(REPO_ROOT)
    except ValueError:
        # If not relative to REPO_ROOT, use as-is
        rel_path = file_path
    
    # Convert to parts and clean up
    parts = []
    for part in rel_path.parts:
        # Remove .md extension only
        if part.endswith('.md'):
            part = part[:-3]
        # Handle dotfiles/dotdirs (like .github) - keep the name without the dot
        if part.startswith('.') and len(part) > 1:
            part = part[1:]  # Remove leading dot
        # Replace remaining dots and underscores with hyphens
        part = part.replace('.', '-').replace('_', '-')
        # Lowercase
        part = part.lower()
        if part:  # Only add non-empty parts
            parts.append(part)
    
    # Join with hyphens and prefix with update-doc-
    change_id = "update-doc-" + "-".join(parts)
    return change_id


def proposal_md(change_id, rel_path):
    """Generate proposal.md content for a change.
    
    Args:
        change_id: The change ID
        rel_path: Relative path to the file being changed
        
    Returns:
        String containing the proposal markdown
    """
    return f"""# Change Proposal: {change_id}

## Summary

Update `{rel_path}` for OpenSpec governance, compliance, and documentation structure. This proposal covers changes to `{rel_path}` and related documentation files for the project-documentation capability.

## Why

The {rel_path} needs to comply with OpenSpec governance to ensure consistent change tracking, validation, and auditability. The current file lacks proper OpenSpec structure and references.

## What Changes

- Revise `{rel_path}` for OpenSpec compliance

- Add documentation for change proposals, tasks, and capability specs

- Reference all updated files in this proposal

- Implement project-documentation capability requirements

## Rationale

Ensures `{rel_path}` reflects current OpenSpec requirements and project documentation standards. Improves auditability and clarity for contributors and AI agents working with the project-documentation capability.

## Scope

Files affected:
- `{rel_path}` (primary)
- `openspec/changes/{change_id}/proposal.md` (this file)
- `openspec/changes/{change_id}/tasks.md`
- `openspec/changes/{change_id}/specs/project-documentation/spec.md`

## Impact

Improves clarity, governance, and auditability of project documentation. Enables automated validation and change tracking for `{rel_path}` and related files under the project-documentation capability.
"""


def tasks_md(change_id, rel_path):
    """Generate tasks.md content for a change.
    
    Args:
        change_id: The change ID
        rel_path: Relative path to the file being changed
        
    Returns:
        String containing the tasks markdown
    """
    return f"""
# Tasks: {change_id}

## 1. Implementation

- [ ] 1.1 Revise `{rel_path}` for OpenSpec compliance

- [ ] 1.2 Add `proposal.md` and capability spec

- [ ] 1.3 Validate tasks.md checklist format

- [ ] 1.4 Run validation: `openspec validate {change_id} --strict`

## 2. Validation

- [ ] 2.1 Run `openspec validate {change_id} --strict` to confirm compliance
"""


def spec_delta_md(change_id, rel_path):
    """Generate spec delta markdown for a change.
    
    Args:
        change_id: The change ID
        rel_path: Relative path to the file being changed
        
    Returns:
        String containing the spec delta markdown
    """
    return f"""# Spec Delta: project-documentation / {change_id}

This change updates `{rel_path}` to comply with OpenSpec documentation governance. All project documentation changes are tracked via proposals, tasks, and capability specs.

## ADDED Requirements

### Requirement: proposal.md present with Why section and capability reference

### Requirement: tasks.md present with ≥3 checklist items and validation command

### Requirement: specs/project-documentation/spec.md present with proper structure

### Requirement: Validation command: `openspec validate {change_id} --strict`

#### Scenario: Update {rel_path} with OpenSpec compliance

- **WHEN** a contributor updates {rel_path} for OpenSpec compliance

- **THEN** the change is tracked via proposal.md, tasks.md, and spec.md, and validated using the OpenSpec command above. All requirements are met for OpenSpec compliance.
"""


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: generate_openspec_changes.py <file_path>")
        return 1
    
    file_path = Path(sys.argv[1])
    change_id = to_change_id(file_path)
    
    # Get relative path
    try:
        rel_path = file_path.relative_to(REPO_ROOT)
    except ValueError:
        rel_path = file_path
    
    # Create change directory
    changes_dir = REPO_ROOT / "openspec" / "changes" / change_id
    changes_dir.mkdir(parents=True, exist_ok=True)
    
    # Create specs directory
    specs_dir = changes_dir / "specs" / "project-documentation"
    specs_dir.mkdir(parents=True, exist_ok=True)
    
    # Write proposal.md (check if exists first)
    proposal_path = changes_dir / "proposal.md"
    if not proposal_path.exists():
        proposal_path.write_text(proposal_md(change_id, str(rel_path)), encoding='utf-8')
    
    # Write tasks.md
    tasks_path = changes_dir / "tasks.md"
    if not tasks_path.exists():
        tasks_path.write_text(tasks_md(change_id, str(rel_path)), encoding='utf-8')
    
    # Write spec.md
    spec_path = specs_dir / "spec.md"
    if not spec_path.exists():
        spec_path.write_text(spec_delta_md(change_id, str(rel_path)), encoding='utf-8')
    
    print(f"Created OpenSpec change: {change_id}")
    print(f"  - {proposal_path}")
    print(f"  - {tasks_path}")
    print(f"  - {spec_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
