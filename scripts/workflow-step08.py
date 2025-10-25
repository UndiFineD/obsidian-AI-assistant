#!/usr/bin/env python3
"""Step 8: Testing & Quality Gates

Tests the implementation changes and records results in test_results.md.
Verifies that the implementation actually changed the project.
Runs quality gates (ruff, mypy, pytest, bandit) with lane-specific thresholds.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

SCRIPT_DIR = Path(__file__).parent

spec = importlib.util.spec_from_file_location(
    "workflow_helpers",
    SCRIPT_DIR / "workflow-helpers.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

# Import quality gates
spec_qg = importlib.util.spec_from_file_location(
    "quality_gates",
    SCRIPT_DIR / "quality_gates.py",
)
quality_gates_module = importlib.util.module_from_spec(spec_qg)
spec_qg.loader.exec_module(quality_gates_module)

# Import progress indicators
try:
    import progress_indicators as progress
except ImportError:
    progress = None


def _mark_complete(change_path: Path) -> None:
    todo = change_path / "todo.md"
    if not todo.exists():
        return
    content = todo.read_text(encoding="utf-8")
    updated = content.replace("[ ] **8. Test", "[x] **8. Test")
    if updated != content:
        helpers.set_content_atomic(todo, updated)


def _check_git_changes(project_root: Path) -> Dict[str, List[str]]:
    """Check for git changes in the project."""
    changes = {
        "modified": [],
        "added": [],
        "deleted": [],
        "untracked": [],
    }

    try:
        # Get modified files
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            changes["modified"] = [
                f.strip() for f in result.stdout.split("\n") if f.strip()
            ]

        # Get added files
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            changes["untracked"] = [
                f.strip() for f in result.stdout.split("\n") if f.strip()
            ]
    except Exception as e:
        helpers.write_warning(f"Could not check git changes: {e}")

    return changes


def _check_file_changes(change_path: Path, project_root: Path) -> Dict[str, any]:
    """Check what files were changed/created by the implementation."""
    test_results = {
        "files_affected": [],
        "files_created": [],
        "files_modified": [],
        "total_changes": 0,
        "implementation_successful": False,
    }

    # Check if implementation notes document what was done
    impl_notes = change_path / "implementation_notes.md"
    if impl_notes.exists():
        content = impl_notes.read_text(encoding="utf-8")

        # Look for success indicators
        if "SUCCESS" in content or "PASSED" in content or "COMPLETED" in content:
            test_results["implementation_successful"] = True

            # Parse what was done
            if "Modules changed" in content:
                test_results["files_affected"].append("Modules documented as changed")
            if "Files created" in content:
                test_results["files_created"].append("Files documented as created")

    # Check git for actual changes
    git_changes = _check_git_changes(project_root)

    test_results["files_modified"] = git_changes["modified"]
    test_results["files_created"] = git_changes["added"] + git_changes["untracked"]
    test_results["total_changes"] = len(git_changes["modified"]) + len(
        git_changes["added"]
    )

    return test_results


def _run_verify_script(script_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Run verification script and return (success, output)."""
    if not script_path.exists():
        return False, f"Verification script not found: {script_path}"

    if dry_run:
        return True, "[DRY RUN] Would execute verification script"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Verification execution timed out"
    except Exception as e:
        return False, f"Error running verification: {e}"


def _run_test_script(script_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Run test.py script and return (success, output)."""
    if not script_path.exists():
        return False, f"Test script not found: {script_path}"

    if dry_run:
        return True, "[DRY RUN] Would execute test script"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Test execution timed out"
    except Exception as e:
        return False, f"Error running tests: {e}"


def _run_quality_gates(
    lane: str = "standard", dry_run: bool = False
) -> tuple[bool, Dict]:
    """Run quality gates for the specified lane and return (success, results)."""
    if dry_run:
        return True, {"overall": "PASS", "lane": lane, "dry_run": True}

    try:
        gates = quality_gates_module.QualityGates(lane=lane)
        success = gates.run_all()

        # Save metrics
        gates.save_metrics(Path.cwd() / f"quality_metrics_{lane}.json")

        return success, gates.results
    except Exception as e:
        helpers.write_error(f"Error running quality gates: {e}")
        return False, {"error": str(e), "overall": "FAIL"}


def _show_remediation_steps(gates_results: Dict) -> None:
    """Display remediation steps for failed quality gates."""
    helpers.write_info("\n📋 Remediation Steps for Quality Gates Failures:\n")

    # Check each tool
    for tool, result in gates_results.items():
        if isinstance(result, dict) and result.get("status") == "FAIL":
            if tool == "ruff":
                helpers.write_info(
                    f"🔧 Ruff Linting Issues ({result.get('errors', 0)} errors):"
                )
                helpers.write_info("  Run: ruff check agent/ scripts/ --fix")
                helpers.write_info("  Review: https://docs.astral.sh/ruff/rules/\n")
            elif tool == "mypy":
                helpers.write_info(
                    f"🔧 Type Checking Issues ({result.get('errors', 0)} errors):"
                )
                helpers.write_info("  Run: mypy agent/ --ignore-missing-imports")
                helpers.write_info("  Add type hints to files with errors\n")
            elif tool == "pytest":
                coverage = result.get("coverage", 0)
                threshold = result.get("coverage_threshold", 0.70)
                helpers.write_info(
                    f"🔧 Test Coverage Issues ({coverage * 100:.0f}% vs {threshold * 100:.0f}% required):"
                )
                helpers.write_info(
                    "  Run: pytest tests/ -v --cov=agent --cov-report=html"
                )
                helpers.write_info("  Add tests to improve coverage\n")
            elif tool == "bandit":
                helpers.write_info(
                    f"🔧 Security Issues ({result.get('high_severity', 0)} high-severity):"
                )
                helpers.write_info("  Run: bandit -r agent/ -f txt")
                helpers.write_info("  Review security best practices\n")

    helpers.write_info(
        "💡 Tip: Run 'ruff check --fix' first to auto-fix linting issues"
    )


def invoke_step8(
    change_path: Path, lane: str = "standard", dry_run: bool = False, **_: dict
) -> bool:
    helpers.write_step(8, "Testing & Quality Gates - Verify Implementation")
    results = change_path / "test_results.md"
    test_script = change_path / "test.py"

    # Get project root for change detection
    project_root = change_path.parent.parent.parent

    # Phase 1: Check for implementation changes
    helpers.write_info("Phase 1: Verifying implementation changes...")
    change_results = _check_file_changes(change_path, project_root)

    files_modified = len(change_results["files_modified"])
    files_created = len(change_results["files_created"])
    total_changes = files_modified + files_created

    impl_success = change_results["implementation_successful"] or total_changes > 0

    if impl_success:
        helpers.write_success(
            f"✓ Implementation verified: {files_modified} modified, "
            f"{files_created} created"
        )
    else:
        helpers.write_warning("⚠ No implementation changes detected")

    # Phase 2: Run test script if available
    helpers.write_info("Phase 2: Running verification tests...")
    test_success = True
    test_output = ""

    if test_script.exists():
        if progress:
            with progress.spinner("Running verification tests", "Tests completed"):
                test_success, test_output = _run_test_script(test_script, dry_run)
        else:
            test_success, test_output = _run_test_script(test_script, dry_run)
            if not dry_run and test_output:
                print(f"Test output:\n{test_output}")

        if test_success or dry_run:
            helpers.write_success("✓ Verification tests passed")
        else:
            helpers.write_warning("⚠ Some verification tests failed")
    else:
        helpers.write_info(f"ℹ No test.py found at {test_script}")
        test_output = "No test script available for verification"

    # Phase 3: Run quality gates
    helpers.write_info(f"Phase 3: Running quality gates ({lane} lane)...")
    gates_success = True
    gates_results = {}

    if progress:
        with progress.spinner(
            f"Running quality gates ({lane} lane)", "Quality gates completed"
        ):
            gates_success, gates_results = _run_quality_gates(lane, dry_run)
    else:
        gates_success, gates_results = _run_quality_gates(lane, dry_run)

    if gates_success or dry_run or gates_results.get("dry_run"):
        helpers.write_success(f"✓ Quality gates passed ({lane} lane)")
    else:
        helpers.write_error(f"✗ Quality gates failed ({lane} lane)")
        # Show remediation steps
        if not dry_run:
            _show_remediation_steps(gates_results)

    # Phase 4: Record comprehensive results
    helpers.write_info("Phase 4: Recording test results...")

    if not dry_run:
        if progress:
            with progress.spinner("Recording results", "Results recorded"):
                _record_test_results(
                    results,
                    change_results,
                    test_success,
                    test_output,
                    gates_success,
                    gates_results,
                )
        else:
            _record_test_results(
                results,
                change_results,
                test_success,
                test_output,
                gates_success,
                gates_results,
            )
            helpers.write_success(f"Updated: {results}")
    else:
        helpers.write_info(f"[DRY RUN] Would record test results: {results}")

    _mark_complete(change_path)
    helpers.write_success("Step 8 completed")

    # Success if implementation happened, tests passed, and quality gates passed
    return impl_success and test_success and gates_success


def _record_test_results(
    results_file: Path,
    change_results: Dict,
    test_success: bool,
    test_output: str,
    gates_success: bool = True,
    gates_results: Dict = None,
) -> None:
    """Record comprehensive test results and quality gates to test_results.md."""
    if gates_results is None:
        gates_results = {}

    existing = results_file.read_text(encoding="utf-8") if results_file.exists() else ""

    # Determine overall status
    impl_status = (
        "SUCCESS" if change_results["implementation_successful"] else "DETECTED"
    )
    test_status = "PASSED" if test_success else "FAILED"
    gates_status = "PASSED" if gates_success else "FAILED"

    block = (
        "\n## Test Results - Implementation Verification\n\n"
        "### Implementation Status\n"
        f"- **Status**: {impl_status}\n"
        f"- **Files Modified**: {len(change_results['files_modified'])}\n"
        f"- **Files Created**: {len(change_results['files_created'])}\n"
        f"- **Total Changes**: {change_results['total_changes']}\n"
    )

    if change_results["files_modified"]:
        block += "\n**Modified Files:**\n"
        for f in change_results["files_modified"][:10]:  # Limit to 10
            block += f"- `{f}`\n"
        if len(change_results["files_modified"]) > 10:
            block += f"- ... and {len(change_results['files_modified']) - 10} more\n"

    if change_results["files_created"]:
        block += "\n**Created Files:**\n"
        for f in change_results["files_created"][:10]:  # Limit to 10
            block += f"- `{f}`\n"
        if len(change_results["files_created"]) > 10:
            block += f"- ... and {len(change_results['files_created']) - 10} more\n"

    block += "\n### Test Execution\n"
    block += f"- **Status**: {test_status}\n"
    block += f"- **Tests Run**: {'Yes' if test_output else 'No'}\n"

    if test_output:
        # Limit output to first 1000 chars
        truncated = test_output[:1000]
        if len(test_output) > 1000:
            truncated += "\n... (output truncated)"
        block += f"\n**Test Output:**\n```\n{truncated}\n```\n"

    # Add quality gates results
    if gates_results and not gates_results.get("dry_run"):
        block += "\n### Quality Gates\n"
        lane = gates_results.get("lane", "standard")
        block += f"- **Status**: {gates_status}\n"
        block += f"- **Lane**: {lane}\n"

        if gates_results.get("ruff"):
            block += f"- **Ruff**: {gates_results['ruff'].get('status', 'SKIP')} "
            block += f"({gates_results['ruff'].get('errors', 0)} errors)\n"
        if gates_results.get("mypy"):
            block += f"- **Mypy**: {gates_results['mypy'].get('status', 'SKIP')} "
            block += f"({gates_results['mypy'].get('errors', 0)} errors)\n"
        if gates_results.get("pytest"):
            coverage = gates_results["pytest"].get("coverage", 0)
            block += f"- **Pytest**: {gates_results['pytest'].get('status', 'SKIP')} "
            block += f"({int(coverage * 100)}% coverage)\n"
        if gates_results.get("bandit"):
            block += f"- **Bandit**: {gates_results['bandit'].get('status', 'SKIP')} "
            block += (
                f"({gates_results['bandit'].get('high_severity', 0)} high-severity)\n"
            )

    block += "\n### Overall Result\n"
    overall = (
        "✅ PASS"
        if (
            change_results["implementation_successful"]
            and test_success
            and gates_success
        )
        else "⚠️ VERIFY"
    )
    block += f"- {overall}\n"

    helpers.set_content_atomic(results_file, existing + block)


if __name__ == "__main__":
    test_dir = Path("openspec/changes/test-step8")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = invoke_step8(test_dir, dry_run=True)
    sys.exit(0 if ok else 1)
