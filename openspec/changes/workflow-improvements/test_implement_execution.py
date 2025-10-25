#!/usr/bin/env python3
"""
EXECUTION TEST HARNESS - Test implement.py generates correct files

This test suite verifies that implement.py actually WORKS - that when executed,
it generates the correct files with correct content.

Tests cover:
1. Phase 1: Lane selection modification to workflow.py
2. Phase 2: Quality gates module creation
3. Phase 3: Status JSON template creation
4. Integration: Full main() execution

Run with: python test_implement_execution.py
"""

import sys
import json
import tempfile
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add parent to path for implement module
sys.path.insert(0, str(Path(__file__).parent))
import implement

# Test tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": [],
    "start_time": datetime.now().isoformat(),
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
    elif status == "SKIP":
        test_results["skipped"] += 1

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
# TEST FIXTURES
# ============================================================================


class TestEnvironment:
    """Create isolated test environment with temporary files"""

    def __init__(self):
        self.temp_dir = None
        self.scripts_backup = {}
        self.original_scripts_root = None

    def setup(self):
        """Create temporary test directory with test fixtures"""
        self.temp_dir = tempfile.mkdtemp(prefix="test_implement_")
        scripts_dir = Path(self.temp_dir) / "scripts"
        scripts_dir.mkdir(parents=True)

        # Create minimal test workflow.py
        workflow_path = scripts_dir / "workflow.py"
        workflow_path.write_text('''#!/usr/bin/env python3
"""Test workflow.py"""

def main():
    """Main workflow function"""
    print("Workflow executed")

if __name__ == "__main__":
    main()
''')

        # Temporarily override scripts root in implement module
        self.original_scripts_root = implement.scripts_root
        implement.scripts_root = scripts_dir

        return scripts_dir

    def cleanup(self):
        """Clean up temporary test environment"""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        if self.original_scripts_root:
            implement.scripts_root = self.original_scripts_root


# ============================================================================
# PHASE 1 TESTS: Lane Selection
# ============================================================================


def test_phase1_lane_selection_execution():
    """Execute Phase 1: Lane selection modification"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        # Execute Phase 1
        result = implement.implement_lane_selection_python()

        if not result:
            record_test(
                "test_phase1_lane_selection_execution",
                "FAIL",
                "implement_lane_selection_python() returned False",
            )
            return False

        # Verify workflow.py was modified
        workflow_file = scripts_dir / "workflow.py"
        content = workflow_file.read_text()

        # Check for LANE_MAPPING
        if "LANE_MAPPING" not in content:
            record_test(
                "test_phase1_lane_selection_execution",
                "FAIL",
                "LANE_MAPPING constant not added to workflow.py",
            )
            return False

        # Check for lane definitions
        required_lanes = ["docs", "standard", "heavy"]
        for lane in required_lanes:
            if f'"{lane}"' not in content:
                record_test(
                    "test_phase1_lane_selection_execution",
                    "FAIL",
                    f"Lane '{lane}' not defined in LANE_MAPPING",
                )
                return False

        # Check for helper functions
        required_functions = ["get_stages_for_lane", "should_run_quality_gates"]
        for func in required_functions:
            if f"def {func}" not in content:
                record_test(
                    "test_phase1_lane_selection_execution",
                    "FAIL",
                    f"Helper function '{func}' not defined",
                )
                return False

        record_test(
            "test_phase1_lane_selection_execution",
            "PASS",
            f"LANE_MAPPING with {len(required_lanes)} lanes added successfully",
        )
        return True

    except Exception as e:
        record_test(
            "test_phase1_lane_selection_execution", "FAIL", f"Exception: {str(e)}"
        )
        return False
    finally:
        env.cleanup()


def test_phase1_lanes_have_stages():
    """Verify each lane has correct stage configuration"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        implement.implement_lane_selection_python()
        workflow_file = scripts_dir / "workflow.py"
        content = workflow_file.read_text()

        # Extract LANE_MAPPING definition
        if "LANE_MAPPING" not in content:
            record_test(
                "test_phase1_lanes_have_stages", "FAIL", "LANE_MAPPING not found"
            )
            return False

        # Check for stage configurations
        checks = [
            ('docs.*"stages"', "docs lane has stages"),
            ('standard.*"stages"', "standard lane has stages"),
            ('heavy.*"stages"', "heavy lane has stages"),
        ]

        for pattern, description in checks:
            if not re.search(pattern, content, re.DOTALL):
                record_test(
                    "test_phase1_lanes_have_stages", "FAIL", f"Missing: {description}"
                )
                return False

        record_test(
            "test_phase1_lanes_have_stages",
            "PASS",
            "All lanes have stage configurations",
        )
        return True

    except Exception as e:
        record_test("test_phase1_lanes_have_stages", "FAIL", f"Exception: {str(e)}")
        return False
    finally:
        env.cleanup()


def test_phase1_quality_gates_flag():
    """Verify quality_gates flag differs by lane"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        implement.implement_lane_selection_python()
        workflow_file = scripts_dir / "workflow.py"
        content = workflow_file.read_text()

        # Check docs lane has quality_gates: False
        docs_section = re.search(r'"docs":\s*{([^}]+)}', content, re.DOTALL)
        if docs_section:
            if '"quality_gates": False' not in docs_section.group(1):
                record_test(
                    "test_phase1_quality_gates_flag",
                    "FAIL",
                    "docs lane should have quality_gates: False",
                )
                return False

        # Check standard/heavy have quality_gates: True
        for lane in ["standard", "heavy"]:
            lane_section = re.search(rf'"{lane}":\s*{{([^}}]+)}}', content, re.DOTALL)
            if lane_section:
                if '"quality_gates": True' not in lane_section.group(1):
                    record_test(
                        "test_phase1_quality_gates_flag",
                        "FAIL",
                        f"{lane} lane should have quality_gates: True",
                    )
                    return False

        record_test(
            "test_phase1_quality_gates_flag",
            "PASS",
            "quality_gates flag correctly configured per lane",
        )
        return True

    except Exception as e:
        record_test("test_phase1_quality_gates_flag", "FAIL", f"Exception: {str(e)}")
        return False
    finally:
        env.cleanup()


# ============================================================================
# PHASE 2 TESTS: Quality Gates Module
# ============================================================================


def test_phase2_quality_gates_creation():
    """Execute Phase 2: Quality gates module creation"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        # Execute Phase 2
        result = implement.create_quality_gates_module()

        if not result:
            record_test(
                "test_phase2_quality_gates_creation",
                "FAIL",
                "create_quality_gates_module() returned False",
            )
            return False

        # Verify quality_gates.py was created
        qg_file = scripts_dir / "quality_gates.py"
        if not qg_file.exists():
            record_test(
                "test_phase2_quality_gates_creation",
                "FAIL",
                "quality_gates.py was not created",
            )
            return False

        content = qg_file.read_text()

        # Check for QualityGates class
        if "class QualityGates" not in content:
            record_test(
                "test_phase2_quality_gates_creation",
                "FAIL",
                "QualityGates class not defined in quality_gates.py",
            )
            return False

        record_test(
            "test_phase2_quality_gates_creation",
            "PASS",
            "quality_gates.py created with QualityGates class",
        )
        return True

    except Exception as e:
        record_test(
            "test_phase2_quality_gates_creation", "FAIL", f"Exception: {str(e)}"
        )
        return False
    finally:
        env.cleanup()


def test_phase2_quality_gates_methods():
    """Verify QualityGates class has required methods"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        implement.create_quality_gates_module()
        qg_file = scripts_dir / "quality_gates.py"
        content = qg_file.read_text()

        required_methods = [
            "run_all",
            "run_ruff",
            "run_mypy",
            "run_pytest",
            "run_bandit",
            "save_metrics",
            "_all_passed",
        ]

        missing_methods = []
        for method in required_methods:
            if f"def {method}" not in content:
                missing_methods.append(method)

        if missing_methods:
            record_test(
                "test_phase2_quality_gates_methods",
                "FAIL",
                f"Missing methods: {', '.join(missing_methods)}",
            )
            return False

        record_test(
            "test_phase2_quality_gates_methods",
            "PASS",
            f"All {len(required_methods)} required methods present",
        )
        return True

    except Exception as e:
        record_test("test_phase2_quality_gates_methods", "FAIL", f"Exception: {str(e)}")
        return False
    finally:
        env.cleanup()


def test_phase2_thresholds_configuration():
    """Verify THRESHOLDS dict with lane-specific configs"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        implement.create_quality_gates_module()
        qg_file = scripts_dir / "quality_gates.py"
        content = qg_file.read_text()

        # Check for THRESHOLDS dict
        if "THRESHOLDS" not in content:
            record_test(
                "test_phase2_thresholds_configuration",
                "FAIL",
                "THRESHOLDS dict not defined",
            )
            return False

        # Check for lane-specific thresholds
        for lane in ["docs", "standard", "heavy"]:
            pattern = rf'"{lane}":\s*{{'
            if not re.search(pattern, content):
                record_test(
                    "test_phase2_thresholds_configuration",
                    "FAIL",
                    f"No thresholds configuration for '{lane}' lane",
                )
                return False

        record_test(
            "test_phase2_thresholds_configuration",
            "PASS",
            "THRESHOLDS configured for all lanes",
        )
        return True

    except Exception as e:
        record_test(
            "test_phase2_thresholds_configuration", "FAIL", f"Exception: {str(e)}"
        )
        return False
    finally:
        env.cleanup()


# ============================================================================
# PHASE 3 TESTS: Status JSON Template
# ============================================================================


def test_phase3_status_json_creation():
    """Execute Phase 3: Status JSON template creation"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        # Execute Phase 3
        result = implement.create_status_json_template()

        if not result:
            record_test(
                "test_phase3_status_json_creation",
                "FAIL",
                "create_status_json_template() returned False",
            )
            return False

        # Verify status.json was created
        status_file = scripts_dir / "status.json"
        if not status_file.exists():
            record_test(
                "test_phase3_status_json_creation",
                "FAIL",
                "status.json was not created",
            )
            return False

        # Verify it's valid JSON
        try:
            with open(status_file) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            record_test(
                "test_phase3_status_json_creation",
                "FAIL",
                f"status.json contains invalid JSON: {str(e)}",
            )
            return False

        record_test(
            "test_phase3_status_json_creation",
            "PASS",
            "status.json created with valid JSON",
        )
        return True

    except Exception as e:
        record_test("test_phase3_status_json_creation", "FAIL", f"Exception: {str(e)}")
        return False
    finally:
        env.cleanup()


def test_phase3_status_json_schema():
    """Verify status.json has required schema fields"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        implement.create_status_json_template()
        status_file = scripts_dir / "status.json"

        with open(status_file) as f:
            data = json.load(f)

        required_fields = [
            "workflow_id",
            "lane",
            "status",
            "current_stage",
            "completed_stages",
            "failed_stages",
            "skipped_stages",
            "quality_gates_results",
            "resumable",
            "created_at",
            "updated_at",
        ]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            record_test(
                "test_phase3_status_json_schema",
                "FAIL",
                f"Missing fields: {', '.join(missing_fields)}",
            )
            return False

        record_test(
            "test_phase3_status_json_schema",
            "PASS",
            f"All {len(required_fields)} required fields present",
        )
        return True

    except Exception as e:
        record_test("test_phase3_status_json_schema", "FAIL", f"Exception: {str(e)}")
        return False
    finally:
        env.cleanup()


def test_phase3_resumption_fields():
    """Verify status.json has resumption fields"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        implement.create_status_json_template()
        status_file = scripts_dir / "status.json"

        with open(status_file) as f:
            data = json.load(f)

        # Check for resumption fields
        if "resumable" not in data:
            record_test(
                "test_phase3_resumption_fields", "FAIL", "Missing 'resumable' field"
            )
            return False

        if "resume_from_stage" not in data:
            record_test(
                "test_phase3_resumption_fields",
                "FAIL",
                "Missing 'resume_from_stage' field",
            )
            return False

        record_test(
            "test_phase3_resumption_fields",
            "PASS",
            "Resumption fields (resumable, resume_from_stage) present",
        )
        return True

    except Exception as e:
        record_test("test_phase3_resumption_fields", "FAIL", f"Exception: {str(e)}")
        return False
    finally:
        env.cleanup()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_integration_main_execution():
    """Execute main() and verify all phases complete"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        # Execute main()
        result = implement.main()

        if not result:
            record_test(
                "test_integration_main_execution", "FAIL", "main() returned False"
            )
            return False

        # Verify all files created
        files_to_check = [
            ("workflow.py", "LANE_MAPPING"),
            ("quality_gates.py", "class QualityGates"),
            ("status.json", None),  # Just check existence
        ]

        for filename, content_check in files_to_check:
            filepath = scripts_dir / filename
            if not filepath.exists():
                record_test(
                    "test_integration_main_execution",
                    "FAIL",
                    f"{filename} was not created",
                )
                return False

            if content_check:
                file_content = filepath.read_text()
                if content_check not in file_content:
                    record_test(
                        "test_integration_main_execution",
                        "FAIL",
                        f"{filename} missing expected content: {content_check}",
                    )
                    return False

        record_test(
            "test_integration_main_execution",
            "PASS",
            "main() executed successfully - all files created",
        )
        return True

    except Exception as e:
        record_test("test_integration_main_execution", "FAIL", f"Exception: {str(e)}")
        return False
    finally:
        env.cleanup()


def test_integration_files_are_valid_python():
    """Verify generated Python files are syntactically valid"""
    env = TestEnvironment()
    scripts_dir = env.setup()

    try:
        import py_compile

        implement.main()

        python_files = [
            "workflow.py",
            "quality_gates.py",
        ]

        for filename in python_files:
            filepath = scripts_dir / filename
            if not filepath.exists():
                record_test(
                    "test_integration_files_are_valid_python",
                    "FAIL",
                    f"{filename} not found",
                )
                return False

            try:
                py_compile.compile(str(filepath), doraise=True)
            except py_compile.PyCompileError as e:
                record_test(
                    "test_integration_files_are_valid_python",
                    "FAIL",
                    f"{filename} has syntax error: {str(e)}",
                )
                return False

        record_test(
            "test_integration_files_are_valid_python",
            "PASS",
            "All generated Python files are syntactically valid",
        )
        return True

    except Exception as e:
        record_test(
            "test_integration_files_are_valid_python", "FAIL", f"Exception: {str(e)}"
        )
        return False
    finally:
        env.cleanup()


# ============================================================================
# TEST RUNNER
# ============================================================================


def main():
    """Run all execution tests"""
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print(f"IMPLEMENT.PY EXECUTION TEST HARNESS")
    print(f"{'=' * 70}{Colors.RESET}\n")

    # Collect all test functions
    test_functions = [
        # Phase 1: Lane Selection
        test_phase1_lane_selection_execution,
        test_phase1_lanes_have_stages,
        test_phase1_quality_gates_flag,
        # Phase 2: Quality Gates
        test_phase2_quality_gates_creation,
        test_phase2_quality_gates_methods,
        test_phase2_thresholds_configuration,
        # Phase 3: Status JSON
        test_phase3_status_json_creation,
        test_phase3_status_json_schema,
        test_phase3_resumption_fields,
        # Integration Tests
        test_integration_main_execution,
        test_integration_files_are_valid_python,
    ]

    # Execute all tests
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            record_test(test_func.__name__, "FAIL", f"Unhandled exception: {str(e)}")

    # Print summary
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 70}{Colors.RESET}")
    print(f"Total:   {test_results['total']}")
    print(f"{Colors.GREEN}Passed:  {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed:  {test_results['failed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}Skipped: {test_results['skipped']}{Colors.RESET}")

    # Calculate pass rate
    if test_results["total"] > 0:
        pass_rate = (test_results["passed"] / test_results["total"]) * 100
        print(f"Pass Rate: {pass_rate:.1f}%")

    test_results["end_time"] = datetime.now().isoformat()

    # Exit code
    return 0 if test_results["failed"] == 0 else 1


if __name__ == "__main__":
    exit(main())
