#!/usr/bin/env python3
"""Step 5: Test Definition

Generates comprehensive test_plan.md and spec.md with requirements extracted
from proposal.md, tasks.md, and existing documentation.
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


def _generate_test_plan_md(
    proposal_path: Path, tasks_path: Path, spec_path: Path
) -> str:
    """Generate comprehensive test_plan.md with full test mapping.

    Returns:
        Complete test_plan.md content
    """
    criteria = _extract_success_criteria(proposal_path)
    file_lists = _extract_file_lists(proposal_path)

    test_plan = "# Test Plan\n\n"
    test_plan += "## Overview\n\n"
    test_plan += "This test plan validates that the implementation successfully meets all acceptance criteria.\n\n"

    # Strategy
    test_plan += "## Testing Strategy\n\n"
    test_plan += "The testing approach validates:\n\n"
    test_plan += "1. **Structure Validation**: Verify docs/ directory structure is created correctly\n"
    test_plan += (
        "2. **File Operations**: Verify files are moved and deleted as specified\n"
    )
    test_plan += "3. **Root Cleanup**: Verify root directory is cleaned (≤10 files)\n"
    test_plan += "4. **Documentation Updates**: Verify README and links are updated\n"
    test_plan += "5. **Link Validation**: Verify no broken internal links\n"
    test_plan += "6. **OpenSpec Separation**: Verify governance files are isolated\n"
    test_plan += "7. **CHANGELOG Updates**: Verify cleanup is documented\n\n"

    # Mapping to Acceptance Criteria
    test_plan += "## Mapping to Acceptance Criteria\n\n"

    # Map success criteria to test suites
    test_mapping = {
        "AC-1": ["Structure validation", "Directory creation tests"],
        "AC-2": ["File inventory", "Categorization tests"],
        "AC-3": ["File move operations", "Reference file tests"],
        "AC-4": ["File deletion", "Celebration file removal tests"],
        "AC-5": ["Root directory check", "File count validation"],
        "AC-6": ["README updates", "Documentation structure tests"],
        "AC-7": ["Link validation", "Reference integrity tests"],
        "AC-8": ["docs/README.md creation", "Navigation guide tests"],
    }

    for i, criterion in enumerate(criteria[:8], 1):
        ac_num = f"AC-{i}"
        tests = test_mapping.get(ac_num, ["General validation"])
        test_plan += f"- **{ac_num}**: {criterion}\n"
        for test in tests:
            test_plan += f"  - Covered by: {test}\n"

    test_plan += "\n"

    # Test Suites
    test_plan += "## Test Suites\n\n"

    test_plan += "### 1. Directory Structure Validation\n"
    test_plan += "- [ ] docs/ directory exists\n"
    test_plan += "- [ ] docs/getting-started/ subdirectory exists\n"
    test_plan += "- [ ] docs/guides/ subdirectory exists\n"
    test_plan += "- [ ] docs/architecture/ subdirectory exists\n"
    test_plan += "- [ ] docs/reference/ subdirectory exists\n"
    test_plan += "- [ ] docs/production/ subdirectory exists\n"
    test_plan += "- [ ] docs/historical/ subdirectory exists\n"
    test_plan += "- [ ] docs/README.md exists and is readable\n\n"

    test_plan += "### 2. File Deletion Validation\n"
    if file_lists["delete"]:
        test_plan += (
            f"- [ ] All {len(file_lists['delete'])} celebration/status files deleted\n"
        )
        for f in file_lists["delete"][:5]:
            test_plan += f"- [ ] {f} deleted\n"
        if len(file_lists["delete"]) > 5:
            test_plan += (
                f"- [ ] ... and {len(file_lists['delete']) - 5} more files deleted\n"
            )
    test_plan += "\n"

    test_plan += "### 3. File Move Validation\n"
    if file_lists["move"]:
        test_plan += (
            f"- [ ] All {len(file_lists['move'])} reference files moved to docs/\n"
        )
        for f in file_lists["move"][:5]:
            test_plan += f"- [ ] {f} moved to correct docs/ subdirectory\n"
        if len(file_lists["move"]) > 5:
            test_plan += (
                f"- [ ] ... and {len(file_lists['move']) - 5} more files moved\n"
            )
    test_plan += "\n"

    test_plan += "### 4. Root Directory Cleanup\n"
    test_plan += "- [ ] Root directory contains ≤10 essential files\n"
    if file_lists["keep"]:
        test_plan += f"- [ ] All {len(file_lists['keep'])} kept files present in root\n"
    test_plan += "- [ ] No extraneous markdown files in root\n\n"

    test_plan += "### 5. Documentation Updates\n"
    test_plan += "- [ ] README.md updated with docs/ navigation\n"
    test_plan += "- [ ] README.md has getting-started link\n"
    test_plan += "- [ ] README.md has guides link\n"
    test_plan += "- [ ] README.md has architecture link\n"
    test_plan += "- [ ] docs/README.md created with full navigation\n"
    test_plan += "- [ ] Contributing.md updated with new structure\n\n"

    test_plan += "### 6. Link Validation\n"
    test_plan += "- [ ] No broken relative links in README.md\n"
    test_plan += "- [ ] No broken relative links in docs/README.md\n"
    test_plan += "- [ ] No broken relative links in docs/ subdirectories\n"
    test_plan += "- [ ] All cross-document links valid\n\n"

    test_plan += "### 7. OpenSpec Separation\n"
    test_plan += "- [ ] openspec/ files remain unchanged\n"
    test_plan += "- [ ] openspec/ files not in root directory\n"
    test_plan += "- [ ] openspec/ path references correct in documentation\n\n"

    test_plan += "### 8. CHANGELOG Updates\n"
    test_plan += "- [ ] CHANGELOG.md documents cleanup change\n"
    test_plan += "- [ ] CHANGELOG.md lists deleted file categories\n"
    test_plan += "- [ ] CHANGELOG.md documents new docs/ structure\n\n"

    return test_plan


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

    test_plan_path = change_path / "test_plan.md"
    spec_path = change_path / "spec.md"
    proposal_path = change_path / "proposal.md"
    tasks_path = change_path / "tasks.md"

    # Generate spec.md if it doesn't exist or is empty
    if not spec_path.exists() or spec_path.stat().st_size < 100:
        if progress:
            with progress.spinner("Generating spec.md from proposal", "Spec generated"):
                content = _generate_spec_md(proposal_path, tasks_path)
                if not dry_run:
                    helpers.set_content_atomic(spec_path, content)
        else:
            content = _generate_spec_md(proposal_path, tasks_path)
            if not dry_run:
                helpers.set_content_atomic(spec_path, content)
                helpers.write_success(f"Generated comprehensive spec.md: {spec_path}")

        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create/update: {spec_path}")

    # Generate test_plan.md if it doesn't exist or is empty
    if not test_plan_path.exists() or test_plan_path.stat().st_size < 100:
        if progress:
            with progress.spinner(
                "Generating test_plan.md from proposal", "Test plan generated"
            ):
                content = _generate_test_plan_md(proposal_path, tasks_path, spec_path)
                if not dry_run:
                    helpers.set_content_atomic(test_plan_path, content)
        else:
            content = _generate_test_plan_md(proposal_path, tasks_path, spec_path)
            if not dry_run:
                helpers.set_content_atomic(test_plan_path, content)
                helpers.write_success(
                    f"Generated comprehensive test_plan.md: {test_plan_path}"
                )

        if dry_run:
            helpers.write_info(f"[DRY RUN] Would create/update: {test_plan_path}")
    else:
        helpers.write_info("test_plan.md already exists; leaving as-is")
        helpers.write_info("spec.md already exists; leaving as-is")

    _mark_complete(change_path)
    helpers.write_success("Step 5 completed")
    return True


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step5")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step5(test_dir, title="Test Plan", dry_run=True)
    sys.exit(0 if ok else 1)
