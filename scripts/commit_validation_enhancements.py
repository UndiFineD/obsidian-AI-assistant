#!/usr/bin/env python3
"""
Enhanced Commit Validation System for OpenSpec Workflow

Provides comprehensive commit validation with message templates, interactive builder,
history tracking, signature verification, and branch protection validation.

Key Features:
    - Commit message templates for different change types
    - Interactive commit message builder
    - Commit history tracking and analysis
    - GPG signature verification
    - Branch protection rule validation
    - Commit conventional format validation (Commitizen)
    - Commit history search and filtering
    - Commit statistics and trends

Classes:
    CommitMessageTemplate: Template for commit messages
    CommitMessageBuilder: Interactive builder
    CommitValidator: Message and format validation
    CommitHistory: Commit history tracking
    CommitSigner: GPG signature management
    BranchProtectionValidator: Branch protection rules

Usage:
    builder = CommitMessageBuilder()
    message = builder.build_interactive()

    validator = CommitValidator()
    result = validator.validate(message)

    if result.is_valid:
        # Create commit

Author: Obsidian AI Agent Team
License: MIT
Version: 0.1.45
"""

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern


class CommitType(Enum):
    """Conventional commit types."""

    FEATURE = "feat"
    BUGFIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    STYLE = "style"
    TEST = "test"
    PERF = "perf"
    CI = "ci"
    CHORE = "chore"
    REVERT = "revert"


class ValidationStatus(Enum):
    """Validation result status."""

    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of commit validation."""

    status: ValidationStatus
    message: str
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.status in (ValidationStatus.VALID, ValidationStatus.WARNING)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "message": self.message,
            "issues": self.issues,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
        }


@dataclass
class CommitInfo:
    """Information about a commit."""

    hash: str
    author: str
    date: datetime
    message: str
    subject: str
    body: str
    commit_type: Optional[str] = None
    scope: Optional[str] = None
    breaking: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hash": self.hash,
            "author": self.author,
            "date": self.date.isoformat(),
            "message": self.message,
            "subject": self.subject,
            "body": self.body,
            "commit_type": self.commit_type,
            "scope": self.scope,
            "breaking": self.breaking,
        }


class CommitMessageTemplate:
    """Template for generating commit messages."""

    TEMPLATES = {
        CommitType.FEATURE: """\
{type}({scope}): {subject}

{body}

Closes {issue}""",
        CommitType.BUGFIX: """\
{type}({scope}): {subject}

**Describe the bug**:
{body}

**Root cause**:
{cause}

**Solution**:
{solution}

Fixes {issue}""",
        CommitType.REFACTOR: (
            """\
{type}({scope}): {subject}

**Changes**:
{body}

**Impact**:
{impact}

BREAKING CHANGE: {breaking_change}"""
            if "{breaking_change}"
            else """\
{type}({scope}): {subject}

**Changes**:
{body}

**Impact**:
{impact}"""
        ),
        CommitType.DOCS: """\
{type}({scope}): {subject}

**Documentation**:
{body}""",
        CommitType.TEST: """\
{type}({scope}): {subject}

**Test cases**:
{body}

**Coverage**:
{coverage}""",
        CommitType.PERF: """\
{type}({scope}): {subject}

**Performance improvement**:
{body}

**Metrics**:
{metrics}""",
    }

    @classmethod
    def get_template(cls, commit_type: CommitType) -> str:
        """Get template for commit type."""
        return cls.TEMPLATES.get(
            commit_type,
            """{type}({scope}): {subject}

{body}""",
        )

    @classmethod
    def get_all_types(cls) -> List[CommitType]:
        """Get all available commit types."""
        return list(CommitType)


class CommitMessageBuilder:
    """Interactive commit message builder."""

    def __init__(self, scopes: Optional[List[str]] = None):
        """
        Initialize builder.

        Args:
            scopes: Available scopes
        """
        self.scopes = scopes or []

    def build_interactive(self) -> str:
        """
        Build commit message interactively.

        Returns:
            Generated commit message
        """
        # Select commit type
        print("\n📋 Select commit type:")
        for i, commit_type in enumerate(CommitMessageTemplate.get_all_types(), 1):
            print(
                f"  {i}. {commit_type.value} - {self._get_type_description(commit_type)}"
            )

        type_choice = input("Enter choice (1-10): ").strip()
        try:
            commit_type = CommitMessageTemplate.get_all_types()[int(type_choice) - 1]
        except (ValueError, IndexError):
            raise ValueError("Invalid commit type selection")

        # Enter scope
        scope = input("Enter scope (optional): ").strip()

        # Enter subject
        subject = input("Enter subject (max 50 chars): ").strip()
        if len(subject) > 50:
            print(f"⚠️  Subject exceeds 50 chars ({len(subject)}). Truncating.")
            subject = subject[:50]

        # Enter body
        print("Enter body (empty line to finish):")
        body_lines = []
        while True:
            line = input()
            if not line:
                break
            body_lines.append(line)
        body = "\n".join(body_lines)

        # Enter issue reference
        issue = input("Enter issue reference (optional, e.g., #123): ").strip()

        # Build message
        template = CommitMessageTemplate.get_template(commit_type)
        message = template.format(
            type=commit_type.value,
            scope=scope or "scope",
            subject=subject,
            body=body,
            issue=issue or "closes #XXX",
            cause="",
            solution="",
            impact="",
            breaking_change="",
            coverage="",
            metrics="",
        )

        return message

    @staticmethod
    def _get_type_description(commit_type: CommitType) -> str:
        """Get description for commit type."""
        descriptions = {
            CommitType.FEATURE: "A new feature",
            CommitType.BUGFIX: "A bug fix",
            CommitType.REFACTOR: "Code refactoring",
            CommitType.DOCS: "Documentation changes",
            CommitType.STYLE: "Code style changes",
            CommitType.TEST: "Test additions or changes",
            CommitType.PERF: "Performance improvements",
            CommitType.CI: "CI/CD changes",
            CommitType.CHORE: "Build, dependencies, etc.",
            CommitType.REVERT: "Revert previous commit",
        }
        return descriptions.get(commit_type, "Unknown")


class CommitValidator:
    """Validates commit messages and formats."""

    # Conventional commit pattern
    CONVENTIONAL_PATTERN: Pattern = re.compile(
        r"^(?P<type>\w+)(?:\((?P<scope>[\w\s/-]*)\))?(?P<breaking>!)?:\s(?P<subject>.+?)$",
        re.MULTILINE,
    )

    # Issue reference pattern
    ISSUE_PATTERN: Pattern = re.compile(r"#\d+|closes #\d+|fixes #\d+")

    def __init__(self, max_subject_length: int = 50, max_line_length: int = 100):
        """
        Initialize validator.

        Args:
            max_subject_length: Maximum subject line length
            max_line_length: Maximum line length in body
        """
        self.max_subject_length = max_subject_length
        self.max_line_length = max_line_length

    def validate(self, message: str) -> ValidationResult:
        """
        Validate commit message.

        Args:
            message: Commit message to validate

        Returns:
            Validation result
        """
        issues = []
        warnings = []
        suggestions = []

        if not message or not message.strip():
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message="Commit message is empty",
                issues=["Empty commit message"],
            )

        lines = message.split("\n")
        subject = lines[0]

        # Check subject line
        if len(subject) > self.max_subject_length:
            issues.append(
                f"Subject line exceeds {self.max_subject_length} characters "
                f"({len(subject)} chars)"
            )

        if not subject.endswith("."):
            warnings.append("Subject line should not end with period")

        # Check conventional format
        match = self.CONVENTIONAL_PATTERN.match(subject)
        if not match:
            suggestions.append("Use conventional commit format: type(scope): subject")
        else:
            commit_type = match.group("type")
            if commit_type not in [ct.value for ct in CommitType]:
                warnings.append(f"Unknown commit type: {commit_type}")

            if match.group("breaking"):
                # Check for BREAKING CHANGE in body
                has_breaking_info = any("BREAKING CHANGE" in line for line in lines[1:])
                if not has_breaking_info:
                    suggestions.append(
                        "Add 'BREAKING CHANGE:' description in body for breaking changes"
                    )

        # Check body lines
        for i, line in enumerate(lines[1:], 1):
            if len(line) > self.max_line_length:
                warnings.append(
                    f"Line {i + 1} exceeds {self.max_line_length} characters "
                    f"({len(line)} chars)"
                )

        # Check for issue references
        if not self.ISSUE_PATTERN.search(message):
            suggestions.append("Consider referencing an issue (e.g., closes #123)")

        # Determine status
        if issues:
            status = ValidationStatus.ERROR
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID

        return ValidationResult(
            status=status,
            message=f"Commit message validation {status.value}",
            issues=issues,
            warnings=warnings,
            suggestions=suggestions,
        )


class CommitHistory:
    """Tracks and analyzes commit history."""

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize commit history tracker.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path or Path.cwd()
        self.commits: List[CommitInfo] = []

    def load_history(self, max_commits: int = 50) -> List[CommitInfo]:
        """
        Load commit history from git.

        Args:
            max_commits: Maximum commits to load

        Returns:
            List of commits
        """
        try:
            # Get commits with format: hash|author|date|subject|body
            cmd = [
                "git",
                f"-C={self.repo_path}",
                "log",
                f"-n={max_commits}",
                "--pretty=format:%H|%an|%ai|%s|%b",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            commits = []
            for entry in result.stdout.split("\n\n"):
                if not entry.strip():
                    continue

                parts = entry.split("|", 4)
                if len(parts) < 4:
                    continue

                commit_hash, author, date_str, subject = parts[:4]
                body = parts[4] if len(parts) > 4 else ""

                try:
                    date = datetime.fromisoformat(date_str.replace(" ", "T"))
                except (ValueError, IndexError):
                    continue

                # Parse conventional format
                match = CommitValidator.CONVENTIONAL_PATTERN.match(subject)
                commit_type = match.group("type") if match else None
                scope = match.group("scope") if match else None
                breaking = bool(match.group("breaking")) if match else False

                commit = CommitInfo(
                    hash=commit_hash[:7],
                    author=author,
                    date=date,
                    message=f"{subject}\n{body}" if body else subject,
                    subject=subject,
                    body=body,
                    commit_type=commit_type,
                    scope=scope,
                    breaking=breaking,
                )

                commits.append(commit)

            self.commits = commits
            return commits

        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get commit statistics."""
        if not self.commits:
            return {}

        type_counts: Dict[str, int] = {}
        author_counts: Dict[str, int] = {}

        for commit in self.commits:
            if commit.commit_type:
                type_counts[commit.commit_type] = (
                    type_counts.get(commit.commit_type, 0) + 1
                )

            author_counts[commit.author] = author_counts.get(commit.author, 0) + 1

        date_range = (
            self.commits[-1].date if self.commits else datetime.now(),
            self.commits[0].date if self.commits else datetime.now(),
        )

        return {
            "total_commits": len(self.commits),
            "by_type": type_counts,
            "by_author": author_counts,
            "date_range": {
                "from": date_range[0].isoformat(),
                "to": date_range[1].isoformat(),
            },
            "breaking_changes": sum(1 for c in self.commits if c.breaking),
        }

    def search(self, pattern: str) -> List[CommitInfo]:
        """Search commits by pattern."""
        regex = re.compile(pattern, re.IGNORECASE)
        return [c for c in self.commits if regex.search(c.message)]


class CommitSigner:
    """GPG signature management for commits."""

    def __init__(self, gpg_key_id: Optional[str] = None):
        """
        Initialize signer.

        Args:
            gpg_key_id: GPG key ID to use for signing
        """
        self.gpg_key_id = gpg_key_id

    def configure_signing(self) -> bool:
        """
        Configure git to sign commits.

        Returns:
            True if successful
        """
        try:
            # Set commit signing config
            subprocess.run(
                ["git", "config", "--global", "commit.gpgSign", "true"],
                check=True,
            )

            if self.gpg_key_id:
                subprocess.run(
                    ["git", "config", "--global", "user.signingKey", self.gpg_key_id],
                    check=True,
                )

            return True
        except subprocess.CalledProcessError:
            return False

    def verify_signature(
        self, commit_hash: str, repo_path: Optional[Path] = None
    ) -> bool:
        """
        Verify GPG signature on commit.

        Args:
            commit_hash: Commit hash
            repo_path: Repository path

        Returns:
            True if signature is valid
        """
        repo_path = repo_path or Path.cwd()

        try:
            result = subprocess.run(
                ["git", f"-C={repo_path}", "verify-commit", commit_hash],
                capture_output=True,
                check=False,
            )

            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False


class BranchProtectionValidator:
    """Validates branch protection rules."""

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            repo_path: Repository path
        """
        self.repo_path = repo_path or Path.cwd()
        self.rules: Dict[str, Dict[str, Any]] = {}

    def load_rules(self, rules_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load branch protection rules.

        Args:
            rules_file: Path to rules configuration file

        Returns:
            Loaded rules
        """
        if rules_file is None:
            rules_file = self.repo_path / ".branch-protection.json"

        if not rules_file.exists():
            return {}

        try:
            with open(rules_file, "r") as f:
                self.rules = json.load(f)
            return self.rules
        except (json.JSONDecodeError, IOError):
            return {}

    def validate_branch(self, branch_name: str) -> ValidationResult:
        """
        Validate if branch matches protection rules.

        Args:
            branch_name: Branch name

        Returns:
            Validation result
        """
        issues: List[str] = []
        warnings: List[str] = []

        # Check if branch matches any protected patterns
        for pattern, rule in self.rules.items():
            if self._pattern_matches(branch_name, pattern):
                # Validate against rule

                # Check commit signature requirement
                if rule.get("require_signed_commits"):
                    warnings.append(f"Branch '{branch_name}' requires signed commits")

                # Check commit count requirement
                min_commits = rule.get("min_commits", 0)
                if min_commits > 0:
                    # Would need to check actual commits
                    pass

                # Check status checks
                if rule.get("require_status_checks"):
                    warnings.append(
                        f"Branch '{branch_name}' requires status checks to pass"
                    )

                # Check review requirements
                if rule.get("require_pull_request_reviews"):
                    min_reviews = rule.get("required_approving_review_count", 1)
                    warnings.append(
                        f"Branch '{branch_name}' requires {min_reviews} review(s)"
                    )

        status = ValidationStatus.WARNING if warnings else ValidationStatus.VALID

        return ValidationResult(
            status=status,
            message=f"Branch protection validation {status.value}",
            warnings=warnings,
            issues=issues,
        )

    @staticmethod
    def _pattern_matches(branch_name: str, pattern: str) -> bool:
        """Check if branch name matches protection pattern."""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        return re.match(f"^{regex_pattern}$", branch_name) is not None


if __name__ == "__main__":
    # Example usage
    print("🔍 Commit Validation Examples\n")

    # Example 1: Validate a message
    validator = CommitValidator()

    good_message = """feat(api): add new endpoint for user data

This adds a new POST endpoint to handle user profile updates.

Closes #123"""

    result = validator.validate(good_message)
    print(f"Message: {result.status.value}")
    if result.issues:
        print(f"Issues: {', '.join(result.issues)}")

    # Example 2: Get history stats
    history = CommitHistory()
    commits = history.load_history(10)
    stats = history.get_statistics()

    print("\nCommit statistics:")
    print(f"  Total: {stats.get('total_commits', 0)}")
    print(f"  By type: {stats.get('by_type', {})}")
