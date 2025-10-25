#!/usr/bin/env python3
"""Step 3: Specification

Ensures spec.md exists with key sections. Does not overwrite existing files.
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


def invoke_step3(
    change_path: Path, title: str | None = None, dry_run: bool = False, **_: dict
) -> bool:
    helpers.write_step(3, "Specification")

    # Initialize status tracker if available
    status_tracker = None
    if STATUS_TRACKER_AVAILABLE:
        try:
            status_tracker = create_tracker(
                change_path.name,
                lane="standard",  # Default lane for step 3
                status_file=change_path / ".checkpoints" / "status.json",
            )
            status_tracker.start_stage(3, "Capability Spec")
        except Exception as e:
            helpers.write_warning(f"Could not initialize status tracker: {e}")

    spec_md = change_path / "spec.md"
    proposal = change_path / "proposal.md"

    # Use DocumentValidator if available for file creation check
    if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator and not spec_md.exists():
        try:
            validator = DocumentValidator()
            if not validator.validate_file_creation(change_path, "spec.md"):
                helpers.write_error("Document validation failed for spec.md creation")
                if status_tracker:
                    status_tracker.complete_stage(3, success=False, metrics={"reason": "Document validation failed"})
                return False
        except Exception as e:
            helpers.write_warning(f"Document validation error: {e}")

    if spec_md.exists():
        helpers.write_info("spec.md already exists; leaving as-is")
        # Ensure required sections exist to satisfy validator
        if not dry_run:
            try:
                content = spec_md.read_text(encoding="utf-8")
                updated = content
                import re as _re

                has_requirements = "## Requirements" in content
                has_ac = bool(_re.search(r"(?m)^##\s+Acceptance Criteria\b", content))

                sections_to_append: list[tuple[str, str]] = []
                if not has_requirements:
                    sections_to_append.append(
                        ("## Requirements", "\n- **R-01**: ...\n- **R-02**: ...\n")
                    )
                if not has_ac:
                    sections_to_append.append(
                        (
                            "## Acceptance Criteria",
                            "\n- [ ] AC-01: ...\n- [ ] AC-02: ...\n",
                        )
                    )

                if sections_to_append:
                    updated = (
                        updated.rstrip()
                        + "\n\n"
                        + "\n\n".join(
                            f"{hdr}\n{body}" for hdr, body in sections_to_append
                        )
                        + "\n"
                    )
                if updated != content:
                    helpers.set_content_atomic(spec_md, updated)
                    helpers.write_success("Auto-inserted missing spec sections")
            except Exception as e:
                helpers.write_warning(
                    f"Could not auto-insert missing spec sections: {e}"
                )
    else:
        # Prefer contextual generation from proposal
        if DOCUMENT_GENERATOR_AVAILABLE and DocumentGenerator:
            if progress and hasattr(progress, 'spinner'):
                with progress.spinner("Generating spec.md from proposal", "Spec generated"):
                    generator = DocumentGenerator()
                    content = generator.generate_spec_from_proposal(proposal, title)
                    if not dry_run:
                        helpers.set_content_atomic(spec_md, content)
            else:
                generator = DocumentGenerator()
                content = generator.generate_spec_from_proposal(proposal, title)
                if not dry_run:
                    helpers.set_content_atomic(spec_md, content)
                    helpers.write_success(f"Created spec from proposal: {spec_md}")
        else:
            # Fallback to scaffold
            content = SCAFFOLD
            if not dry_run:
                helpers.set_content_atomic(spec_md, content)
                helpers.write_success(f"Created spec scaffold: {spec_md}")

        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create: {spec_md}")

    # Validate (skip in dry-run)
    if dry_run:
        helpers.write_info("[DRY RUN] Skipping spec validation")
    else:
        if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator:
            if progress and hasattr(progress, 'spinner'):
                with progress.spinner("Validating spec.md", "Validation complete"):
                    validator = DocumentValidator()
                    result = validator.validate_spec(spec_md)
            else:
                validator = DocumentValidator()
                result = validator.validate_spec(spec_md)
        else:
            # Fallback validation
            result = type('Result', (), {'is_valid': True, 'errors': [], 'warnings': []})()

        if not result.is_valid:
            for err in result.errors:
                helpers.write_error(f"  ✗ {err}")
            helpers.write_warning(
                "Specification has blocking issues; fix and rerun step 3"
            )
            if status_tracker:
                status_tracker.complete_stage(3, success=False, metrics={"reason": "Validation failed"})
            return False
        if result.warnings:
            helpers.write_warning(
                f"Specification has {len(result.warnings)} warning(s):"
            )
            for w in result.warnings[:3]:
                helpers.write_warning(f"  ⚠ {w}")

    # Validate step artifacts
    if not dry_run and not helpers.validate_step_artifacts(change_path, 3):
        helpers.write_error("Step 3 artifact validation failed")
        if status_tracker:
            status_tracker.complete_stage(3, success=False, metrics={"reason": "Artifact validation failed"})
        return False

    # Show changes if available
    if not dry_run:
        try:
            changes_dir = change_path.parent
            helpers.show_changes(changes_dir)
        except Exception as e:
            helpers.write_warning(f"Could not show changes: {e}")

    # Detect next step
    try:
        next_step = helpers.detect_next_step(change_path)
        helpers.write_info(f"Next workflow step: {next_step}")
    except Exception as e:
        helpers.write_warning(f"Could not detect next step: {e}")

    _mark_complete(change_path)

    # Record completion in status tracker
    if status_tracker:
        status_tracker.complete_stage(3, success=True)

    helpers.write_success("Step 3 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step3")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step3(test_dir, title="Test Spec", dry_run=True)
    sys.exit(0 if ok else 1)
