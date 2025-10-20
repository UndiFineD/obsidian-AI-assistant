#!/usr/bin/env python3
"""Step 11: Archive

Archives the change by moving its directory to openspec/archive/<change-id>.
Supports dry-run for preview. Will not overwrite existing archive.
"""

import sys
import shutil
import importlib.util
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

# Import progress indicators
try:
    import progress_indicators as progress
except ImportError:
    progress = None


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
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    target = ARCHIVE_DIR / change_path.name
    if target.exists():
        helpers.write_warning(f"Archive target already exists: {target}")
        if change_path.exists():
            helpers.write_info(f"Removing change directory since archive already exists.")
            if dry_run:
                helpers.write_info(f"[DRY RUN] Would remove {change_path}")
            else:
                shutil.rmtree(str(change_path))
                helpers.write_success(f"Removed from active changes: {change_path}")
        else:
            helpers.write_info("Change directory already removed. Archive exists.")
        _mark_complete(target)
        helpers.write_success("Step 11 completed (removal only)")
        return True

    if dry_run:
        helpers.write_info(f"[DRY RUN] Would move {change_path} -> {target}")
    else:
        if progress:
            with progress.spinner("Archiving change directory", f"Archived to: {target}"):
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

    _mark_complete(target if target.exists() else change_path)
    helpers.write_success("Step 11 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step11")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step11(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)
