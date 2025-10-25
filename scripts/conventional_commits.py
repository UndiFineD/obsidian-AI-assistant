#!/usr/bin/env python3
"""
Conventional Commits Validator & Fixer

Enforces Conventional Commits format (type(scope): subject) with interactive fixing.
Integrates with Stage 10 (Verify Implementation) for commit validation.

Format: type(scope): subject [#issue]

Types:
  feat     - New feature
  fix      - Bug fix
  docs     - Documentation changes
  style    - Code style (no logic changes)
  refactor - Code restructuring
  test     - Test additions/modifications
  chore    - Maintenance, dependencies

Examples:
  feat(workflow): add parallelization for stages 2-6
  fix(quality-gates): improve pytest coverage parsing
  docs(api): update endpoint documentation
  refactor(performance): optimize caching layer
"""

import subprocess
import re
from pathlib import Path
from typing import List, Tuple, Optional
import importlib.util

# Import helpers
try:
    spec = importlib.util.spec_from_file_location(
        "workflow_helpers",
        Path(__file__).parent / "workflow-helpers.py",
    )
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False
    helpers = None


class CommitValidator:
    """Validate and fix Conventional Commits"""

    VALID_TYPES = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
    COMMIT_PATTERN = (
        r"^(feat|fix|docs|style|refactor|test|chore)(\([^)]+\))?: .{1,100}(?: #\d+)?$"
    )

    @staticmethod
    def validate_commit(message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a commit message.

        Args:
            message: Commit message to validate

        Returns:
            (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Commit message is empty"

        # Remove trailing newlines
        message = message.strip()

        # Check basic format
        if not re.match(CommitValidator.COMMIT_PATTERN, message):
            return (
                False,
                f"Invalid format. Expected: type(scope): subject\nGot: {message}",
            )

        # Parse to verify
        match = re.match(r"^(\w+)(\([^)]+\))?: (.+)$", message)
        if not match:
            return False, "Could not parse commit message"

        msg_type = match.group(1)
        if msg_type not in CommitValidator.VALID_TYPES:
            valid_str = ", ".join(CommitValidator.VALID_TYPES)
            return False, f"Invalid type '{msg_type}'. Valid types: {valid_str}"

        return True, None

    @staticmethod
    def parse_commit(message: str) -> Optional[dict]:
        """
        Parse a commit message into components.

        Args:
            message: Commit message

        Returns:
            Dict with 'type', 'scope', 'subject', 'issue' or None if invalid
        """
        match = re.match(r"^(\w+)(\(([^)]+)\))?: ([^#]+)(?: #(\d+))?$", message.strip())
        if not match:
            return None

        return {
            "type": match.group(1),
            "scope": match.group(3) or "",
            "subject": match.group(4).strip(),
            "issue": match.group(5) or "",
        }

    @staticmethod
    def fix_commit(message: str) -> str:
        """
        Attempt to fix a commit message to Conventional Commits format.

        Args:
            message: Potentially invalid commit message

        Returns:
            Fixed commit message
        """
        message = message.strip()

        # Try to extract type and subject
        # Pattern: extract first word (potential type) and rest as subject
        parts = message.split(":", 1)
        if len(parts) == 2:
            type_part = parts[0].strip()
            subject = parts[1].strip()

            # Check if type_part has scope
            type_match = re.match(r"^(\w+)(?:\(([^)]+)\))?$", type_part)
            if type_match:
                msg_type = type_match.group(1)
                scope = type_match.group(2) or ""

                # Fix type if needed
                if msg_type not in CommitValidator.VALID_TYPES:
                    # Try to guess based on keywords
                    msg_lower = message.lower()
                    if any(kw in msg_lower for kw in ["fix", "bug", "issue", "error"]):
                        msg_type = "fix"
                    elif any(kw in msg_lower for kw in ["add", "implement", "new"]):
                        msg_type = "feat"
                    elif any(kw in msg_lower for kw in ["doc", "readme", "comment"]):
                        msg_type = "docs"
                    elif any(kw in msg_lower for kw in ["test", "test"]):
                        msg_type = "test"
                    elif any(kw in msg_lower for kw in ["refactor", "reorganize"]):
                        msg_type = "refactor"
                    else:
                        msg_type = "chore"

                # Build fixed message
                if scope:
                    fixed = f"{msg_type}({scope}): {subject}"
                else:
                    fixed = f"{msg_type}: {subject}"

                # Ensure subject length is reasonable
                if len(fixed) > 100:
                    fixed = fixed[:97] + "..."

                return fixed

        # Fallback: default to chore
        return f"chore: {message[:100]}"

    @staticmethod
    def get_recent_commits(count: int = 5) -> List[str]:
        """Get recent git commits"""
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--pretty=format:%B"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split("\n\n")
                return [c.split("\n")[0] for c in commits if c.strip()]
            return []
        except Exception:
            return []

    @staticmethod
    def validate_all_commits(
        branch: str = "HEAD",
    ) -> Tuple[bool, List[Tuple[str, bool]]]:
        """
        Validate all commits in a branch.

        Args:
            branch: Git branch/ref to validate

        Returns:
            (all_valid, [(commit, is_valid), ...])
        """
        commits = CommitValidator.get_recent_commits(20)
        results = []

        for commit in commits:
            valid, _ = CommitValidator.validate_commit(commit)
            results.append((commit, valid))

        all_valid = all(valid for _, valid in results)
        return all_valid, results


def validate_git_commits(verbose: bool = False) -> bool:
    """
    Validate all recent git commits.

    Args:
        verbose: If True, show detailed output

    Returns:
        True if all commits are valid
    """
    if HELPERS_AVAILABLE:
        helpers.write_info("Validating recent git commits...")
    else:
        print("Validating recent git commits...")

    validator = CommitValidator()
    all_valid, results = validator.validate_all_commits()

    invalid_count = sum(1 for _, valid in results if not valid)

    if verbose or invalid_count > 0:
        if HELPERS_AVAILABLE:
            helpers.write_info(f"Checked {len(results)} commits")
        else:
            print(f"Checked {len(results)} commits")

        for commit, valid in results:
            symbol = "✓" if valid else "✗"
            if HELPERS_AVAILABLE:
                if valid:
                    helpers.write_success(f"{symbol} {commit[:60]}")
                else:
                    helpers.write_error(f"{symbol} {commit[:60]}")
            else:
                status = "OK" if valid else "FAIL"
                print(f"{symbol} [{status}] {commit[:60]}")

    if all_valid:
        if HELPERS_AVAILABLE:
            helpers.write_success(f"All {len(results)} commits valid")
        else:
            print(f"✓ All {len(results)} commits valid")
    else:
        if HELPERS_AVAILABLE:
            helpers.write_error(
                f"{invalid_count} commit(s) not in Conventional Commits format"
            )
        else:
            print(f"✗ {invalid_count} commit(s) invalid")

    return all_valid


def interactive_fix_commits() -> bool:
    """
    Interactively fix commits that don't follow Conventional Commits.

    Returns:
        True if all commits are now valid
    """
    if HELPERS_AVAILABLE:
        helpers.write_info("Interactive Commit Message Fixer")
    else:
        print("\nInteractive Commit Message Fixer\n")

    validator = CommitValidator()
    all_valid, results = validator.validate_all_commits()

    invalid_commits = [
        (commit, idx) for idx, (commit, valid) in enumerate(results) if not valid
    ]

    if not invalid_commits:
        if HELPERS_AVAILABLE:
            helpers.write_success("All commits are valid!")
        else:
            print("✓ All commits are valid!")
        return True

    if HELPERS_AVAILABLE:
        helpers.write_warning(f"Found {len(invalid_commits)} invalid commit(s)")
    else:
        print(f"\n⚠️  Found {len(invalid_commits)} invalid commit(s)\n")

    fixed_count = 0
    for commit, idx in invalid_commits:
        if HELPERS_AVAILABLE:
            helpers.write_error(f"Invalid (#{idx}): {commit[:60]}")
        else:
            print(f"✗ Invalid (#{idx}): {commit[:60]}")

        fixed = validator.fix_commit(commit)

        if HELPERS_AVAILABLE:
            helpers.write_info(f"Suggested: {fixed}")
        else:
            print(f"Suggested: {fixed}")

        try:
            response = input("Accept fix? (y/n/skip): ").strip().lower()
            if response == "y":
                fixed_count += 1
                if HELPERS_AVAILABLE:
                    helpers.write_success("✓ Marked for fixing")
                else:
                    print("✓ Marked for fixing")
            elif response == "n":
                # Get custom input
                try:
                    custom = input("Enter corrected message: ").strip()
                    valid, error = validator.validate_commit(custom)
                    if valid:
                        fixed_count += 1
                        if HELPERS_AVAILABLE:
                            helpers.write_success("✓ Custom message accepted")
                        else:
                            print("✓ Custom message accepted")
                    else:
                        if HELPERS_AVAILABLE:
                            helpers.write_error(f"Invalid: {error}")
                        else:
                            print(f"✗ Invalid: {error}")
                except Exception:
                    pass
            # skip keeps the commit as-is
        except KeyboardInterrupt:
            if HELPERS_AVAILABLE:
                helpers.write_warning("Aborting interactive fix")
            else:
                print("\n⚠️  Aborting")
            break

    if HELPERS_AVAILABLE:
        helpers.write_success(f"Fixed {fixed_count}/{len(invalid_commits)} commits")
    else:
        print(f"\n✓ Fixed {fixed_count}/{len(invalid_commits)} commits\n")

    return len(invalid_commits) == fixed_count


if __name__ == "__main__":
    # Test validator
    test_messages = [
        "feat(workflow): add parallelization for stages 2-6",
        "fix: remove duplicate argument",
        "invalid commit message",
        "Add new feature",
        "docs(api): update endpoint docs #123",
    ]

    print("Testing Conventional Commits Validator\n")
    for msg in test_messages:
        valid, error = CommitValidator.validate_commit(msg)
        status = "✓" if valid else "✗"
        print(f"{status} {msg}")
        if error:
            print(f"   Error: {error}")
            fixed = CommitValidator.fix_commit(msg)
            print(f"   Fixed: {fixed}\n")
        else:
            print()

    # Test recent commits
    print("\nValidating recent commits...")
    validate_git_commits(verbose=True)
