#!/usr/bin/env python3
"""Step 11: Archive

Archives the change by moving its directory to openspec/archive/<change-id>.
Supports dry-run for preview. Will not overwrite existing archive.
"""

import importlib.util
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ARCHIVE_DIR = PROJECT_ROOT / "openspec" / "archive"

spec = importlib.util.spec_from_file_location(
    "workflow_helpers",
    SCRIPT_DIR / "workflow-helpers.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

try:
    import progress_indicators as progress
except ImportError:
    progress = None

# Import status tracking
try:
    from status_tracker import StatusTracker
except ImportError:
    StatusTracker = None

# Remove any .checkpoints directory creation or usage in step 11


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **11. Archive", "[x] **11. Archive")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step11(change_path: Path, dry_run: bool = False, **_: dict) -> bool:
    helpers.write_step(11, "Archive")

    # Initialize status tracker
    tracker = StatusTracker(change_path, "step11") if StatusTracker else None

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    target = ARCHIVE_DIR / change_path.name
    if target.exists():
        helpers.write_warning(f"Archive target already exists: {target}")
        if change_path.exists():
            helpers.write_info(
                "Removing change directory since archive already exists."
            )
            if dry_run:
                helpers.write_info(f"[DRY RUN] Would remove {change_path}")
            else:
                try:
                    shutil.rmtree(str(change_path))
                    helpers.write_success(f"Removed from active changes: {change_path}")
                except Exception as e:
                    helpers.write_error(
                        f"Failed to remove change directory: {change_path}"
                    )
                    helpers.write_error_hint(
                        str(e),
                        "Check for file locks, permissions, or open files in the directory.",
                    )
                    return False
        else:
            helpers.write_info("Change directory already removed. Archive exists.")
        _mark_complete(target)
        helpers.write_success("Step 11 completed (removal only)")
        return True

    if dry_run:
        helpers.write_info(f"[DRY RUN] Would move {change_path} -> {target}")
    else:
        try:
            if progress:
                with progress.spinner(
                    "Archiving change directory", f"Archived to: {target}"
                ):
                    # Copy the directory to archive
                    shutil.copytree(str(change_path), str(target))
                    # Remove the original change directory
                    shutil.rmtree(str(change_path))
            else:
                # Copy the directory to archive
                shutil.copytree(str(change_path), str(target))
                helpers.write_success(f"Archived to: {target}")
                # Remove the original change directory
                shutil.rmtree(str(change_path))
                helpers.write_success(f"Removed from active changes: {change_path}")
        except Exception as e:
            helpers.write_error(
                f"Failed to archive or remove change directory: {change_path}"
            )
            helpers.write_error_hint(
                str(e),
                "Check for file locks, permissions, or open files in the directory.",
            )
            return False

    _mark_complete(target if target.exists() else change_path)
    # No .checkpoints creation or management here
    helpers.write_success("Step 11 completed")

    # Show changes and validate artifacts
    if not dry_run:
        helpers.show_changes(change_path)
        helpers.validate_step_artifacts(change_path, 11)

    return True


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="OpenSpec Step 11: Archive change directory"
    )
    parser.add_argument(
        "change_path",
        type=str,
        help="Path to change directory (e.g. openspec/changes/CHANGE-ID)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview actions without making changes"
    )
    args = parser.parse_args()

    change_dir = Path(args.change_path)
    ok = invoke_step11(change_dir, dry_run=args.dry_run)
    sys.exit(0 if ok else 1)
