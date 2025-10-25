#!/usr/bin/env python3
"""
IMPLEMENT.PY EXECUTION TEST - VERIFY ACTUAL FILE GENERATION

This test suite verifies that implement.py ACTUALLY WORKS by:
1. Executing each phase
2. Checking that files are created/modified in the real project
3. Validating file contents match expectations

This is INTEGRATION TESTING - verifying the real implementation works as documented.

Run with: python test_implement_direct.py
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import implement module
sys.path.insert(0, str(Path(__file__).parent))
import implement

# Test tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": [],
}


# Colored output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def log_test(name: str, status: str, details: str = ""):
    """Log test result with color"""
    colors = {
        "PASS": Colors.GREEN,
        "FAIL": Colors.RED,
        "SKIP": Colors.YELLOW,
    }
    color = colors.get(status, Colors.BLUE)
    print(f"{color}[{status}]{Colors.RESET} {name}")
    if details:
        print(f"       {details}")


def record_test(name: str, status: str, message: str = ""):
    """Record test result"""
    test_results["total"] += 1
    if status == "PASS":
        test_results["passed"] += 1
    elif status == "FAIL":
        test_results["failed"] += 1

    test_results["tests"].append(
        {
            "name": name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
    )
    log_test(name, status, message)


# ============================================================================
# EXECUTION TESTS
# ============================================================================


def test_phase1_execution():
    """Execute Phase 1: Lane selection - verify workflow.py is modified"""
    try:
        print(f"\n{Colors.BOLD}[PHASE 1] Lane Selection Execution{Colors.RESET}")

        # Get reference to actual files that will be modified
        project_root = implement.project_root
        workflow_file = implement.scripts_root / "workflow.py"

        # Get original content
        original_content = workflow_file.read_text() if workflow_file.exists() else ""
        original_has_lane = "LANE_MAPPING" in original_content

        # Execute Phase 1
        result = implement.implement_lane_selection_python()

        if not result:
            record_test(
                "phase1_execution_result",
                "FAIL",
                "implement_lane_selection_python() returned False",
            )
            return False

        # Verify workflow.py was modified
        if not workflow_file.exists():
            record_test(
                "phase1_workflow_exists",
                "FAIL",
                f"workflow.py not found at {workflow_file}",
            )
            return False

        new_content = workflow_file.read_text()

        # Check for LANE_MAPPING
        if "LANE_MAPPING" not in new_content:
            record_test(
                "phase1_lane_mapping_added",
                "FAIL",
                "LANE_MAPPING constant not in workflow.py",
            )
            return False

        record_test(
            "phase1_lane_mapping_added", "PASS", "LANE_MAPPING added to workflow.py"
        )

        # Check for lane definitions
        required_lanes = ["docs", "standard", "heavy"]
        for lane in required_lanes:
            if f'"{lane}"' not in new_content:
                record_test(
                    "phase1_lanes_defined", "FAIL", f"Lane '{lane}' not defined"
                )
                return False

        record_test(
            "phase1_lanes_defined",
            "PASS",
            f"All 3 lanes (docs, standard, heavy) defined",
        )

        # Check for helper functions
        if "def get_stages_for_lane" not in new_content:
            record_test(
                "phase1_helpers_exist",
                "FAIL",
                "get_stages_for_lane() function not found",
            )
            return False

        if "def should_run_quality_gates" not in new_content:
            record_test(
                "phase1_helpers_exist",
                "FAIL",
                "should_run_quality_gates() function not found",
            )
            return False

        record_test(
            "phase1_helpers_exist",
            "PASS",
            "Helper functions (get_stages_for_lane, should_run_quality_gates) exist",
        )

        return True

    except Exception as e:
        record_test("phase1_execution", "FAIL", f"Exception: {str(e)}")
        return False


def test_phase2_execution():
    """Execute Phase 2: Quality gates module - verify quality_gates.py is created"""
    try:
        print(f"\n{Colors.BOLD}[PHASE 2] Quality Gates Module Execution{Colors.RESET}")

        qg_file = implement.scripts_root / "quality_gates.py"
        qg_existed = qg_file.exists()

        # Execute Phase 2
        result = implement.create_quality_gates_module()

        if not result:
            record_test(
                "phase2_execution_result",
                "FAIL",
                "create_quality_gates_module() returned False",
            )
            return False

        # Verify quality_gates.py was created
        if not qg_file.exists():
            record_test(
                "phase2_file_created",
                "FAIL",
                f"quality_gates.py not created at {qg_file}",
            )
            return False

        action = "modified" if qg_existed else "created"
        record_test("phase2_file_created", "PASS", f"quality_gates.py {action}")

        # Verify content
        content = qg_file.read_text()

        if "class QualityGates" not in content:
            record_test(
                "phase2_qualitygates_class", "FAIL", "QualityGates class not defined"
            )
            return False

        record_test("phase2_qualitygates_class", "PASS", "QualityGates class defined")

        # Check for required methods
        required_methods = [
            "run_all",
            "run_ruff",
            "run_mypy",
            "run_pytest",
            "run_bandit",
            "save_metrics",
            "_all_passed",
        ]

        missing_methods = [m for m in required_methods if f"def {m}" not in content]

        if missing_methods:
            record_test(
                "phase2_methods_exist",
                "FAIL",
                f"Missing methods: {', '.join(missing_methods)}",
            )
            return False

        record_test(
            "phase2_methods_exist",
            "PASS",
            f"All {len(required_methods)} required methods defined",
        )

        # Check for THRESHOLDS
        if "THRESHOLDS" not in content:
            record_test("phase2_thresholds", "FAIL", "THRESHOLDS dict not defined")
            return False

        record_test("phase2_thresholds", "PASS", "THRESHOLDS configuration defined")

        return True

    except Exception as e:
        record_test("phase2_execution", "FAIL", f"Exception: {str(e)}")
        return False


def test_phase3_execution():
    """Execute Phase 3: Status JSON - verify status.json is created"""
    try:
        print(f"\n{Colors.BOLD}[PHASE 3] Status Tracking Execution{Colors.RESET}")

        status_file = (
            implement.project_root
            / "openspec"
            / "changes"
            / "workflow-improvements"
            / "status.json"
        )
        status_existed = status_file.exists()

        # Execute Phase 3
        result = implement.create_status_json_template()

        if not result:
            record_test(
                "phase3_execution_result",
                "FAIL",
                "create_status_json_template() returned False",
            )
            return False

        # Verify status.json was created
        if not status_file.exists():
            record_test(
                "phase3_file_created",
                "FAIL",
                f"status.json not created at {status_file}",
            )
            return False

        action = "modified" if status_existed else "created"
        record_test("phase3_file_created", "PASS", f"status.json {action}")

        # Verify it's valid JSON
        try:
            with open(status_file) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            record_test("phase3_json_valid", "FAIL", f"Invalid JSON: {str(e)}")
            return False

        record_test("phase3_json_valid", "PASS", "status.json contains valid JSON")

        # Check required schema fields
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

        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            record_test(
                "phase3_schema_complete",
                "FAIL",
                f"Missing fields: {', '.join(missing_fields)}",
            )
            return False

        record_test(
            "phase3_schema_complete",
            "PASS",
            f"All {len(required_fields)} required fields present",
        )

        # Verify resumption support
        if not isinstance(data.get("resumable"), bool):
            record_test(
                "phase3_resumption_support", "FAIL", "resumable should be boolean"
            )
            return False

        if data.get("resume_from_stage") is None:
            record_test(
                "phase3_resumption_support", "FAIL", "resume_from_stage not set"
            )
            return False

        record_test(
            "phase3_resumption_support",
            "PASS",
            "Resumption support (resumable, resume_from_stage) configured",
        )

        return True

    except Exception as e:
        record_test("phase3_execution", "FAIL", f"Exception: {str(e)}")
        return False


def test_integration_all_phases():
    """Integration test: Verify all files exist after direct execution"""
    try:
        print(f"\n{Colors.BOLD}[INTEGRATION] All Phases Complete{Colors.RESET}")

        # Check all expected files
        checks = [
            (
                implement.scripts_root / "workflow.py",
                "LANE_MAPPING",
                "Lane selection in workflow.py",
            ),
            (
                implement.scripts_root / "quality_gates.py",
                "class QualityGates",
                "QualityGates module",
            ),
            (
                implement.project_root
                / "openspec"
                / "changes"
                / "workflow-improvements"
                / "status.json",
                None,
                "Status tracking template",
            ),
        ]

        all_valid = True
        for filepath, content_check, description in checks:
            if not filepath.exists():
                record_test(
                    "integration_files_exist", "FAIL", f"File not found: {filepath}"
                )
                all_valid = False
                continue

            if content_check:
                file_content = filepath.read_text()
                if content_check not in file_content:
                    record_test(
                        "integration_files_content",
                        "FAIL",
                        f"Missing '{content_check}' in {filepath.name}",
                    )
                    all_valid = False

        if all_valid:
            record_test(
                "integration_all_phases",
                "PASS",
                "All 3 phases generated files successfully",
            )

        return all_valid

    except Exception as e:
        record_test("integration_all_phases", "FAIL", f"Exception: {str(e)}")
        return False


def test_python_syntax_validity():
    """Verify generated Python files are syntactically valid"""
    try:
        print(f"\n{Colors.BOLD}[VALIDATION] Python Syntax{Colors.RESET}")

        import py_compile

        python_files = [
            implement.scripts_root / "workflow.py",
            implement.scripts_root / "quality_gates.py",
        ]

        all_valid = True
        for filepath in python_files:
            if not filepath.exists():
                continue

            try:
                py_compile.compile(str(filepath), doraise=True)
                record_test(
                    "python_syntax_valid",
                    "PASS",
                    f"{filepath.name} is syntactically valid",
                )
            except py_compile.PyCompileError as e:
                record_test("python_syntax_valid", "FAIL", f"{filepath.name}: {str(e)}")
                all_valid = False

        return all_valid

    except Exception as e:
        record_test("python_syntax_valid", "FAIL", f"Exception: {str(e)}")
        return False


# ============================================================================
# TEST RUNNER
# ============================================================================


def main():
    """Run all execution tests"""
    print(f"\n{Colors.BOLD}{'=' * 80}")
    print(f"IMPLEMENT.PY - DIRECT EXECUTION TEST")
    print(f"Testing that implement.py generates correct files")
    print(f"{'=' * 80}{Colors.RESET}")

    print(f"\n{Colors.BLUE}Project Paths:{Colors.RESET}")
    print(f"  Project Root:  {implement.project_root}")
    print(f"  Scripts Root:  {implement.scripts_root}")
    print(f"  Change Root:   {implement.change_root}")

    # Execute phase tests
    test_phase1_execution()
    test_phase2_execution()
    test_phase3_execution()

    # Integration tests
    test_integration_all_phases()
    test_python_syntax_validity()

    # Print summary
    print(f"\n{Colors.BOLD}{'=' * 80}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 80}{Colors.RESET}")
    print(f"Total:   {test_results['total']}")
    print(f"{Colors.GREEN}Passed:  {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed:  {test_results['failed']}{Colors.RESET}")

    if test_results["total"] > 0:
        pass_rate = (test_results["passed"] / test_results["total"]) * 100
        print(f"Pass Rate: {pass_rate:.1f}%\n")

    # Show what was tested
    print(f"{Colors.BOLD}What Was Tested:{Colors.RESET}")
    print(f"  ✓ Phase 1: Lane selection (LANE_MAPPING, helper functions)")
    print(f"  ✓ Phase 2: Quality gates module (QualityGates class, 7 methods)")
    print(f"  ✓ Phase 3: Status tracking (status.json with resumption)")
    print(f"  ✓ Integration: All files created and syntactically valid")
    print()

    return 0 if test_results["failed"] == 0 else 1


if __name__ == "__main__":
    exit(main())
