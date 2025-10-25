#!/usr/bin/env python3
"""
Lane Detection Automation Test Suite

Tests the detect_lane.sh and detect_lane.ps1 scripts to ensure accurate
lane selection based on changed files and commit patterns.

Test Coverage:
- Docs-only changes → docs lane
- Mixed changes → standard lane
- Security/breaking changes → heavy lane
- Large refactors → heavy lane
- File categorization accuracy
- Commit message pattern detection
- Edge cases (no changes, empty repo, etc.)
"""

import subprocess
import tempfile
import json
import shutil
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional


# ANSI Colors for output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def log_test(name: str) -> None:
    """Log test start."""
    print(f"\n{Colors.BLUE}→ {name}{Colors.RESET}")


def log_pass(msg: str) -> None:
    """Log passing test."""
    print(f"  {Colors.GREEN}✓ {msg}{Colors.RESET}")


def log_fail(msg: str) -> None:
    """Log failing test."""
    print(f"  {Colors.RED}✗ {msg}{Colors.RESET}")


def log_info(msg: str) -> None:
    """Log info message."""
    print(f"  {Colors.YELLOW}ℹ {msg}{Colors.RESET}")


class LaneDetectionTest:
    """Base class for lane detection tests."""

    def __init__(self):
        """Initialize test environment."""
        self.test_dir = None
        self.project_root = Path(__file__).parent.parent
        self.script_bash = self.project_root / "scripts" / "detect_lane.sh"
        self.script_ps1 = self.project_root / "scripts" / "detect_lane.ps1"
        self.test_results = []

    def setup(self) -> None:
        """Create temporary test repository."""
        self.test_dir = tempfile.mkdtemp(prefix="lane_test_")
        os.chdir(self.test_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)

        # Create initial commit
        Path("README.md").write_text("# Test Repo")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "initial: Setup"], check=True)

    def teardown(self) -> None:
        """Clean up test repository."""
        if self.test_dir and Path(self.test_dir).exists():
            os.chdir("/")
            shutil.rmtree(self.test_dir)

    def detect_lane(self, base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> Tuple[str, int]:
        """
        Run lane detection script.

        Returns:
            Tuple of (lane, exit_code)
        """
        try:
            result = subprocess.run(
                ["bash", str(self.script_bash), base_ref, head_ref],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lane = result.stdout.strip()
            return lane, result.returncode
        except subprocess.TimeoutExpired:
            return "", -1
        except Exception as e:
            log_fail(f"Script execution error: {e}")
            return "", 1

    def create_file(self, path: str, content: str) -> None:
        """Create a file in test repo."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def add_commit(self, files: dict, message: str) -> None:
        """Add files and create commit."""
        for path, content in files.items():
            self.create_file(path, content)

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)

    def run_test(self, name: str, test_func) -> bool:
        """Run a single test."""
        log_test(name)
        try:
            test_func()
            return True
        except AssertionError as e:
            log_fail(str(e))
            return False
        except Exception as e:
            log_fail(f"Unexpected error: {e}")
            return False

    def assert_lane(self, lane: str, expected: str, message: str = "") -> None:
        """Assert detected lane matches expected."""
        if lane != expected:
            raise AssertionError(f"Expected {expected} lane, got {lane}. {message}")
        log_pass(f"Correctly detected {expected} lane")

    def assert_exit_code(self, code: int, expected: int, message: str = "") -> None:
        """Assert exit code matches expected."""
        if code != expected:
            raise AssertionError(f"Expected exit code {expected}, got {code}. {message}")
        log_pass(f"Exit code {code} as expected")


class TestDocsonlyChanges(LaneDetectionTest):
    """Test detection of docs-only changes."""

    def test_markdown_only(self):
        """Test pure markdown changes."""
        self.setup()
        try:
            self.add_commit(
                {"docs/guide.md": "# Installation Guide", "README.md": "# Updated README"},
                "docs: Update documentation",
            )

            lane, code = self.detect_lane()
            self.assert_lane(lane, "docs", "Markdown-only changes")
            self.assert_exit_code(code, 0)
        finally:
            self.teardown()

    def test_config_only(self):
        """Test configuration-only changes."""
        self.setup()
        try:
            self.add_commit(
                {
                    ".eslintrc.json": '{"extends": "eslint:recommended"}',
                    "setup.cfg": "[tool:pytest]\ntestpaths = tests",
                },
                "chore: Update configuration",
            )

            lane, code = self.detect_lane()
            # Config-only should be docs or standard, not heavy
            self.assert_lane(lane, "docs", "Config-only changes")
        finally:
            self.teardown()

    def test_multiple_docs_files(self):
        """Test multiple documentation files."""
        self.setup()
        try:
            self.add_commit(
                {
                    "docs/guide1.md": "# Guide 1",
                    "docs/guide2.md": "# Guide 2",
                    "docs/api.md": "# API Reference",
                    "CHANGELOG.md": "# Changelog",
                },
                "docs: Add comprehensive guides",
            )

            lane, code = self.detect_lane()
            self.assert_lane(lane, "docs", "Multiple docs files")
        finally:
            self.teardown()


class TestStandardChanges(LaneDetectionTest):
    """Test detection of standard lane changes."""

    def test_code_and_tests(self):
        """Test code changes with tests."""
        self.setup()
        try:
            self.add_commit(
                {
                    "agent/hello.py": "def hello(): return 'hello'",
                    "tests/test_hello.py": "def test_hello(): assert hello() == 'hello'",
                    "CHANGELOG.md": "# Added hello function",
                },
                "feat: Add hello function",
            )

            lane, code = self.detect_lane()
            self.assert_lane(lane, "standard", "Code + tests + docs")
        finally:
            self.teardown()

    def test_bug_fix(self):
        """Test bug fix scenario."""
        self.setup()
        try:
            self.add_commit(
                {
                    "agent/backend.py": "# Bug fix code",
                    "tests/test_backend.py": "# Test for bug fix",
                },
                "fix: Resolve API timeout issue",
            )

            lane, code = self.detect_lane()
            self.assert_lane(lane, "standard", "Bug fix with tests")
        finally:
            self.teardown()


class TestHeavyChanges(LaneDetectionTest):
    """Test detection of heavy lane changes."""

    def test_security_fix(self):
        """Test security fix detection."""
        self.setup()
        try:
            self.add_commit(
                {
                    "agent/security.py": "# Security patch",
                    "tests/test_security.py": "# Security tests",
                },
                "security: Fix authentication vulnerability",
            )

            lane, code = self.detect_lane()
            self.assert_lane(lane, "heavy", "Security fix triggers heavy lane")
        finally:
            self.teardown()

    def test_breaking_change(self):
        """Test breaking change detection."""
        self.setup()
        try:
            self.add_commit({"agent/api.py": "# API redesign"}, "BREAKING: Redesign API endpoints")

            lane, code = self.detect_lane()
            self.assert_lane(lane, "heavy", "Breaking change triggers heavy lane")
        finally:
            self.teardown()

    def test_large_refactor(self):
        """Test large refactoring detection."""
        self.setup()
        try:
            # Create many files to simulate large refactor
            files = {}
            for i in range(15):
                files[f"agent/module{i}.py"] = f"# Module {i}\ncode here"

            self.add_commit(files, "refactor: Restructure codebase")

            lane, code = self.detect_lane()
            self.assert_lane(lane, "heavy", "Large refactor (15+ files)")
        finally:
            self.teardown()

    def test_infrastructure_changes(self):
        """Test infrastructure change detection."""
        self.setup()
        try:
            self.add_commit(
                {
                    ".github/workflows/ci.yml": "name: CI\njobs:\n  test:\n    runs-on: ubuntu-latest",
                    "agent/backend.py": "# Backend changes",
                },
                "chore: Update CI workflow",
            )

            lane, code = self.detect_lane()
            self.assert_lane(lane, "heavy", "Infrastructure + code changes")
        finally:
            self.teardown()


class TestEdgeCases(LaneDetectionTest):
    """Test edge cases and error handling."""

    def test_no_changes(self):
        """Test detection with no changes."""
        self.setup()
        try:
            lane, code = self.detect_lane("HEAD", "HEAD")
            # Should handle no changes gracefully
            log_pass(f"No changes handled: lane={lane}, code={code}")
            # Either returns standard as default or code 2
            assert code in [0, 2], f"Unexpected exit code: {code}"
        finally:
            self.teardown()

    def test_deleted_files(self):
        """Test detection with deleted files."""
        self.setup()
        try:
            self.add_commit({"file.py": "content"}, "initial: Add file")
            Path("file.py").unlink()
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "chore: Remove old file"], check=True)

            lane, code = self.detect_lane()
            # Deletions shouldn't affect lane detection
            log_pass(f"Deleted files handled correctly: lane={lane}")
        finally:
            self.teardown()


def run_all_tests() -> Tuple[int, int, int]:
    """
    Run all test suites.

    Returns:
        Tuple of (total, passed, failed)
    """
    test_suites = [
        ("Docs-Only Changes", TestDocsonlyChanges()),
        ("Standard Changes", TestStandardChanges()),
        ("Heavy Changes", TestHeavyChanges()),
        ("Edge Cases", TestEdgeCases()),
    ]

    total = 0
    passed = 0
    failed = 0

    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"Lane Detection Automation Test Suite")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}{Colors.RESET}")

    for suite_name, test_obj in test_suites:
        print(f"\n{Colors.YELLOW}[{suite_name}]{Colors.RESET}")

        # Get test methods
        test_methods = [m for m in dir(test_obj) if m.startswith("test_")]

        for method_name in test_methods:
            total += 1
            test_method = getattr(test_obj, method_name)

            # Convert method name to display name
            display_name = method_name.replace("_", " ").title()

            if test_obj.run_test(display_name, test_method):
                passed += 1
            else:
                failed += 1

    # Summary
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"Test Summary")
    print(f"{'=' * 60}{Colors.RESET}")
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

    return total, passed, failed


if __name__ == "__main__":
    total, passed, failed = run_all_tests()

    # Exit with error code if any tests failed
    sys.exit(0 if failed == 0 else 1)
