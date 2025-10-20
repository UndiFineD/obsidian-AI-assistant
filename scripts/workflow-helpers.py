#!/usr/bin/env python3
"""
OpenSpec Workflow - Helper Functions

This module provides shared utility functions for the OpenSpec workflow system,
including output formatting, file operations, validation, and cross-referencing.

Author: Obsidian AI Assistant Team
License: MIT
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ANSI color codes for terminal output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def write_step(number: int, description: str) -> None:
    """Format and display a step header."""
    print(f"\n{Colors.CYAN}═════════  STEP {number}: {description} ═════════{Colors.RESET}")


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
            content = todo_path.read_text(encoding='utf-8')
            completed = len(re.findall(r'- \[x\]', content))
            total = len(re.findall(r'- \[[ x]\]', content))
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
    required_files = ['todo.md', 'proposal.md', 'spec.md', 'tasks.md', 'test_plan.md']
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
        'proposal_to_tasks': [],
        'spec_to_test_plan': [],
        'tasks_to_spec': [],
        'orphaned_references': []
    }
    
    # Load all documentation files
    docs = {}
    for doc_name in ['proposal', 'spec', 'tasks', 'test_plan']:
        doc_path = change_path / f"{doc_name}.md"
        if doc_path.exists():
            docs[doc_name] = doc_path.read_text(encoding='utf-8')
        else:
            docs[doc_name] = None
    
    # Validation 1: Verify all "What Changes" from proposal.md appear in tasks.md
    if docs['proposal'] and docs['tasks']:
        print(f"{Colors.CYAN}  [CROSS-VALIDATION] Checking proposal.md → tasks.md alignment...{Colors.RESET}")
        
        # Extract "What Changes" section
        what_match = re.search(r'##\s+What Changes\s+(.+?)(?=##|$)', docs['proposal'], re.DOTALL)
        if what_match:
            changes_block = what_match.group(1)
            proposal_changes = re.findall(r'(?m)^\s*-\s+(.+?)$', changes_block)
            
            missing_in_tasks = []
            for change in proposal_changes:
                # Skip template placeholders
                if re.match(r'^\[.*\]$', change):
                    continue
                
                # Check if change is referenced in tasks.md
                # Use first 30 chars as search pattern
                change_pattern = re.escape(change[:min(30, len(change))])
                if not re.search(change_pattern, docs['tasks']):
                    missing_in_tasks.append(change)
            
            if missing_in_tasks:
                result.issues.append(
                    f"Proposal changes missing from tasks.md: {len(missing_in_tasks)} item(s)"
                )
                for missing in missing_in_tasks:
                    result.warnings.append(f"  → Missing in tasks.md: '{missing}'")
                result.is_valid = False
            else:
                result.cross_references['proposal_to_tasks'] = proposal_changes
                print(f"{Colors.GREEN}    ✓ All proposal changes referenced in tasks.md{Colors.RESET}")
    
    # Validation 2: Verify spec.md acceptance criteria match test_plan.md test cases
    if docs['spec'] and docs['test_plan']:
        print(f"{Colors.CYAN}  [CROSS-VALIDATION] Checking spec.md → test_plan.md alignment...{Colors.RESET}")
        
        # Extract acceptance criteria
        criteria_match = re.search(
            r'##\s+Acceptance Criteria\s+(.+?)(?=\r?\n##\s|\Z)',
            docs['spec'],
            re.DOTALL
        )
        
        acceptance_criteria = []
        if criteria_match:
            criteria_block = criteria_match.group(1)
            acceptance_criteria = re.findall(r'(?m)^\s*-\s+\[\s?\]\s+(.+?)$', criteria_block)
        
        # Check coverage against test_plan.md
        criteria_without_tests = []
        for criteria in acceptance_criteria:
            # Skip template placeholders
            if re.match(r'^\[.*\]$', criteria) or 'provides' in criteria.lower():
                continue
            
            # Extract key terms for matching (words > 4 chars)
            key_terms = [w for w in re.findall(r'\w+', criteria) if len(w) > 4][:3]
            
            has_test_coverage = False
            for term in key_terms:
                if re.search(re.escape(term), docs['test_plan'], re.IGNORECASE):
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
            result.cross_references['spec_to_test_plan'] = acceptance_criteria
            print(f"{Colors.GREEN}    ✓ Acceptance criteria have test coverage{Colors.RESET}")
    
    # Validation 3: Verify tasks.md implementation tasks align with spec.md requirements
    if docs['tasks'] and docs['spec']:
        print(f"{Colors.CYAN}  [CROSS-VALIDATION] Checking tasks.md → spec.md alignment...{Colors.RESET}")
        
        # Extract requirements from spec.md
        req_match = re.search(
            r'##\s+(?:Requirements|Functional Requirements)\s+(.+?)(?=\r?\n##\s|\Z)',
            docs['spec'],
            re.DOTALL
        )
        
        spec_requirements = []
        if req_match:
            req_block = req_match.group(1)
            spec_requirements = re.findall(r'(?m)^\s*-\s+(.+?)$', req_block)
        
        # Extract implementation tasks from tasks.md
        impl_match = re.search(
            r'##\s+1\.\s+Implementation\s+(.+?)(?=\r?\n##\s|\Z)',
            docs['tasks'],
            re.DOTALL
        )
        
        impl_tasks = []
        if impl_match:
            impl_block = impl_match.group(1)
            impl_tasks = re.findall(r'(?m)^\s*-\s+\[\s?\]\s+(.+?)$', impl_block)
        
        # Check alignment
        requirements_without_tasks = []
        for req in spec_requirements:
            # Skip template placeholders
            if re.match(r'^\[.*\]$', req) or req.startswith(('Remove', 'Update', 'Identify', 'Archive')):
                continue
            
            # Extract key terms
            key_terms = [w for w in re.findall(r'\w+', req) if len(w) > 4][:3]
            
            has_task = False
            for term in key_terms:
                if re.search(re.escape(term), docs['tasks'], re.IGNORECASE):
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
            result.cross_references['tasks_to_spec'] = impl_tasks
            print(f"{Colors.GREEN}    ✓ Spec requirements have implementation tasks{Colors.RESET}")
    
    # Validation 4: Check for orphaned references (broken links)
    print(f"{Colors.CYAN}  [CROSS-VALIDATION] Checking for orphaned references...{Colors.RESET}")
    
    all_docs = [docs[k] for k in ['proposal', 'spec', 'tasks', 'test_plan'] if docs[k]]
    orphaned_refs = []
    
    for doc in all_docs:
        # Find markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', doc)
        for link_text, link_path in links:
            # Skip external URLs
            if link_path.startswith(('http://', 'https://')):
                continue
            
            # Check if referenced file exists
            full_link_path = change_path / link_path
            if not full_link_path.exists():
                orphaned_refs.append(f"{link_text} → {link_path}")
    
    if orphaned_refs:
        result.warnings.append(f"Found orphaned references: {len(orphaned_refs)} link(s)")
        for orphan in orphaned_refs[:3]:
            result.warnings.append(f"  → Broken link: {orphan}")
    else:
        print(f"{Colors.GREEN}    ✓ No orphaned references found{Colors.RESET}")
    
    # Validation 5: Verify affected files consistency across documents
    print(f"{Colors.CYAN}  [CROSS-VALIDATION] Checking affected files consistency...{Colors.RESET}")
    
    affected_files_proposal = []
    affected_files_spec = []
    
    if docs['proposal']:
        match = re.search(r'(?m)^-\s*\*\*Affected files\*\*:\s*(.+)', docs['proposal'])
        if match:
            affected_files_proposal = [f.strip() for f in match.group(1).split(',')]
    
    if docs['spec']:
        match = re.search(r'(?m)^-\s*\*\*Affected files\*\*:\s*(.+)', docs['spec'])
        if match:
            affected_files_spec = [f.strip() for f in match.group(1).split(',')]
    
    if affected_files_proposal and affected_files_spec:
        # Find differences
        only_in_proposal = set(affected_files_proposal) - set(affected_files_spec)
        only_in_spec = set(affected_files_spec) - set(affected_files_proposal)
        
        if only_in_proposal or only_in_spec:
            result.warnings.append("Affected files mismatch between proposal.md and spec.md")
            for file in only_in_proposal:
                result.warnings.append(f"  → {file} (in proposal, missing in spec)")
            for file in only_in_spec:
                result.warnings.append(f"  → {file} (in spec, missing in proposal)")
        else:
            print(f"{Colors.GREEN}    ✓ Affected files consistent across documents{Colors.RESET}")
    
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
        file_path.write_text(content, encoding='utf-8')
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
        content = proposal_path.read_text(encoding='utf-8')
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
        content = spec_path.read_text(encoding='utf-8')
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
        content = tasks_path.read_text(encoding='utf-8')
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
        content = plan_path.read_text(encoding='utf-8')
        if "## Strategy" not in content:
            res.suggestions.append("Consider adding '## Strategy' section")
        return res


class TemplateManager:
    """Manage workflow templates for common scenarios."""
    
    TEMPLATES = {
        'feature': 'proposal-feature.md',
        'bugfix': 'proposal-bugfix.md',
        'docs': 'proposal-docs.md',
        'refactor': 'proposal-refactor.md',
        'default': None  # Uses basic scaffold
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
            template_type = 'default'
        
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
            content = template_path.read_text(encoding='utf-8')
        
        # Substitute placeholders
        content = content.replace('<date>', datetime.utcnow().strftime("%Y-%m-%d"))
        content = content.replace('<owner>', '[owner]')
        content = content.replace('<reviewers>', '[reviewers]')
        
        # Optionally substitute title
        if title:
            content = re.sub(r'# Proposal:?\s*\[.*?\]', f'# Proposal: {title}', content)
        
        return content
    
    @classmethod
    def describe_template(cls, template_type: str) -> str:
        """Get a description of what a template is for."""
        descriptions = {
            'feature': 'New functionality or capability addition',
            'bugfix': 'Fixing incorrect behavior or defects',
            'docs': 'Documentation creation or updates',
            'refactor': 'Code quality improvements without behavior changes',
            'default': 'Generic proposal with basic sections'
        }
        return descriptions.get(template_type, 'Unknown template type')


class DocumentGenerator:
    """Generate contextual scaffolds from existing docs."""

    def _extract_proposal_changes(self, proposal_text: str) -> List[str]:
        m = re.search(r'##\s+What Changes\s+(.+?)(?=##|$)', proposal_text, re.DOTALL)
        if not m:
            return []
        block = m.group(1)
        return re.findall(r'(?m)^\s*-\s+(.+?)$', block)

    def generate_spec_from_proposal(self, proposal_path: Path, title: Optional[str] = None) -> str:
        if not proposal_path.exists():
            title_line = f"# Specification{': ' + title if title else ''}\n\n"
            return title_line + "## Requirements\n\n- **R-01**: ...\n\n## Acceptance Criteria\n\n- [ ] ...\n"
        proposal = proposal_path.read_text(encoding='utf-8')
        changes = [c for c in self._extract_proposal_changes(proposal) if not re.match(r'^\[.*\]$', c)]
        title_line = f"# Specification{': ' + title if title else ''}\n\n"
        out = [title_line, "## Requirements\n\n"]
        for i, c in enumerate(changes, 1):
            out.append(f"- **R-{i:02d}**: {c}\n")
        out.append("\n## Acceptance Criteria\n\n")
        for i, c in enumerate(changes, 1):
            out.append(f"- [ ] AC-{i:02d}: Verify {c.lower()}\n")
        out.append("\n")
        return ''.join(out)

    def generate_tasks_from_spec(self, spec_path: Path, title: Optional[str] = None) -> str:
        title_line = f"# Task Breakdown{': ' + title if title else ''}\n\n"
        if not spec_path.exists():
            return title_line + "## Tasks\n\n- [ ] Implement ...\n\n## Dependencies\n\n- ...\n"
        spec = spec_path.read_text(encoding='utf-8')
        reqs = re.findall(r'(?m)^\s*-\s+\*\*R-(\d+)\*\*: (.+)$', spec)
        out = [title_line, "## Tasks\n\n"]
        for _, text in reqs:
            out.append(f"- [ ] Implement: {text}\n")
        out.append("\n## Dependencies\n\n- ...\n")
        return ''.join(out)

    def generate_test_plan(self, spec_path: Path, tasks_path: Path, title: Optional[str] = None) -> str:
        title_line = f"# Test Plan{': ' + title if title else ''}\n\n## Strategy\n\nDescribe the test approach.\n\n"
        spec = spec_path.read_text(encoding='utf-8') if spec_path.exists() else ""
        tasks = tasks_path.read_text(encoding='utf-8') if tasks_path.exists() else ""
        ac = re.findall(r'(?m)^\s*-\s+\[[ x]\]\s+(.+)$', spec)
        impl = re.findall(r'(?m)^\s*-\s+\[[ x]\]\s+(.+)$', tasks)
        out = [title_line, "## Mapping to Acceptance Criteria\n\n"]
        for item in ac:
            out.append(f"- {item}\n")
        out.append("\n## Test Cases\n\n")
        for item in impl[:10]:
            out.append(f"- [ ] {item}\n")
        out.append("\n")
        return ''.join(out)
