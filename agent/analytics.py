#!/usr/bin/env python3
"""
Analytics and Metrics Collection Framework for Workflow Lanes

Collects comprehensive metrics on lane usage, execution times, quality gate
pass rates, and performance characteristics. Provides historical tracking,
trend analysis, and reporting capabilities.

Features:
- Real-time metrics collection during workflow execution
- Historical data storage with SQLite backend
- Metrics aggregation and analysis
- Dashboard data generation
- Trend analysis and anomaly detection
- Performance SLA validation

Usage:
    from agent.analytics import MetricsCollector, MetricsAnalyzer

    collector = MetricsCollector()
    collector.record_workflow_execution(
        lane="standard",
        duration=450.5,
        success=True,
        quality_gates_passed=12
    )

    analyzer = MetricsAnalyzer()
    summary = analyzer.get_lane_summary("standard", days=7)
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import statistics


class LaneType(Enum):
    """Workflow lane types."""

    DOCS = "docs"
    STANDARD = "standard"
    HEAVY = "heavy"


class QualityGateStatus(Enum):
    """Quality gate pass/fail status."""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class WorkflowMetrics:
    """Single workflow execution metrics."""

    timestamp: str
    lane: str
    duration_seconds: float
    success: bool
    quality_gates_passed: int
    quality_gates_failed: int
    total_quality_gates: int
    tests_passed: int
    tests_failed: int
    total_tests: int
    documentation_files_checked: int
    documentation_files_valid: int
    sla_met: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def quality_gate_pass_rate(self) -> float:
        """Calculate quality gate pass rate."""
        if self.total_quality_gates == 0:
            return 100.0
        return 100.0 * self.quality_gates_passed / self.total_quality_gates

    @property
    def test_pass_rate(self) -> float:
        """Calculate test pass rate."""
        if self.total_tests == 0:
            return 100.0
        return 100.0 * self.tests_passed / self.total_tests

    @property
    def documentation_validity_rate(self) -> float:
        """Calculate documentation validity rate."""
        if self.documentation_files_checked == 0:
            return 100.0
        return 100.0 * self.documentation_files_valid / self.documentation_files_checked


@dataclass
class LaneSummary:
    """Summary statistics for a lane over a time period."""

    lane: str
    period_days: int
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    avg_duration: float
    min_duration: float
    max_duration: float
    median_duration: float
    avg_quality_gate_pass_rate: float
    avg_test_pass_rate: float
    sla_compliance_rate: float
    total_time_saved: float  # vs standard lane
    trend: str  # "improving", "stable", "degrading"


class MetricsCollector:
    """Collects and stores workflow metrics."""

    def __init__(self, db_path: str = "agent/metrics/metrics.db"):
        """Initialize metrics collector."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                lane TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                success BOOLEAN NOT NULL,
                quality_gates_passed INTEGER NOT NULL,
                quality_gates_failed INTEGER NOT NULL,
                total_quality_gates INTEGER NOT NULL,
                tests_passed INTEGER NOT NULL,
                tests_failed INTEGER NOT NULL,
                total_tests INTEGER NOT NULL,
                documentation_files_checked INTEGER NOT NULL,
                documentation_files_valid INTEGER NOT NULL,
                sla_met BOOLEAN NOT NULL,
                error_message TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lane ON workflow_metrics(lane)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON workflow_metrics(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_success ON workflow_metrics(success)"
        )

        conn.commit()
        conn.close()

    def record_workflow_execution(
        self,
        lane: str,
        duration_seconds: float,
        success: bool,
        quality_gates_passed: int,
        quality_gates_failed: int,
        total_quality_gates: int,
        tests_passed: int,
        tests_failed: int,
        total_tests: int,
        documentation_files_checked: int,
        documentation_files_valid: int,
        sla_met: bool,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Record a workflow execution."""
        metrics = WorkflowMetrics(
            timestamp=datetime.now().isoformat(),
            lane=lane,
            duration_seconds=duration_seconds,
            success=success,
            quality_gates_passed=quality_gates_passed,
            quality_gates_failed=quality_gates_failed,
            total_quality_gates=total_quality_gates,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            total_tests=total_tests,
            documentation_files_checked=documentation_files_checked,
            documentation_files_valid=documentation_files_valid,
            sla_met=sla_met,
            error_message=error_message,
            metadata=metadata or {},
        )

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO workflow_metrics (
                timestamp, lane, duration_seconds, success,
                quality_gates_passed, quality_gates_failed, total_quality_gates,
                tests_passed, tests_failed, total_tests,
                documentation_files_checked, documentation_files_valid,
                sla_met, error_message, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics.timestamp,
                metrics.lane,
                metrics.duration_seconds,
                metrics.success,
                metrics.quality_gates_passed,
                metrics.quality_gates_failed,
                metrics.total_quality_gates,
                metrics.tests_passed,
                metrics.tests_failed,
                metrics.total_tests,
                metrics.documentation_files_checked,
                metrics.documentation_files_valid,
                metrics.sla_met,
                metrics.error_message,
                json.dumps(metrics.metadata),
            ),
        )

        conn.commit()
        conn.close()

    def export_metrics(self, output_path: str) -> None:
        """Export all metrics to JSON."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row

        cursor.execute("SELECT * FROM workflow_metrics ORDER BY timestamp DESC")
        rows = cursor.fetchall()

        metrics_list = []
        for row in rows:
            metrics_dict = dict(row)
            if metrics_dict.get("metadata"):
                metrics_dict["metadata"] = json.loads(metrics_dict["metadata"])
            metrics_list.append(metrics_dict)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(metrics_list, indent=2))

        conn.close()


class MetricsAnalyzer:
    """Analyzes collected metrics."""

    def __init__(self, db_path: str = "agent/metrics/metrics.db"):
        """Initialize analyzer."""
        self.db_path = Path(db_path)

    def get_lane_summary(self, lane: str, days: int = 7) -> LaneSummary:
        """Get summary statistics for a lane."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failure_count,
                AVG(duration_seconds) as avg_duration,
                MIN(duration_seconds) as min_duration,
                MAX(duration_seconds) as max_duration,
                AVG(quality_gates_passed * 100.0 / NULLIF(total_quality_gates, 0)) as avg_qg_pass_rate,
                AVG(tests_passed * 100.0 / NULLIF(total_tests, 0)) as avg_test_pass_rate,
                SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) as sla_met_count
            FROM workflow_metrics
            WHERE lane = ? AND timestamp > ?
        """,
            (lane, cutoff_date),
        )

        result = cursor.fetchone()

        if not result or result[0] == 0:
            conn.close()
            return LaneSummary(
                lane=lane,
                period_days=days,
                execution_count=0,
                success_count=0,
                failure_count=0,
                success_rate=0.0,
                avg_duration=0.0,
                min_duration=0.0,
                max_duration=0.0,
                median_duration=0.0,
                avg_quality_gate_pass_rate=0.0,
                avg_test_pass_rate=0.0,
                sla_compliance_rate=0.0,
                total_time_saved=0.0,
                trend="unknown",
            )

        (
            total,
            success_count,
            failure_count,
            avg_dur,
            min_dur,
            max_dur,
            avg_qg,
            avg_test,
            sla_count,
        ) = result

        # Get median duration
        cursor.execute(
            """
            SELECT duration_seconds FROM workflow_metrics
            WHERE lane = ? AND timestamp > ?
            ORDER BY duration_seconds
        """,
            (lane, cutoff_date),
        )

        durations = [row[0] for row in cursor.fetchall()]
        median_dur = statistics.median(durations) if durations else 0.0

        # Calculate trend
        trend = self._calculate_trend(lane, days)

        # Calculate time saved vs standard lane
        time_saved = self._calculate_time_saved(lane, days)

        summary = LaneSummary(
            lane=lane,
            period_days=days,
            execution_count=total,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=100.0 * success_count / total if total > 0 else 0.0,
            avg_duration=avg_dur or 0.0,
            min_duration=min_dur or 0.0,
            max_duration=max_dur or 0.0,
            median_duration=median_dur,
            avg_quality_gate_pass_rate=avg_qg or 0.0,
            avg_test_pass_rate=avg_test or 0.0,
            sla_compliance_rate=100.0 * sla_count / total if total > 0 else 0.0,
            total_time_saved=time_saved,
            trend=trend,
        )

        conn.close()
        return summary

    def _calculate_trend(self, lane: str, days: int) -> str:
        """Calculate trend over time period."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        mid_date = (datetime.now() - timedelta(days=days // 2)).isoformat()

        # Compare first half vs second half
        cursor.execute(
            """
            SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
            FROM workflow_metrics
            WHERE lane = ? AND timestamp BETWEEN ? AND ?
        """,
            (lane, cutoff_date, mid_date),
        )

        first_half = cursor.fetchone()[0] or 0.0

        cursor.execute(
            """
            SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
            FROM workflow_metrics
            WHERE lane = ? AND timestamp > ?
        """,
            (lane, mid_date),
        )

        second_half = cursor.fetchone()[0] or 0.0
        conn.close()

        diff = second_half - first_half
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "degrading"
        else:
            return "stable"

    def _calculate_time_saved(self, lane: str, days: int) -> float:
        """Calculate time saved vs standard lane."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Get average duration for this lane and standard lane
        cursor.execute(
            """
            SELECT AVG(duration_seconds)
            FROM workflow_metrics
            WHERE lane = ? AND timestamp > ? AND success = 1
        """,
            (lane, cutoff_date),
        )

        lane_avg = cursor.fetchone()[0] or 0.0

        cursor.execute(
            """
            SELECT AVG(duration_seconds)
            FROM workflow_metrics
            WHERE lane = 'standard' AND timestamp > ? AND success = 1
        """,
            (cutoff_date,),
        )

        standard_avg = cursor.fetchone()[0] or 0.0

        # Get count of executions in this lane
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM workflow_metrics
            WHERE lane = ? AND timestamp > ?
        """,
            (lane, cutoff_date),
        )

        count = cursor.fetchone()[0] or 0

        time_saved = max(0, (standard_avg - lane_avg) * count)
        conn.close()

        return time_saved

    def get_all_lanes_summary(self, days: int = 7) -> Dict[str, LaneSummary]:
        """Get summary for all lanes."""
        summaries = {}
        for lane_type in ["docs", "standard", "heavy"]:
            summaries[lane_type] = self.get_lane_summary(lane_type, days)
        return summaries

    def get_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """Get data for dashboard visualization."""
        all_summaries = self.get_all_lanes_summary(days)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Get total stats
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_runs,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as total_success,
                AVG(quality_gates_passed * 100.0 / NULLIF(total_quality_gates, 0)) as avg_quality_rate,
                AVG(tests_passed * 100.0 / NULLIF(total_tests, 0)) as avg_test_rate,
                SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) as sla_met_count
            FROM workflow_metrics
            WHERE timestamp > ?
        """,
            (cutoff_date,),
        )

        total_runs, total_success, avg_quality, avg_tests, sla_met = cursor.fetchone()

        # Get hourly trend data
        cursor.execute(
            """
            SELECT
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as runs,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                AVG(duration_seconds) as avg_duration
            FROM workflow_metrics
            WHERE timestamp > ?
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 24
        """,
            (cutoff_date,),
        )

        hourly_data = [
            dict(zip(["hour", "runs", "successes", "avg_duration"], row))
            for row in cursor.fetchall()
        ]

        conn.close()

        return {
            "period_days": days,
            "timestamp": datetime.now().isoformat(),
            "total_runs": total_runs or 0,
            "total_success": total_success or 0,
            "success_rate": 100.0 * (total_success or 0) / (total_runs or 1),
            "avg_quality_rate": avg_quality or 0.0,
            "avg_test_rate": avg_tests or 0.0,
            "sla_compliance": 100.0 * (sla_met or 0) / (total_runs or 1),
            "lanes": {lane: asdict(summary) for lane, summary in all_summaries.items()},
            "hourly_trend": hourly_data,
        }

    def get_quality_gate_analysis(self, lane: str, days: int = 7) -> Dict[str, Any]:
        """Analyze quality gate patterns."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute(
            """
            SELECT
                COUNT(*) as total,
                AVG(quality_gates_passed * 100.0 / NULLIF(total_quality_gates, 0)) as avg_pass_rate,
                MAX(quality_gates_passed * 100.0 / NULLIF(total_quality_gates, 0)) as max_pass_rate,
                MIN(quality_gates_passed * 100.0 / NULLIF(total_quality_gates, 0)) as min_pass_rate,
                SUM(CASE WHEN quality_gates_passed = total_quality_gates THEN 1 ELSE 0 END) as perfect_runs
            FROM workflow_metrics
            WHERE lane = ? AND timestamp > ?
        """,
            (lane, cutoff_date),
        )

        result = cursor.fetchone()
        total, avg_rate, max_rate, min_rate, perfect = result

        conn.close()

        return {
            "lane": lane,
            "period_days": days,
            "total_executions": total or 0,
            "average_pass_rate": avg_rate or 0.0,
            "max_pass_rate": max_rate or 0.0,
            "min_pass_rate": min_rate or 0.0,
            "perfect_runs": perfect or 0,
            "perfect_run_percentage": 100.0 * (perfect or 0) / (total or 1),
        }

    def detect_anomalies(self, lane: str, days: int = 7) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute(
            """
            SELECT timestamp, duration_seconds, success, quality_gates_passed, total_quality_gates
            FROM workflow_metrics
            WHERE lane = ? AND timestamp > ?
            ORDER BY timestamp DESC
        """,
            (lane, cutoff_date),
        )

        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 3:
            return []

        # Calculate average duration
        durations = [row[1] for row in rows]
        avg_duration = statistics.mean(durations)
        std_duration = statistics.stdev(durations) if len(durations) > 1 else 0

        anomalies = []
        threshold = avg_duration + (2 * std_duration)  # 2 standard deviations

        for timestamp, duration, success, gates_passed, total_gates in rows:
            if duration > threshold:
                anomalies.append(
                    {
                        "type": "slow_execution",
                        "timestamp": timestamp,
                        "duration": duration,
                        "expected": avg_duration,
                        "deviation": duration - avg_duration,
                        "severity": "high" if duration > threshold * 1.5 else "medium",
                    }
                )

            if not success and total_gates > 0:
                pass_rate = gates_passed / total_gates
                if pass_rate < 0.5:
                    anomalies.append(
                        {
                            "type": "quality_gate_failure",
                            "timestamp": timestamp,
                            "pass_rate": pass_rate,
                            "passed": gates_passed,
                            "total": total_gates,
                            "severity": "high" if pass_rate < 0.3 else "medium",
                        }
                    )

        return anomalies


class MetricsReporter:
    """Generates metrics reports."""

    def __init__(self, analyzer: MetricsAnalyzer):
        """Initialize reporter."""
        self.analyzer = analyzer

    def generate_summary_report(self, days: int = 7) -> str:
        """Generate text summary report."""
        dashboard = self.analyzer.get_dashboard_data(days)

        report = []
        report.append("=" * 70)
        report.append("WORKFLOW LANES - METRICS SUMMARY REPORT")
        report.append("=" * 70)
        report.append(f"Period: Last {days} days")
        report.append(f"Generated: {dashboard['timestamp']}")
        report.append("")

        report.append("OVERALL STATISTICS")
        report.append("-" * 70)
        report.append(f"Total Workflow Executions: {dashboard['total_runs']}")
        report.append(f"Successful Executions: {dashboard['total_success']}")
        report.append(f"Success Rate: {dashboard['success_rate']:.1f}%")
        report.append(
            f"Average Quality Gate Pass Rate: {dashboard['avg_quality_rate']:.1f}%"
        )
        report.append(f"Average Test Pass Rate: {dashboard['avg_test_rate']:.1f}%")
        report.append(f"SLA Compliance Rate: {dashboard['sla_compliance']:.1f}%")
        report.append("")

        report.append("LANE PERFORMANCE")
        report.append("-" * 70)
        for lane, stats in dashboard["lanes"].items():
            report.append(f"\n{lane.upper()} LANE")
            report.append(f"  Executions: {stats['execution_count']}")
            report.append(f"  Success Rate: {stats['success_rate']:.1f}%")
            report.append(f"  Avg Duration: {stats['avg_duration']:.1f}s")
            report.append(
                f"  Duration Range: {stats['min_duration']:.1f}s - {stats['max_duration']:.1f}s"
            )
            report.append(f"  SLA Compliance: {stats['sla_compliance_rate']:.1f}%")
            report.append(
                f"  Quality Gate Pass Rate: {stats['avg_quality_gate_pass_rate']:.1f}%"
            )
            report.append(f"  Trend: {stats['trend']}")
            report.append(f"  Time Saved vs Standard: {stats['total_time_saved']:.1f}s")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def generate_json_report(
        self, days: int = 7, output_path: Optional[str] = None
    ) -> Dict:
        """Generate JSON report."""
        report = self.analyzer.get_dashboard_data(days)

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json.dumps(report, indent=2))

        return report

    def generate_anomaly_report(self, days: int = 7) -> str:
        """Generate anomaly detection report."""
        report = []
        report.append("=" * 70)
        report.append("ANOMALY DETECTION REPORT")
        report.append("=" * 70)
        report.append(f"Period: Last {days} days")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        for lane in ["docs", "standard", "heavy"]:
            anomalies = self.analyzer.detect_anomalies(lane, days)

            if anomalies:
                report.append(
                    f"\n{lane.upper()} LANE - {len(anomalies)} anomalies detected"
                )
                report.append("-" * 70)

                for anom in anomalies[:10]:  # Limit to top 10 per lane
                    report.append(f"Type: {anom['type']}")
                    report.append(f"Timestamp: {anom['timestamp']}")
                    report.append(f"Severity: {anom['severity'].upper()}")

                    if anom["type"] == "slow_execution":
                        report.append(
                            f"Duration: {anom['duration']:.1f}s (expected ~{anom['expected']:.1f}s)"
                        )
                        report.append(f"Deviation: +{anom['deviation']:.1f}s")
                    elif anom["type"] == "quality_gate_failure":
                        report.append(f"Pass Rate: {anom['pass_rate']:.1%}")
                        report.append(f"Gates: {anom['passed']}/{anom['total']}")

                    report.append("")
            else:
                report.append(f"\n{lane.upper()} LANE - No anomalies detected ✓")

        report.append("=" * 70)
        return "\n".join(report)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analytics and Metrics Collection")
    parser.add_argument(
        "--collect", action="store_true", help="Collect metrics (for testing)"
    )
    parser.add_argument("--analyze", action="store_true", help="Analyze metrics")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--lane", default="standard", help="Lane for analysis")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    if args.analyze:
        analyzer = MetricsAnalyzer()
        summary = analyzer.get_lane_summary(args.lane, args.days)
        print(f"Lane: {summary.lane}")
        print(f"Executions: {summary.execution_count}")
        print(f"Success Rate: {summary.success_rate:.1f}%")
        print(f"Avg Duration: {summary.avg_duration:.1f}s")

    if args.report:
        analyzer = MetricsAnalyzer()
        reporter = MetricsReporter(analyzer)
        print(reporter.generate_summary_report(args.days))

        if args.output:
            reporter.generate_json_report(args.days, args.output)
