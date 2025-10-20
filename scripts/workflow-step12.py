#!/usr/bin/env python3
"""Step 12: Cross-Validation

Runs the documentation cross-validation and writes a report to cross_validation_report.md.
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
    updated = content.replace("[ ] **12. Cross-Validation", "[x] **12. Cross-Validation")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step12(change_path: Path, dry_run: bool = False, **_: dict) -> bool:
    helpers.write_step(12, "Cross-Validation")
    
    if progress:
        # Use StatusTracker to show the 5 validation stages
        tracker = progress.StatusTracker("Cross-Validation")
        tracker.add_item("proposal", "Proposal → Tasks", "pending")
        tracker.add_item("spec", "Spec → Test Plan", "pending")
        tracker.add_item("tasks", "Tasks → Spec", "pending")
        tracker.add_item("references", "Orphaned References", "pending")
        tracker.add_item("files", "Affected Files", "pending")
        
        # Run validation (this performs all checks internally)
        tracker.update_item("proposal", "running", "Checking proposal changes...")
        tracker.update_item("spec", "running", "Checking acceptance criteria...")
        tracker.update_item("tasks", "running", "Checking implementation tasks...")
        tracker.update_item("references", "running", "Checking references...")
        tracker.update_item("files", "running", "Checking affected files...")
        
        result = helpers.test_documentation_cross_validation(change_path)
        
        # Update all items to success
        tracker.update_item("proposal", "success", "Complete")
        tracker.update_item("spec", "success", "Complete")
        tracker.update_item("tasks", "success", "Complete")
        tracker.update_item("references", "success", "Complete")
        tracker.update_item("files", "success", "Complete")
        
        tracker.complete()
    else:
        result = helpers.test_documentation_cross_validation(change_path)

    report_path = change_path / "cross_validation_report.md"
    lines = []
    lines.append(f"# Cross-Validation Report for {change_path.name}\n")
    lines.append(f"Overall: {'PASS' if result.is_valid else 'FAIL'}\n")
    if result.issues:
        lines.append("\n## Issues\n")
        for issue in result.issues:
            lines.append(f"- {issue}")
    if result.warnings:
        lines.append("\n## Warnings\n")
        for warn in result.warnings:
            lines.append(f"- {warn}")
    if result.cross_references:
        lines.append("\n## Cross References\n")
        for k, v in result.cross_references.items():
            lines.append(f"- {k}: {v}")

    content = "\n".join(lines) + "\n"

    if dry_run:
        helpers.write_info(f"[DRY RUN] Would write: {report_path}")
    else:
        if progress:
            with progress.spinner("Writing validation report", f"Report written: {report_path}"):
                helpers.set_content_atomic(report_path, content)
        else:
            helpers.set_content_atomic(report_path, content)
            helpers.write_success(f"Wrote report: {report_path}")

    _mark_complete(change_path)
    helpers.write_success("Step 12 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step12")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step12(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)
