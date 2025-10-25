#!/usr/bin/env python3
"""Step 5: Specification Definition

Generates comprehensive spec.md from template or by analyzing
proposal.md and tasks.md. Requests Copilot assistance to improve
specifications based on supporting documents.
"""

import importlib.util
import re
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


def _extract_success_criteria(proposal_path: Path) -> list:
    """Extract success criteria from proposal.md.

    Returns:
        List of success criteria strings
    """
    if not proposal_path.exists():
        return []

    content = proposal_path.read_text(encoding="utf-8")

    # Find success criteria section
    criteria_match = re.search(
        r"## 🎓 Success Criteria\s*\n([\s\S]*?)(?=\n---|\n##|\Z)", content
    )
    if not criteria_match:
        return []

    criteria_section = criteria_match.group(1)

    # Extract individual criteria (looking for checkboxes)
    criteria = re.findall(r"- \[\s*\]\s*(.+?)(?=\n|$)", criteria_section)
    return [c.strip() for c in criteria if c.strip()]


def _extract_file_lists(proposal_path: Path) -> dict:
    """Extract KEEP/MOVE/DELETE file lists from proposal.md.

    Returns:
        Dictionary with 'keep', 'move', and 'delete' keys
    """
    if not proposal_path.exists():
        return {"keep": [], "move": [], "delete": []}

    content = proposal_path.read_text(encoding="utf-8")

    # Find categorization details
    categ_match = re.search(
        r"### Categorization Details([\s\S]*?)(?=\n---|\n##|\Z)", content
    )

    result = {"keep": [], "move": [], "delete": []}

    if not categ_match:
        return result

    categ_section = categ_match.group(1)

    # Extract KEEP section
    keep_match = re.search(
        r"\*\*A\. KEEP IN ROOT\*\*.*?\n([\s\S]*?)(?=\*\*B\.|$)", categ_section
    )
    if keep_match:
        keep_files = re.findall(
            r"^- (.+?)(?:\s*-|$)", keep_match.group(1), re.MULTILINE
        )
        result["keep"].extend([f.strip() for f in keep_files if f.strip()])

    # Extract MOVE section
    move_match = re.search(
        r"\*\*B\. MOVE TO docs/\*\*.*?\n([\s\S]*?)(?=\*\*C\.|$)", categ_section
    )
    if move_match:
        move_files = re.findall(r"←\s*(.+?)(?:,|$)", move_match.group(1))
        result["move"].extend([f.strip() for f in move_files if f.strip()])

    # Extract DELETE section
    delete_match = re.search(
        r"\*\*C\. DELETE\*\*.*?\n```\n([\s\S]*?)\n```", categ_section
    )
    if delete_match:
        delete_files = delete_match.group(1).strip().split("\n")
        result["delete"].extend([f.strip() for f in delete_files if f.strip()])

    return result


def _extract_phases(proposal_path: Path) -> list:
    """Extract implementation phases from proposal.md.

    Returns:
        List of phase descriptions
    """
    if not proposal_path.exists():
        return []

    content = proposal_path.read_text(encoding="utf-8")

    # Find scope section with phases
    scope_match = re.search(
        r"## 🎯 Scope of Changes\s*\n### Five Implementation Phases\s*\n([\s\S]*?)(?=\n---|\n##|\Z)",
        content,
    )
    if not scope_match:
        return []

    scope_section = scope_match.group(1)

    # Extract phases
    phases = re.findall(
        r"#### Phase \d+: (.+?)\n(.+?)(?=#### Phase|\Z)", scope_section, re.DOTALL
    )

    return [{"title": p[0].strip(), "description": p[1].strip()} for p in phases]


def _generate_spec_md(proposal_path: Path, tasks_path: Path) -> str:
    """Generate comprehensive spec.md with acceptance criteria.

    Returns:
        Complete spec.md content
    """
    criteria = _extract_success_criteria(proposal_path)
    phases = _extract_phases(proposal_path)
    file_lists = _extract_file_lists(proposal_path)

    # Start spec
    spec_content = "# Specification\n\n"
    spec_content += "## Overview\n\n"
    spec_content += "This specification documents the acceptance criteria and requirements for the change.\n\n"

    # Acceptance Criteria
    spec_content += "## Acceptance Criteria\n\n"
    if criteria:
        for i, c in enumerate(criteria, 1):
            spec_content += f"- **AC-{i}**: {c}\n"
    else:
        spec_content += "- **AC-1**: Documentation is properly organized\n"
        spec_content += "- **AC-2**: All requirements are met\n"

    spec_content += "\n"

    # Requirements from file operations
    spec_content += "## Implementation Requirements\n\n"
    spec_content += "### Directory Structure\n"
    spec_content += "- Create `docs/` directory with subdirectories:\n"
    spec_content += "  - docs/getting-started/\n"
    spec_content += "  - docs/guides/\n"
    spec_content += "  - docs/architecture/\n"
    spec_content += "  - docs/reference/\n"
    spec_content += "  - docs/production/\n"
    spec_content += "  - docs/historical/\n"
    spec_content += "- Create docs/README.md with navigation\n\n"

    spec_content += "### File Operations\n"
    if file_lists["keep"]:
        spec_content += f"- **Keep in root**: {len(file_lists['keep'])} files\n"
    if file_lists["move"]:
        spec_content += f"- **Move to docs/**: {len(file_lists['move'])} files\n"
    if file_lists["delete"]:
        spec_content += f"- **Delete**: {len(file_lists['delete'])} files\n"
    spec_content += "\n"

    spec_content += "### Documentation Updates\n"
    spec_content += "- Update README.md with docs/ navigation\n"
    spec_content += "- Update all internal links\n"
    spec_content += "- Validate no broken links\n"
    spec_content += "- Update CHANGELOG.md to document cleanup\n"
    spec_content += "- Update Contributing guidelines with new structure\n\n"

    # Implementation Phases
    if phases:
        spec_content += "## Implementation Phases\n\n"
        for i, phase in enumerate(phases, 1):
            spec_content += f"### Phase {i}: {phase['title']}\n\n"
            spec_content += phase["description"] + "\n\n"

    return spec_content


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

    # Initialize status tracker if available
    status_tracker = None
    if STATUS_TRACKER_AVAILABLE:
        try:
            status_tracker = create_tracker(
                change_path.name,
                lane="standard",  # Default lane for step 5
                status_file=change_path / ".checkpoints" / "status.json",
            )
            status_tracker.start_stage(5, "Implementation Checklist")
        except Exception as e:
            helpers.write_warning(f"Could not initialize status tracker: {e}")

    spec_path = change_path / "spec.md"
    proposal_path = change_path / "proposal.md"
    tasks_path = change_path / "tasks.md"
    todo_path = change_path / "todo.md"
    templates_dir = change_path.parent.parent / "templates"

    # Check if spec.md exists, if not copy from templates or generate
    if not spec_path.exists() or spec_path.stat().st_size < 100:
        template_spec_path = templates_dir / "spec.md"

        if template_spec_path.exists():
            # Copy template to spec.md
            if not dry_run:
                spec_content = template_spec_path.read_text(encoding="utf-8")
                helpers.set_content_atomic(spec_path, spec_content)
                helpers.write_success(f"Copied spec.md template: {spec_path}")

                # Ask Copilot to improve spec.md based on supporting documents
                helpers.write_info("---")
                helpers.write_info(
                    "📝 Requesting Copilot assistance to improve spec.md..."
                )
                helpers.write_info("Copilot will enhance spec.md based on:")
                helpers.write_info(f"  • proposal.md: {proposal_path}")
                helpers.write_info(f"  • tasks.md: {tasks_path}")
                helpers.write_info(f"  • todo.md: {todo_path}")
                helpers.write_info("")
                helpers.write_info("Use @copilot in your editor to:")
                helpers.write_info("  1. Review the spec.md template structure")
                helpers.write_info(
                    "  2. Extract key information from proposal.md, tasks.md, and todo.md"
                )
                helpers.write_info(
                    "  3. Fill in the relevant sections with accurate project details"
                )
                helpers.write_info(
                    "  4. Ensure specifications are clear, complete, and testable"
                )
                helpers.write_info("  5. Add any missing non-functional requirements")
                helpers.write_info("---")
            else:
                helpers.write_info(
                    f"[DRY RUN] Would copy template: {template_spec_path} → {spec_path}"
                )
        else:
            # No template found, generate from proposal
            if progress and hasattr(progress, 'spinner'):
                with progress.spinner(
                    "Generating spec.md from proposal", "Spec generated"
                ):
                    content = _generate_spec_md(proposal_path, tasks_path)
                    if not dry_run:
                        helpers.set_content_atomic(spec_path, content)
            else:
                content = _generate_spec_md(proposal_path, tasks_path)
                if not dry_run:
                    helpers.set_content_atomic(spec_path, content)
                    helpers.write_success(
                        f"Generated comprehensive spec.md: {spec_path}"
                    )

            if dry_run:
                helpers.write_info(f"[DRY RUN] Would create/update: {spec_path}")

    # Validate step artifacts
    if not dry_run and not helpers.validate_step_artifacts(change_path, 5):
        helpers.write_error("Step 5 artifact validation failed")
        if status_tracker:
            status_tracker.complete_stage(5, success=False, metrics={"reason": "Artifact validation failed"})
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
        status_tracker.complete_stage(5, success=True)

    helpers.write_success("Step 5 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step5")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step5(test_dir, title="Test Plan", dry_run=True)
    sys.exit(0 if ok else 1)
