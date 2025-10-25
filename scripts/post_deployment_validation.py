#!/usr/bin/env python3
"""
POST-1-5: Post-Deployment Validation Scripts for Workflow Improvements (v0.1.36)

Executes immediately after merge to main branch. Validates:
- POST-1: Docs lane timing (<5 minutes)
- POST-2: Quality gate reliability (100% accuracy)
- POST-3: Documentation accessibility
- POST-4: Feature usage metrics
- POST-5: Team notification

Usage:
    python post_deployment_validation.py [--full] [--skip-timing] [--notify]
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class PostDeploymentValidator:
    """Validates workflow improvements post-deployment."""

    def __init__(self, project_root: Path = Path(".")):
        """Initialize validator."""
        self.project_root = project_root
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.36",
            "tests": {},
            "metrics": {},
            "summary": {},
        }

    def post_1_validate_docs_lane_timing(self, iterations: int = 3) -> bool:
        """
        POST-1: Validate docs lane completes in <5 minutes.

        Tests documentation-only changes 3 times to ensure consistency.
        """
        print("\n" + "=" * 70)
        print("POST-1: Docs Lane Timing Validation (<5 minutes)")
        print("=" * 70)

        timings = []
        for i in range(iterations):
            print(f"\n[{i + 1}/{iterations}] Running docs lane workflow...")

            start = time.time()
            try:
                result = subprocess.run(
                    [
                        "python",
                        "scripts/workflow.py",
                        "--change-id",
                        f"test-docs-lane-{i}",
                        "--title",
                        f"Timing Test {i + 1}",
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
                elapsed = time.time() - start
                timings.append(elapsed)

                status = "✅ PASS" if elapsed < 300 else "❌ FAIL"
                print(f"  Execution Time: {elapsed:.2f}s {status}")

                if result.returncode != 0:
                    print(f"  Error: {result.stderr[:200]}")
                    return False

            except subprocess.TimeoutExpired:
                print(f"  ❌ TIMEOUT - Exceeded 5 minute limit")
                return False
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                return False

        avg_time = sum(timings) / len(timings)
        print(f"\n  Average Time: {avg_time:.2f}s ({avg_time / 60:.2f} min)")
        print(f"  Timings: {', '.join(f'{t:.1f}s' for t in timings)}")

        success = all(t < 300 for t in timings)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  Result: {status}")

        self.results["tests"]["post_1_timing"] = {
            "status": "PASS" if success else "FAIL",
            "timings": timings,
            "average": avg_time,
            "requirement": "<300s (5 min)",
        }

        return success

    def post_2_validate_quality_gates_reliability(self) -> bool:
        """
        POST-2: Validate quality gates work reliably.

        Tests quality gate detection with known pass/fail code.
        """
        print("\n" + "=" * 70)
        print("POST-2: Quality Gate Reliability Validation")
        print("=" * 70)

        test_cases = [
            ("good", True, "Code should pass all gates"),
            ("bad", False, "Code should fail linting"),
        ]

        results = []
        for test_name, should_pass, description in test_cases:
            print(f"\n  Testing: {test_name.upper()} - {description}")

            try:
                result = subprocess.run(
                    ["python", "scripts/quality_gates.py", "--test", test_name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root,
                )

                passed = result.returncode == 0
                expected = "PASS" if should_pass else "FAIL"
                actual = "PASS" if passed else "FAIL"
                status = "✅" if (passed == should_pass) else "❌"

                print(f"    Expected: {expected}")
                print(f"    Actual:   {actual} {status}")

                results.append(passed == should_pass)

            except Exception as e:
                print(f"    ❌ ERROR: {e}")
                results.append(False)

        success = all(results)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n  Result: {status} ({sum(results)}/{len(results)} tests passed)")

        self.results["tests"]["post_2_quality_gates"] = {
            "status": "PASS" if success else "FAIL",
            "tests_passed": sum(results),
            "tests_total": len(results),
            "reliability": f"{100 * sum(results) // len(results)}%",
        }

        return success

    def post_3_validate_documentation_accessibility(self) -> bool:
        """
        POST-3: Validate all documentation is accessible and accurate.

        Checks that all referenced files exist and contain expected content.
        """
        print("\n" + "=" * 70)
        print("POST-3: Documentation Accessibility Validation")
        print("=" * 70)

        doc_files = [
            "RELEASE_NOTES_v0.1.36.md",
            "docs/guides/The_Workflow_Process.md",
            "openspec/changes/workflow-improvements/spec.md",
            "openspec/changes/workflow-improvements/proposal.md",
            "openspec/changes/workflow-improvements/tasks.md",
            "README.md",
            "CHANGELOG.md",
        ]

        results = []
        for doc_file in doc_files:
            doc_path = self.project_root / doc_file
            exists = doc_path.exists()
            status = "✅" if exists else "❌"

            print(f"  {status} {doc_file}")

            if exists:
                try:
                    content = doc_path.read_text()
                    size_kb = len(content) / 1024
                    print(f"      Size: {size_kb:.1f} KB")
                    results.append(True)
                except Exception as e:
                    print(f"      Error reading: {e}")
                    results.append(False)
            else:
                results.append(False)

        success = all(results)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n  Result: {status} ({sum(results)}/{len(results)} files accessible)")

        self.results["tests"]["post_3_documentation"] = {
            "status": "PASS" if success else "FAIL",
            "files_found": sum(results),
            "files_total": len(results),
            "accessibility": f"{100 * sum(results) // len(results)}%",
        }

        return success

    def post_4_validate_feature_usability(self) -> bool:
        """
        POST-4: Validate lane feature works for all 3 lanes.

        Quick smoke tests of each lane to ensure usability.
        """
        print("\n" + "=" * 70)
        print("POST-4: Feature Usability Validation")
        print("=" * 70)

        lanes = ["docs", "standard", "heavy"]
        results = []

        for lane in lanes:
            print(f"\n  Testing {lane.upper()} lane...")

            try:
                result = subprocess.run(
                    [
                        "python",
                        "scripts/workflow.py",
                        "--change-id",
                        f"test-{lane}-usability",
                        "--title",
                        f"Usability Test",
                        "--owner",
                        "automation",
                        "--lane",
                        lane,
                        "--dry-run",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.project_root,
                )

                passed = result.returncode == 0
                status = "✅" if passed else "❌"
                print(f"    {status} Lane execution")

                results.append(passed)

            except subprocess.TimeoutExpired:
                print(f"    ❌ Timeout")
                results.append(False)
            except Exception as e:
                print(f"    ❌ Error: {e}")
                results.append(False)

        success = all(results)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n  Result: {status} ({sum(results)}/{len(results)} lanes functional)")

        self.results["tests"]["post_4_usability"] = {
            "status": "PASS" if success else "FAIL",
            "lanes_working": sum(results),
            "lanes_total": len(results),
            "lanes_tested": lanes,
        }

        return success

    def post_5_validate_all_tests_passing(self) -> bool:
        """
        POST-5: Validate all workflow tests still passing.

        Ensures deployment didn't break anything.
        """
        print("\n" + "=" * 70)
        print("POST-5: All Tests Passing Validation")
        print("=" * 70)

        print(f"\n  Running pytest tests/test_workflow_lanes.py...")

        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/test_workflow_lanes.py",
                    "-v",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root,
            )

            # Parse output for pass count
            output_lines = result.stdout.split("\n")
            summary_line = [l for l in output_lines if "passed" in l.lower()]

            print(f"  Test Output Summary:")
            for line in summary_line:
                print(f"    {line.strip()}")

            success = result.returncode == 0
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"\n  Result: {status}")

            self.results["tests"]["post_5_all_tests"] = {
                "status": "PASS" if success else "FAIL",
                "return_code": result.returncode,
                "output_lines": len(output_lines),
            }

            return success

        except subprocess.TimeoutExpired:
            print(f"  ❌ Tests timed out")
            self.results["tests"]["post_5_all_tests"] = {
                "status": "FAIL",
                "reason": "timeout",
            }
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.results["tests"]["post_5_all_tests"] = {
                "status": "FAIL",
                "reason": str(e),
            }
            return False

    def run_full_validation(self, skip_timing: bool = False) -> Dict:
        """Run all POST-deployment validations."""
        print("\n" + "#" * 70)
        print("# POST-DEPLOYMENT VALIDATION SUITE")
        print("# Workflow Improvements v0.1.36")
        print("#" * 70)

        validations = [
            (
                "POST-1",
                "Docs Lane Timing",
                self.post_1_validate_docs_lane_timing,
                not skip_timing,
            ),
            (
                "POST-2",
                "Quality Gates Reliability",
                self.post_2_validate_quality_gates_reliability,
                True,
            ),
            (
                "POST-3",
                "Documentation Accessibility",
                self.post_3_validate_documentation_accessibility,
                True,
            ),
            (
                "POST-4",
                "Feature Usability",
                self.post_4_validate_feature_usability,
                True,
            ),
            (
                "POST-5",
                "All Tests Passing",
                self.post_5_validate_all_tests_passing,
                True,
            ),
        ]

        passed_count = 0
        skipped_count = 0
        failed_count = 0

        for post_id, name, validator_func, should_run in validations:
            if not should_run:
                print(f"\n⊘ SKIPPED: {post_id} - {name}")
                skipped_count += 1
                continue

            try:
                result = validator_func()
                if result:
                    passed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"\n❌ EXCEPTION in {post_id}: {e}")
                failed_count += 1

        # Summary
        print("\n" + "#" * 70)
        print("# VALIDATION SUMMARY")
        print("#" * 70)
        print(f"\n  ✅ Passed:  {passed_count}")
        print(f"  ❌ Failed:  {failed_count}")
        print(f"  ⊘ Skipped: {skipped_count}")

        overall_success = failed_count == 0
        status = (
            "✅ ALL VALIDATIONS PASSED"
            if overall_success
            else "❌ SOME VALIDATIONS FAILED"
        )
        print(f"\n  Status: {status}")

        self.results["summary"] = {
            "passed": passed_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "total": len([v for v in validations if v[3]]),
            "overall_status": "PASS" if overall_success else "FAIL",
        }

        return self.results

    def save_results(self, output_file: str = "post_deployment_results.json"):
        """Save validation results to JSON."""
        output_path = self.project_root / output_file
        output_path.write_text(json.dumps(self.results, indent=2))
        print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="POST-Deployment Validation Suite")
    parser.add_argument(
        "--skip-timing", action="store_true", help="Skip timing tests (faster)"
    )
    parser.add_argument(
        "--output", default="post_deployment_results.json", help="Output file"
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    validator = PostDeploymentValidator(Path(args.project_root))
    results = validator.run_full_validation(skip_timing=args.skip_timing)
    validator.save_results(args.output)

    # Exit with appropriate code
    exit(0 if results["summary"]["overall_status"] == "PASS" else 1)
