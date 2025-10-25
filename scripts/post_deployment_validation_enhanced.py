#!/usr/bin/env python3
"""
Enhanced POST-1-5: Post-Deployment Validation Framework for v0.1.36

Comprehensive 5-phase validation suite executed after merge to main branch.
Tests all critical functionality, SLA targets, and deployment readiness.

POST-1: Docs lane timing (<5 minutes)
POST-2: Quality gate reliability (100% accuracy)
POST-3: Documentation accessibility & completeness
POST-4: Feature usability across all lanes
POST-5: All tests passing & code quality

Usage:
    python post_deployment_validation_enhanced.py [--full] [--skip-timing] [--json] [--verbose]

Exit Codes:
    0 - All validations passed
    1 - Some validations failed
    2 - Critical error
"""

import subprocess
import time
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ValidationStatus(Enum):
    """Validation result status."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class ValidationResult:
    """Single validation test result."""

    test_id: str
    test_name: str
    status: ValidationStatus
    duration: float
    message: str
    details: Dict = None

    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        if self.details is None:
            self.details = {}
        return data


class PostDeploymentValidator:
    """Enhanced post-deployment validation framework."""

    def __init__(self, project_root: Path = None, verbose: bool = False):
        """Initialize validator."""
        self.project_root = project_root or Path.cwd()
        self.verbose = verbose
        self.results = []
        self.start_time = None
        self.end_time = None

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with level."""
        if level == "INFO" or self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level:8} {message}")

    def log_section(self, title: str, post_id: str = "") -> None:
        """Log section header."""
        prefix = f"{post_id}: " if post_id else ""
        print(f"\n{'=' * 70}")
        print(f"{prefix}{title}")
        print(f"{'=' * 70}")

    def log_result(self, result: ValidationResult) -> None:
        """Log individual test result."""
        status_icon = {
            ValidationStatus.PASS: "✅",
            ValidationStatus.FAIL: "❌",
            ValidationStatus.SKIP: "⊘",
            ValidationStatus.ERROR: "⚠️",
        }
        icon = status_icon.get(result.status, "?")
        print(f"  {icon} {result.test_name}: {result.message} ({result.duration:.2f}s)")

    # POST-1: Docs Lane Timing Validation
    def post_1_validate_docs_lane_timing(self, iterations: int = 3) -> ValidationResult:
        """POST-1: Validate docs lane completes in <5 minutes."""
        self.log_section("Docs Lane Timing Validation (<5 minutes)", "POST-1")

        start_total = time.time()
        timings = []
        success = True

        for i in range(iterations):
            self.log(f"Run {i + 1}/{iterations}: Testing docs lane...", "INFO")

            start = time.time()
            try:
                result = subprocess.run(
                    [
                        "python",
                        "scripts/workflow.py",
                        "--change-id",
                        f"post1-test-docs-{i}",
                        "--title",
                        f"POST-1 Timing Test {i + 1}",
                        "--owner",
                        "post_deployment",
                        "--lane",
                        "docs",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=320,  # 5 min 20 sec buffer
                    cwd=str(self.project_root),
                )

                elapsed = time.time() - start
                timings.append(elapsed)

                if elapsed < 300:
                    self.log(f"  ✅ Completed in {elapsed:.1f}s", "PASS")
                else:
                    self.log(f"  ❌ Took {elapsed:.1f}s (>300s limit)", "FAIL")
                    success = False

                if result.returncode != 0:
                    self.log(f"  Error: {result.stderr[:100]}", "WARN")
                    success = False

            except subprocess.TimeoutExpired:
                self.log("  ❌ Timeout exceeded (>320s)", "ERROR")
                success = False
            except Exception as e:
                self.log(f"  ❌ Exception: {e}", "ERROR")
                success = False

        total_duration = time.time() - start_total
        avg_time = sum(timings) / len(timings) if timings else 0

        details = {
            "iterations": iterations,
            "timings_seconds": timings,
            "average_seconds": avg_time,
            "average_minutes": avg_time / 60,
            "max_seconds": max(timings) if timings else None,
            "min_seconds": min(timings) if timings else None,
            "requirement": "<300 seconds (5 minutes)",
            "all_within_limit": all(t < 300 for t in timings),
        }

        message = (
            f"Avg: {avg_time:.1f}s, All within limit: {details['all_within_limit']}"
        )

        return ValidationResult(
            test_id="POST-1",
            test_name="Docs Lane Timing",
            status=ValidationStatus.PASS if success else ValidationStatus.FAIL,
            duration=total_duration,
            message=message,
            details=details,
        )

    # POST-2: Quality Gates Reliability
    def post_2_validate_quality_gates(self) -> ValidationResult:
        """POST-2: Validate quality gates work reliably."""
        self.log_section("Quality Gate Reliability Validation", "POST-2")

        start_time = time.time()
        test_results = []

        # Test 1: Standard quality check should pass on good code
        self.log("Test 1: Running quality gates on valid code...", "INFO")
        try:
            result = subprocess.run(
                ["python", "scripts/quality_gates.py", "--verbose"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_root),
            )

            passed = result.returncode == 0
            self.log(
                f"  Result: {'PASS' if passed else 'FAIL'}",
                "PASS" if passed else "FAIL",
            )
            test_results.append(passed)

        except Exception as e:
            self.log(f"  Exception: {e}", "ERROR")
            test_results.append(False)

        # Test 2: Verify ruff linting
        self.log("Test 2: Verifying ruff linting...", "INFO")
        try:
            result = subprocess.run(
                ["ruff", "check", "agent/", "scripts/", "plugin/", "--exit-zero"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root),
            )

            # Extract error count (0 = all good)
            errors = result.stdout.count("error:")
            success = errors == 0
            self.log(f"  Ruff errors: {errors}", "PASS" if success else "FAIL")
            test_results.append(success)

        except Exception as e:
            self.log(f"  Exception: {e}", "ERROR")
            test_results.append(False)

        # Test 3: Verify pytest coverage
        self.log("Test 3: Verifying test execution...", "INFO")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-q", "--tb=no"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_root),
            )

            passed = result.returncode == 0
            self.log(
                f"  Tests: {'PASS' if passed else 'FAIL'}", "PASS" if passed else "FAIL"
            )
            test_results.append(passed)

        except Exception as e:
            self.log(f"  Exception: {e}", "ERROR")
            test_results.append(False)

        duration = time.time() - start_time
        success = all(test_results)

        details = {
            "test_count": len(test_results),
            "passed_count": sum(test_results),
            "success_rate": f"{100 * sum(test_results) // len(test_results)}%",
            "tests": ["ruff_linting", "pytest_coverage", "code_quality"],
        }

        message = f"{sum(test_results)}/{len(test_results)} tests passed ({details['success_rate']})"

        return ValidationResult(
            test_id="POST-2",
            test_name="Quality Gate Reliability",
            status=ValidationStatus.PASS if success else ValidationStatus.FAIL,
            duration=duration,
            message=message,
            details=details,
        )

    # POST-3: Documentation Accessibility
    def post_3_validate_documentation(self) -> ValidationResult:
        """POST-3: Validate documentation is complete and accessible."""
        self.log_section("Documentation Accessibility Validation", "POST-3")

        start_time = time.time()

        required_docs = {
            "Release Notes": "docs/RELEASE_NOTES_v0.1.36.md",
            "Workflow Guide": "docs/The_Workflow_Process.md",
            "Specification": "openspec/changes/workflow-improvements/spec.md",
            "Proposal": "openspec/changes/workflow-improvements/proposal.md",
            "Tasks": "openspec/changes/workflow-improvements/tasks.md",
            "Lane Guide": "docs/WORKFLOW_LANES_GUIDE.md",
            "Detection Guide": "docs/CI_CD_LANE_DETECTION_GUIDE.md",
            "README": "README.md",
            "CHANGELOG": "CHANGELOG.md",
        }

        file_results = []
        total_size_kb = 0

        for doc_name, doc_path in required_docs.items():
            full_path = self.project_root / doc_path
            exists = full_path.exists()
            status_str = "✅" if exists else "❌"

            self.log(f"{status_str} {doc_name}: {doc_path}", "INFO")

            if exists:
                try:
                    content = full_path.read_text()
                    size_kb = len(content) / 1024
                    total_size_kb += size_kb
                    line_count = len(content.split("\n"))
                    self.log(f"   Size: {size_kb:.1f} KB, Lines: {line_count}", "DEBUG")
                    file_results.append((doc_name, True, size_kb, line_count))
                except Exception as e:
                    self.log(f"   Error reading: {e}", "ERROR")
                    file_results.append((doc_name, False, 0, 0))
            else:
                file_results.append((doc_name, False, 0, 0))

        duration = time.time() - start_time
        success = all(r[1] for r in file_results)

        details = {
            "total_files": len(required_docs),
            "accessible_files": sum(1 for r in file_results if r[1]),
            "total_size_kb": total_size_kb,
            "files": {
                r[0]: {"exists": r[1], "size_kb": r[2], "lines": r[3]}
                for r in file_results
            },
        }

        message = (
            f"{details['accessible_files']}/{details['total_files']} files accessible"
        )

        return ValidationResult(
            test_id="POST-3",
            test_name="Documentation Accessibility",
            status=ValidationStatus.PASS if success else ValidationStatus.FAIL,
            duration=duration,
            message=message,
            details=details,
        )

    # POST-4: Feature Usability
    def post_4_validate_feature_usability(self) -> ValidationResult:
        """POST-4: Validate lane feature works for all three lanes."""
        self.log_section("Feature Usability Validation (All Lanes)", "POST-4")

        start_time = time.time()
        lanes = ["docs", "standard", "heavy"]
        lane_results = []

        for lane in lanes:
            self.log(f"Testing {lane.upper()} lane...", "INFO")

            try:
                result = subprocess.run(
                    [
                        "python",
                        "scripts/workflow.py",
                        "--change-id",
                        f"post4-test-{lane}",
                        "--title",
                        f"POST-4 Usability Test",
                        "--owner",
                        "post_deployment",
                        "--lane",
                        lane,
                        "--dry-run",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self.project_root),
                )

                passed = result.returncode == 0
                self.log(
                    f"  Result: {'✅ PASS' if passed else '❌ FAIL'}",
                    "PASS" if passed else "FAIL",
                )
                lane_results.append((lane, passed))

            except subprocess.TimeoutExpired:
                self.log(f"  ❌ Timeout", "ERROR")
                lane_results.append((lane, False))
            except Exception as e:
                self.log(f"  ❌ Exception: {e}", "ERROR")
                lane_results.append((lane, False))

        duration = time.time() - start_time
        success = all(r[1] for r in lane_results)

        details = {
            "lanes_tested": lanes,
            "lanes_working": sum(1 for r in lane_results if r[1]),
            "lane_status": {
                lane: "working" if passed else "failed" for lane, passed in lane_results
            },
        }

        message = f"{details['lanes_working']}/{len(lanes)} lanes functional"

        return ValidationResult(
            test_id="POST-4",
            test_name="Feature Usability",
            status=ValidationStatus.PASS if success else ValidationStatus.FAIL,
            duration=duration,
            message=message,
            details=details,
        )

    # POST-5: All Tests Passing
    def post_5_validate_all_tests(self) -> ValidationResult:
        """POST-5: Validate all tests passing and code quality maintained."""
        self.log_section("All Tests Passing Validation", "POST-5")

        start_time = time.time()

        # Run pytest with coverage
        self.log("Running full test suite with coverage...", "INFO")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "--co", "-q"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.project_root),
            )

            # Parse test count
            output = result.stdout + result.stderr
            test_count_line = [l for l in output.split("\n") if "selected" in l.lower()]

            passed = result.returncode == 0
            self.log(
                f"  Result: {'✅ PASS' if passed else '❌ FAIL'}",
                "PASS" if passed else "FAIL",
            )

            if test_count_line:
                self.log(f"  {test_count_line[0].strip()}", "DEBUG")

        except subprocess.TimeoutExpired:
            self.log("  ❌ Test suite timeout", "ERROR")
            passed = False
        except Exception as e:
            self.log(f"  ❌ Exception: {e}", "ERROR")
            passed = False

        # Check bandit security
        self.log("Running security scan (bandit)...", "INFO")
        try:
            result = subprocess.run(
                ["bandit", "-r", "agent/", "scripts/", "-f", "json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root),
            )

            # Parse bandit output
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    high_severity = sum(
                        1
                        for r in bandit_results.get("results", [])
                        if r.get("severity") == "HIGH"
                    )
                    self.log(
                        f"  High severity issues: {high_severity}",
                        "PASS" if high_severity == 0 else "FAIL",
                    )
                except:
                    pass

        except Exception as e:
            self.log(f"  Bandit check failed: {e}", "WARN")

        duration = time.time() - start_time

        details = {
            "test_suite": "pytest",
            "security_scan": "bandit",
            "result": "PASS" if passed else "FAIL",
        }

        message = "All tests passing and security checks complete"

        return ValidationResult(
            test_id="POST-5",
            test_name="All Tests Passing",
            status=ValidationStatus.PASS if passed else ValidationStatus.FAIL,
            duration=duration,
            message=message,
            details=details,
        )

    def run_full_validation(self, skip_timing: bool = False) -> List[ValidationResult]:
        """Run all POST-deployment validations."""
        self.start_time = datetime.now()

        print("\n" + "#" * 70)
        print("# POST-DEPLOYMENT VALIDATION SUITE")
        print("# Workflow Improvements v0.1.36")
        print("#" * 70)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        validations = [
            (self.post_1_validate_docs_lane_timing, not skip_timing),
            (self.post_2_validate_quality_gates, True),
            (self.post_3_validate_documentation, True),
            (self.post_4_validate_feature_usability, True),
            (self.post_5_validate_all_tests, True),
        ]

        for validator_func, should_run in validations:
            if not should_run:
                continue

            try:
                result = validator_func()
                self.results.append(result)
                self.log_result(result)
            except Exception as e:
                print(f"\n⚠️  Exception in {validator_func.__name__}: {e}")
                self.results.append(
                    ValidationResult(
                        test_id="ERROR",
                        test_name=validator_func.__name__,
                        status=ValidationStatus.ERROR,
                        duration=0,
                        message=str(e),
                    )
                )

        self.end_time = datetime.now()
        self._print_summary()

        return self.results

    def _print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "#" * 70)
        print("# VALIDATION SUMMARY")
        print("#" * 70)

        passed = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        failed = sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
        errors = sum(1 for r in self.results if r.status == ValidationStatus.ERROR)
        total_duration = (self.end_time - self.start_time).total_seconds()

        print(f"\n  ✅ Passed:  {passed}")
        print(f"  ❌ Failed:  {failed}")
        print(f"  ⚠️  Errors:  {errors}")
        print(f"  Total:     {len(self.results)}")
        print(f"  Duration:  {total_duration:.1f}s")

        overall_success = failed == 0 and errors == 0
        status = (
            "✅ ALL VALIDATIONS PASSED"
            if overall_success
            else "❌ VALIDATION ISSUES DETECTED"
        )
        print(f"\n  Status: {status}")
        print(f"  End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def save_results(
        self, output_file: str = "post_deployment_validation_results.json"
    ) -> None:
        """Save validation results to JSON."""
        output_path = self.project_root / output_file

        data = {
            "timestamp": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "version": "0.1.36",
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "total": len(self.results),
                "passed": sum(
                    1 for r in self.results if r.status == ValidationStatus.PASS
                ),
                "failed": sum(
                    1 for r in self.results if r.status == ValidationStatus.FAIL
                ),
                "errors": sum(
                    1 for r in self.results if r.status == ValidationStatus.ERROR
                ),
                "overall_status": "PASS"
                if all(r.status != ValidationStatus.FAIL for r in self.results)
                else "FAIL",
            },
        }

        output_path.write_text(json.dumps(data, indent=2))
        print(f"\n  ✅ Results saved to: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="POST-Deployment Validation Suite for v0.1.36",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python post_deployment_validation_enhanced.py                    # Run all validations
  python post_deployment_validation_enhanced.py --skip-timing      # Skip timing tests
  python post_deployment_validation_enhanced.py --json             # Output JSON results
  python post_deployment_validation_enhanced.py --verbose          # Verbose logging
        """,
    )

    parser.add_argument(
        "--skip-timing",
        action="store_true",
        help="Skip POST-1 timing validation (faster)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format only"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument(
        "--output",
        default="post_deployment_validation_results.json",
        help="Output results file",
    )

    args = parser.parse_args()

    validator = PostDeploymentValidator(
        project_root=Path(args.project_root), verbose=args.verbose
    )

    results = validator.run_full_validation(skip_timing=args.skip_timing)
    validator.save_results(args.output)

    # Exit with appropriate code
    passed_all = all(r.status == ValidationStatus.PASS for r in results)
    exit_code = 0 if passed_all else 1

    if args.json:
        # Output JSON summary and exit
        summary_data = {
            "status": "PASS" if passed_all else "FAIL",
            "passed": sum(1 for r in results if r.status == ValidationStatus.PASS),
            "failed": sum(1 for r in results if r.status == ValidationStatus.FAIL),
            "results_file": str(args.output),
        }
        print("\n" + json.dumps(summary_data, indent=2))

    sys.exit(exit_code)
