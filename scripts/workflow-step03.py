#!/usr/bin/env python3
"""Step 3: Specification

Ensures spec.md exists with key sections. Does not overwrite existing files.
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


SCAFFOLD = """# Specification

## Overview

Summarize the solution.

## Requirements

- [ ] Requirement 1
- [ ] Requirement 2

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Out of Scope

- ...
"""


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **3. Specification", "[x] **3. Specification")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def invoke_step3(change_path: Path, title: str | None = None, dry_run: bool = False, **_: dict) -> bool:
    helpers.write_step(3, "Specification")
    spec_md = change_path / "spec.md"
    proposal = change_path / "proposal.md"

    if spec_md.exists():
        helpers.write_info("spec.md already exists; leaving as-is")
    else:
        # Prefer contextual generation from proposal
        if progress:
            with progress.spinner("Generating spec.md from proposal", "Spec generated"):
                generator = helpers.DocumentGenerator()
                content = generator.generate_spec_from_proposal(proposal, title)
                if not dry_run:
                    helpers.set_content_atomic(spec_md, content)
        else:
            generator = helpers.DocumentGenerator()
            content = generator.generate_spec_from_proposal(proposal, title)
            if not dry_run:
                helpers.set_content_atomic(spec_md, content)
                helpers.write_success(f"Created spec from proposal: {spec_md}")
        
        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create: {spec_md}")
    
    # Validate (skip in dry-run)
    if dry_run:
        helpers.write_info("[DRY RUN] Skipping spec validation")
    else:
        if progress:
            with progress.spinner("Validating spec.md", "Validation complete"):
                validator = helpers.DocumentValidator()
                result = validator.validate_spec(spec_md)
        else:
            validator = helpers.DocumentValidator()
            result = validator.validate_spec(spec_md)
        
        if not result.is_valid:
            for err in result.errors:
                helpers.write_error(f"  ✗ {err}")
            helpers.write_warning("Specification has blocking issues; fix and rerun step 3")
            return False
        if result.warnings:
            helpers.write_warning(f"Specification has {len(result.warnings)} warning(s):")
            for w in result.warnings[:3]:
                helpers.write_warning(f"  ⚠ {w}")

    _mark_complete(change_path)
    helpers.write_success("Step 3 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step3")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step3(test_dir, title="Test Spec", dry_run=True)
    sys.exit(0 if ok else 1)
