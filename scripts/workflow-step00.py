#!/usr/bin/env python3
"""
OpenSpec Workflow - Step 0: Create TODOs

Creates the todo.md file from template with placeholders replaced
for the new change. This is the first step in the OpenSpec workflow.

Author: Obsidian AI Agent Team
License: MIT
"""

import sys
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import with underscore since Python doesn't like hyphens in module names
import importlib.util

spec = importlib.util.spec_from_file_location(
    "workflow_helpers", Path(__file__).parent / "workflow-helpers.py"
)
workflow_helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow_helpers)

write_step = workflow_helpers.write_step
write_info = workflow_helpers.write_info
write_success = workflow_helpers.write_success
write_error = workflow_helpers.write_error
write_error_hint = workflow_helpers.write_error_hint
write_warning = workflow_helpers.write_warning
set_content_atomic = workflow_helpers.set_content_atomic

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

# Import document validator
try:
    DocumentValidator = workflow_helpers.DocumentValidator
    DOCUMENT_VALIDATOR_AVAILABLE = True
except AttributeError:
    DOCUMENT_VALIDATOR_AVAILABLE = False
    DocumentValidator = None


def invoke_step0(
    change_path: Path, title: str, owner: str, dry_run: bool = False
) -> bool:
    """
    Create todo.md checklist for the change.

    Args:
        change_path: Full path to the change directory
        title: Human-readable title of the change
        owner: GitHub handle of the change owner (e.g., @username)
        dry_run: If True, preview actions without making changes

    Returns:
        True if successful, False otherwise
    """
    write_step(0, "Create TODOs")

    # Initialize status tracker if available
    status_tracker = None
    if STATUS_TRACKER_AVAILABLE:
        try:
            status_tracker = create_tracker(
                change_path.name,
                lane="standard",  # Default lane for step 0
                status_file=change_path / ".checkpoints" / "status.json",
            )
            status_tracker.start_stage(0, "Create TODOs")
        except Exception as e:
            write_warning(f"Could not initialize status tracker: {e}")

    # Log environment validation
    write_info("Validating environment and workspace structure")
    write_info(f"  Change path: {change_path}")
    write_info(f"  Title: {title}")
    write_info(f"  Owner: {owner}")
    write_info(f"  Dry run: {dry_run}")

    todo_path = change_path / "todo.md"
    # Calculate template path: go up from change_path to project root, then to templates
    # change_path is like: project_root/openspec/changes/change-id
    project_root = change_path.parent.parent.parent
    template_path = project_root / "openspec" / "templates" / "todo.md"

    # Validate template exists
    if not template_path.exists():
        write_error_hint(
            f"Template not found: {template_path}",
            "Ensure you're running from the project root so openspec/templates/todo.md resolves.",
        )
        write_info(f"Expected location: {template_path}")
        if status_tracker:
            status_tracker.complete_stage(0, success=False, metrics={"reason": "Template not found"})
        return False

    # Use DocumentValidator if available
    if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator:
        try:
            validator = DocumentValidator()
            # Validate that we can create the todo file
            if not validator.validate_file_creation(change_path, "todo.md"):
                write_error("Document validation failed for todo.md creation")
                if status_tracker:
                    status_tracker.complete_stage(0, success=False, metrics={"reason": "Document validation failed"})
                return False
        except Exception as e:
            write_warning(f"Document validation error: {e}")

    # Detect next step
    try:
        next_step = workflow_helpers.detect_next_step(change_path)
        write_info(f"Next workflow phase: Step {next_step}")
    except Exception as e:
        write_warning(f"Could not detect next step: {e}")

    if not dry_run:
        try:
            # Show progress while creating file
            if progress and hasattr(progress, 'spinner'):
                with progress.spinner(
                    "Creating todo.md from template", "Todo file created"
                ):
                    # Load template and replace placeholders
                    content = template_path.read_text(encoding="utf-8")
                    change_id = change_path.name

                    # Replace placeholders
                    content = content.replace("<Change Title>", title)
                    content = content.replace("<change-id>", change_id)
                    content = content.replace("@username", owner)
                    content = content.replace(
                        "YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d")
                    )

                    # Mark Step 0 as complete
                    content = content.replace(
                        "[ ] **0. Create TODOs**", "[x] **0. Create TODOs**"
                    )

                    # Write to file
                    if not set_content_atomic(todo_path, content):
                        if status_tracker:
                            status_tracker.complete_stage(0, success=False, metrics={"reason": "Failed to write file"})
                        return False
            else:
                # No progress available - run directly
                content = template_path.read_text(encoding="utf-8")
                change_id = change_path.name

                content = content.replace("<Change Title>", title)
                content = content.replace("<change-id>", change_id)
                content = content.replace("@username", owner)
                content = content.replace(
                    "YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d")
                )
                content = content.replace(
                    "[ ] **0. Create TODOs**", "[x] **0. Create TODOs**"
                )

                if not set_content_atomic(todo_path, content):
                    if status_tracker:
                        status_tracker.complete_stage(0, success=False, metrics={"reason": "Failed to write file"})
                    return False

            # Write status.json in WorkflowStatusTracker format
            status_data = {
                "workflow_version": "0.1.41",
                "last_updated": datetime.now().isoformat(),
                "total_steps": 1,  # Only step 0 completed so far
                "completed_steps": 1,
                "steps": [
                    {
                        "step_id": 0,
                        "step_name": "Create TODOs",
                        "start_time": datetime.now().isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "result": "success",
                        "duration_seconds": 0.0,
                        "metrics": {},
                        "errors": [],
                        "files_created": ["todo.md"],
                        "files_modified": []
                    }
                ]
            }
            
            status_file = change_path / "status.json"
            import json
            if not set_content_atomic(status_file, json.dumps(status_data, indent=2)):
                write_warning("Failed to write status.json")
            else:
                write_success("Created status.json")

            # Validate step artifacts
            if not workflow_helpers.validate_step_artifacts(change_path, 0):
                write_error("Step 0 artifact validation failed")
                if status_tracker:
                    status_tracker.complete_stage(0, success=False, metrics={"reason": "Artifact validation failed"})
                return False

            # Show changes if available
            try:
                changes_dir = change_path.parent
                workflow_helpers.show_changes(changes_dir)
            except Exception as e:
                write_warning(f"Could not show changes: {e}")

            write_success("Created todo.md")
            write_info(f"  Location: {todo_path}")
            write_info(f"  Change ID: {change_id}")
            write_info(f"  Owner: {owner}")

            # Record completion in status tracker
            if status_tracker:
                status_tracker.complete_stage(0, success=True)

            return True

        except Exception as e:
            write_error(f"Failed to create todo.md: {e}")
            if status_tracker:
                status_tracker.complete_stage(0, success=False, metrics={"error": str(e)})
            return False
    else:
        write_info(f"[DRY RUN] Would create: {todo_path}")
        write_info(f"  Template: {template_path}")
        write_info(f"  Title: {title}")
        write_info(f"  Owner: {owner}")

        # Record dry run completion in status tracker
        if status_tracker:
            status_tracker.complete_stage(0, success=True, metrics={"dry_run": True})

        return True


if __name__ == "__main__":
    # Test the step function
    import sys
    from pathlib import Path

    test_change_path = Path("openspec/changes/test-change")
    test_change_path.mkdir(parents=True, exist_ok=True)

    success = invoke_step0(
        change_path=test_change_path,
        title="Test Change",
        owner="@test-user",
        dry_run=True,
    )

    sys.exit(0 if success else 1)
