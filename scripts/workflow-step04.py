#!/usr/bin/env python3
"""Step 4: Task Breakdown

Ensures tasks.md exists listing tasks mapped to requirements.
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


SCAFFOLD = """# Task Breakdown

## Tasks

- [ ] T-001: Describe task 1 (maps to Requirement 1)
- [ ] T-002: Describe task 2 (maps to Requirement 2)

## Dependencies

- ...
"""


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **4. Task Breakdown", "[x] **4. Task Breakdown")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step4(
    change_path: Path, title: str | None = None, dry_run: bool = False, **_: dict
) -> bool:
    helpers.write_step(4, "Task Breakdown")
    tasks = change_path / "tasks.md"
    spec_md = change_path / "spec.md"

    if tasks.exists():
        helpers.write_info("tasks.md already exists; leaving as-is")
    else:
        if progress:
            with progress.spinner("Generating tasks.md from spec", "Tasks generated"):
                generator = helpers.DocumentGenerator()
                content = generator.generate_tasks_from_spec(spec_md, title)
                if not dry_run:
                    helpers.set_content_atomic(tasks, content)
        else:
            generator = helpers.DocumentGenerator()
            content = generator.generate_tasks_from_spec(spec_md, title)
            if not dry_run:
                helpers.set_content_atomic(tasks, content)
                helpers.write_success(f"Created tasks from spec: {tasks}")

        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create: {tasks}")

    # Validate (skip in dry-run)
    if dry_run:
        helpers.write_info("[DRY RUN] Skipping tasks validation")
    else:
        if progress:
            with progress.spinner("Validating tasks.md", "Validation complete"):
                validator = helpers.DocumentValidator()
                result = validator.validate_tasks(tasks)
        else:
            validator = helpers.DocumentValidator()
            result = validator.validate_tasks(tasks)

        if not result.is_valid:
            for err in result.errors:
                helpers.write_error(f"  ✗ {err}")
            helpers.write_warning("Tasks have blocking issues; fix and rerun step 4")
            return False
        if result.warnings or result.suggestions:
            if result.warnings:
                helpers.write_warning(f"Tasks have {len(result.warnings)} warning(s):")
                for w in result.warnings[:3]:
                    helpers.write_warning(f"  ⚠ {w}")
            if result.suggestions:
                helpers.write_info(f"Suggestions ({len(result.suggestions)}):")
                for s in result.suggestions[:3]:
                    helpers.write_info(f"  • {s}")

    _mark_complete(change_path)
    helpers.write_success("Step 4 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step4")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step4(test_dir, title="Test Tasks", dry_run=True)
    sys.exit(0 if ok else 1)
