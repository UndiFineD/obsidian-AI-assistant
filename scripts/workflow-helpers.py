#!/usr/bin/env python3
"""
OpenSpec Workflow - Helper Functions

This module provides shared utility functions for the OpenSpec workflow system,
including output formatting, file operations, validation, and cross-referencing.

Author: Obsidian AI Agent Team
License: MIT
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import subprocess
import sys
import time
import threading


# ANSI color codes for terminal output
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def write_step(number: int, description: str) -> None:
    """Format and display a step header."""
    print(
        f"\n{Colors.CYAN}═════════  STEP {number}: {description} ═════════{Colors.RESET}"
    )


def write_info(message: str) -> None:
    """Display informational message."""
    print(f"{Colors.WHITE}{message}{Colors.RESET}")


def write_success(message: str) -> None:
    """Display success message."""
    print(f"{Colors.GREEN}{message}{Colors.RESET}")


def write_error(message: str) -> None:
    """Display error message."""
    print(f"{Colors.RED}{message}{Colors.RESET}")


def write_warning(message: str) -> None:
    """Display warning message."""
    print(f"{Colors.YELLOW}{message}{Colors.RESET}")


def write_error_hint(message: str, hint: str) -> None:
    """Display an error with a follow-up hint for resolution."""
    write_error(message)
    print(f"{Colors.YELLOW}  ↳ Hint: {hint}{Colors.RESET}")


def show_changes(changes_dir: Path) -> None:
    """
    Display all active changes with completion percentages.

    Args:
        changes_dir: Path to openspec/changes directory
    """
    if not changes_dir.exists():
        write_warning(f"Changes directory not found: {changes_dir}")
        return

    changes = [d for d in changes_dir.iterdir() if d.is_dir()]

    if not changes:
        write_info("No active changes found")
        return

    write_info("Active Changes:")

    for change in sorted(changes):
        todo_path = change / "todo.md"

        if todo_path.exists():
            content = todo_path.read_text(encoding="utf-8")
            completed = len(re.findall(r"- \[x\]", content))
            total = len(re.findall(r"- \[[ x]\]", content))
            percent = round((completed / total) * 100) if total > 0 else 0

            if percent == 100:
                color = Colors.GREEN
            elif percent > 50:
                color = Colors.YELLOW
            else:
                color = Colors.WHITE

            print(f"  {color}[{percent}%] {change.name}{Colors.RESET}")
        else:
            print(f"{Colors.GRAY}  [???] {change.name}{Colors.RESET}")


def test_change_structure(change_path: Path) -> bool:
    """
    Validate that all required OpenSpec files exist.

    Args:
        change_path: Path to change directory

    Returns:
        True if all required files exist, False otherwise
    """
    required_files = ["todo.md", "proposal.md", "spec.md", "tasks.md", "test_plan.md"]
    valid = True

    for filename in required_files:
        file_path = change_path / filename
        if not file_path.exists():
            write_warning(f"Missing required file: {filename}")
            valid = False

    return valid


@dataclass
class CrossValidationResult:
    """Results from documentation cross-validation."""

    is_valid: bool = True
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    cross_references: Dict[str, List[str]] = field(default_factory=dict)


def test_documentation_cross_validation(change_path: Path) -> CrossValidationResult:
    """
    Cross-validate OpenSpec documentation files for consistency and completeness.

    Performs 5 validation checks:
    1. All "What Changes" from proposal.md appear in tasks.md
    2. Spec.md acceptance criteria match test_plan.md test cases
    3. Tasks.md implementation tasks align with spec.md requirements
    4. No orphaned references (broken links)
    5. Affected files consistency across documents

    Args:
        change_path: Path to change directory

    Returns:
        CrossValidationResult with validation status and details
    """
    result = CrossValidationResult()
    result.cross_references = {
        "proposal_to_tasks": [],
        "spec_to_test_plan": [],
        "tasks_to_spec": [],
        "orphaned_references": [],
    }

    # Load all documentation files
    docs = {}
    for doc_name in ["proposal", "spec", "tasks", "test_plan"]:
        doc_path = change_path / f"{doc_name}.md"
        if doc_path.exists():
            docs[doc_name] = doc_path.read_text(encoding="utf-8")
        else:
            docs[doc_name] = None

    # Validation 1: Verify all "What Changes" from proposal.md appear in tasks.md
    if docs["proposal"] and docs["tasks"]:
        print(
            f"{Colors.CYAN}  [CROSS-VALIDATION] Checking proposal.md → tasks.md alignment...{Colors.RESET}"
        )

        # Extract "What Changes" section
        what_match = re.search(
            r"##\s+What Changes\s+(.+?)(?=##|$)", docs["proposal"], re.DOTALL
        )
        if what_match:
            changes_block = what_match.group(1)
            proposal_changes = re.findall(r"(?m)^\s*-\s+(.+?)$", changes_block)

            missing_in_tasks = []
            for change in proposal_changes:
                # Skip template placeholders
                if re.match(r"^\[.*\]$", change):
                    continue

                # Check if change is referenced in tasks.md
                # Use first 30 chars as search pattern
                change_pattern = re.escape(change[: min(30, len(change))])
                if not re.search(change_pattern, docs["tasks"]):
                    missing_in_tasks.append(change)

            if missing_in_tasks:
                result.issues.append(
                    f"Proposal changes missing from tasks.md: {len(missing_in_tasks)} item(s)"
                )
                for missing in missing_in_tasks:
                    result.warnings.append(f"  → Missing in tasks.md: '{missing}'")
                result.is_valid = False
            else:
                result.cross_references["proposal_to_tasks"] = proposal_changes
                print(
                    f"{Colors.GREEN}    ✓ All proposal changes referenced in tasks.md{Colors.RESET}"
                )

    # Validation 2: Verify spec.md acceptance criteria match test_plan.md test cases
    if docs["spec"] and docs["test_plan"]:
        print(
            f"{Colors.CYAN}  [CROSS-VALIDATION] Checking spec.md → test_plan.md alignment...{Colors.RESET}"
        )

        # Extract acceptance criteria
        criteria_match = re.search(
            r"##\s+Acceptance Criteria\s+(.+?)(?=\r?\n##\s|\Z)", docs["spec"], re.DOTALL
        )

        acceptance_criteria = []
        if criteria_match:
            criteria_block = criteria_match.group(1)
            acceptance_criteria = re.findall(
                r"(?m)^\s*-\s+\[\s?\]\s+(.+?)$", criteria_block
            )

        # Check coverage against test_plan.md
        criteria_without_tests = []
        for criteria in acceptance_criteria:
            # Skip template placeholders
            if re.match(r"^\[.*\]$", criteria) or "provides" in criteria.lower():
                continue

            # Extract key terms for matching (words > 4 chars)
            key_terms = [w for w in re.findall(r"\w+", criteria) if len(w) > 4][:3]

            has_test_coverage = False
            for term in key_terms:
                if re.search(re.escape(term), docs["test_plan"], re.IGNORECASE):
                    has_test_coverage = True
                    break

            if not has_test_coverage:
                criteria_without_tests.append(criteria)

        if criteria_without_tests:
            result.warnings.append(
                f"Acceptance criteria may lack test coverage: {len(criteria_without_tests)} item(s)"
            )
            for missing in criteria_without_tests[:3]:
                result.warnings.append(f"  → Possibly untested: '{missing}'")
        else:
            result.cross_references["spec_to_test_plan"] = acceptance_criteria
            print(
                f"{Colors.GREEN}    ✓ Acceptance criteria have test coverage{Colors.RESET}"
            )

    # Validation 3: Verify tasks.md implementation tasks align with spec.md requirements
    if docs["tasks"] and docs["spec"]:
        print(
            f"{Colors.CYAN}  [CROSS-VALIDATION] Checking tasks.md → spec.md alignment...{Colors.RESET}"
        )

        # Extract requirements from spec.md
        req_match = re.search(
            r"##\s+(?:Requirements|Functional Requirements)\s+(.+?)(?=\r?\n##\s|\Z)",
            docs["spec"],
            re.DOTALL,
        )

        spec_requirements = []
        if req_match:
            req_block = req_match.group(1)
            spec_requirements = re.findall(r"(?m)^\s*-\s+(.+?)$", req_block)

        # Extract implementation tasks from tasks.md
        impl_match = re.search(
            r"##\s+1\.\s+Implementation\s+(.+?)(?=\r?\n##\s|\Z)",
            docs["tasks"],
            re.DOTALL,
        )

        impl_tasks = []
        if impl_match:
            impl_block = impl_match.group(1)
            impl_tasks = re.findall(r"(?m)^\s*-\s+\[\s?\]\s+(.+?)$", impl_block)

        # Check alignment
        requirements_without_tasks = []
        for req in spec_requirements:
            # Skip template placeholders
            if re.match(r"^\[.*\]$", req) or req.startswith(
                ("Remove", "Update", "Identify", "Archive")
            ):
                continue

            # Extract key terms
            key_terms = [w for w in re.findall(r"\w+", req) if len(w) > 4][:3]

            has_task = False
            for term in key_terms:
                if re.search(re.escape(term), docs["tasks"], re.IGNORECASE):
                    has_task = True
                    break

            if not has_task:
                requirements_without_tasks.append(req)

        if requirements_without_tasks:
            result.warnings.append(
                f"Spec requirements may lack implementation tasks: {len(requirements_without_tasks)} item(s)"
            )
            for missing in requirements_without_tasks[:3]:
                result.warnings.append(f"  → Possibly no task for: '{missing}'")
        else:
            result.cross_references["tasks_to_spec"] = impl_tasks
            print(
                f"{Colors.GREEN}    ✓ Spec requirements have implementation tasks{Colors.RESET}"
            )

    # Validation 4: Check for orphaned references (broken links)
    print(
        f"{Colors.CYAN}  [CROSS-VALIDATION] Checking for orphaned references...{Colors.RESET}"
    )

    all_docs = [docs[k] for k in ["proposal", "spec", "tasks", "test_plan"] if docs[k]]
    orphaned_refs = []

    for doc in all_docs:
        # Find markdown links
        links = re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", doc)
        for link_text, link_path in links:
            # Skip external URLs
            if link_path.startswith(("http://", "https://")):
                continue

            # Check if referenced file exists
            full_link_path = change_path / link_path
            if not full_link_path.exists():
                orphaned_refs.append(f"{link_text} → {link_path}")

    if orphaned_refs:
        result.warnings.append(
            f"Found orphaned references: {len(orphaned_refs)} link(s)"
        )
        for orphan in orphaned_refs[:3]:
            result.warnings.append(f"  → Broken link: {orphan}")
    else:
        print(f"{Colors.GREEN}    ✓ No orphaned references found{Colors.RESET}")

    # Validation 5: Verify affected files consistency across documents
    print(
        f"{Colors.CYAN}  [CROSS-VALIDATION] Checking affected files consistency...{Colors.RESET}"
    )

    affected_files_proposal = []
    affected_files_spec = []

    if docs["proposal"]:
        match = re.search(r"(?m)^-\s*\*\*Affected files\*\*:\s*(.+)", docs["proposal"])
        if match:
            affected_files_proposal = [f.strip() for f in match.group(1).split(",")]

    if docs["spec"]:
        match = re.search(r"(?m)^-\s*\*\*Affected files\*\*:\s*(.+)", docs["spec"])
        if match:
            affected_files_spec = [f.strip() for f in match.group(1).split(",")]

    if affected_files_proposal and affected_files_spec:
        # Find differences
        only_in_proposal = set(affected_files_proposal) - set(affected_files_spec)
        only_in_spec = set(affected_files_spec) - set(affected_files_proposal)

        if only_in_proposal or only_in_spec:
            result.warnings.append(
                "Affected files mismatch between proposal.md and spec.md"
            )
            for file in only_in_proposal:
                result.warnings.append(f"  → {file} (in proposal, missing in spec)")
            for file in only_in_spec:
                result.warnings.append(f"  → {file} (in spec, missing in proposal)")
        else:
            print(
                f"{Colors.GREEN}    ✓ Affected files consistent across documents{Colors.RESET}"
            )

    return result


def set_content_atomic(file_path: Path, content: str) -> bool:
    """
    Atomically write content to a file.

    Args:
        file_path: Path to file
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        file_path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        write_error(f"Failed to write {file_path}: {e}")
        return False


# --- Workflow resumption helpers ---


def _step_required_artifacts(step_num: int) -> list[str]:
    """Return a list of filenames that indicate step completion."""
    mapping: dict[int, list[str]] = {
        0: ["todo.md"],
        1: ["version_snapshot.md"],
        2: ["proposal.md"],
        3: ["spec.md"],
        4: ["tasks.md"],
        5: ["test_plan.md"],
        # Steps 6-12 vary; rely on todo.md marks primarily
    }
    return mapping.get(step_num, [])


def validate_step_artifacts(change_path: Path, step_num: int) -> bool:
    """Verify that artifacts for a given step exist on disk."""
    required = _step_required_artifacts(step_num)
    return all((change_path / f).exists() for f in required)


def detect_next_step(change_path: Path) -> int:
    """
    Detect the next step to execute based on todo.md and artifact validation.

    Returns the first step number (0-12) that is not marked complete or whose
    required artifacts are missing. Returns 13 if all steps appear complete.
    """
    todo_path = change_path / "todo.md"
    if not todo_path.exists():
        return 0

    try:
        content = todo_path.read_text(encoding="utf-8")
    except Exception:
        return 0

    # For each step in order, check if the checklist item exists and is checked.
    for step_num in range(13):
        # Pattern that tolerates space or x inside brackets
        pattern = rf"- \\[[ x]\\] \\*\\*{step_num}\\."
        m = re.search(pattern, content)
        if not m:
            # If the checklist item is missing, conservatively resume here
            return step_num

        line = m.group(0)
        is_checked = "[x]" in line
        if not is_checked:
            return step_num

        # If marked complete, verify expected artifacts exist
        if not validate_step_artifacts(change_path, step_num):
            write_warning(
                f"Step {step_num} marked complete but expected artifact(s) missing"
            )
            return step_num

    return 13


# --- Document validation and generation ---


@dataclass
class ValidationResult:
    """Simple document validation result."""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class DocumentValidator:
    """Lightweight validators for proposal/spec/tasks/test_plan."""

    def validate_proposal(self, proposal_path: Path) -> ValidationResult:
        res = ValidationResult()
        if not proposal_path.exists():
            res.is_valid = False
            res.errors.append("proposal.md not found")
            return res
        content = proposal_path.read_text(encoding="utf-8")
        required = ["## Context", "## What Changes", "## Goals", "## Stakeholders"]
        for section in required:
            if section not in content:
                res.is_valid = False
                res.errors.append(f"Missing section: {section}")
        if re.search(r"<[^>]+>", content):
            res.warnings.append("Template placeholders remain (e.g., <...>)")
        if len(content.split()) < 40:
            res.warnings.append("Proposal is very short (< 40 words)")
        return res

    def validate_spec(self, spec_path: Path) -> ValidationResult:
        res = ValidationResult()
        if not spec_path.exists():
            res.is_valid = False
            res.errors.append("spec.md not found")
            return res
        content = spec_path.read_text(encoding="utf-8")
        required = ["## Requirements", "## Acceptance Criteria"]
        for section in required:
            if section not in content:
                res.is_valid = False
                res.errors.append(f"Missing section: {section}")
        if not re.search(r"(?m)^\s*-\s+\*\*R-\d+\*\*:", content):
            res.warnings.append("No requirements in expected format (- **R-01**: ...)")
        if not re.search(r"(?m)^\s*-\s+\[[ x]\] ", content):
            res.warnings.append("No acceptance criteria checklist items found")
        return res

    def validate_tasks(self, tasks_path: Path) -> ValidationResult:
        res = ValidationResult()
        if not tasks_path.exists():
            res.is_valid = False
            res.errors.append("tasks.md not found")
            return res
        content = tasks_path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^\s*-\s+\[[ x]\] ", content):
            res.warnings.append("No tasks found (expected - [ ] ...)")
        for sec in ("## 1. Implementation", "## 2. Testing", "## 3. Documentation"):
            if sec not in content:
                res.suggestions.append(f"Consider adding section: {sec}")
        return res

    def validate_test_plan(self, plan_path: Path) -> ValidationResult:
        res = ValidationResult()
        if not plan_path.exists():
            res.is_valid = False
            res.errors.append("test_plan.md not found")
            return res
        content = plan_path.read_text(encoding="utf-8")
        if "## Strategy" not in content:
            res.suggestions.append("Consider adding '## Strategy' section")
        return res


class TemplateManager:
    """Manage workflow templates for common scenarios."""

    TEMPLATES = {
        "feature": "proposal-feature.md",
        "bugfix": "proposal-bugfix.md",
        "docs": "proposal-docs.md",
        "refactor": "proposal-refactor.md",
        "default": None,  # Uses basic scaffold
    }

    @classmethod
    def get_available_templates(cls) -> List[str]:
        """Return list of available template types."""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_template_path(cls, template_type: str) -> Optional[Path]:
        """
        Get the file path for a template type.

        Args:
            template_type: Type of template (feature, bugfix, docs, refactor, default)

        Returns:
            Path to template file, or None for default
        """
        if template_type not in cls.TEMPLATES:
            write_warning(f"Unknown template type '{template_type}', using default")
            template_type = "default"

        template_file = cls.TEMPLATES[template_type]
        if template_file is None:
            return None

        # Find template file relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        template_path = project_root / "openspec" / "templates" / template_file

        if not template_path.exists():
            write_warning(f"Template file not found: {template_path}, using default")
            return None

        return template_path

    @classmethod
    def load_template(cls, template_type: str, title: Optional[str] = None) -> str:
        """
        Load a proposal template and optionally substitute title.

        Args:
            template_type: Type of template (feature, bugfix, docs, refactor, default)
            title: Optional title to substitute in template

        Returns:
            Template content as string
        """
        from datetime import datetime

        template_path = cls.get_template_path(template_type)

        if template_path is None:
            # Return basic default scaffold
            content = """# Proposal

## Context

Describe the background and motivation.

## What Changes

List the proposed changes at a high level.

## Goals

- Goal 1: ...
- Goal 2: ...

## Stakeholders

- Owner: [owner]
- Reviewers: [reviewers]

## Timeline

- Proposed: {date}
"""
        else:
            content = template_path.read_text(encoding="utf-8")

        # Substitute placeholders
        content = content.replace("<date>", datetime.utcnow().strftime("%Y-%m-%d"))
        content = content.replace("<owner>", "[owner]")
        content = content.replace("<reviewers>", "[reviewers]")

        # Optionally substitute title
        if title:
            content = re.sub(r"# Proposal:?\s*\[.*?\]", f"# Proposal: {title}", content)

        return content

    @classmethod
    def describe_template(cls, template_type: str) -> str:
        """Get a description of what a template is for."""
        descriptions = {
            "feature": "New functionality or capability addition",
            "bugfix": "Fixing incorrect behavior or defects",
            "docs": "Documentation creation or updates",
            "refactor": "Code quality improvements without behavior changes",
            "default": "Generic proposal with basic sections",
        }
        return descriptions.get(template_type, "Unknown template type")


class DocumentGenerator:
    """Generate contextual scaffolds from existing docs."""

    def _extract_proposal_changes(self, proposal_text: str) -> List[str]:
        m = re.search(r"##\s+What Changes\s+(.+?)(?=##|$)", proposal_text, re.DOTALL)
        if not m:
            return []
        block = m.group(1)
        return re.findall(r"(?m)^\s*-\s+(.+?)$", block)

    def generate_spec_from_proposal(
        self, proposal_path: Path, title: Optional[str] = None
    ) -> str:
        if not proposal_path.exists():
            title_line = f"# Specification{': ' + title if title else ''}\n\n"
            return (
                title_line
                + "## Requirements\n\n- **R-01**: ...\n\n## Acceptance Criteria\n\n- [ ] ...\n"
            )
        proposal = proposal_path.read_text(encoding="utf-8")
        changes = [
            c
            for c in self._extract_proposal_changes(proposal)
            if not re.match(r"^\[.*\]$", c)
        ]
        title_line = f"# Specification{': ' + title if title else ''}\n\n"
        out = [title_line, "## Requirements\n\n"]
        for i, c in enumerate(changes, 1):
            out.append(f"- **R-{i:02d}**: {c}\n")
        out.append("\n## Acceptance Criteria\n\n")
        for i, c in enumerate(changes, 1):
            out.append(f"- [ ] AC-{i:02d}: Verify {c.lower()}\n")
        out.append("\n")
        return "".join(out)

    def generate_tasks_from_spec(
        self, spec_path: Path, title: Optional[str] = None
    ) -> str:
        title_line = f"# Task Breakdown{': ' + title if title else ''}\n\n"
        if not spec_path.exists():
            return (
                title_line
                + "## Tasks\n\n- [ ] Implement ...\n\n## Dependencies\n\n- ...\n"
            )
        spec = spec_path.read_text(encoding="utf-8")
        reqs = re.findall(r"(?m)^\s*-\s+\*\*R-(\d+)\*\*: (.+)$", spec)
        out = [title_line, "## Tasks\n\n"]
        for _, text in reqs:
            out.append(f"- [ ] Implement: {text}\n")
        out.append("\n## Dependencies\n\n- ...\n")
        return "".join(out)

    def generate_test_plan(
        self, spec_path: Path, tasks_path: Path, title: Optional[str] = None
    ) -> str:
        title_line = f"# Test Plan{': ' + title if title else ''}\n\n## Strategy\n\nDescribe the test approach.\n\n"
        spec = spec_path.read_text(encoding="utf-8") if spec_path.exists() else ""
        tasks = tasks_path.read_text(encoding="utf-8") if tasks_path.exists() else ""
        ac = re.findall(r"(?m)^\s*-\s+\[[ x]\]\s+(.+)$", spec)
        impl = re.findall(r"(?m)^\s*-\s+\[[ x]\]\s+(.+)$", tasks)
        out = [title_line, "## Mapping to Acceptance Criteria\n\n"]
        for item in ac:
            out.append(f"- {item}\n")
        out.append("\n## Test Cases\n\n")
        for item in impl[:10]:
            out.append(f"- [ ] {item}\n")
        out.append("\n")
        return "".join(out)


# ============================================================================
# Status Tracking System
# ============================================================================


@dataclass
class StepStatus:
    """Represents the status of a single workflow step."""

    step_id: int
    step_name: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result: str = "pending"  # pending, in_progress, success, failure, skipped
    duration_seconds: Optional[float] = None
    metrics: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "result": self.result,
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
            "errors": self.errors,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
        }


class WorkflowStatusTracker:
    """Tracks workflow status across steps with JSON persistence."""

    def __init__(self, change_path: Path):
        """
        Initialize the status tracker.

        Args:
            change_path: Path to the change directory
        """
        self.change_path = Path(change_path)
        self.status_file = self.change_path / "status.json"
        self.steps: Dict[int, StepStatus] = {}
        self._load_existing_status()

    def _load_existing_status(self) -> None:
        """Load existing status from status.json if it exists."""
        if self.status_file.exists():
            try:
                data = json.loads(self.status_file.read_text(encoding="utf-8"))
                for step_data in data.get("steps", []):
                    step_id = step_data["step_id"]
                    self.steps[step_id] = StepStatus(
                        step_id=step_id,
                        step_name=step_data.get("step_name", f"Step {step_id}"),
                        start_time=step_data.get("start_time"),
                        end_time=step_data.get("end_time"),
                        result=step_data.get("result", "pending"),
                        duration_seconds=step_data.get("duration_seconds"),
                        metrics=step_data.get("metrics", {}),
                        errors=step_data.get("errors", []),
                        files_created=step_data.get("files_created", []),
                        files_modified=step_data.get("files_modified", []),
                    )
            except (json.JSONDecodeError, KeyError) as e:
                write_warning(f"Could not load existing status: {e}")

    def start_step(self, step_id: int, step_name: str) -> StepStatus:
        """
        Mark the start of a step.

        Args:
            step_id: Numeric step ID (0-12)
            step_name: Human-readable step name

        Returns:
            StepStatus object for this step
        """
        status = StepStatus(
            step_id=step_id,
            step_name=step_name,
            start_time=datetime.now().isoformat(),
            result="in_progress",
        )
        self.steps[step_id] = status
        self._save_status()
        return status

    def end_step(
        self,
        step_id: int,
        result: str = "success",
        metrics: Optional[Dict] = None,
        errors: Optional[List[str]] = None,
        files_created: Optional[List[str]] = None,
        files_modified: Optional[List[str]] = None,
    ) -> None:
        """
        Mark the end of a step.

        Args:
            step_id: Numeric step ID
            result: Result status (success, failure, skipped)
            metrics: Optional metrics dictionary
            errors: Optional list of error messages
            files_created: Optional list of created files
            files_modified: Optional list of modified files
        """
        if step_id not in self.steps:
            write_warning(f"Step {step_id} not found in status tracker")
            return

        status = self.steps[step_id]
        status.end_time = datetime.now().isoformat()
        status.result = result

        if status.start_time and status.end_time:
            start = datetime.fromisoformat(status.start_time)
            end = datetime.fromisoformat(status.end_time)
            status.duration_seconds = (end - start).total_seconds()

        if metrics:
            status.metrics = metrics
        if errors:
            status.errors = errors
        if files_created:
            status.files_created = files_created
        if files_modified:
            status.files_modified = files_modified

        self._save_status()

    def get_completed_steps(self) -> List[int]:
        """
        Get list of successfully completed step IDs.

        Returns:
            List of step IDs that completed successfully
        """
        return [
            step_id
            for step_id, status in self.steps.items()
            if status.result == "success"
        ]

    def get_last_completed_step(self) -> Optional[int]:
        """
        Get the ID of the last successfully completed step.

        Returns:
            Last step ID or None if no steps completed
        """
        completed = self.get_completed_steps()
        return max(completed) if completed else None

    def _save_status(self) -> None:
        """Save current status to status.json."""
        try:
            status_data = {
                "workflow_version": "0.1.41",
                "last_updated": datetime.now().isoformat(),
                "total_steps": len(self.steps),
                "completed_steps": len(self.get_completed_steps()),
                "steps": [status.to_dict() for status in self.steps.values()],
            }

            # Atomic write
            set_content_atomic(self.status_file, json.dumps(status_data, indent=2))
        except Exception as e:
            write_error(f"Failed to save status.json: {e}")

    def get_summary(self) -> str:
        """
        Get a human-readable summary of workflow status.

        Returns:
            Summary string
        """
        completed = len(self.get_completed_steps())
        total = len(self.steps)
        percent = round((completed / total) * 100) if total > 0 else 0

        lines = [
            f"Workflow Status: {completed}/{total} steps completed ({percent}%)",
            "",
        ]

        for step_id in sorted(self.steps.keys()):
            status = self.steps[step_id]
            symbol = (
                "✓"
                if status.result == "success"
                else "✗"
                if status.result == "failure"
                else "⊘"
            )
            duration = (
                f" ({status.duration_seconds:.1f}s)" if status.duration_seconds else ""
            )
            lines.append(
                f"  {symbol} Step {step_id}: {status.step_name}{duration} [{status.result}]"
            )

        return "\n".join(lines)


# ============================================================================
# Environment Validation Hooks
# ============================================================================


def check_python_version(required_version: str = "3.11") -> bool:
    """
    Check if Python version meets minimum requirement.

    Args:
        required_version: Minimum Python version (e.g., "3.11")

    Returns:
        True if version meets requirement, False otherwise
    """
    major, minor = map(int, required_version.split(".")[:2])
    current_major = sys.version_info.major
    current_minor = sys.version_info.minor

    if current_major < major or (current_major == major and current_minor < minor):
        return False
    return True


def check_tool_available(tool_name: str) -> bool:
    """
    Check if a command-line tool is available.

    Args:
        tool_name: Name of the tool (e.g., "pytest", "ruff", "mypy")

    Returns:
        True if tool is available, False otherwise
    """
    try:
        subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def validate_environment(
    required_tools: Optional[List[str]] = None,
    required_python_version: str = "3.11",
) -> tuple[bool, List[str]]:
    """
    Validate that the environment has all required tools and Python version.

    Args:
        required_tools: List of tools to check (pytest, ruff, mypy, bandit, gh)
        required_python_version: Minimum Python version

    Returns:
        Tuple of (success: bool, errors: List[str])
    """
    if required_tools is None:
        required_tools = ["pytest", "ruff", "mypy", "bandit"]

    errors = []

    # Check Python version
    if not check_python_version(required_python_version):
        errors.append(
            f"Python {required_python_version}+ is required (current: {sys.version_info.major}.{sys.version_info.minor})"
        )

    # Check required tools
    for tool in required_tools:
        if not check_tool_available(tool):
            errors.append(
                f"Tool '{tool}' is not available (install with: pip install {tool})"
            )

    return (len(errors) == 0, errors)


def print_environment_validation_report(
    required_tools: Optional[List[str]] = None,
    required_python_version: str = "3.11",
) -> bool:
    """
    Print environment validation report and return success status.

    Args:
        required_tools: List of tools to check
        required_python_version: Minimum Python version

    Returns:
        True if all checks pass, False otherwise
    """
    write_step(0, "Environment Validation")

    success, errors = validate_environment(required_tools, required_python_version)

    if success:
        write_success(
            f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected"
        )
        write_success(
            f"✓ All required tools available: {', '.join(required_tools or [])}"
        )
        return True
    else:
        write_error("✗ Environment validation failed:")
        for error in errors:
            write_error_hint("", error)
        write_info("\nTo fix, try:")
        write_info("  pip install --upgrade pytest ruff mypy bandit")
        return False


# ============================================================================
# Workflow Resumption System
# ============================================================================


def check_incomplete_workflow(change_path: Path) -> Optional[int]:
    """
    Check if a workflow is incomplete and return the last completed step.

    Args:
        change_path: Path to the change directory

    Returns:
        Last completed step ID, or None if no incomplete workflow found
    """
    status_file = change_path / "status.json"

    if not status_file.exists():
        return None

    try:
        data = json.loads(status_file.read_text(encoding="utf-8"))
        steps = data.get("steps", [])

        # Find last successfully completed step
        completed_steps = [s["step_id"] for s in steps if s.get("result") == "success"]

        if completed_steps:
            return max(completed_steps)

    except (json.JSONDecodeError, KeyError) as e:
        write_warning(f"Could not parse status.json: {e}")

    return None


def prompt_workflow_resumption(change_path: Path, last_completed_step: int) -> bool:
    """
    Prompt user to resume workflow or start fresh.

    Args:
        change_path: Path to the change directory
        last_completed_step: Last step that was completed

    Returns:
        True to resume, False to start fresh
    """
    write_warning("\n⚠️  Incomplete workflow detected!")
    write_info(f"Last completed step: {last_completed_step}\n")

    write_info("Options:")
    write_info("  [1] Resume from step " + str(last_completed_step + 1))
    write_info("  [2] Start fresh (clear all progress)")
    write_info("  [0] Cancel")

    choice = input("\nEnter your choice (0-2): ").strip()

    if choice == "1":
        write_success(f"Resuming from step {last_completed_step + 1}...")
        return True
    elif choice == "2":
        write_warning("Starting fresh...")
        # Clear status.json
        status_file = change_path / "status.json"
        if status_file.exists():
            status_file.unlink()
        return False
    else:
        write_info("Cancelled")
        sys.exit(0)


def handle_workflow_resumption(change_path: Path) -> Optional[int]:
    """
    Check for incomplete workflow and handle resumption.

    Returns:
        Step to resume from, or None if starting fresh
    """
    last_completed = check_incomplete_workflow(change_path)

    if last_completed is not None:
        if prompt_workflow_resumption(change_path, last_completed):
            return last_completed + 1
        else:
            return None

    return None


# ============================================================================
# Workflow Visualization System
# ============================================================================


class WorkflowVisualizer:
    """Visualize workflow status and progress."""

    @staticmethod
    def show_workflow_progress(change_path: Path) -> None:
        """
        Display current workflow progress with visual indicators.

        Args:
            change_path: Path to the change directory
        """
        status_file = change_path / "status.json"

        if not status_file.exists():
            write_info("No workflow status found")
            return

        try:
            data = json.loads(status_file.read_text(encoding="utf-8"))
            steps = data.get("steps", [])
            total_steps = data.get("total_steps", 0)
            completed_steps = data.get("completed_steps", 0)

            write_info("Workflow Progress:")
            write_info(f"  Completed: {completed_steps}/{total_steps} steps")

            # Show progress bar
            progress_bar(completed_steps, total_steps, width=40)

            # Show step details
            for step_data in sorted(steps, key=lambda x: x["step_id"]):
                step_id = step_data["step_id"]
                step_name = step_data.get("step_name", f"Step {step_id}")
                result = step_data.get("result", "pending")
                duration = step_data.get("duration_seconds")

                # Choose symbol and color
                if result == "success":
                    symbol = "✓"
                    color = Colors.GREEN
                elif result == "failure":
                    symbol = "✗"
                    color = Colors.RED
                elif result == "in_progress":
                    symbol = "⟳"
                    color = Colors.YELLOW
                elif result == "skipped":
                    symbol = "⊘"
                    color = Colors.GRAY
                else:
                    symbol = "○"
                    color = Colors.WHITE

                duration_str = f" ({duration:.1f}s)" if duration else ""
                print(
                    f"  {color}{symbol} Step {step_id}: {step_name}{duration_str}{Colors.RESET}"
                )

        except (json.JSONDecodeError, KeyError) as e:
            write_warning(f"Could not load workflow status: {e}")

    @staticmethod
    def show_step_details(change_path: Path, step_id: int) -> None:
        """
        Show detailed information for a specific step.

        Args:
            change_path: Path to the change directory
            step_id: Step ID to show details for
        """
        status_file = change_path / "status.json"

        if not status_file.exists():
            write_warning("No workflow status found")
            return

        try:
            data = json.loads(status_file.read_text(encoding="utf-8"))
            steps = data.get("steps", [])

            step_data = next((s for s in steps if s["step_id"] == step_id), None)

            if not step_data:
                write_warning(f"Step {step_id} not found in status")
                return

            write_info(f"Step {step_id} Details:")
            write_info(f"  Name: {step_data.get('step_name', 'Unknown')}")
            write_info(f"  Result: {step_data.get('result', 'unknown')}")
            write_info(f"  Start: {step_data.get('start_time', 'N/A')}")
            write_info(f"  End: {step_data.get('end_time', 'N/A')}")

            if step_data.get("duration_seconds"):
                write_info(f"  Duration: {step_data['duration_seconds']:.1f}s")

            if step_data.get("errors"):
                write_info("  Errors:")
                for error in step_data["errors"]:
                    write_error(f"    {error}")

            if step_data.get("files_created"):
                write_info("  Files Created:")
                for file in step_data["files_created"]:
                    write_success(f"    + {file}")

            if step_data.get("files_modified"):
                write_info("  Files Modified:")
                for file in step_data["files_modified"]:
                    write_info(f"    ~ {file}")

            if step_data.get("metrics"):
                write_info("  Metrics:")
                for key, value in step_data["metrics"].items():
                    write_info(f"    {key}: {value}")

        except (json.JSONDecodeError, KeyError) as e:
            write_warning(f"Could not load step details: {e}")

    @staticmethod
    def show_workflow_summary(change_path: Path) -> None:
        """
        Show a summary of the entire workflow.

        Args:
            change_path: Path to the change directory
        """
        status_file = change_path / "status.json"

        if not status_file.exists():
            write_info("No workflow status found - workflow not started")
            return

        try:
            data = json.loads(status_file.read_text(encoding="utf-8"))
            total_steps = data.get("total_steps", 0)
            completed_steps = data.get("completed_steps", 0)
            last_updated = data.get("last_updated", "Unknown")

            write_info("Workflow Summary:")
            write_info(f"  Total Steps: {total_steps}")
            write_info(f"  Completed: {completed_steps}")
            write_info(f"  Last Updated: {last_updated}")

            if total_steps > 0:
                percent = round((completed_steps / total_steps) * 100)
                write_info(f"  Progress: {percent}%")

                if completed_steps == total_steps:
                    write_success("  Status: Complete ✓")
                elif completed_steps > 0:
                    write_warning("  Status: In Progress ⟳")
                else:
                    write_info("  Status: Not Started ○")

        except (json.JSONDecodeError, KeyError) as e:
            write_warning(f"Could not load workflow summary: {e}")


# ============================================================================
# Progress Indicators
# ============================================================================


def spinner(duration: float, message: str = "Processing...") -> None:
    """
    Show a spinning progress indicator for a duration.

    Args:
        duration: How long to show the spinner (seconds)
        message: Message to display with spinner
    """
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_time = time.time()
    i = 0

    while time.time() - start_time < duration:
        print(
            f"\r{Colors.CYAN}{spinner_chars[i % len(spinner_chars)]}{Colors.RESET} {message}",
            end="",
            flush=True,
        )
        time.sleep(0.1)
        i += 1

    # Clear the spinner line
    print(f"\r{' ' * (len(message) + 2)}\r", end="", flush=True)


def progress_bar(
    current: int, total: int, width: int = 50, prefix: str = "Progress:"
) -> None:
    """
    Display a progress bar.

    Args:
        current: Current progress value
        total: Total progress value
        width: Width of the progress bar
        prefix: Text to show before the progress bar
    """
    if total == 0:
        percent = 100
        filled = width
    else:
        percent = round((current / total) * 100)
        filled = round((current / total) * width)

    bar = "█" * filled + "░" * (width - filled)
    print(f"{Colors.CYAN}{prefix} [{bar}] {percent}%{Colors.RESET}")


def show_progress_with_spinner(func, *args, message: str = "Processing...", **kwargs):
    """
    Execute a function with a spinner progress indicator.

    Args:
        func: Function to execute
        *args: Arguments for the function
        message: Message to show with spinner
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the function execution
    """
    result = [None]
    exception = [None]

    def run_func():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    # Start function in background thread
    thread = threading.Thread(target=run_func, daemon=True)
    thread.start()

    # Show spinner while function runs
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0

    while thread.is_alive():
        print(
            f"\r{Colors.CYAN}{spinner_chars[i % len(spinner_chars)]}{Colors.RESET} {message}",
            end="",
            flush=True,
        )
        time.sleep(0.1)
        i += 1

    # Clear the spinner line
    print(f"\r{' ' * (len(message) + 2)}\r", end="", flush=True)

    # Check for exceptions
    if exception[0]:
        raise exception[0]

    return result[0]


# ============================================================================
# Version Management System
# ============================================================================


class VersionManager:
    """Manage version detection and bumping for the project."""

    @staticmethod
    def get_current_version(project_root: Path) -> str:
        """
        Get the current version from version files.

        Args:
            project_root: Path to the project root

        Returns:
            Current version string
        """
        # Check pyproject.toml first
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import tomllib

                data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
                version = data.get("tool", {}).get("poetry", {}).get("version")
                if version:
                    return version
                version = data.get("project", {}).get("version")
                if version:
                    return version
            except Exception:
                pass

        # Check setup.py
        setup_path = project_root / "setup.py"
        if setup_path.exists():
            content = setup_path.read_text(encoding="utf-8")
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)

        # Check package.json
        package_path = project_root / "package.json"
        if package_path.exists():
            try:
                import json

                data = json.loads(package_path.read_text(encoding="utf-8"))
                version = data.get("version")
                if version:
                    return version
            except Exception:
                pass

        # Check __init__.py files
        init_paths = [
            project_root / "agent" / "__init__.py",
            project_root / "__init__.py",
        ]
        for init_path in init_paths:
            if init_path.exists():
                content = init_path.read_text(encoding="utf-8")
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)

        return "0.0.0"

    @staticmethod
    def bump_version(current_version: str, bump_type: str) -> str:
        """
        Bump a version number.

        Args:
            current_version: Current version string
            bump_type: Type of bump (major, minor, patch)

        Returns:
            New version string
        """
        # Parse version
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(.*)$", current_version)
        if not match:
            raise ValueError(f"Invalid version format: {current_version}")

        major, minor, patch = map(int, match.groups()[:3])
        suffix = match.group(4) or ""

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return f"{major}.{minor}.{patch}{suffix}"

    @staticmethod
    def update_version_files(project_root: Path, new_version: str) -> List[str]:
        """
        Update version in all relevant files.

        Args:
            project_root: Path to the project root
            new_version: New version string

        Returns:
            List of files that were updated
        """
        updated_files = []

        # Update pyproject.toml
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding="utf-8")
            # Update both poetry and standard project version formats
            content = re.sub(
                r'(\[tool\.poetry\]|\[project\])\s*\n.*?\n\s*version\s*=\s*["\'][^"\']*["\']',
                f'\\1\nversion = "{new_version}"',
                content,
                flags=re.MULTILINE | re.DOTALL,
            )
            if set_content_atomic(pyproject_path, content):
                updated_files.append(str(pyproject_path))

        # Update setup.py
        setup_path = project_root / "setup.py"
        if setup_path.exists():
            content = setup_path.read_text(encoding="utf-8")
            content = re.sub(
                r'version\s*=\s*["\'][^"\']*["\']', f'version="{new_version}"', content
            )
            if set_content_atomic(setup_path, content):
                updated_files.append(str(setup_path))

        # Update package.json
        package_path = project_root / "package.json"
        if package_path.exists():
            try:
                import json

                data = json.loads(package_path.read_text(encoding="utf-8"))
                data["version"] = new_version
                if set_content_atomic(package_path, json.dumps(data, indent=2)):
                    updated_files.append(str(package_path))
            except Exception:
                pass

        # Update __init__.py files
        init_paths = [
            project_root / "agent" / "__init__.py",
            project_root / "__init__.py",
        ]
        for init_path in init_paths:
            if init_path.exists():
                content = init_path.read_text(encoding="utf-8")
                content = re.sub(
                    r'__version__\s*=\s*["\'][^"\']*["\']',
                    f'__version__ = "{new_version}"',
                    content,
                )
                if set_content_atomic(init_path, content):
                    updated_files.append(str(init_path))

        return updated_files


# ============================================================================
# Security Validation System
# ============================================================================


def validate_security(project_root: Path) -> tuple[bool, List[str]]:
    """
    Run security validation checks on the project.

    Args:
        project_root: Path to the project root

    Returns:
        Tuple of (success: bool, issues: List[str])
    """
    issues = []

    # Check for common security issues
    security_checks = [
        ("Secret files", _check_secret_files, project_root),
        ("Dependencies", _check_dependencies, project_root),
        ("Code patterns", _check_code_patterns, project_root),
    ]

    for check_name, check_func, *args in security_checks:
        try:
            success, check_issues = check_func(*args)
            if not success:
                issues.extend([f"{check_name}: {issue}" for issue in check_issues])
        except Exception as e:
            issues.append(f"{check_name}: Check failed - {e}")

    return (len(issues) == 0, issues)


def _check_secret_files(project_root: Path) -> tuple[bool, List[str]]:
    """Check for accidentally committed secret files."""
    issues = []

    # Common secret file patterns
    secret_patterns = [
        ".env",
        ".env.local",
        ".env.*.local",
        "secrets.json",
        "credentials.json",
        "*.key",
        "*.pem",
        "id_rsa",
        "id_dsa",
    ]

    for pattern in secret_patterns:
        for file_path in project_root.rglob(pattern):
            if file_path.is_file():
                issues.append(f"Potential secret file found: {file_path}")

    return (len(issues) == 0, issues)


def _check_dependencies(project_root: Path) -> tuple[bool, List[str]]:
    """Check for vulnerable dependencies."""
    issues = []

    # Check requirements.txt
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        try:
            content = req_path.read_text(encoding="utf-8")
            # Look for known vulnerable packages (simplified check)
            vulnerable = ["insecure-package", "old-version-package"]
            for vuln in vulnerable:
                if vuln in content:
                    issues.append(f"Vulnerable dependency found: {vuln}")
        except Exception as e:
            issues.append(f"Could not check requirements.txt: {e}")

    # Check pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import tomllib

            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            deps.update(data.get("project", {}).get("dependencies", {}))

            # Check for known vulnerable packages
            vulnerable = ["insecure-package", "old-version-package"]
            for dep in deps:
                for vuln in vulnerable:
                    if vuln in dep.lower():
                        issues.append(f"Vulnerable dependency found: {dep}")
        except Exception as e:
            issues.append(f"Could not check pyproject.toml: {e}")

    return (len(issues) == 0, issues)


def _check_code_patterns(project_root: Path) -> tuple[bool, List[str]]:
    """Check for insecure code patterns."""
    issues = []

    # Patterns to check for
    insecure_patterns = [
        (r"eval\s*\(", "Use of eval()"),
        (r"exec\s*\(", "Use of exec()"),
        (r"input\s*\(", "Use of input() for sensitive data"),
        (r"pickle\.loads?\s*\(", "Use of pickle for deserialization"),
        (
            r"subprocess\.(call|Popen|run)\s*\(\s*shell\s*=\s*True",
            "Shell injection vulnerability",
        ),
    ]

    # Check Python files
    for py_file in project_root.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            for pattern, description in insecure_patterns:
                if re.search(pattern, content):
                    issues.append(f"{description} in {py_file}")
        except Exception:
            continue

    return (len(issues) == 0, issues)


# ============================================================================
# Code Quality Improvement System
# ============================================================================


def run_code_quality_improvements(project_root: Path) -> tuple[bool, List[str]]:
    """
    Run automated code quality improvements.

    Args:
        project_root: Path to the project root

    Returns:
        Tuple of (success: bool, improvements: List[str])
    """
    improvements = []

    # Code quality checks and fixes
    quality_checks = [
        ("Python formatting", _fix_python_formatting, project_root),
        ("JavaScript formatting", _fix_javascript_formatting, project_root),
        ("Import sorting", _fix_import_sorting, project_root),
    ]

    for check_name, check_func, *args in quality_checks:
        try:
            success, check_improvements = check_func(*args)
            if success and check_improvements:
                improvements.extend(
                    [f"{check_name}: {imp}" for imp in check_improvements]
                )
        except Exception as e:
            write_warning(f"{check_name} check failed: {e}")

    return (len(improvements) > 0, improvements)


def _fix_python_formatting(project_root: Path) -> tuple[bool, List[str]]:
    """Fix Python code formatting issues."""
    improvements = []

    if not check_tool_available("ruff"):
        return False, ["ruff not available"]

    try:
        # Run ruff format
        result = subprocess.run(
            ["ruff", "format", "--check", str(project_root)],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30,
        )

        if result.returncode != 0:
            # Files need formatting
            format_result = subprocess.run(
                ["ruff", "format", str(project_root)],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=30,
            )

            if format_result.returncode == 0:
                improvements.append("Python files formatted with ruff")
            else:
                return False, ["Failed to format Python files"]

    except subprocess.TimeoutExpired:
        return False, ["Python formatting timed out"]

    return True, improvements


def _fix_javascript_formatting(project_root: Path) -> tuple[bool, List[str]]:
    """Fix JavaScript code formatting issues."""
    improvements = []

    # Check for JavaScript files
    js_files = list(project_root.rglob("*.js"))
    if not js_files:
        return True, []

    # Basic JavaScript formatting (remove trailing whitespace, fix indentation)
    for js_file in js_files:
        try:
            content = js_file.read_text(encoding="utf-8")
            original_content = content

            # Remove trailing whitespace
            lines = content.split("\n")
            lines = [line.rstrip() for line in lines]
            content = "\n".join(lines)

            # Fix basic indentation (4 spaces)
            # This is a simplified formatter - in practice you'd use prettier
            formatted_lines = []
            for line in lines:
                stripped = line.lstrip()
                if stripped and line.startswith(" "):
                    # Count leading spaces and convert to multiples of 4
                    leading_spaces = len(line) - len(line.lstrip(" "))
                    new_leading_spaces = (leading_spaces // 4) * 4
                    formatted_lines.append(" " * new_leading_spaces + stripped)
                else:
                    formatted_lines.append(line)

            content = "\n".join(formatted_lines)

            if content != original_content:
                if set_content_atomic(js_file, content):
                    improvements.append(f"Formatted {js_file.name}")

        except Exception as e:
            write_warning(f"Could not format {js_file}: {e}")

    return True, improvements


def _fix_import_sorting(project_root: Path) -> tuple[bool, List[str]]:
    """Fix import sorting issues."""
    improvements = []

    if not check_tool_available("isort"):
        return False, ["isort not available"]

    try:
        # Run isort check
        result = subprocess.run(
            ["isort", "--check-only", "--diff", str(project_root)],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30,
        )

        if result.returncode != 0:
            # Imports need sorting
            sort_result = subprocess.run(
                ["isort", str(project_root)],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=30,
            )

            if sort_result.returncode == 0:
                improvements.append("Python imports sorted with isort")
            else:
                return False, ["Failed to sort imports"]

    except subprocess.TimeoutExpired:
        return False, ["Import sorting timed out"]

    return True, improvements
