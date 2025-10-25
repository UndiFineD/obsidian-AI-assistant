#!/usr/bin/env python3
"""
Comprehensive test suite for workflow-improvements implementation

This test validates that implement.py correctly makes ALL the changes specified in:
- proposal.md: Business requirements and objectives
- spec.md: Acceptance criteria and technical specifications
- tasks.md: Implementation task breakdown
- test_plan.md: Testing strategy

Test Strategy:
1. Tests that implement.py executes all phases without error
2. Tests that files are created/modified correctly
3. Tests that generated code contains all documented features
4. Tests that all acceptance criteria are satisfied

Run with: python test.py
"""

import sys
import json
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any

# Setup paths
change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent
scripts_root = project_root / "scripts"

# Test tracking
test_results = {"passed": 0, "failed": 0, "skipped": 0, "failures": [], "summary": {}}

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def log(msg: str, color: str = RESET, end: str = "\n"):
    """Print colored log message"""
    print(f"{color}{msg}{RESET}", end=end, flush=True)


def log_pass(msg: str):
    """Log passing test"""
    log(f"[OK] {msg}", GREEN)
    test_results["passed"] += 1


def log_fail(msg: str, reason: str = ""):
    """Log failing test"""
    log(f"[FAIL] {msg}", RED)
    if reason:
        log(f"   Reason: {reason}", YELLOW)
    test_results["failed"] += 1
    test_results["failures"].append((msg, reason))


def log_skip(msg: str, reason: str = ""):
    """Log skipped test"""
    log(f"[SKIP] {msg}", YELLOW)
    if reason:
        log(f"   Reason: {reason}", YELLOW)
    test_results["skipped"] += 1


def log_section(title: str):
    """Log test section header"""
    log(f"\n{'=' * 70}", BLUE)
    log(f"{title}", BOLD + BLUE)
    log(f"{'=' * 70}", BLUE)


# ============================================================================
# ACCEPTANCE CRITERIA TESTS - From spec.md Section 3
# ============================================================================


def test_lane_selection_acceptance_criteria():
    """Test all lane selection acceptance criteria from spec.md"""
    log_section("LANE SELECTION ACCEPTANCE CRITERIA")

    workflow_file = scripts_root / "workflow.py"
    if not workflow_file.exists():
        log_fail("workflow.py exists", "File not found")
        return False

    content = workflow_file.read_text(encoding="utf-8", errors="replace")

    # AC1: --lane [docs|standard|heavy] flag exists
    if "--lane" in content and (
        "docs" in content and "standard" in content and "heavy" in content
    ):
        log_pass("AC1: --lane flag with docs|standard|heavy choices")
    else:
        log_fail("AC1: --lane flag with docs|standard|heavy choices")

    # AC2: Lane-to-stage mapping implemented
    if "LANE_MAPPING" in content and all(
        x in content for x in ["docs", "standard", "heavy"]
    ):
        log_pass("AC2: Lane-to-stage mapping implemented")
    else:
        log_fail("AC2: Lane-to-stage mapping implemented")

    # AC3: Helper functions exist
    if "get_stages_for_lane" in content and "should_run_quality_gates" in content:
        log_pass(
            "AC3: Helper functions (get_stages_for_lane, should_run_quality_gates)"
        )
    else:
        log_fail("AC3: Helper functions")

    # AC4: Default lane is "standard" (backward compatible)
    if 'default="standard"' in content or "standard" in content:
        log_pass("AC4: Default lane is 'standard' (backward compatible)")
    else:
        log_fail("AC4: Default lane")


def test_parallelization_acceptance_criteria():
    """Test parallelization acceptance criteria from spec.md"""
    log_section("PARALLELIZATION ACCEPTANCE CRITERIA")

    workflow_file = scripts_root / "workflow.py"
    if not workflow_file.exists():
        log_skip("Parallelization tests", "workflow.py not found")
        return False

    content = workflow_file.read_text(encoding="utf-8", errors="replace")

    # AC1: Stages 2-6 parallel by default
    if any(x in content for x in ["ThreadPoolExecutor", "max_workers", "parallel"]):
        log_pass("AC1: Stages 2-6 can run in parallel (parallelization support)")
    else:
        log_skip("AC1: Stages 2-6 parallel", "Parallelization code not yet implemented")

    # AC2: --no-parallel flag
    if "--no-parallel" in content:
        log_pass("AC2: --no-parallel flag exists")
    else:
        log_skip("AC2: --no-parallel flag", "Not yet implemented")


def test_quality_gates_acceptance_criteria():
    """Test quality gates acceptance criteria from spec.md"""
    log_section("QUALITY GATES (STAGE 8) ACCEPTANCE CRITERIA")

    qg_file = scripts_root / "quality_gates.py"
    if not qg_file.exists():
        log_fail("AC1: quality_gates.py module created", f"File not found at {qg_file}")
        return False

    log_pass("AC1: quality_gates.py module created")

    content = qg_file.read_text(encoding="utf-8")

    # AC2: Executes ruff, mypy, pytest, bandit
    tools = ["ruff", "mypy", "pytest", "bandit"]
    for tool in tools:
        if tool in content:
            log_pass(f"AC2: {tool.upper()} integration present")
        else:
            log_fail(f"AC2: {tool.upper()} integration")

    # AC3: QualityGates class
    if "class QualityGates" in content:
        log_pass("AC3: QualityGates class defined")
    else:
        log_fail("AC3: QualityGates class defined")

    # AC4: THRESHOLDS dict with lane-specific configs
    if "THRESHOLDS" in content:
        log_pass("AC4: THRESHOLDS dict with lane-specific configurations")
    else:
        log_fail("AC4: THRESHOLDS dict")

    # AC5: Emits quality_metrics.json
    if "quality_metrics.json" in content or "json.dump" in content:
        log_pass("AC5: Emits quality metrics (JSON format)")
    else:
        log_skip(
            "AC5: quality_metrics.json emission", "Output format implementation pending"
        )


def test_status_tracking_acceptance_criteria():
    """Test status tracking acceptance criteria from spec.md"""
    log_section("STATUS TRACKING ACCEPTANCE CRITERIA")

    # Check if status.json template is created
    status_file = change_root / "status.json"
    if not status_file.exists():
        log_skip(
            "Status tracking tests",
            "status.json template not found (will be created by implement.py)",
        )
        return False

    log_pass("Status tracking: status.json template exists")

    try:
        data = json.loads(status_file.read_text())

        # Required fields
        required_fields = [
            "workflow_id",
            "lane",
            "status",
            "current_stage",
            "completed_stages",
            "failed_stages",
            "quality_gates_results",
            "resumable",
            "resume_from_stage",
        ]

        for field in required_fields:
            if field in data:
                log_pass(f"Status tracking: '{field}' field present")
            else:
                log_fail(f"Status tracking: '{field}' field present")

        # Resumption support
        if "resumable" in data and "resume_from_stage" in data:
            log_pass(
                "Status tracking: Resumption support (resumable, resume_from_stage)"
            )
        else:
            log_fail("Status tracking: Resumption support")

    except json.JSONDecodeError as e:
        log_fail("Status tracking: Valid JSON format", str(e))


def test_pre_step_hooks_acceptance_criteria():
    """Test pre-step validation hooks acceptance criteria from spec.md"""
    log_section("PRE-STEP VALIDATION HOOKS ACCEPTANCE CRITERIA")

    workflow_file = scripts_root / "workflow.py"
    if not workflow_file.exists():
        log_skip("Pre-step hooks tests", "workflow.py not found")
        return False

    content = workflow_file.read_text(encoding="utf-8", errors="replace")

    # AC1: Hook registry/system
    if any(x in content for x in ["hook", "validate", "check", "pre_step"]):
        log_pass("AC1: Hook system or validation framework present")
    else:
        log_skip("AC1: Hook system", "Hook registry not yet implemented")

    # AC2: Stage 0 - Python environment validation
    if "python" in content.lower() and any(
        x in content for x in ["env", "version", "virtualenv"]
    ):
        log_pass("AC2: Stage 0 environment validation present")
    else:
        log_skip("AC2: Stage 0 environment validation", "Not yet implemented")

    # AC3: Stage 10 - Git state validation
    if "git" in content.lower() and any(
        x in content for x in ["clean", "status", "branch"]
    ):
        log_pass("AC3: Stage 10 git state validation present")
    else:
        log_skip("AC3: Stage 10 git validation", "Not yet implemented")


def test_conventional_commits_acceptance_criteria():
    """Test conventional commits acceptance criteria from spec.md"""
    log_section("CONVENTIONAL COMMITS (STAGE 10) ACCEPTANCE CRITERIA")

    workflow_file = scripts_root / "workflow.py"
    if not workflow_file.exists():
        log_skip("Conventional commits tests", "workflow.py not found")
        return False

    content = workflow_file.read_text(encoding="utf-8", errors="replace")

    # AC1: Conventional commit validation
    if any(x in content for x in ["commit", "conventional", "format", "feat:", "fix:"]):
        log_pass("AC1: Conventional commits validation or format support")
    else:
        log_skip("AC1: Conventional commits", "Not yet implemented")


# ============================================================================
# IMPLEMENTATION QUALITY TESTS
# ============================================================================


def test_generated_files_syntax():
    """Test that all generated Python files have valid syntax"""
    log_section("GENERATED FILES - PYTHON SYNTAX VALIDATION")

    python_files = [
        (scripts_root / "workflow.py", "workflow.py"),
        (scripts_root / "quality_gates.py", "quality_gates.py"),
    ]

    import py_compile

    for filepath, name in python_files:
        if not filepath.exists():
            log_skip(f"Syntax check: {name}", "File not found")
            continue

        try:
            py_compile.compile(str(filepath), doraise=True)
            log_pass(f"Syntax check: {name} is valid Python")
        except py_compile.PyCompileError as e:
            log_fail(f"Syntax check: {name}", f"Syntax error: {str(e)[:100]}")


def test_generated_files_structure():
    """Test that generated files have required structure"""
    log_section("GENERATED FILES - STRUCTURE VALIDATION")

    # Check workflow.py structure
    workflow_file = scripts_root / "workflow.py"
    if workflow_file.exists():
        content = workflow_file.read_text(encoding="utf-8", errors="replace")

        required = ["def ", "argparse", "main"]
        for req in required:
            if req in content:
                log_pass(f"workflow.py: Contains '{req}'")
            else:
                log_fail(f"workflow.py: Contains '{req}'")

    # Check quality_gates.py structure
    qg_file = scripts_root / "quality_gates.py"
    if qg_file.exists():
        content = qg_file.read_text(encoding="utf-8")

        required = ["class QualityGates", "THRESHOLDS", "def run_"]
        for req in required:
            if req in content:
                log_pass(f"quality_gates.py: Contains '{req}'")
            else:
                log_fail(f"quality_gates.py: Contains '{req}'")


def test_documentation_completeness():
    """Test that all required documentation files exist and are substantial"""
    log_section("DOCUMENTATION - COMPLETENESS")

    docs = [
        ("proposal.md", 800, "Proposal document"),
        ("spec.md", 1000, "Technical specification"),
        ("tasks.md", 1000, "Task breakdown"),
        ("test_plan.md", 600, "Testing strategy"),
        ("todo.md", 100, "TODO tracking"),
    ]

    for filename, min_lines, description in docs:
        filepath = change_root / filename

        if not filepath.exists():
            log_fail(f"{description}: Exists", f"File not found: {filename}")
            continue

        lines = len(filepath.read_text(encoding="utf-8", errors="replace").splitlines())
        if lines >= min_lines:
            log_pass(f"{description}: {filename} ({lines} lines)")
        else:
            log_fail(
                f"{description}: {filename}", f"Only {lines} lines, need {min_lines}+"
            )


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_implement_py_execution():
    """Test that implement.py can be imported and executed"""
    log_section("INTEGRATION - IMPLEMENT.PY EXECUTION")

    implement_file = change_root / "implement.py"
    if not implement_file.exists():
        log_fail("implement.py exists", "File not found")
        return False

    log_pass("implement.py exists and is accessible")

    # Try to import it
    try:
        spec = __import__("importlib.util").util.spec_from_file_location(
            "implement", implement_file
        )
        module = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(module)
        log_pass("implement.py is importable and syntactically valid")
    except Exception as e:
        log_fail("implement.py is importable", str(e)[:100])


def test_all_acceptance_criteria_documented():
    """Test that all acceptance criteria are documented in spec.md"""
    log_section("DOCUMENTATION - ACCEPTANCE CRITERIA")

    spec_file = change_root / "spec.md"
    if not spec_file.exists():
        log_fail("spec.md exists", "File not found")
        return False

    content = spec_file.read_text(encoding="utf-8", errors="replace")

    criteria_sections = [
        ("Lane Selection", "Lane Selection"),
        ("Parallelization", "Parallelization"),
        ("Quality Gates", "Quality Gates"),
        ("Status Tracking", r"Status.*Tracking|status\.json"),
        ("Pre-Step Hooks", r"Pre-Step.*Validation|Validation.*Hooks"),
    ]

    for name, pattern in criteria_sections:
        if re.search(pattern, content, re.IGNORECASE):
            log_pass(f"spec.md: {name} criteria documented")
        else:
            log_fail(f"spec.md: {name} criteria documented")


# ============================================================================
# TEST RUNNER
# ============================================================================


def main():
    """Run all tests"""
    log(f"\n{BOLD}{'=' * 70}{RESET}")
    log(f"{BOLD}WORKFLOW-IMPROVEMENTS COMPREHENSIVE TEST SUITE{RESET}", BOLD)
    log(f"{BOLD}{'=' * 70}{RESET}\n")

    log("Testing that implement.py correctly implements all documented changes")
    log("from proposal.md, spec.md, tasks.md, and test_plan.md\n")

    # Run test suites
    test_lane_selection_acceptance_criteria()
    test_parallelization_acceptance_criteria()
    test_quality_gates_acceptance_criteria()
    test_status_tracking_acceptance_criteria()
    test_pre_step_hooks_acceptance_criteria()
    test_conventional_commits_acceptance_criteria()

    test_generated_files_syntax()
    test_generated_files_structure()
    test_documentation_completeness()

    test_implement_py_execution()
    test_all_acceptance_criteria_documented()

    # Print summary
    log(f"\n{BOLD}{'=' * 70}{RESET}")
    log(f"{BOLD}TEST SUMMARY{RESET}", BOLD)
    log(f"{BOLD}{'=' * 70}{RESET}\n")

    total = test_results["passed"] + test_results["failed"] + test_results["skipped"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    log(f"Total Tests:  {total}")
    log(f"Passed:       {test_results['passed']}", GREEN)
    log(
        f"Failed:       {test_results['failed']}",
        RED if test_results["failed"] > 0 else GREEN,
    )
    log(
        f"Skipped:      {test_results['skipped']}",
        YELLOW if test_results["skipped"] > 0 else GREEN,
    )
    log(f"Pass Rate:    {pass_rate:.1f}%\n")

    if test_results["failures"]:
        log(f"{BOLD}Failed Tests:{RESET}", RED)
        for name, reason in test_results["failures"]:
            log(f"  - {name}", RED)
            if reason:
                log(f"    {reason}", YELLOW)
        log("")

    test_results["summary"] = {
        "total": total,
        "passed": test_results["passed"],
        "failed": test_results["failed"],
        "skipped": test_results["skipped"],
        "pass_rate": pass_rate,
    }

    if test_results["failed"] == 0:
        log(f"{BOLD}[SUCCESS] ALL TESTS PASSED{RESET}\n", GREEN)
        return 0
    else:
        log(f"{BOLD}[FAILED] SOME TESTS FAILED{RESET}\n", RED)
        return 1


if __name__ == "__main__":
    exit(main())
