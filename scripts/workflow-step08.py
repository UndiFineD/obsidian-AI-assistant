#!/usr/bin/env python3
"""Step 8: Testing

Creates/updates test_results.md with a placeholder section for results.
"""

import sys
import importlib.util
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
    updated = content.replace("[ ] **8. Test", "[x] **8. Test")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step8(change_path: Path, dry_run: bool = False, **_: dict) -> bool:
    helpers.write_step(8, "Testing")
    results = change_path / "test_results.md"

    if dry_run:
        helpers.write_info(f"[DRY RUN] Would append test results section: {results}")
    else:
        if progress:
            with progress.spinner("Recording test results", "Test results recorded"):
                existing = results.read_text(encoding="utf-8") if results.exists() else ""
                block = (
                    "\n## Test Results\n\n"
                    "- Summary: \n"
                    "- Coverage: \n"
                    "- Failures: \n"
                )
                helpers.set_content_atomic(results, existing + block)
        else:
            existing = results.read_text(encoding="utf-8") if results.exists() else ""
            block = (
                "\n## Test Results\n\n"
                "- Summary: \n"
                "- Coverage: \n"
                "- Failures: \n"
            )
            helpers.set_content_atomic(results, existing + block)
            helpers.write_success(f"Updated: {results}")

    _mark_complete(change_path)
    helpers.write_success("Step 8 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step8")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step8(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)
