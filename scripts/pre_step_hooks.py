#!/usr/bin/env python3
"""
Pre-Step Hooks System - Extensible Workflow Hook Registry

Allows registration and execution of custom logic before specific workflow stages.
Supports hook execution, error handling, and remediation suggestions.

Hook Registry:
- Stage 0: Initialize workflow environment
- Stage 1: Version compatibility check
- Stage 10: Pre-documentation review
- Stage 12: Final validation and cleanup

Hook Results:
- SUCCESS: Hook passed, continue to stage
- SKIP: Skip to next hook/stage
- REMEDIATE: Show remediation and exit
- FAIL: Abort workflow
"""

import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class HookStatus(Enum):
    """Hook execution status"""
    SUCCESS = "SUCCESS"      # Hook passed
    SKIP = "SKIP"           # Skip stage
    REMEDIATE = "REMEDIATE"  # Show remediation and exit
    FAIL = "FAIL"           # Abort workflow


@dataclass
class HookResult:
    """Result of hook execution"""
    status: HookStatus
    message: str
    remediation: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PreStepHooks:
    """Registry and executor for pre-step workflow hooks"""

    def __init__(self):
        """Initialize hook registry"""
        self.hooks: Dict[int, List[Callable]] = {}
        self.remediation: Dict[int, str] = {}

        # Register default hooks for critical stages
        self._register_default_hooks()

    def _register_default_hooks(self) -> None:
        """Register default hooks for stages 0, 1, 10, 12"""
        # Stage 0: Initialize workflow environment
        self.register_hook(0, self._hook_stage0_init)
        self.remediation[0] = (
            "Stage 0 Failed: Could not initialize workflow environment\n"
            "  • Ensure .checkpoints/ directory is writable\n"
            "  • Check git configuration (git config --list)\n"
            "  • Verify Python 3.11+ installed\n"
        )

        # Stage 1: Version compatibility check
        self.register_hook(1, self._hook_stage1_version)
        self.remediation[1] = (
            "Stage 1 Failed: Version compatibility issue\n"
            "  • Check Python version: python --version (requires 3.11+)\n"
            "  • Update to Python 3.11+\n"
            "  • Or use a virtual environment with correct Python version\n"
        )

        # Stage 10: Pre-documentation review
        self.register_hook(10, self._hook_stage10_docs)
        self.remediation[10] = (
            "Stage 10 Failed: Documentation review prerequisites not met\n"
            "  • Ensure all documentation files exist\n"
            "  • Check markdown syntax in docs/\n"
            "  • Verify cross-references are valid\n"
        )

        # Stage 12: Final validation and cleanup
        self.register_hook(12, self._hook_stage12_final)
        self.remediation[12] = (
            "Stage 12 Failed: Final validation failed\n"
            "  • Run tests: pytest tests/ -v\n"
            "  • Check code quality: ruff check agent/ scripts/\n"
            "  • Review git status: git status\n"
            "  • Clean up temporary files: git clean -fd\n"
        )

    @staticmethod
    def _hook_stage0_init() -> HookResult:
        """Hook: Initialize workflow environment"""
        try:
            # Check if checkpoints directory can be created
            checkpoint_dir = Path.cwd() / ".checkpoints"
            checkpoint_dir.mkdir(parents=True, exist_ok=True)

            # Create initial state file if needed
            state_file = checkpoint_dir / "state.json"
            if not state_file.exists():
                state_file.write_text("{\"workflows\": {}}", encoding="utf-8")

            return HookResult(
                status=HookStatus.SUCCESS,
                message="✓ Workflow environment initialized",
            )
        except Exception as e:
            return HookResult(
                status=HookStatus.REMEDIATE,
                message=f"✗ Failed to initialize workflow: {e}",
            )

    @staticmethod
    def _hook_stage1_version() -> HookResult:
        """Hook: Version compatibility check"""
        import sys

        major, minor = sys.version_info[:2]
        if major < 3 or (major == 3 and minor < 11):
            return HookResult(
                status=HookStatus.REMEDIATE,
                message=f"✗ Python version {major}.{minor} < 3.11 required",
            )

        return HookResult(
            status=HookStatus.SUCCESS,
            message=f"✓ Python version {major}.{minor} OK",
        )

    @staticmethod
    def _hook_stage10_docs() -> HookResult:
        """Hook: Pre-documentation review"""
        docs_dir = Path.cwd() / "docs"

        if not docs_dir.exists():
            return HookResult(
                status=HookStatus.REMEDIATE,
                message="✗ docs/ directory not found",
            )

        # Check for key documentation files
        required_files = [
            "guides/The_Workflow_Process.md",
            "README.md",
            "API_REFERENCE.md",
        ]

        missing = []
        for file in required_files:
            if not (docs_dir / file).exists():
                missing.append(file)

        if missing:
            return HookResult(
                status=HookStatus.REMEDIATE,
                message=f"✗ Missing documentation files: {', '.join(missing)}",
            )

        return HookResult(
            status=HookStatus.SUCCESS,
            message="✓ Documentation files present",
        )

    @staticmethod
    def _hook_stage12_final() -> HookResult:
        """Hook: Final validation and cleanup"""
        # Check git repository status
        try:
            import subprocess

            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # It's OK to have untracked files, but index should be clean for commit
            if result.returncode != 0:
                return HookResult(
                    status=HookStatus.REMEDIATE,
                    message="✗ Git repository issue detected",
                )

            return HookResult(
                status=HookStatus.SUCCESS,
                message="✓ Final validation passed",
            )
        except Exception as e:
            return HookResult(
                status=HookStatus.SKIP,
                message=f"⊘ Skipping git validation: {e}",
            )

    def register_hook(
        self,
        stage_num: int,
        hook_func: Callable[[], HookResult],
    ) -> None:
        """
        Register a hook function for a stage.

        Args:
            stage_num: Stage number (0-12)
            hook_func: Function that returns HookResult
        """
        if stage_num not in self.hooks:
            self.hooks[stage_num] = []
        self.hooks[stage_num].append(hook_func)

    def register_remediation(self, stage_num: int, text: str) -> None:
        """
        Register remediation text for a stage.

        Args:
            stage_num: Stage number
            text: Remediation instructions
        """
        self.remediation[stage_num] = text

    def execute_hooks(self, stage_num: int, verbose: bool = False) -> HookResult:
        """
        Execute all hooks for a stage.

        Args:
            stage_num: Stage number to execute hooks for
            verbose: Print hook details

        Returns:
            Overall hook result
        """
        if stage_num not in self.hooks:
            return HookResult(
                status=HookStatus.SUCCESS,
                message=f"ℹ No hooks registered for stage {stage_num}",
            )

        hooks = self.hooks[stage_num]

        if verbose:
            print(f"\n🪝 Executing {len(hooks)} hook(s) for stage {stage_num}...")

        # Execute each hook
        for i, hook in enumerate(hooks):
            try:
                result = hook()

                if verbose:
                    print(f"  Hook {i+1}/{len(hooks)}: {result.message}")

                # Check result status
                if result.status == HookStatus.SUCCESS:
                    continue
                elif result.status == HookStatus.SKIP:
                    return result
                elif result.status == HookStatus.REMEDIATE:
                    return result
                elif result.status == HookStatus.FAIL:
                    return result

            except Exception as e:
                return HookResult(
                    status=HookStatus.REMEDIATE,
                    message=f"✗ Hook {i+1} failed with exception: {e}",
                )

        return HookResult(
            status=HookStatus.SUCCESS,
            message=f"✓ All {len(hooks)} hooks passed for stage {stage_num}",
        )

    def get_remediation(self, stage_num: int) -> Optional[str]:
        """Get remediation text for a stage"""
        return self.remediation.get(stage_num)

    def print_result(self, result: HookResult, stage_num: int) -> None:
        """Print hook result with appropriate formatting"""
        print(f"\n{result.message}")

        if result.status == HookStatus.REMEDIATE:
            remediation = self.get_remediation(stage_num)
            if remediation:
                print(f"\n{remediation}")

        if result.details:
            print("\nDetails:")
            for key, value in result.details.items():
                print(f"  {key}: {value}")


def create_hooks_registry() -> PreStepHooks:
    """Factory function to create hooks registry"""
    return PreStepHooks()


if __name__ == "__main__":
    # Example usage
    hooks = create_hooks_registry()

    # Test Stage 0 hook
    print("Testing Stage 0 (Initialize):")
    result = hooks.execute_hooks(0, verbose=True)
    hooks.print_result(result, 0)

    # Test Stage 1 hook
    print("\n\nTesting Stage 1 (Version):")
    result = hooks.execute_hooks(1, verbose=True)
    hooks.print_result(result, 1)

    # Test Stage 10 hook
    print("\n\nTesting Stage 10 (Documentation):")
    result = hooks.execute_hooks(10, verbose=True)
    hooks.print_result(result, 10)

    # Test Stage 12 hook
    print("\n\nTesting Stage 12 (Final):")
    result = hooks.execute_hooks(12, verbose=True)
    hooks.print_result(result, 12)

    # Test non-existent stage
    print("\n\nTesting Stage 5 (no hooks):")
    result = hooks.execute_hooks(5, verbose=True)
    hooks.print_result(result, 5)
