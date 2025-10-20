#!/usr/bin/env python3
"""Step 5: Test Definition

Ensures test_plan.md exists with mapping to acceptance criteria.
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


SCAFFOLD = """# Test Plan

## Strategy

Describe the test approach.

## Mapping to Acceptance Criteria

- AC-1: Covered by tests: ...
- AC-2: Covered by tests: ...

## Test Cases

1. [ ] Test Case 1
2. [ ] Test Case 2
"""


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **5. Test Definition", "[x] **5. Test Definition")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step5(
    change_path: Path, title: str | None = None, dry_run: bool = False, **_: dict
) -> bool:
    helpers.write_step(5, "Test Definition")
    test_plan = change_path / "test_plan.md"
    spec_md = change_path / "spec.md"
    tasks_md = change_path / "tasks.md"

    if test_plan.exists():
        helpers.write_info("test_plan.md already exists; leaving as-is")
    else:
        if progress:
            with progress.spinner("Generating test_plan.md", "Test plan generated"):
                generator = helpers.DocumentGenerator()
                content = generator.generate_test_plan(spec_md, tasks_md, title)
                if not dry_run:
                    helpers.set_content_atomic(test_plan, content)
        else:
            generator = helpers.DocumentGenerator()
            content = generator.generate_test_plan(spec_md, tasks_md, title)
            if not dry_run:
                helpers.set_content_atomic(test_plan, content)
                helpers.write_success(f"Created test_plan from spec/tasks: {test_plan}")

        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create: {test_plan}")

    # Validate (skip in dry-run)
    if dry_run:
        helpers.write_info("[DRY RUN] Skipping test plan validation")
    else:
        if progress:
            with progress.spinner("Validating test_plan.md", "Validation complete"):
                validator = helpers.DocumentValidator()
                result = validator.validate_test_plan(test_plan)
        else:
            validator = helpers.DocumentValidator()
            result = validator.validate_test_plan(test_plan)

        if not result.is_valid:
            for err in result.errors:
                helpers.write_error(f"  ✗ {err}")
            helpers.write_warning("Test Plan has blocking issues; fix and rerun step 5")
            return False
        if result.warnings or result.suggestions:
            if result.warnings:
                helpers.write_warning(
                    f"Test Plan has {len(result.warnings)} warning(s)"
                )
            if result.suggestions:
                helpers.write_info(f"Suggestions ({len(result.suggestions)}):")
                for s in result.suggestions[:3]:
                    helpers.write_info(f"  • {s}")

    _mark_complete(change_path)
    helpers.write_success("Step 5 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step5")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step5(test_dir, title="Test Plan", dry_run=True)
    sys.exit(0 if ok else 1)
