#!/usr/bin/env python3
"""
OpenSpec Workflow - Step 0: Create TODOs

Creates the todo.md file from template with placeholders replaced
for the new change. This is the first step in the OpenSpec workflow.

Author: Obsidian AI Assistant Team
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
set_content_atomic = workflow_helpers.set_content_atomic

# Import progress indicators
try:
    import progress_indicators as progress
except ImportError:
    progress = None


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
        return False

    if not dry_run:
        try:
            # Show progress while creating file
            if progress:
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
                    return False

            write_success("Created todo.md")
            write_info(f"  Location: {todo_path}")
            write_info(f"  Change ID: {change_id}")
            write_info(f"  Owner: {owner}")
            return True

        except Exception as e:
            write_error(f"Failed to create todo.md: {e}")
            return False
    else:
        write_info(f"[DRY RUN] Would create: {todo_path}")
        write_info(f"  Template: {template_path}")
        write_info(f"  Title: {title}")
        write_info(f"  Owner: {owner}")
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
