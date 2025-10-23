#!/usr/bin/env python3
"""Step 7: Implementation

Executes generated implementation scripts and test scripts:
1. Runs test.py to validate the change
2. Runs implement.py to execute implementation tasks
3. Creates/updates implementation_notes.md to capture implementation details.
"""

import importlib.util
import subprocess
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


def _execute_script(script_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Execute a generated script and return (success, output)."""
    if not script_path.exists():
        return False, f"Script not found: {script_path}"

    if dry_run:
        return True, f"[DRY RUN] Would execute: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output
    except subprocess.TimeoutExpired:
        return False, f"Script execution timed out: {script_path}"
    except Exception as e:
        return False, f"Error executing script: {e}"


def invoke_step7(change_path: Path, dry_run: bool = False, **_: dict) -> bool:
    helpers.write_step(7, "Implementation")
    notes = change_path / "implementation_notes.md"
    test_script = change_path / "test.py"
    implement_script = change_path / "implement.py"

    # Step 1: Execute test.py if it exists
    helpers.write_info("Step 7.1: Running test script...")
    test_success = True
    test_output = ""

    if test_script.exists():
        if progress:
            with progress.spinner("Running tests", "Tests completed"):
                test_success, test_output = _execute_script(test_script, dry_run)
        else:
            test_success, test_output = _execute_script(test_script, dry_run)
            if not dry_run:
                helpers.write_info(f"Test output:\n{test_output}")

        if test_success or dry_run:
            helpers.write_success(f"✓ Test script executed: {test_script}")
        else:
            helpers.write_warning(f"⚠ Test script failed with output:\n{test_output}")
    else:
        helpers.write_info(f"ℹ No test.py found at {test_script}")

    # Step 2: Execute implement.py if it exists (with --what-if first)
    helpers.write_info("Step 7.2: Running implementation script...")
    implement_success = True
    implement_output = ""

    if implement_script.exists():
        # First run with --what-if to preview
        if not dry_run:
            if progress:
                with progress.spinner("Previewing implementation", "Preview completed"):
                    impl_preview_success, impl_preview_output = _execute_script(
                        implement_script, dry_run=False
                    )
            else:
                impl_preview_success, impl_preview_output = _execute_script(
                    implement_script, dry_run=False
                )
                helpers.write_info(f"Implementation preview:\n{impl_preview_output}")

        # Then run actual implementation
        if progress:
            with progress.spinner(
                "Executing implementation", "Implementation completed"
            ):
                implement_success, implement_output = _execute_script(
                    implement_script, dry_run
                )
        else:
            implement_success, implement_output = _execute_script(
                implement_script, dry_run
            )
            if not dry_run:
                helpers.write_info(f"Implementation output:\n{implement_output}")

        if implement_success or dry_run:
            helpers.write_success(
                f"✓ Implementation script executed: {implement_script}"
            )
        else:
            helpers.write_warning(
                f"⚠ Implementation script failed with output:\n{implement_output}"
            )
    else:
        helpers.write_info(f"ℹ No implement.py found at {implement_script}")

    # Step 3: Update implementation notes with results
    helpers.write_info("Step 7.3: Updating implementation notes...")
    if not dry_run:
        if progress:
            with progress.spinner("Updating implementation notes", "Notes updated"):
                existing = notes.read_text(encoding="utf-8") if notes.exists() else ""
                block = (
                    "\n## Implementation Details\n\n"
                    "- Modules changed:\n"
                    "- Rationale:\n"
                    "- Alternatives considered:\n"
                    "\n## Script Execution Results\n\n"
                    f"- Test script: {'PASSED' if test_success else 'FAILED'}\n"
                    f"- Implementation script: {'PASSED' if implement_success else 'FAILED'}\n"
                )
                if test_output:
                    block += f"\n### Test Output\n```\n{test_output[:500]}\n```\n"
                if implement_output:
                    block += f"\n### Implementation Output\n```\n{implement_output[:500]}\n```\n"

                helpers.set_content_atomic(notes, existing + block)
        else:
            existing = notes.read_text(encoding="utf-8") if notes.exists() else ""
            block = (
                "\n## Implementation Details\n\n"
                "- Modules changed:\n"
                "- Rationale:\n"
                "- Alternatives considered:\n"
                "\n## Script Execution Results\n\n"
                f"- Test script: {'PASSED' if test_success else 'FAILED'}\n"
                f"- Implementation script: {'PASSED' if implement_success else 'FAILED'}\n"
            )
            if test_output:
                block += f"\n### Test Output\n```\n{test_output[:500]}\n```\n"
            if implement_output:
                block += (
                    f"\n### Implementation Output\n```\n{implement_output[:500]}\n```\n"
                )

            helpers.set_content_atomic(notes, existing + block)
            helpers.write_success(f"Updated: {notes}")
    else:
        helpers.write_info("[DRY RUN] Would update implementation notes")

    _mark_complete(change_path)
    helpers.write_success("Step 7 completed")
    return test_success and implement_success


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step7")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step7(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)
