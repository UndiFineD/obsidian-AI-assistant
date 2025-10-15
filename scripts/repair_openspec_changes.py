#!/usr/bin/env python3
"""Repair and validate OpenSpec change directories."""
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Repository root detection
REPO_ROOT = Path(__file__).parent.parent

# Paths to exclude from OpenSpec change generation
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "htmlcov",
    "dist",
    "build",
    ".mypy_cache",
    ".ruff_cache",
    "/openspec/changes/",
    "/.git/",
    "/node_modules/",
    "/.venv/",
    "/.pytest_cache/",
}


def to_change_id_for_path(file_path):
    """Convert a file path to an OpenSpec change ID (alias for compatibility).

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
        if part.endswith(".md"):
            part = part[:-3]
        # Handle dotfiles/dotdirs (like .github) - keep the name without the dot
        if part.startswith(".") and len(part) > 1:
            part = part[1:]  # Remove leading dot
        # Replace remaining dots and underscores with hyphens
        part = part.replace(".", "-").replace("_", "-")
        # Lowercase
        part = part.lower()
        if part:  # Only add non-empty parts
            parts.append(part)

    # Join with hyphens and prefix with update-doc-
    change_id = "update-doc-" + "-".join(parts)
    return change_id


def infer_target_relpath_from_text(text, existing_files=None, file_map=None):
    """Infer the target file path from proposal or tasks text.

    Args:
        text: Content of proposal.md or tasks.md
        existing_files: Optional set of existing files (for compatibility)
        file_map: Optional file mapping dict (for compatibility)

    Returns:
        Inferred relative path or None
    """
    # Look for common patterns like:
    # - `README.md`
    # - Revise `path/to/file.md`
    # - Update `file.yaml`

    # Pattern 1: Backtick-quoted paths
    backtick_pattern = r"`([^`]+\.(md|yaml|py|txt))`"
    matches = re.findall(backtick_pattern, text)
    if matches:
        # Return the first match (just the path, not the extension group)
        return matches[0][0]

    # Pattern 2: Look for "Update <path>" or "Revise <path>"
    update_pattern = r"(?:Update|Revise|Modify)\s+([^\s]+\.(md|yaml|py|txt))"
    matches = re.findall(update_pattern, text, re.IGNORECASE)
    if matches:
        return matches[0][0]

    return None


def canonical_change_dir_for(file_path):
    """Get the canonical change directory for a given file path.

    Args:
        file_path: Path to the file

    Returns:
        Path to the canonical change directory
    """
    change_id = to_change_id_for_path(file_path)
    return REPO_ROOT / "openspec" / "changes" / change_id


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


def find_duplicate_changes(changes_dir):
    """Find duplicate change directories that reference the same file.

    Args:
        changes_dir: Path to openspec/changes directory

    Returns:
        Dict mapping file paths to lists of change IDs
    """
    duplicates = {}

    for change_path in changes_dir.iterdir():
        if not change_path.is_dir():
            continue

        change_id = change_path.name

        # Read proposal to infer target file
        proposal_path = change_path / "proposal.md"
        if proposal_path.exists():
            content = proposal_path.read_text()
            target = infer_target_relpath_from_text(content)

            if target:
                if target not in duplicates:
                    duplicates[target] = []
                duplicates[target].append(change_id)

    # Filter to only actual duplicates (>1 change for same file)
    return {k: v for k, v in duplicates.items() if len(v) > 1}


def archive_change(change_path, archive_dir):
    """Archive a change directory.

    Args:
        change_path: Path to the change directory
        archive_dir: Path to the archive directory
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archived_name = f"{change_path.name}-{timestamp}"
    dest = archive_dir / archived_name

    shutil.move(str(change_path), str(dest))
    print(f"Archived: {change_path.name} -> {archived_name}")


def repair_change(change_path):
    """Repair a change directory by regenerating missing files.

    Args:
        change_path: Path to the change directory

    Returns:
        bool: True if repairs were made
    """
    change_id = change_path.name
    repaired = False

    # Check for proposal.md
    proposal_path = change_path / "proposal.md"
    if not proposal_path.exists():
        print(f"Warning: {change_id} missing proposal.md")
        return False

    # Infer target file from proposal
    content = proposal_path.read_text()
    target = infer_target_relpath_from_text(content)

    if not target:
        print(f"Warning: Cannot infer target file for {change_id}")
        return False

    # Check and repair tasks.md
    tasks_path = change_path / "tasks.md"
    if not tasks_path.exists():
        print(f"Repairing: Creating tasks.md for {change_id}")
        tasks_path.write_text(tasks_md(change_id, target), encoding="utf-8")
        repaired = True

    # Check and repair spec delta
    specs_dir = change_path / "specs" / "project-documentation"
    spec_path = specs_dir / "spec.md"
    if not spec_path.exists():
        print(f"Repairing: Creating spec.md for {change_id}")
        specs_dir.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(spec_delta_md(change_id, target), encoding="utf-8")
        repaired = True

    return repaired


def main():
    """Main entry point for repair script."""
    changes_dir = REPO_ROOT / "openspec" / "changes"
    archive_dir = changes_dir / "archive"

    if not changes_dir.exists():
        print("Error: openspec/changes directory not found")
        return 1

    # Create archive directory if needed
    archive_dir.mkdir(exist_ok=True)

    # Find and report duplicates
    duplicates = find_duplicate_changes(changes_dir)
    if duplicates:
        print("\n=== Duplicate Changes Found ===")
        for target, change_ids in duplicates.items():
            print(f"\n{target}:")
            for change_id in change_ids:
                print(f"  - {change_id}")

    # Repair all changes
    print("\n=== Repairing Changes ===")
    repair_count = 0
    for change_path in changes_dir.iterdir():
        if not change_path.is_dir() or change_path.name == "archive":
            continue

        if repair_change(change_path):
            repair_count += 1

    print("\n=== Summary ===")
    print(f"Repaired {repair_count} changes")
    print(f"Found {len(duplicates)} files with duplicate changes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
