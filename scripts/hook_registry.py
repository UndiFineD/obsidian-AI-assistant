#!/usr/bin/env python3
"""
Pre-Step Hook Registry - Validation hooks executed before workflow stages

Implements a hook registry system allowing pre-step validation for specific stages.
Hooks can perform environment checks, validate prerequisites, and provide remediation.

Hook Registry:
  Stage 0 (Create TODOs): Python version, required tools (git, ruff, mypy, pytest, bandit)
  Stage 1 (Version Bump): Pre-version checks (no uncommitted changes, valid semver)
  Stage 10 (Verify Implementation): Git repository state check
  Stage 12 (Final Commit): GitHub CLI availability check, authentication

Exit Codes:
  0: All hooks passed, continue
  1: Hook failed, remediation provided, user should fix
  2: Hook warning, can continue with --force-hooks flag
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import Callable, Dict, List, Tuple, Optional
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


class HookResult:
    """Result from hook execution"""
    def __init__(self, passed: bool, message: str = "", remediation: str = "", warning: bool = False):
        self.passed = passed
        self.message = message
        self.remediation = remediation
        self.warning = warning

    def __bool__(self):
        return self.passed


class Hook:
    """Single validation hook"""
    def __init__(self, name: str, description: str, check_func: Callable):
        self.name = name
        self.description = description
        self.check_func = check_func

    def execute(self) -> HookResult:
        """Execute the hook and return result"""
        try:
            return self.check_func()
        except Exception as e:
            return HookResult(False, f"Hook error: {e}", f"Exception in {self.name}: {str(e)}")


class HookRegistry:
    """Registry of pre-step validation hooks"""

    def __init__(self):
        self.hooks: Dict[int, List[Hook]] = {
            0: [],   # Create TODOs
            1: [],   # Version Bump
            10: [],  # Verify Implementation
            12: [],  # Final Commit
        }
        self._setup_hooks()

    def _setup_hooks(self):
        """Register all pre-defined hooks"""
        # Stage 0 hooks
        self.register_hook(0, Hook("python_version", "Python 3.11+ required", self._check_python_version))
        self.register_hook(0, Hook("git_installed", "Git is installed", self._check_git_installed))
        self.register_hook(0, Hook("tools_available", "Required tools available", self._check_tools_available))

        # Stage 1 hooks
        self.register_hook(1, Hook("no_uncommitted", "No uncommitted changes", self._check_no_uncommitted))
        self.register_hook(1, Hook("valid_branch", "On valid branch", self._check_valid_branch))

        # Stage 10 hooks
        self.register_hook(10, Hook("git_state", "Git repository state valid", self._check_git_state))

        # Stage 12 hooks
        self.register_hook(12, Hook("gh_cli_available", "GitHub CLI available", self._check_gh_cli_available))
        self.register_hook(12, Hook("gh_auth", "GitHub authentication", self._check_gh_auth))

    def register_hook(self, stage: int, hook: Hook):
        """Register a hook for a specific stage"""
        if stage not in self.hooks:
            self.hooks[stage] = []
        self.hooks[stage].append(hook)

    def run_hooks(self, stage: int, force: bool = False) -> Tuple[bool, List[Tuple[str, HookResult]]]:
        """
        Run all hooks for a stage.

        Args:
            stage: Stage number
            force: If True, skip hooks (not recommended)

        Returns:
            (all_passed, [(hook_name, result), ...])
        """
        if force:
            if HELPERS_AVAILABLE:
                helpers.write_warning("⚠️  Skipping pre-step hooks (--force-hooks used)")
            else:
                print("⚠️  Skipping pre-step hooks (--force-hooks used)")
            return True, []

        if stage not in self.hooks:
            return True, []  # No hooks for this stage

        hooks = self.hooks[stage]
        if not hooks:
            return True, []  # No hooks registered

        if HELPERS_AVAILABLE:
            helpers.write_info(f"Running {len(hooks)} pre-step hooks for Stage {stage}...")
        else:
            print(f"Running {len(hooks)} pre-step hooks for Stage {stage}...")

        results = []
        all_passed = True

        for hook in hooks:
            result = hook.execute()
            results.append((hook.name, result))

            if result.warning:
                if HELPERS_AVAILABLE:
                    helpers.write_warning(f"⚠️  {hook.name}: {result.message}")
                else:
                    print(f"⚠️  {hook.name}: {result.message}")
            elif result.passed:
                if HELPERS_AVAILABLE:
                    helpers.write_success(f"✓ {hook.name}")
                else:
                    print(f"✓ {hook.name}")
            else:
                all_passed = False
                if HELPERS_AVAILABLE:
                    helpers.write_error(f"✗ {hook.name}: {result.message}")
                else:
                    print(f"✗ {hook.name}: {result.message}")

                if result.remediation:
                    if HELPERS_AVAILABLE:
                        helpers.write_info(f"  Remediation: {result.remediation}")
                    else:
                        print(f"  Remediation: {result.remediation}")

        return all_passed, results

    # ===== Hook Implementations =====

    @staticmethod
    def _check_python_version() -> HookResult:
        """Check Python version is 3.11+"""
        version_info = sys.version_info
        if version_info.major > 3 or (version_info.major == 3 and version_info.minor >= 11):
            return HookResult(True, f"Python {version_info.major}.{version_info.minor}")
        else:
            return HookResult(
                False,
                f"Python {version_info.major}.{version_info.minor} found",
                "Install Python 3.11 or later"
            )

    @staticmethod
    def _check_git_installed() -> HookResult:
        """Check git is installed"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                return HookResult(True, version)
            else:
                return HookResult(False, "Git command failed", "Reinstall git")
        except FileNotFoundError:
            return HookResult(False, "Git not found in PATH", "Install git and add to PATH")
        except Exception as e:
            return HookResult(False, str(e), "Check git installation")

    @staticmethod
    def _check_tools_available() -> HookResult:
        """Check required tools (ruff, mypy, pytest, bandit) are available"""
        tools = ["ruff", "mypy", "pytest", "bandit"]
        missing = []

        for tool in tools:
            try:
                result = subprocess.run([tool, "--version"], capture_output=True, timeout=5)
                if result.returncode != 0:
                    missing.append(tool)
            except FileNotFoundError:
                missing.append(tool)
            except Exception:
                missing.append(tool)

        if missing:
            return HookResult(
                False,
                f"Missing: {', '.join(missing)}",
                f"Install: pip install {' '.join(missing)}"
            )
        else:
            return HookResult(True, f"All {len(tools)} tools available")

    @staticmethod
    def _check_no_uncommitted() -> HookResult:
        """Check no uncommitted changes"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                if result.stdout.strip():
                    return HookResult(
                        False,
                        "Uncommitted changes detected",
                        "Run: git add -A && git commit -m 'temp'"
                    )
                else:
                    return HookResult(True, "Working directory clean")
            else:
                return HookResult(False, "Git status failed", "Check git repository")
        except Exception as e:
            return HookResult(False, str(e), "Check git repository state")

    @staticmethod
    def _check_valid_branch() -> HookResult:
        """Check on valid branch (not detached, not main)"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                if branch == "HEAD":
                    return HookResult(False, "On detached HEAD", "Checkout a valid branch")
                elif branch in ["main", "master", "develop"]:
                    return HookResult(
                        False,
                        f"On protected branch: {branch}",
                        "Create feature branch: git checkout -b feature/name"
                    )
                else:
                    return HookResult(True, f"On branch: {branch}")
            else:
                return HookResult(False, "Could not determine branch", "Check git repository")
        except Exception as e:
            return HookResult(False, str(e), "Check git branch")

    @staticmethod
    def _check_git_state() -> HookResult:
        """Check git repository state is valid"""
        try:
            # Check if in git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return HookResult(False, "Not in git repository", "Initialize git repo: git init")

            # Check if there are no conflicts
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return HookResult(
                    False,
                    "Merge conflicts detected",
                    "Resolve conflicts and commit: git add . && git commit"
                )

            return HookResult(True, "Git state valid")
        except Exception as e:
            return HookResult(False, str(e), "Check git repository")

    @staticmethod
    def _check_gh_cli_available() -> HookResult:
        """Check GitHub CLI is available"""
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip().split("\n")[0]
                return HookResult(True, version, warning=False)
            else:
                return HookResult(
                    False,
                    "GitHub CLI not working",
                    "Install: https://cli.github.com/",
                    warning=True
                )
        except FileNotFoundError:
            return HookResult(
                False,
                "GitHub CLI not found",
                "Install: https://cli.github.com/",
                warning=True
            )
        except Exception as e:
            return HookResult(False, str(e), "Check GitHub CLI installation", warning=True)

    @staticmethod
    def _check_gh_auth() -> HookResult:
        """Check GitHub authentication is configured"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return HookResult(True, "GitHub authentication OK")
            else:
                return HookResult(
                    False,
                    "Not authenticated with GitHub",
                    "Run: gh auth login",
                    warning=True
                )
        except FileNotFoundError:
            return HookResult(
                False,
                "GitHub CLI not available",
                "Install: https://cli.github.com/",
                warning=True
            )
        except Exception as e:
            return HookResult(False, str(e), "Check GitHub CLI auth", warning=True)


# Global registry instance
_registry = None

def get_registry() -> HookRegistry:
    """Get global hook registry instance"""
    global _registry
    if _registry is None:
        _registry = HookRegistry()
    return _registry

def run_stage_hooks(stage: int, force: bool = False) -> bool:
    """
    Run all hooks for a stage.

    Args:
        stage: Stage number
        force: If True, skip hooks

    Returns:
        True if all hooks passed or warnings only
    """
    registry = get_registry()
    all_passed, results = registry.run_hooks(stage, force)
    return all_passed

if __name__ == "__main__":
    # Test hook registry
    registry = HookRegistry()

    print("Testing Stage 0 hooks:")
    all_passed, results = registry.run_hooks(0)
    print(f"Result: {'PASS' if all_passed else 'FAIL'}\n")

    print("Testing Stage 1 hooks:")
    all_passed, results = registry.run_hooks(1)
    print(f"Result: {'PASS' if all_passed else 'FAIL'}\n")

    print("Testing Stage 10 hooks:")
    all_passed, results = registry.run_hooks(10)
    print(f"Result: {'PASS' if all_passed else 'FAIL'}\n")

    print("Testing Stage 12 hooks:")
    all_passed, results = registry.run_hooks(12)
    print(f"Result: {'PASS' if all_passed else 'FAIL'}")

