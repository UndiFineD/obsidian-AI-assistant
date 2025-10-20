#!/usr/bin/env python3
"""Step 7: Implementation

Creates/updates implementation_notes.md to capture implementation details.
"""

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

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
    updated = content.replace("[ ] **7. Implementation", "[x] **7. Implementation")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step7(change_path: Path, dry_run: bool = False, **_: dict) -> bool:
    helpers.write_step(7, "Implementation")
    notes = change_path / "implementation_notes.md"

    if dry_run:
        helpers.write_info(f"[DRY RUN] Would append implementation section: {notes}")
    else:
        if progress:
            with progress.spinner("Updating implementation notes", "Notes updated"):
                existing = notes.read_text(encoding="utf-8") if notes.exists() else ""
                block = (
                    "\n## Implementation Details\n\n"
                    "- Modules changed:\n"
                    "- Rationale:\n"
                    "- Alternatives considered:\n"
                )
                helpers.set_content_atomic(notes, existing + block)
        else:
            existing = notes.read_text(encoding="utf-8") if notes.exists() else ""
            block = (
                "\n## Implementation Details\n\n"
                "- Modules changed:\n"
                "- Rationale:\n"
                "- Alternatives considered:\n"
            )
            helpers.set_content_atomic(notes, existing + block)
            helpers.write_success(f"Updated: {notes}")

    _mark_complete(change_path)
    helpers.write_success("Step 7 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step7")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step7(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)
