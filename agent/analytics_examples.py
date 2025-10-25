#!/usr/bin/env python3
"""
Analytics Integration Examples

Demonstrates how to integrate the analytics framework into workflow execution,
quality gates, and reporting systems.
"""

import time
from pathlib import Path

from agent.analytics import MetricsAnalyzer, MetricsCollector, MetricsReporter

# ============================================================================
# EXAMPLE 1: Integration with Workflow Execution
# ============================================================================


class WorkflowExecutor:
    """Workflow executor with metrics collection."""

    def __init__(self):
        self.collector = MetricsCollector()

    def execute_workflow(self, lane: str, changes: dict) -> bool:
        """Execute workflow and record metrics."""
        start_time = time.time()
        success = False
        error_msg = None

        try:
            print(f"Starting {lane} lane workflow...")

            # Phase 1: Run quality gates
            qg_results = self._run_quality_gates()
            qg_passed = qg_results["passed"]
            qg_failed = qg_results["failed"]
            qg_total = qg_passed + qg_failed

            # Phase 2: Run tests
            test_results = self._run_tests()
            tests_passed = test_results["passed"]
            tests_failed = test_results["failed"]
            total_tests = tests_passed + tests_failed

            # Phase 3: Check documentation
            doc_results = self._check_documentation()
            docs_checked = doc_results["checked"]
            docs_valid = doc_results["valid"]

            # All phases successful
            success = qg_failed == 0 and tests_failed == 0

        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")

        finally:
            # Record metrics
            duration = time.time() - start_time
            sla_targets = {"docs": 300, "standard": 900, "heavy": 1200}
            sla_met = duration < sla_targets.get(lane, 900) and success

            self.collector.record_workflow_execution(
                lane=lane,
                duration_seconds=duration,
                success=success,
                quality_gates_passed=qg_passed,
                quality_gates_failed=qg_failed,
                total_quality_gates=qg_total,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                total_tests=total_tests,
                documentation_files_checked=docs_checked,
                documentation_files_valid=docs_valid,
                sla_met=sla_met,
                error_message=error_msg,
                metadata={
                    "change_files": len(changes.get("files", [])),
                    "change_scope": changes.get("scope", "unknown"),
                },
            )

            print(
                f"Workflow completed in {duration:.1f}s (SLA: {'✅' if sla_met else '❌'})"
            )

        return success

    def _run_quality_gates(self):
        """Run quality gates and return results."""
        # Simulate quality gate execution
        time.sleep(0.1)
        return {"passed": 12, "failed": 0}

    def _run_tests(self):
        """Run tests and return results."""
        # Simulate test execution
        time.sleep(0.1)
        return {"passed": 1043, "failed": 0}

    def _check_documentation(self):
        """Check documentation and return results."""
        # Simulate documentation check
        time.sleep(0.1)
        return {"checked": 9, "valid": 9}


# ============================================================================
# EXAMPLE 2: Analytics Dashboard Generation
# ============================================================================


class AnalyticsDashboard:
    """Generate analytics dashboard."""

    def __init__(self):
        self.analyzer = MetricsAnalyzer()
        self.reporter = MetricsReporter(self.analyzer)

    def generate_daily_report(self) -> str:
        """Generate daily metrics report."""
        return self.reporter.generate_summary_report(days=1)

    def generate_weekly_report(self) -> str:
        """Generate weekly metrics report."""
        return self.reporter.generate_summary_report(days=7)

    def generate_monthly_report(self) -> str:
        """Generate monthly metrics report."""
        return self.reporter.generate_summary_report(days=30)

    def get_sla_compliance_status(self) -> dict:
        """Get SLA compliance status across all lanes."""
        summaries = self.analyzer.get_all_lanes_summary(days=7)

        status = {"overall_compliance": 0, "lanes": {}, "alerts": []}

        total_compliance = 0
        for lane, summary in summaries.items():
            compliance = summary.sla_compliance_rate
            total_compliance += compliance

            status["lanes"][lane] = {
                "compliance": compliance,
                "status": (
                    "good"
                    if compliance >= 95
                    else "warning" if compliance >= 90 else "critical"
                ),
            }

            # Generate alerts
            if compliance < 90:
                status["alerts"].append(
                    {
                        "lane": lane,
                        "severity": "critical",
                        "message": f"{lane} lane SLA compliance at {compliance:.1f}%",
                    }
                )
            elif compliance < 95:
                status["alerts"].append(
                    {
                        "lane": lane,
                        "severity": "warning",
                        "message": f"{lane} lane SLA compliance dropped to {compliance:.1f}%",
                    }
                )

        status["overall_compliance"] = total_compliance / len(summaries)

        return status

    def get_performance_trends(self) -> dict:
        """Get performance trends."""
        summaries = self.analyzer.get_all_lanes_summary(days=7)

        trends = {}
        for lane, summary in summaries.items():
            trends[lane] = {
                "trend": summary.trend,
                "avg_duration": summary.avg_duration,
                "success_rate": summary.success_rate,
                "executions": summary.execution_count,
            }

        return trends


# ============================================================================
# EXAMPLE 3: Anomaly Detection and Alerting
# ============================================================================


class AnomalyDetectionSystem:
    """Detect and alert on anomalies."""

    def __init__(self):
        self.analyzer = MetricsAnalyzer()
        self.reporter = MetricsReporter(self.analyzer)

    def check_for_anomalies(self) -> dict:
        """Check all lanes for anomalies."""
        results = {"timestamp": time.time(), "anomalies_found": False, "lanes": {}}

        for lane in ["docs", "standard", "heavy"]:
            anomalies = self.analyzer.detect_anomalies(lane, days=7)

            if anomalies:
                results["anomalies_found"] = True
                results["lanes"][lane] = {
                    "count": len(anomalies),
                    "anomalies": anomalies,
                }

                # Generate alerts
                self._generate_alerts(lane, anomalies)

        return results

    def _generate_alerts(self, lane: str, anomalies: list) -> None:
        """Generate alerts for anomalies."""
        for anom in anomalies:
            if anom["severity"] == "high":
                print(f"🚨 ALERT: {lane} lane - {anom['type']}")
                print(f"   Details: {anom}")


# ============================================================================
# EXAMPLE 4: Performance Optimization Analysis
# ============================================================================


class PerformanceOptimizer:
    """Analyze performance for optimization opportunities."""

    def __init__(self):
        self.analyzer = MetricsAnalyzer()

    def identify_slow_lanes(self) -> list:
        """Identify lanes that are slower than expected."""
        slow_lanes = []

        summaries = self.analyzer.get_all_lanes_summary(days=7)

        targets = {"docs": 300, "standard": 900, "heavy": 1200}

        for lane, summary in summaries.items():
            target = targets[lane]
            if summary.avg_duration > target * 1.1:  # 10% over target
                slow_lanes.append(
                    {
                        "lane": lane,
                        "current_avg": summary.avg_duration,
                        "target": target,
                        "overhead": summary.avg_duration - target,
                        "executio_count": summary.execution_count,
                    }
                )

        return slow_lanes

    def get_optimization_recommendations(self) -> list:
        """Get optimization recommendations."""
        recommendations = []

        slow_lanes = self.identify_slow_lanes()
        for lane_info in slow_lanes:
            recommendations.append(
                {
                    "lane": lane_info["lane"],
                    "issue": f"Average duration {lane_info['overhead']:.1f}s over target",
                    "actions": [
                        f"Profile workflow execution in {lane_info['lane']} lane",
                        "Identify bottleneck quality gates",
                        "Consider parallelizing independent gates",
                        "Review test suite for slow tests",
                    ],
                }
            )

        return recommendations


# ============================================================================
# EXAMPLE 5: Quality Gate Analysis
# ============================================================================


class QualityMetricsAnalyzer:
    """Analyze quality metrics across lanes."""

    def __init__(self):
        self.analyzer = MetricsAnalyzer()

    def get_quality_gate_health(self) -> dict:
        """Get quality gate health across lanes."""
        health = {}

        for lane in ["docs", "standard", "heavy"]:
            analysis = self.analyzer.get_quality_gate_analysis(lane, days=7)

            health[lane] = {
                "pass_rate": analysis["avg_pass_rate"],
                "executions": analysis["total_executions"],
                "perfect_runs": analysis["perfect_runs"],
                "perfect_rate": analysis["perfect_run_percentage"],
                "status": (
                    "excellent"
                    if analysis["avg_pass_rate"] > 99
                    else "good" if analysis["avg_pass_rate"] > 95 else "needs_attention"
                ),
            }

        return health

    def identify_flaky_gates(self) -> list:
        """Identify potentially flaky quality gates."""
        flaky = []

        for lane in ["docs", "standard", "heavy"]:
            analysis = self.analyzer.get_quality_gate_analysis(lane, days=7)

            # If quality varies significantly, gates might be flaky
            if analysis["avg_pass_rate"] < 100 and analysis["total_executions"] > 20:
                variance = analysis["max_pass_rate"] - analysis["min_pass_rate"]
                if variance > 10:  # >10% variance
                    flaky.append(
                        {
                            "lane": lane,
                            "variance": variance,
                            "avg_rate": analysis["avg_pass_rate"],
                            "min_rate": analysis["min_pass_rate"],
                            "max_rate": analysis["max_pass_rate"],
                        }
                    )

        return flaky


# ============================================================================
# EXAMPLE 6: Integration with CI/CD
# ============================================================================


def github_actions_integration_example():
    """Example of integrating with GitHub Actions."""

    import json
    import sys

    # Collect metrics during workflow
    executor = WorkflowExecutor()
    success = executor.execute_workflow(
        lane="standard", changes={"files": [], "scope": "feature"}
    )

    # Generate dashboard
    dashboard = AnalyticsDashboard()
    print("\n" + "=" * 70)
    print("WEEKLY ANALYTICS REPORT")
    print("=" * 70)
    print(dashboard.generate_weekly_report())

    # Check SLA compliance
    sla_status = dashboard.get_sla_compliance_status()
    print(f"\nOverall SLA Compliance: {sla_status['overall_compliance']:.1f}%")

    for lane, status in sla_status["lanes"].items():
        print(f"  {lane}: {status['compliance']:.1f}% ({status['status']})")

    # Export dashboard data as JSON (for external systems)
    analyzer = MetricsAnalyzer()
    dashboard_data = analyzer.get_dashboard_data(days=7)

    output_file = Path("analytics_dashboard.json")
    output_file.write_text(json.dumps(dashboard_data, indent=2))
    print(f"\n✅ Dashboard data exported to {output_file}")

    # Return exit code based on SLA compliance
    exit_code = 0 if sla_status["overall_compliance"] >= 90 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    # Example 1: Workflow execution with metrics
    print("EXAMPLE 1: Workflow Execution")
    print("=" * 70)
    executor = WorkflowExecutor()
    executor.execute_workflow(
        lane="standard", changes={"files": ["agent/backend.py"], "scope": "bugfix"}
    )

    # Example 2: Dashboard generation
    print("\n\nEXAMPLE 2: Analytics Dashboard")
    print("=" * 70)
    dashboard = AnalyticsDashboard()
    print(dashboard.get_performance_trends())

    # Example 3: Anomaly detection
    print("\n\nEXAMPLE 3: Anomaly Detection")
    print("=" * 70)
    anomaly_system = AnomalyDetectionSystem()
    results = anomaly_system.check_for_anomalies()
    print(f"Anomalies found: {results['anomalies_found']}")

    # Example 4: Performance optimization
    print("\n\nEXAMPLE 4: Performance Optimization")
    print("=" * 70)
    optimizer = PerformanceOptimizer()
    recommendations = optimizer.get_optimization_recommendations()
    for rec in recommendations:
        print(f"Lane: {rec['lane']}")
        print(f"Issue: {rec['issue']}")
        for action in rec["actions"]:
            print(f"  - {action}")

    # Example 5: Quality analysis
    print("\n\nEXAMPLE 5: Quality Gate Analysis")
    print("=" * 70)
    quality = QualityMetricsAnalyzer()
    health = quality.get_quality_gate_health()
    for lane, stats in health.items():
        print(f"{lane}: {stats['pass_rate']:.1f}% pass rate ({stats['status']})")
