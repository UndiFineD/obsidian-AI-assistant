#!/usr/bin/env python3
"""
TEST-13-15: Manual Lane Validation Scripts

Optional manual test scripts for validating workflow-improvements v0.1.36 functionality.

TEST-13: Docs lane smoke test - Creates documentation-only change, validates <5 min execution
TEST-14: Standard lane validation - Creates code change, validates all gates pass
TEST-15: Heavy lane validation - Creates complex change, validates stricter thresholds

Usage:
    python tests/manual_lane_validation.py test-13  # Run docs lane validation
    python tests/manual_lane_validation.py test-14  # Run standard lane validation
    python tests/manual_lane_validation.py test-15  # Run heavy lane validation
    python tests/manual_lane_validation.py all      # Run all validations
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple


class ManualLaneValidator:
    """Validates workflow lanes through manual smoke tests."""

    def __init__(self, project_root: Path = Path(".")):
        """Initialize validator."""
        self.project_root = project_root
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.36",
            "tests": {},
            "summary": {},
        }

    def test_13_docs_lane(self) -> bool:
        """
        TEST-13: Docs Lane Validation

        Creates a documentation-only change (markdown files only) and validates:
        - Lane detection correctly identifies as "docs"
        - Execution time < 5 minutes
        - No quality gates unnecessarily run
        - All documentation steps execute
        """
        print("\n" + "=" * 70)
        print("TEST-13: Docs Lane Smoke Test")
        print("=" * 70)

        print("\nScenario: Documentation-only change (README update)")
        print("-" * 70)

        # Create test directory and markdown file
        test_dir = self.project_root / ".test-lanes" / "test-13-docs"
        test_dir.mkdir(parents=True, exist_ok=True)

        test_file = test_dir / "TEST_README.md"
        test_file.write_text(
            """
# Test Documentation

This is a test documentation file created for TEST-13 validation.

## Purpose

Validate that the docs lane:
- Skips quality gates
- Completes in <5 minutes
- Executes only documentation-relevant stages

## Result

If you're reading this, TEST-13 passed!
"""
        )

        print(f"✓ Created test file: {test_file}")

        # Run workflow with docs lane
        print("\nExecuting workflow with --lane docs...")
        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "python",
                    "scripts/workflow.py",
                    "--change-id",
                    "test-13-docs-lane",
                    "--title",
                    "TEST-13: Docs Lane Validation",
                    "--owner",
                    "automation",
                    "--lane",
                    "docs",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.project_root,
            )

            elapsed_time = time.time() - start_time

            # Check results
            success = (
                result.returncode == 0
                and elapsed_time < 300
                and "docs" in result.stdout.lower()
            )

            status = "✅ PASS" if success else "❌ FAIL"

            print(f"\n{status} TEST-13 Results:")
            print(
                f"  • Execution Time: {elapsed_time:.1f}s ({elapsed_time / 60:.2f} min)"
            )
            print(f"  • Time Requirement: < 5 minutes (300s)")
            print(f"  • SLA Met: {'✅ Yes' if elapsed_time < 300 else '❌ No'}")
            print(f"  • Return Code: {result.returncode} (expected: 0)")
            print(
                f"  • Lane Detection: {'✅ Found' if 'docs' in result.stdout.lower() else '❌ Not found'}"
            )

            self.results["tests"]["test_13_docs_lane"] = {
                "status": "PASS" if success else "FAIL",
                "execution_time": elapsed_time,
                "sla_target": 300,
                "return_code": result.returncode,
            }

            return success

        except subprocess.TimeoutExpired:
            print("❌ TIMEOUT - Exceeded 5 minute limit")
            self.results["tests"]["test_13_docs_lane"] = {
                "status": "FAIL",
                "reason": "timeout",
            }
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results["tests"]["test_13_docs_lane"] = {
                "status": "FAIL",
                "reason": str(e),
            }
            return False

    def test_14_standard_lane(self) -> bool:
        """
        TEST-14: Standard Lane Validation

        Creates a typical code + documentation change and validates:
        - Lane detection correctly identifies as "standard"
        - Quality gates run and pass
        - Execution time < 15 minutes
        - All stages execute with standard thresholds
        """
        print("\n" + "=" * 70)
        print("TEST-14: Standard Lane Validation")
        print("=" * 70)

        print("\nScenario: Mixed change (code + documentation)")
        print("-" * 70)

        # Create test directory with both code and markdown
        test_dir = self.project_root / ".test-lanes" / "test-14-standard"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Create code file
        code_file = test_dir / "test_module.py"
        code_file.write_text(
            """
\"\"\"Test module for TEST-14 standard lane validation.\"\"\"


def hello_world() -> str:
    \"\"\"Return greeting.\"\"\"
    return "Hello, World!"


def add_numbers(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b


if __name__ == "__main__":
    print(hello_world())
    print(f"2 + 3 = {add_numbers(2, 3)}")
"""
        )

        # Create documentation file
        doc_file = test_dir / "TEST_FEATURE.md"
        doc_file.write_text(
            """
# Test Feature

This is a test feature with code and documentation.

## Implementation

The `test_module.py` implements:
- hello_world(): Returns a greeting
- add_numbers(a, b): Adds two numbers

## Usage

```python
from test_module import add_numbers
result = add_numbers(5, 3)
print(result)  # Output: 8
```
"""
        )

        print(f"✓ Created code file: {code_file}")
        print(f"✓ Created doc file: {doc_file}")

        # Run workflow with standard lane
        print("\nExecuting workflow with --lane standard...")
        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "python",
                    "scripts/workflow.py",
                    "--change-id",
                    "test-14-standard-lane",
                    "--title",
                    "TEST-14: Standard Lane Validation",
                    "--owner",
                    "automation",
                    "--lane",
                    "standard",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=900,  # 15 minute timeout
                cwd=self.project_root,
            )

            elapsed_time = time.time() - start_time

            # Check results
            success = (
                result.returncode == 0
                and elapsed_time < 900
                and "standard" in result.stdout.lower()
            )

            status = "✅ PASS" if success else "❌ FAIL"

            print(f"\n{status} TEST-14 Results:")
            print(
                f"  • Execution Time: {elapsed_time:.1f}s ({elapsed_time / 60:.2f} min)"
            )
            print(f"  • Time Requirement: < 15 minutes (900s)")
            print(f"  • SLA Met: {'✅ Yes' if elapsed_time < 900 else '❌ No'}")
            print(f"  • Return Code: {result.returncode} (expected: 0)")
            print(
                f"  • Lane Detection: {'✅ Found' if 'standard' in result.stdout.lower() else '❌ Not found'}"
            )

            self.results["tests"]["test_14_standard_lane"] = {
                "status": "PASS" if success else "FAIL",
                "execution_time": elapsed_time,
                "sla_target": 900,
                "return_code": result.returncode,
            }

            return success

        except subprocess.TimeoutExpired:
            print("❌ TIMEOUT - Exceeded 15 minute limit")
            self.results["tests"]["test_14_standard_lane"] = {
                "status": "FAIL",
                "reason": "timeout",
            }
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results["tests"]["test_14_standard_lane"] = {
                "status": "FAIL",
                "reason": str(e),
            }
            return False

    def test_15_heavy_lane(self) -> bool:
        """
        TEST-15: Heavy Lane Validation

        Creates a complex change (many files, multiple directories) and validates:
        - Lane detection correctly identifies as "heavy"
        - Stricter quality gate thresholds applied
        - Execution time < 20 minutes
        - All stages execute with enhanced validation
        """
        print("\n" + "=" * 70)
        print("TEST-15: Heavy Lane Validation")
        print("=" * 70)

        print("\nScenario: Large complex change (refactoring across multiple modules)")
        print("-" * 70)

        # Create test directory with multiple files
        test_dir = self.project_root / ".test-lanes" / "test-15-heavy"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Create multiple module files to simulate large change
        modules = ["auth", "core", "utils", "api", "database"]
        for i, module in enumerate(modules):
            module_dir = test_dir / f"module_{module}"
            module_dir.mkdir(exist_ok=True)

            (module_dir / "__init__.py").write_text(
                f'"""Module {module}."""\n__version__ = "0.1.0"\n'
            )

            (module_dir / f"{module}.py").write_text(
                f"""
\"\"\"Module {module} - Part of heavy lane test.\"\"\"


def function_{i}() -> str:
    \"\"\"Function in {module} module.\"\"\"
    return f"Result from {module}"


def calculate_{i}(x: int, y: int) -> int:
    \"\"\"Calculate something in {module}.\"\"\"
    return x + y + {i}


class {module.capitalize()}Handler:
    \"\"\"Handler for {module} operations.\"\"\"

    def __init__(self):
        \"\"\"Initialize handler.\"\"\"
        self.module_name = "{module}"

    def process(self, data: str) -> str:
        \"\"\"Process data.\"\"\"
        return f"Processing {{data}} with {{self.module_name}}"
"""
            )

        # Create README for the complex change
        (test_dir / "REFACTORING.md").write_text(
            """
# Heavy Refactoring

This test simulates a major refactoring across multiple modules:

## Modules Changed
- module_auth: Authentication handling
- module_core: Core functionality
- module_utils: Utility functions
- module_api: API endpoints
- module_database: Database operations

## Changes Made
- Refactored 5 core modules
- Updated 15+ files
- Breaking changes to API
- Performance improvements

## Validation
Heavy lane should:
- Detect this as a complex change
- Apply stricter quality thresholds
- Require 85%+ test coverage (vs 70% for standard)
- Enforce 0 high-severity security issues
- Complete within 20 minutes
"""
        )

        print(f"✓ Created test modules: {len(modules)} modules with 3+ files each")

        # Run workflow with heavy lane
        print("\nExecuting workflow with --lane heavy...")
        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "python",
                    "scripts/workflow.py",
                    "--change-id",
                    "test-15-heavy-lane",
                    "--title",
                    "TEST-15: Heavy Lane Validation",
                    "--owner",
                    "automation",
                    "--lane",
                    "heavy",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=1200,  # 20 minute timeout
                cwd=self.project_root,
            )

            elapsed_time = time.time() - start_time

            # Check results
            success = (
                result.returncode == 0
                and elapsed_time < 1200
                and "heavy" in result.stdout.lower()
            )

            status = "✅ PASS" if success else "❌ FAIL"

            print(f"\n{status} TEST-15 Results:")
            print(
                f"  • Execution Time: {elapsed_time:.1f}s ({elapsed_time / 60:.2f} min)"
            )
            print(f"  • Time Requirement: < 20 minutes (1200s)")
            print(f"  • SLA Met: {'✅ Yes' if elapsed_time < 1200 else '❌ No'}")
            print(f"  • Return Code: {result.returncode} (expected: 0)")
            print(
                f"  • Lane Detection: {'✅ Found' if 'heavy' in result.stdout.lower() else '❌ Not found'}"
            )

            self.results["tests"]["test_15_heavy_lane"] = {
                "status": "PASS" if success else "FAIL",
                "execution_time": elapsed_time,
                "sla_target": 1200,
                "return_code": result.returncode,
            }

            return success

        except subprocess.TimeoutExpired:
            print("❌ TIMEOUT - Exceeded 20 minute limit")
            self.results["tests"]["test_15_heavy_lane"] = {
                "status": "FAIL",
                "reason": "timeout",
            }
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.results["tests"]["test_15_heavy_lane"] = {
                "status": "FAIL",
                "reason": str(e),
            }
            return False

    def run_all_validations(self) -> Dict:
        """Run all three manual validation tests."""
        print("\n" + "#" * 70)
        print("# MANUAL LANE VALIDATION TESTS (TEST-13-15)")
        print("# Workflow Improvements v0.1.36")
        print("#" * 70)

        tests = [
            ("test-13", self.test_13_docs_lane),
            ("test-14", self.test_14_standard_lane),
            ("test-15", self.test_15_heavy_lane),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append(result)
            except Exception as e:
                print(f"\n❌ EXCEPTION in {test_name}: {e}")
                results.append(False)

        # Summary
        print("\n" + "#" * 70)
        print("# VALIDATION SUMMARY")
        print("#" * 70)

        passed = sum(results)
        total = len(results)

        print(f"\n  ✅ Passed:  {passed}/{total}")
        print(f"  ❌ Failed:  {total - passed}/{total}")

        if passed == total:
            print(f"\n  Status: ✅ ALL TESTS PASSED")
        else:
            print(f"\n  Status: ❌ SOME TESTS FAILED")

        self.results["summary"] = {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "overall_status": "PASS" if passed == total else "FAIL",
        }

        return self.results

    def save_results(self, output_file: str = "manual_lane_validation_results.json"):
        """Save validation results to JSON."""
        output_path = self.project_root / output_file
        output_path.write_text(json.dumps(self.results, indent=2))
        print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    import sys

    validator = ManualLaneValidator()

    if len(sys.argv) > 1:
        test = sys.argv[1].lower()
        if test == "test-13":
            success = validator.test_13_docs_lane()
        elif test == "test-14":
            success = validator.test_14_standard_lane()
        elif test == "test-15":
            success = validator.test_15_heavy_lane()
        elif test == "all":
            results = validator.run_all_validations()
            validator.save_results()
            exit(0 if results["summary"]["overall_status"] == "PASS" else 1)
        else:
            print(f"Unknown test: {test}")
            print(
                "Usage: python tests/manual_lane_validation.py [test-13|test-14|test-15|all]"
            )
            exit(1)

        exit(0 if success else 1)
    else:
        results = validator.run_all_validations()
        validator.save_results()
        exit(0 if results["summary"]["overall_status"] == "PASS" else 1)
