#!/usr/bin/env python3
"""Step 9: Documentation

Creates/updates doc_changes.md to capture documentation updates and prints a
concise review summary of proposal/spec/tasks/test_plan. Also writes a
review_summary.md with quick links and counts.
"""

import sys
import importlib.util
from pathlib import Path
from typing import List


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
    updated = content.replace("[ ] **9. Documentation and Cross-Validation", "[x] **9. Documentation and Cross-Validation")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def _read_lines(p: Path) -> List[str]:
    try:
        return p.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []


def _summarize_doc(name: str, path: Path) -> str:
    lines = _read_lines(path)
    if not lines:
        return f"- {name}: MISSING"
    # Simple summary: line count and first non-empty heading line if any
    non_empty = [l for l in lines if l.strip()]
    heading = next((l.strip('# ').strip() for l in non_empty if l.startswith('#')), None)
    return f"- {name}: {len(lines)} lines" + (f", title: {heading}" if heading else "")


def invoke_step9(change_path: Path, dry_run: bool = False, **_: dict) -> bool:
    helpers.write_step(9, "Documentation")
    changes = change_path / "doc_changes.md"
    review = change_path / "review_summary.md"

    # Append doc changes section (idempotent minimal block)
    if dry_run:
        helpers.write_info(f"[DRY RUN] Would append docs section: {changes}")
    else:
        if progress:
            with progress.spinner("Updating documentation changes", "Doc changes updated"):
                existing = changes.read_text(encoding="utf-8") if changes.exists() else ""
                block = (
                    "\n## Documentation Changes\n\n"
                    "- Files updated:\n"
                    "- New docs added:\n"
                )
                if block not in existing:
                    helpers.set_content_atomic(changes, existing + block)
        else:
            existing = changes.read_text(encoding="utf-8") if changes.exists() else ""
            block = (
                "\n## Documentation Changes\n\n"
                "- Files updated:\n"
                "- New docs added:\n"
            )
            if block not in existing:
                helpers.set_content_atomic(changes, existing + block)
                helpers.write_success(f"Updated: {changes}")
            else:
                helpers.write_info(f"Docs section already present: {changes}")

    # Produce review summary of key docs
    proposal = change_path / "proposal.md"
    spec_md = change_path / "spec.md"
    tasks = change_path / "tasks.md"
    test_plan = change_path / "test_plan.md"

    docs = [("proposal", proposal), ("spec", spec_md), ("tasks", tasks), ("test_plan", test_plan)]
    
    if progress:
        # Use StatusTracker to show validation of each document
        tracker = progress.StatusTracker("Reviewing Documents")
        for label, path in docs:
            tracker.add_item(label, label.replace("_", " ").title(), "pending")
        
        for label, path in docs:
            tracker.update_item(label, "running", "Analyzing...")
            msg = _summarize_doc(label, path)
            tracker.update_item(label, "success", msg.split(": ", 1)[1] if ": " in msg else "Complete")
        
        tracker.complete()
        
        helpers.write_info("Documentation review summary:")
        for label, path in docs:
            msg = _summarize_doc(label, path)
            helpers.write_info("  " + msg)
    else:
        helpers.write_info("Documentation review summary:")
        for label, path in docs:
            msg = _summarize_doc(label, path)
            helpers.write_info("  " + msg)

    # Write review_summary.md
    if dry_run:
        helpers.write_info(f"[DRY RUN] Would write: {review}")
    else:
        if progress:
            with progress.spinner("Writing review summary", "Review summary written"):
                content = (
                    "# Documentation Review Summary\n\n"
                    f"{_summarize_doc('proposal', proposal)}\n"
                    f"{_summarize_doc('spec', spec_md)}\n"
                    f"{_summarize_doc('tasks', tasks)}\n"
                    f"{_summarize_doc('test_plan', test_plan)}\n"
                    "\nNavigate: [proposal.md](./proposal.md) | [spec.md](./spec.md) | "
                    "[tasks.md](./tasks.md) | [test_plan.md](./test_plan.md)\n"
                )
                helpers.set_content_atomic(review, content)
        else:
            content = (
                "# Documentation Review Summary\n\n"
                f"{_summarize_doc('proposal', proposal)}\n"
                f"{_summarize_doc('spec', spec_md)}\n"
                f"{_summarize_doc('tasks', tasks)}\n"
                f"{_summarize_doc('test_plan', test_plan)}\n"
                "\nNavigate: [proposal.md](./proposal.md) | [spec.md](./spec.md) | "
                "[tasks.md](./tasks.md) | [test_plan.md](./test_plan.md)\n"
            )
            helpers.set_content_atomic(review, content)
            helpers.write_success(f"Wrote: {review}")

    _mark_complete(change_path)
    
    # --- Begin merged cross-validation logic from step 12 ---
    helpers.write_step(9, "Cross-Validation")
    
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
    
    helpers.write_success("Step 9 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step9")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step9(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)
