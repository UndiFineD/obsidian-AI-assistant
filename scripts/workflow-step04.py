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

# Import status tracker
try:
    from status_tracker import StatusTracker, create_tracker
    STATUS_TRACKER_AVAILABLE = True
except ImportError:
    STATUS_TRACKER_AVAILABLE = False
    StatusTracker = None
    create_tracker = None

# Import document generator and validator
try:
    DocumentGenerator = helpers.DocumentGenerator
    DocumentValidator = helpers.DocumentValidator
    DOCUMENT_GENERATOR_AVAILABLE = True
    DOCUMENT_VALIDATOR_AVAILABLE = True
except AttributeError:
    DOCUMENT_GENERATOR_AVAILABLE = False
    DOCUMENT_VALIDATOR_AVAILABLE = False
    DocumentGenerator = None
    DocumentValidator = None


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

    # Initialize status tracker if available
    status_tracker = None
    if STATUS_TRACKER_AVAILABLE:
        try:
            status_tracker = create_tracker(
                change_path.name,
                lane="standard",  # Default lane for step 4
                status_file=change_path / ".checkpoints" / "status.json",
            )
            status_tracker.start_stage(4, "Task Breakdown")
        except Exception as e:
            helpers.write_warning(f"Could not initialize status tracker: {e}")

    tasks = change_path / "tasks.md"
    spec_md = change_path / "spec.md"

    # Use DocumentValidator if available for file creation check
    if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator and not tasks.exists():
        try:
            validator = DocumentValidator()
            if not validator.validate_file_creation(change_path, "tasks.md"):
                helpers.write_error("Document validation failed for tasks.md creation")
                if status_tracker:
                    status_tracker.complete_stage(4, success=False, metrics={"reason": "Document validation failed"})
                return False
        except Exception as e:
            helpers.write_warning(f"Document validation error: {e}")

    if tasks.exists():
        helpers.write_info("tasks.md already exists; leaving as-is")
    else:
        if DOCUMENT_GENERATOR_AVAILABLE and DocumentGenerator:
            if progress and hasattr(progress, 'spinner'):
                with progress.spinner("Generating tasks.md from spec", "Tasks generated"):
                    generator = DocumentGenerator()
                    content = generator.generate_tasks_from_spec(spec_md, title)
                    if not dry_run:
                        helpers.set_content_atomic(tasks, content)
            else:
                generator = DocumentGenerator()
                content = generator.generate_tasks_from_spec(spec_md, title)
                if not dry_run:
                    helpers.set_content_atomic(tasks, content)
                    helpers.write_success(f"Created tasks from spec: {tasks}")
        else:
            # Fallback to scaffold
            content = SCAFFOLD
            if not dry_run:
                helpers.set_content_atomic(tasks, content)
                helpers.write_success(f"Created tasks scaffold: {tasks}")

        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create: {tasks}")

    # Validate (skip in dry-run)
    if dry_run:
        helpers.write_info("[DRY RUN] Skipping tasks validation")
    else:
        if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator:
            if progress and hasattr(progress, 'spinner'):
                with progress.spinner("Validating tasks.md", "Validation complete"):
                    validator = DocumentValidator()
                    result = validator.validate_tasks(tasks)
            else:
                validator = DocumentValidator()
                result = validator.validate_tasks(tasks)
        else:
            # Fallback validation
            result = type('Result', (), {'is_valid': True, 'errors': [], 'warnings': [], 'suggestions': []})()

        if not result.is_valid:
            for err in result.errors:
                helpers.write_error(f"  ✗ {err}")
            helpers.write_warning("Tasks have blocking issues; fix and rerun step 4")
            if status_tracker:
                status_tracker.complete_stage(4, success=False, metrics={"reason": "Validation failed"})
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

    # Validate step artifacts
    if not dry_run and not helpers.validate_step_artifacts(change_path, 4):
        helpers.write_error("Step 4 artifact validation failed")
        if status_tracker:
            status_tracker.complete_stage(4, success=False, metrics={"reason": "Artifact validation failed"})
        return False

    # Show changes if available
    if not dry_run:
        try:
            changes_dir = change_path.parent
            helpers.show_changes(changes_dir)
        except Exception as e:
            helpers.write_warning(f"Could not show changes: {e}")

    _mark_complete(change_path)

    # Record completion in status tracker
    if status_tracker:
        status_tracker.complete_stage(4, success=True)

    helpers.write_success("Step 4 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step4")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step4(test_dir, title="Test Tasks", dry_run=True)
    sys.exit(0 if ok else 1)
