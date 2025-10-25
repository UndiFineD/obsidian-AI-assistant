#!/usr/bin/env python3
"""
OpenSpec Workflow - Helper Functions

This module provides shared utility functions for the OpenSpec workflow system,
including output formatting, file operations, validation, and cross-referencing.

Author: Obsidian AI Agent Team
License: MIT
"""

import json
import logging
import logging.handlers
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


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


class LogLevel(Enum):
    """Log verbosity levels."""

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


class StructuredLogger:
    """
    Structured JSON logger for workflow operations.

    Provides both console output (colored) and JSON logging to files.
    Supports different verbosity levels and log rotation.
    """

    def __init__(
        self,
        log_file: Optional[Path] = None,
        level: LogLevel = LogLevel.NORMAL,
        enable_json: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        """
        Initialize structured logger.

        Args:
            log_file: Path to log file (optional)
            level: Logging verbosity level
            enable_json: Whether to write JSON logs
            max_bytes: Max log file size before rotation
            backup_count: Number of backup files to keep
        """
        self.level = level
        self.enable_json = enable_json
        self.log_file = log_file

        # Setup Python logging for JSON output
        if enable_json and log_file:
            self.logger = logging.getLogger("openspec_workflow")
            self.logger.setLevel(logging.DEBUG)

            # Create rotating file handler
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
            handler.setFormatter(logging.Formatter("%(message)s"))  # Raw JSON
            self.logger.addHandler(handler)
        else:
            self.logger = None

    def _should_log(self, message_level: LogLevel) -> bool:
        """Check if message should be logged at current verbosity level."""
        return message_level.value <= self.level.value

    def _log_json(self, event_type: str, data: Dict) -> None:
        """Log structured data as JSON."""
        if not self.enable_json or not self.logger:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "level": self.level.name.lower(),
            **data,
        }

        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

    def log_step_start(
        self, step_id: int, step_name: str, change_id: str, lane: str = "standard"
    ) -> None:
        """Log the start of a workflow step."""
        if not self._should_log(LogLevel.NORMAL):
            return

        self._log_json(
            "step_start",
            {
                "step_id": step_id,
                "step_name": step_name,
                "change_id": change_id,
                "lane": lane,
            },
        )

    def log_step_end(
        self,
        step_id: int,
        step_name: str,
        change_id: str,
        success: bool,
        duration: Optional[float] = None,
        error: Optional[str] = None,
        files_created: Optional[List[str]] = None,
        files_modified: Optional[List[str]] = None,
    ) -> None:
        """Log the completion of a workflow step."""
        if not self._should_log(LogLevel.NORMAL):
            return

        data = {
            "step_id": step_id,
            "step_name": step_name,
            "change_id": change_id,
            "success": success,
            "duration_seconds": duration,
        }

        if error:
            data["error"] = error
        if files_created:
            data["files_created"] = files_created
        if files_modified:
            data["files_modified"] = files_modified

        self._log_json("step_end", data)

    def log_file_operation(
        self,
        operation: str,
        file_path: str,
        change_id: str,
        step_id: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """Log file operations (create, modify, delete)."""
        if not self._should_log(LogLevel.VERBOSE):
            return

        data = {
            "operation": operation,
            "file_path": file_path,
            "change_id": change_id,
            "success": success,
        }

        if step_id is not None:
            data["step_id"] = step_id
        if error:
            data["error"] = error

        self._log_json("file_operation", data)

    def log_command_execution(
        self,
        command: str,
        change_id: str,
        step_id: Optional[int] = None,
        success: bool = True,
        exit_code: Optional[int] = None,
        duration: Optional[float] = None,
        output: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Log external command execution."""
        if not self._should_log(LogLevel.VERBOSE):
            return

        data = {"command": command, "change_id": change_id, "success": success}

        if step_id is not None:
            data["step_id"] = step_id
        if exit_code is not None:
            data["exit_code"] = exit_code
        if duration is not None:
            data["duration_seconds"] = duration
        if output and self._should_log(LogLevel.DEBUG):
            data["output"] = output[:1000]  # Truncate long output
        if error:
            data["error"] = error

        self._log_json("command_execution", data)

    def log_workflow_start(
        self,
        change_id: str,
        title: str,
        owner: str,
        lane: str,
        total_steps: int,
        dry_run: bool = False,
    ) -> None:
        """Log the start of a workflow execution."""
        if not self._should_log(LogLevel.NORMAL):
            return

        self._log_json(
            "workflow_start",
            {
                "change_id": change_id,
                "title": title,
                "owner": owner,
                "lane": lane,
                "total_steps": total_steps,
                "dry_run": dry_run,
            },
        )

    def log_workflow_end(
        self,
        change_id: str,
        success: bool,
        total_duration: Optional[float] = None,
        steps_completed: Optional[int] = None,
    ) -> None:
        """Log the completion of a workflow execution."""
        if not self._should_log(LogLevel.NORMAL):
            return

        data = {"change_id": change_id, "success": success}

        if total_duration is not None:
            data["total_duration_seconds"] = total_duration
        if steps_completed is not None:
            data["steps_completed"] = steps_completed

        self._log_json("workflow_end", data)

    def log_error(
        self,
        message: str,
        change_id: str,
        step_id: Optional[int] = None,
        error_type: str = "general",
        context: Optional[Dict] = None,
    ) -> None:
        """Log error conditions."""
        if not self._should_log(LogLevel.NORMAL):
            return

        data = {"message": message, "change_id": change_id, "error_type": error_type}

        if step_id is not None:
            data["step_id"] = step_id
        if context:
            data["context"] = context

        self._log_json("error", data)

    def log_checkpoint(
        self,
        change_id: str,
        step_id: int,
        checkpoint_id: str,
        operation: str,  # "create", "restore", "delete"
    ) -> None:
        """Log checkpoint operations."""
        if not self._should_log(LogLevel.VERBOSE):
            return

        self._log_json(
            "checkpoint",
            {
                "change_id": change_id,
                "step_id": step_id,
                "checkpoint_id": checkpoint_id,
                "operation": operation,
            },
        )

    def log_agent_execution(
        self,
        change_id: str,
        step_id: int,
        agent_available: bool,
        agent_success: bool,
        fallback_used: bool,
        duration: Optional[float] = None,
        error: Optional[str] = None,
    ) -> None:
        """Log AI agent execution attempts."""
        if not self._should_log(LogLevel.NORMAL):
            return

        data = {
            "change_id": change_id,
            "step_id": step_id,
            "agent_available": agent_available,
            "agent_success": agent_success,
            "fallback_used": fallback_used,
        }

        if duration is not None:
            data["duration_seconds"] = duration
        if error:
            data["error"] = error

        self._log_json("agent_execution", data)


# Global logger instance
_logger: Optional[StructuredLogger] = None


def get_logger() -> StructuredLogger:
    """Get the global structured logger instance."""
    global _logger
    if _logger is None:
        # Default logger configuration
        _logger = StructuredLogger()
    return _logger


def configure_logger(
    log_file: Optional[Path] = None,
    level: LogLevel = LogLevel.NORMAL,
    enable_json: bool = True,
) -> StructuredLogger:
    """Configure the global structured logger."""
    global _logger
    _logger = StructuredLogger(log_file=log_file, level=level, enable_json=enable_json)
    return _logger


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
                else "✗" if status.result == "failure" else "⊘"
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

    @staticmethod
    def generate_summary_report(
        change_path: Path, output_file: Optional[Path] = None
    ) -> str:
        """
        Generate a comprehensive summary report of the workflow.

        Args:
            change_path: Path to the change directory
            output_file: Optional file to save the report to

        Returns:
            The summary report as a string
        """
        # Check for checkpoint state first, then fall back to status.json
        checkpoint_state_file = change_path / ".checkpoints" / "state.json"
        status_file = change_path / "status.json"

        state_data = None
        last_updated = "Unknown"

        # Try to read from checkpoint state first
        if checkpoint_state_file.exists():
            try:
                data = json.loads(checkpoint_state_file.read_text(encoding="utf-8"))
                checkpoints = data.get("checkpoints", [])
                last_successful_step = data.get("last_successful_step", 0)

                # Convert checkpoint data to step format
                steps = []
                for checkpoint in checkpoints:
                    step_data = {
                        "step_id": checkpoint["step_num"],
                        "step_name": checkpoint["step_name"],
                        "result": "success",  # Checkpoints are created before successful steps
                        "duration_seconds": 0,  # Not tracked in checkpoints
                        "timestamp": checkpoint["timestamp"],
                    }
                    steps.append(step_data)

                # Add any remaining steps that haven't been checkpointed
                total_expected_steps = 13  # Standard workflow has 13 steps
                for step_num in range(last_successful_step + 1, total_expected_steps):
                    if step_num not in [cp["step_num"] for cp in checkpoints]:
                        steps.append({
                            "step_id": step_num,
                            "step_name": f"Step {step_num}",
                            "result": "pending",
                            "duration_seconds": 0,
                        })

                state_data = {
                    "steps": steps,
                    "total_steps": total_expected_steps,
                    "completed_steps": last_successful_step + 1,
                    "last_updated": checkpoints[-1]["timestamp"] if checkpoints else "Unknown"
                }
                last_updated = state_data["last_updated"]

            except (json.JSONDecodeError, KeyError) as e:
                # Fall back to status.json if checkpoint parsing fails
                pass

        # Fall back to status.json if checkpoint data not available
        if state_data is None and status_file.exists():
            try:
                data = json.loads(status_file.read_text(encoding="utf-8"))
                steps = data.get("steps", [])
                total_steps = data.get("total_steps", 0)
                completed_steps = data.get("completed_steps", 0)
                last_updated = data.get("last_updated", "Unknown")

                state_data = {
                    "steps": steps,
                    "total_steps": total_steps,
                    "completed_steps": completed_steps,
                    "last_updated": last_updated
                }

            except (json.JSONDecodeError, KeyError) as e:
                pass

        if not state_data:
            report = "No workflow status found - workflow not started"
            if output_file:
                output_file.write_text(report, encoding="utf-8")
            return report

        # Extract data from state
        steps = state_data.get("steps", [])
        total_steps = state_data.get("total_steps", len(steps))
        completed_steps = state_data.get("completed_steps", len([s for s in steps if s.get("result") == "success"]))
        last_updated = state_data.get("last_updated", "Unknown")

        # Calculate metrics
        successful_steps = len([s for s in steps if s.get("result") == "success"])
        failed_steps = len([s for s in steps if s.get("result") == "failure"])
        skipped_steps = len([s for s in steps if s.get("result") == "skipped"])
        pending_steps = len([s for s in steps if s.get("result") == "pending"])

        total_duration = sum(
            s.get("duration_seconds", 0) for s in steps if s.get("duration_seconds")
        )
        avg_duration = total_duration / len([s for s in steps if s.get("duration_seconds")]) if any(s.get("duration_seconds") for s in steps) else 0

        # Generate report
        report_lines = [
            "# Workflow Summary Report",
            "",
            f"**Change ID:** {change_path.name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Last Updated:** {last_updated}",
            "",
            "## Progress Overview",
            "",
            f"- **Total Steps:** {total_steps}",
            f"- **Completed Steps:** {completed_steps}",
            f"- **Successful Steps:** {successful_steps}",
            f"- **Failed Steps:** {failed_steps}",
            f"- **Skipped Steps:** {skipped_steps}",
            f"- **Pending Steps:** {pending_steps}",
            "",
            "## Performance Metrics",
            "",
            f"- **Total Duration:** {total_duration:.1f} seconds",
            f"- **Average Step Duration:** {avg_duration:.1f} seconds",
            (
                f"- **Completion Rate:** {(successful_steps/total_steps*100):.1f}%"
                if total_steps > 0
                else "0%"
            ),
            "",
            "## Step Details",
            "",
        ]

        # Add step details
        for step_data in sorted(steps, key=lambda x: x["step_id"]):
            step_id = step_data["step_id"]
            step_name = step_data.get("step_name", f"Step {step_id}")
            result = step_data.get("result", "pending")
            duration = step_data.get("duration_seconds", 0)

            status_icon = {
                "success": "✅",
                "failure": "❌",
                "skipped": "⏭️",
                "in_progress": "🔄",
                "pending": "⏳",
            }.get(result, "❓")

            report_lines.append(f"### {status_icon} Step {step_id}: {step_name}")
            report_lines.append(f"- **Status:** {result}")
            report_lines.append(
                f"- **Duration:** {duration:.1f}s"
                if duration
                else "- **Duration:** N/A"
            )

            if step_data.get("files_created"):
                report_lines.append(
                    f"- **Files Created:** {', '.join(step_data['files_created'])}"
                )

            if step_data.get("errors"):
                report_lines.append(
                    f"- **Errors:** {len(step_data['errors'])} error(s)"
                )

            if step_data.get("metrics"):
                report_lines.append("- **Metrics:**")
                for key, value in step_data["metrics"].items():
                    report_lines.append(f"  - {key}: {value}")

            report_lines.append("")

        report = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report, encoding="utf-8")
            write_success(f"Summary report saved to {output_file}")

        return report

    @staticmethod
    def generate_quality_metrics_report(
        change_path: Path, project_root: Path, output_file: Optional[Path] = None
    ) -> str:
        """
        Generate a quality metrics report for the workflow and codebase.

        Args:
            change_path: Path to the change directory
            project_root: Path to the project root
            output_file: Optional file to save the report to

        Returns:
            The quality metrics report as a string
        """
        try:
            report_lines = [
                "# Quality Metrics Report",
                "",
                f"**Change ID:** {change_path.name}",
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## Code Quality Metrics",
                "",
            ]

            # Check for quality tools
            tools_status = {
                "pytest": check_tool_available("pytest"),
                "ruff": check_tool_available("ruff"),
                "mypy": check_tool_available("mypy"),
                "bandit": check_tool_available("bandit"),
                "isort": check_tool_available("isort"),
            }

            report_lines.append("### Tool Availability")
            for tool, available in tools_status.items():
                status = "✅ Available" if available else "❌ Not Available"
                report_lines.append(f"- **{tool}:** {status}")
            report_lines.append("")

            # Run quality checks if tools are available
            if tools_status["ruff"]:
                report_lines.append("### Code Quality Checks")
                try:
                    result = subprocess.run(
                        ["ruff", "check", "--output-format=json", str(project_root)],
                        capture_output=True,
                        text=True,
                        cwd=project_root,
                        timeout=60,
                    )
                    if result.returncode == 0:
                        report_lines.append("✅ **Ruff:** No issues found")
                    else:
                        try:
                            issues = json.loads(result.stdout)
                            report_lines.append(f"⚠️ **Ruff:** {len(issues)} issue(s) found")
                            # Group by severity
                            severity_count = {}
                            for issue in issues:
                                severity = issue.get("code", "UNK")[
                                    :1
                                ]  # First letter indicates severity
                                severity_count[severity] = (
                                    severity_count.get(severity, 0) + 1
                                )
                            for severity, count in severity_count.items():
                                report_lines.append(f"  - {severity}: {count} issue(s)")
                        except json.JSONDecodeError:
                            report_lines.append(
                                "⚠️ **Ruff:** Issues found (could not parse output)"
                            )
                except subprocess.TimeoutExpired:
                    report_lines.append("⏱️ **Ruff:** Check timed out")
                except Exception as e:
                    report_lines.append(f"❌ **Ruff:** Check failed - {e}")
                report_lines.append("")

            # Security checks
            report_lines.append("### Security Analysis")
            try:
                security_success, security_issues = validate_security(project_root)
                if security_success:
                    report_lines.append("✅ **Security:** No issues found")
                else:
                    report_lines.append(
                        f"⚠️ **Security:** {len(security_issues)} issue(s) found"
                    )
                    for issue in security_issues[:10]:  # Limit to first 10
                        report_lines.append(f"  - {issue}")
                    if len(security_issues) > 10:
                        report_lines.append(f"  ... and {len(security_issues) - 10} more")
            except Exception as e:
                report_lines.append(f"❌ **Security:** Analysis failed - {e}")
            report_lines.append("")

            # Test coverage (if available)
            if tools_status["pytest"]:
                report_lines.append("### Test Coverage")
                coverage_file = project_root / "coverage.xml"
                if coverage_file.exists():
                    try:
                        import xml.etree.ElementTree as ET

                        tree = ET.parse(coverage_file)
                        root = tree.getroot()
                        line_rate = root.get("line-rate")
                        if line_rate:
                            coverage_percent = float(line_rate) * 100
                            report_lines.append(f"📊 **Coverage:** {coverage_percent:.1f}%")
                        else:
                            report_lines.append(
                                "📊 **Coverage:** Data available but could not parse"
                            )
                    except Exception as e:
                        report_lines.append(
                            f"📊 **Coverage:** Could not read coverage data - {e}"
                        )
                else:
                    report_lines.append(
                        "📊 **Coverage:** No coverage data found (run tests with coverage)"
                    )
                report_lines.append("")

            # Workflow quality metrics - read from checkpoint data first
            checkpoint_state_file = change_path / ".checkpoints" / "state.json"
            status_file = change_path / "status.json"

            workflow_data = None

            # Try to read from checkpoint state first
            if checkpoint_state_file.exists():
                try:
                    data = json.loads(checkpoint_state_file.read_text(encoding="utf-8"))
                    checkpoints = data.get("checkpoints", [])
                    last_successful_step = data.get("last_successful_step", 0)

                    # Convert checkpoint data to step format
                    steps = []
                    for checkpoint in checkpoints:
                        step_data = {
                            "step_id": checkpoint["step_num"],
                            "step_name": checkpoint["step_name"],
                            "result": "success",
                            "duration_seconds": 0,
                            "errors": [],
                            "files_created": [],
                            "metrics": {},
                        }
                        steps.append(step_data)

                    workflow_data = {"steps": steps}

                except (json.JSONDecodeError, KeyError) as e:
                    pass

            # Fall back to status.json if checkpoint data not available
            if workflow_data is None and status_file.exists():
                try:
                    workflow_data = json.loads(status_file.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, KeyError) as e:
                    pass

            if workflow_data:
                steps = workflow_data.get("steps", [])

                report_lines.append("### Workflow Quality Metrics")
                report_lines.append("")

                # Success rate
                successful_steps = len(
                    [s for s in steps if s.get("result") == "success"]
                )
                total_steps = len(steps)
                if total_steps > 0:
                    success_rate = (successful_steps / total_steps) * 100
                    report_lines.append(f"- **Step Success Rate:** {success_rate:.1f}%")

                # Error analysis
                error_steps = [s for s in steps if s.get("errors")]
                if error_steps:
                    total_errors = sum(len(s.get("errors", [])) for s in error_steps)
                    report_lines.append(f"- **Steps with Errors:** {len(error_steps)}")
                    report_lines.append(f"- **Total Errors:** {total_errors}")

                # Performance analysis
                durations = [
                    s.get("duration_seconds", 0)
                    for s in steps
                    if s.get("duration_seconds")
                ]
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    max_duration = max(durations)
                    report_lines.append(
                        f"- **Average Step Duration:** {avg_duration:.1f}s"
                    )
                    report_lines.append(
                        f"- **Longest Step Duration:** {max_duration:.1f}s"
                    )
            else:
                report_lines.append("### Workflow Quality Metrics")
                report_lines.append("❌ No workflow data available for quality analysis")
                report_lines.append("")

            report = "\n".join(report_lines)

            if output_file:
                output_file.write_text(report, encoding="utf-8")
                write_success(f"Quality metrics report saved to {output_file}")

            return report

        except Exception as e:
            write_error(f"Could not generate quality metrics report: {e}")
            error_report = f"Error generating quality metrics report: {e}"
            if output_file:
                output_file.write_text(error_report, encoding="utf-8")
            return error_report

    @staticmethod
    def generate_cross_validation_report(
        change_path: Path, project_root: Path, output_file: Optional[Path] = None
    ) -> str:
        """
        Generate a cross-validation report checking consistency across workflow outputs.

        Args:
            change_path: Path to the change directory
            project_root: Path to the project root
            output_file: Optional file to save the report to

        Returns:
            The cross-validation report as a string
        """
        report_lines = [
            "# Cross-Validation Report",
            "",
            f"**Change ID:** {change_path.name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Validation Overview",
            "",
            "This report validates consistency across workflow outputs and project state.",
            "",
            "## File Consistency Checks",
            "",
        ]

        # Check for required files
        required_files = ["proposal.md", "spec.md", "tasks.md", "status.json"]

        for filename in required_files:
            file_path = change_path / filename
            if file_path.exists():
                report_lines.append(f"✅ **{filename}:** Present")
            else:
                report_lines.append(f"❌ **{filename}:** Missing")

        report_lines.append("")

        # Check version consistency
        report_lines.append("## Version Consistency")
        report_lines.append("")

        try:
            current_version = VersionManager.get_current_version(project_root)
            report_lines.append(f"✅ **Current Project Version:** {current_version}")

            # Check if version was updated in workflow
            version_snapshot = change_path / "version_snapshot.md"
            if version_snapshot.exists():
                content = version_snapshot.read_text(encoding="utf-8")
                # Look for version information in the snapshot
                version_match = re.search(r"(\d+\.\d+\.\d+)", content)
                if version_match:
                    workflow_version = version_match.group(1)
                    report_lines.append(f"✅ **Workflow Version:** {workflow_version}")
                    if workflow_version == current_version:
                        report_lines.append(
                            "✅ **Version Consistency:** Versions match"
                        )
                    else:
                        report_lines.append(
                            f"⚠️ **Version Consistency:** Version mismatch (workflow: {workflow_version}, current: {current_version})"
                        )
                else:
                    report_lines.append(
                        "⚠️ **Workflow Version:** Could not extract from snapshot"
                    )
            else:
                report_lines.append(
                    "❌ **Workflow Version:** No version snapshot found"
                )

        except Exception as e:
            report_lines.append(f"❌ **Version Check:** Failed - {e}")

        report_lines.append("")

        # Validate workflow status consistency - read from checkpoint data first
        checkpoint_state_file = change_path / ".checkpoints" / "state.json"
        status_file = change_path / "status.json"

        workflow_data = None

        # Try to read from checkpoint state first
        if checkpoint_state_file.exists():
            try:
                data = json.loads(checkpoint_state_file.read_text(encoding="utf-8"))
                checkpoints = data.get("checkpoints", [])
                last_successful_step = data.get("last_successful_step", 0)

                # Convert checkpoint data to step format
                steps = []
                for checkpoint in checkpoints:
                    step_data = {
                        "step_id": checkpoint["step_num"],
                        "step_name": checkpoint["step_name"],
                        "result": "success",
                        "duration_seconds": 0,
                        "errors": [],
                        "files_created": [],
                        "metrics": {},
                    }
                    steps.append(step_data)

                workflow_data = {"steps": steps, "total_steps": 13, "completed_steps": last_successful_step + 1}

            except (json.JSONDecodeError, KeyError) as e:
                pass

        # Fall back to status.json if checkpoint data not available
        if workflow_data is None and status_file.exists():
            try:
                workflow_data = json.loads(status_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, KeyError) as e:
                pass

        if workflow_data:
            steps = workflow_data.get("steps", [])
            total_steps = workflow_data.get("total_steps", 0)
            completed_steps = workflow_data.get("completed_steps", 0)

            # Check step count consistency
            if len(steps) == total_steps:
                report_lines.append("✅ **Step Count:** Consistent")
            else:
                report_lines.append(
                    f"⚠️ **Step Count:** Mismatch (recorded: {len(steps)}, expected: {total_steps})"
                )

            # Check completed steps consistency
            actual_completed = len(
                [s for s in steps if s.get("result") == "success"]
            )
            if actual_completed == completed_steps:
                report_lines.append("✅ **Completed Steps:** Consistent")
            else:
                report_lines.append(
                    f"⚠️ **Completed Steps:** Mismatch (recorded: {completed_steps}, actual: {actual_completed})"
                )

            # Check for orphaned files
            all_created_files = []
            for step in steps:
                all_created_files.extend(step.get("files_created", []))

            orphaned_files = []
            for created_file in all_created_files:
                file_path = change_path / created_file
                if not file_path.exists():
                    orphaned_files.append(created_file)

            if orphaned_files:
                report_lines.append(
                    f"⚠️ **Orphaned Files:** {len(orphaned_files)} file(s) marked as created but not found"
                )
                for orphaned in orphaned_files[:5]:  # Show first 5
                    report_lines.append(f"  - {orphaned}")
                if len(orphaned_files) > 5:
                    report_lines.append(f"  ... and {len(orphaned_files) - 5} more")
            else:
                report_lines.append(
                    "✅ **File Tracking:** All created files present"
                )
        else:
            report_lines.append(f"❌ **Workflow Validation:** No workflow data available")

        # Check for consistency between documents
        report_lines.append("## Document Consistency")
        report_lines.append("")

        proposal_file = change_path / "proposal.md"
        spec_file = change_path / "spec.md"
        tasks_file = change_path / "tasks.md"

        documents = [
            ("Proposal", proposal_file),
            ("Specification", spec_file),
            ("Tasks", tasks_file),
        ]

        for doc_name, doc_path in documents:
            if doc_path.exists():
                try:
                    content = doc_path.read_text(encoding="utf-8")
                    word_count = len(content.split())
                    line_count = len(content.split("\n"))
                    report_lines.append(
                        f"✅ **{doc_name}:** {word_count} words, {line_count} lines"
                    )
                except Exception as e:
                    report_lines.append(f"❌ **{doc_name}:** Could not read - {e}")
            else:
                report_lines.append(f"❌ **{doc_name}:** File not found")

        report_lines.append("")

        report = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report, encoding="utf-8")
            write_success(f"Cross-validation report saved to {output_file}")

        return report

    @staticmethod
    def generate_performance_report(
        change_path: Path, output_file: Optional[Path] = None
    ) -> str:
        """
        Generate a performance analysis report for the workflow.

        Args:
            change_path: Path to the change directory
            output_file: Optional file to save the report to

        Returns:
            The performance report as a string
        """
        # Read workflow data from checkpoint first, then status.json
        checkpoint_state_file = change_path / ".checkpoints" / "state.json"
        status_file = change_path / "status.json"

        workflow_data = None

        # Try to read from checkpoint state first
        if checkpoint_state_file.exists():
            try:
                data = json.loads(checkpoint_state_file.read_text(encoding="utf-8"))
                checkpoints = data.get("checkpoints", [])

                # Convert checkpoint data to step format
                steps = []
                for checkpoint in checkpoints:
                    step_data = {
                        "step_id": checkpoint["step_num"],
                        "step_name": checkpoint["step_name"],
                        "result": "success",
                        "duration_seconds": 0,  # Not tracked in checkpoints
                    }
                    steps.append(step_data)

                workflow_data = {"steps": steps}

            except (json.JSONDecodeError, KeyError) as e:
                pass

        # Fall back to status.json if checkpoint data not available
        if workflow_data is None and status_file.exists():
            try:
                workflow_data = json.loads(status_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, KeyError) as e:
                pass

        if not workflow_data:
            report = "No workflow status found - cannot generate performance report"
            if output_file:
                output_file.write_text(report, encoding="utf-8")
            return report

        report_lines = [
            "# Performance Analysis Report",
            "",
            f"**Change ID:** {change_path.name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Performance Overview",
            "",
        ]

        steps = workflow_data.get("steps", [])

        if not steps:
            report_lines.append("No step data available for performance analysis.")
            report = "\n".join(report_lines)
            if output_file:
                output_file.write_text(report, encoding="utf-8")
            return report

        # Calculate performance metrics
        durations = [
            s.get("duration_seconds", 0) for s in steps if s.get("duration_seconds")
        ]
        successful_durations = [
            s.get("duration_seconds", 0)
            for s in steps
            if s.get("duration_seconds") and s.get("result") == "success"
        ]

        if durations:
            total_duration = sum(durations)
            avg_duration = total_duration / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)

            report_lines.append("### Overall Performance")
            report_lines.append(
                f"- **Total Workflow Duration:** {total_duration:.1f} seconds"
            )
            report_lines.append(
                f"- **Average Step Duration:** {avg_duration:.1f} seconds"
            )
            report_lines.append(f"- **Fastest Step:** {min_duration:.1f} seconds")
            report_lines.append(f"- **Slowest Step:** {max_duration:.1f} seconds")
            report_lines.append("")

            # Performance distribution
            report_lines.append("### Performance Distribution")
            if len(durations) > 1:
                # Calculate percentiles
                sorted_durations = sorted(durations)
                p50 = sorted_durations[len(sorted_durations) // 2]
                p90 = sorted_durations[int(len(sorted_durations) * 0.9)]
                p95 = sorted_durations[int(len(sorted_durations) * 0.95)]

                report_lines.append(
                    f"- **50th Percentile (Median):** {p50:.1f} seconds"
                )
                report_lines.append(f"- **90th Percentile:** {p90:.1f} seconds")
                report_lines.append(f"- **95th Percentile:** {p95:.1f} seconds")
            report_lines.append("")

        # Step-by-step performance breakdown
        report_lines.append("### Step Performance Breakdown")
        report_lines.append("")

        # Sort steps by duration (descending)
        steps_with_duration = [
            (s, s.get("duration_seconds", 0))
            for s in steps
            if s.get("duration_seconds")
        ]
        steps_with_duration.sort(key=lambda x: x[1], reverse=True)

        for step, duration in steps_with_duration[:10]:  # Top 10 slowest
            step_id = step["step_id"]
            step_name = step.get("step_name", f"Step {step_id}")
            result = step.get("result", "unknown")

            status_icon = (
                "✅"
                if result == "success"
                else "❌" if result == "failure" else "⚠️"
            )
            report_lines.append(
                f"1. **{status_icon} {step_name}** ({step_id}): {duration:.1f}s"
            )

        report = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report, encoding="utf-8")
            write_success(f"Performance report saved to {output_file}")

        return report


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


def validate_security(project_root: Path) -> tuple[bool, List[str]]:
    """
    Validate security configuration and files.

    Args:
        project_root: Path to the project root directory

    Returns:
        Tuple of (success: bool, issues: List[str])
    """
    try:
        # Import the validate_security module
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "validate_security", project_root / "scripts" / "validate_security.py"
        )
        if spec is None or spec.loader is None:
            return False, ["Could not load validate_security module"]

        validate_security_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate_security_module)

        # Call the validation function
        success, issues = validate_security_module.validate_security_workflow()
        return success, issues

    except Exception as e:
        return False, [f"Security validation failed: {str(e)}"]


def run_code_quality_improvements(project_root: Path) -> tuple[bool, List[str]]:
    """
    Run automated code quality improvements.

    Args:
        project_root: Path to the project root directory

    Returns:
        Tuple of (success: bool, improvements: List[str])
    """
    try:
        # Run the code quality improvements script
        script_path = project_root / "scripts" / "code_quality_improvements.py"

        if not script_path.exists():
            return False, ["Code quality improvements script not found"]

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=300,  # 5 minute timeout
        )

        improvements = []

        if result.returncode == 0:
            # Parse output for improvements made
            lines = result.stdout.split("\n")
            for line in lines:
                if "[ok]" in line or "[PASS]" in line or "Fixed" in line:
                    improvements.append(line.strip())
            return True, (
                improvements if improvements else ["Code quality checks completed"]
            )
        else:
            # Check stderr for specific errors
            error_lines = result.stderr.split("\n") if result.stderr else []
            return False, (
                error_lines if error_lines else ["Code quality improvements failed"]
            )

    except subprocess.TimeoutExpired:
        return False, ["Code quality improvements timed out"]
    except Exception as e:
        return False, [f"Code quality improvements failed: {str(e)}"]
