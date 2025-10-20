#!/usr/bin/env python3
"""Step 2: Proposal

Ensures proposal.md exists. If missing, creates a minimal scaffold with
sections. Does not overwrite existing content.
"""

import sys
import importlib.util
from datetime import datetime
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
    updated = content.replace("[ ] **2. Proposal", "[x] **2. Proposal")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step2(change_path: Path, title: str | None = None, template: str = "default", dry_run: bool = False, **_: dict) -> bool:
    """
    Create and validate proposal.md.
    
    Args:
        change_path: Path to change directory
        title: Optional title for the proposal
        template: Template type (feature, bugfix, docs, refactor, default)
        dry_run: If True, don't write files
    """
    helpers.write_step(2, "Proposal")
    proposal = change_path / "proposal.md"

    # Step 2a: Check/Create proposal.md
    if proposal.exists():
        helpers.write_info("proposal.md already exists; leaving as-is")
    else:
        # Load template
        template_manager = helpers.TemplateManager()
        
        if template != "default":
            helpers.write_info(f"Using '{template}' template: {template_manager.describe_template(template)}")
        
        if progress:
            with progress.spinner("Creating proposal.md from template", "Proposal created from template"):
                content = template_manager.load_template(template, title)
                if not dry_run:
                    helpers.set_content_atomic(proposal, content)
        else:
            content = template_manager.load_template(template, title)
            if not dry_run:
                helpers.set_content_atomic(proposal, content)
                helpers.write_success(f"Created from template: {proposal}")
        
        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create: {proposal}")

    # Step 2b: Validate proposal quality
    if dry_run:
        helpers.write_info("[DRY RUN] Skipping proposal validation")
    else:
        if progress:
            with progress.spinner("Validating proposal.md", "Validation complete"):
                validator = helpers.DocumentValidator()
                result = validator.validate_proposal(proposal)
        else:
            validator = helpers.DocumentValidator()
            result = validator.validate_proposal(proposal)
        
        if not result.is_valid:
            for err in result.errors:
                helpers.write_error(f"  ✗ {err}")
            helpers.write_warning("Proposal has blocking issues; please fix and rerun step 2")
            return False
        if result.warnings:
            helpers.write_warning(f"Proposal has {len(result.warnings)} warning(s):")
            for w in result.warnings[:3]:
                helpers.write_warning(f"  ⚠ {w}")

    _mark_complete(change_path)
    helpers.write_success("Step 2 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step2")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step2(test_dir, title="Test Proposal", dry_run=True)
    sys.exit(0 if ok else 1)
