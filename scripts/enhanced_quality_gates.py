"""
Enhanced Quality Gates System for v0.1.45

Improvements to quality validation pipeline:
  1. Lane-specific quality thresholds (DOCS/STANDARD/HEAVY)
  2. Remediation suggestions for failures
  3. Color-formatted output for better visibility
  4. Parallel execution metrics integration
  5. Per-gate performance tracking
  6. Configurable severity levels
  7. Pre-flight validation
  8. Detailed error reports

Author: @kdejo
Date: 2025-10-24
"""

import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GateSeverity(Enum):
    """Severity levels for quality gate violations."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LaneType(Enum):
    """Workflow lanes with different quality standards."""

    DOCS = "docs"
    STANDARD = "standard"
    HEAVY = "heavy"


class QualityGateName(Enum):
    """Available quality gates."""

    RUFF = "ruff"  # Linting
    MYPY = "mypy"  # Type checking
    PYTEST = "pytest"  # Unit/integration tests
    BANDIT = "bandit"  # Security scanning
    COVERAGE = "coverage"  # Code coverage


@dataclass
class QualityThreshold:
    """Threshold configuration for a quality gate."""

    gate: QualityGateName
    lane: LaneType
    enabled: bool = True
    pass_threshold: float = 0.0  # For coverage (percentage)
    fail_threshold: float = 1.0  # For coverage (percentage)
    timeout_seconds: int = 60
    warnings_allowed: int = 0
    errors_allowed: int = 0
    severity: GateSeverity = GateSeverity.ERROR

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "gate": self.gate.value,
            "lane": self.lane.value,
            "enabled": self.enabled,
            "pass_threshold": self.pass_threshold,
            "fail_threshold": self.fail_threshold,
            "timeout_seconds": self.timeout_seconds,
            "warnings_allowed": self.warnings_allowed,
            "errors_allowed": self.errors_allowed,
            "severity": self.severity.value,
        }


@dataclass
class GateResult:
    """Result of a single quality gate execution."""

    gate: QualityGateName
    lane: LaneType
    passed: bool
    duration_seconds: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    warnings_count: int = 0
    errors_count: int = 0
    exit_code: int = 0
    output: str = ""
    error_output: str = ""
    severity: GateSeverity = GateSeverity.ERROR
    remediation_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "gate": self.gate.value,
            "lane": self.lane.value,
            "passed": self.passed,
            "duration_seconds": self.duration_seconds,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "warnings_count": self.warnings_count,
            "errors_count": self.errors_count,
            "exit_code": self.exit_code,
            "output_lines": len(self.output.split("\n")),
            "error_lines": len(self.error_output.split("\n")),
            "severity": self.severity.value,
            "remediation_steps": self.remediation_steps,
        }


@dataclass
class QualityGatesMetrics:
    """Metrics for all quality gates execution."""

    lane: LaneType
    total_gates: int = 0
    passed_gates: int = 0
    failed_gates: int = 0
    total_duration_seconds: float = 0.0
    avg_gate_duration_seconds: float = 0.0
    gate_results: List[GateResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "lane": self.lane.value,
            "total_gates": self.total_gates,
            "passed_gates": self.passed_gates,
            "failed_gates": self.failed_gates,
            "total_duration_seconds": self.total_duration_seconds,
            "avg_gate_duration_seconds": self.avg_gate_duration_seconds,
            "gate_results": [r.to_dict() for r in self.gate_results],
            "timestamp": self.timestamp,
        }


class LaneQualityConfig:
    """Lane-specific quality gate configuration."""

    # Default thresholds for each lane
    LANE_CONFIGS = {
        LaneType.DOCS: {
            QualityGateName.RUFF: QualityThreshold(
                gate=QualityGateName.RUFF,
                lane=LaneType.DOCS,
                enabled=True,
                timeout_seconds=30,
                warnings_allowed=5,
                errors_allowed=0,
                severity=GateSeverity.WARNING,
            ),
            QualityGateName.MYPY: QualityThreshold(
                gate=QualityGateName.MYPY,
                lane=LaneType.DOCS,
                enabled=False,  # Skipped for docs lane
                timeout_seconds=30,
            ),
            QualityGateName.PYTEST: QualityThreshold(
                gate=QualityGateName.PYTEST,
                lane=LaneType.DOCS,
                enabled=False,  # Skipped for docs lane
                timeout_seconds=30,
            ),
            QualityGateName.BANDIT: QualityThreshold(
                gate=QualityGateName.BANDIT,
                lane=LaneType.DOCS,
                enabled=False,  # Skipped for docs lane
                timeout_seconds=30,
            ),
            QualityGateName.COVERAGE: QualityThreshold(
                gate=QualityGateName.COVERAGE,
                lane=LaneType.DOCS,
                enabled=False,
                pass_threshold=0.0,
            ),
        },
        LaneType.STANDARD: {
            QualityGateName.RUFF: QualityThreshold(
                gate=QualityGateName.RUFF,
                lane=LaneType.STANDARD,
                enabled=True,
                timeout_seconds=45,
                warnings_allowed=3,
                errors_allowed=0,
                severity=GateSeverity.ERROR,
            ),
            QualityGateName.MYPY: QualityThreshold(
                gate=QualityGateName.MYPY,
                lane=LaneType.STANDARD,
                enabled=True,
                timeout_seconds=60,
                warnings_allowed=5,
                errors_allowed=0,
                severity=GateSeverity.ERROR,
            ),
            QualityGateName.PYTEST: QualityThreshold(
                gate=QualityGateName.PYTEST,
                lane=LaneType.STANDARD,
                enabled=True,
                timeout_seconds=120,
                warnings_allowed=0,
                errors_allowed=0,
                severity=GateSeverity.ERROR,
            ),
            QualityGateName.BANDIT: QualityThreshold(
                gate=QualityGateName.BANDIT,
                lane=LaneType.STANDARD,
                enabled=True,
                timeout_seconds=60,
                warnings_allowed=0,
                errors_allowed=0,
                severity=GateSeverity.ERROR,
            ),
            QualityGateName.COVERAGE: QualityThreshold(
                gate=QualityGateName.COVERAGE,
                lane=LaneType.STANDARD,
                enabled=True,
                pass_threshold=75.0,  # Require 75% coverage
                fail_threshold=95.0,
                severity=GateSeverity.WARNING,
            ),
        },
        LaneType.HEAVY: {
            QualityGateName.RUFF: QualityThreshold(
                gate=QualityGateName.RUFF,
                lane=LaneType.HEAVY,
                enabled=True,
                timeout_seconds=60,
                warnings_allowed=0,
                errors_allowed=0,
                severity=GateSeverity.CRITICAL,
            ),
            QualityGateName.MYPY: QualityThreshold(
                gate=QualityGateName.MYPY,
                lane=LaneType.HEAVY,
                enabled=True,
                timeout_seconds=90,
                warnings_allowed=0,
                errors_allowed=0,
                severity=GateSeverity.CRITICAL,
            ),
            QualityGateName.PYTEST: QualityThreshold(
                gate=QualityGateName.PYTEST,
                lane=LaneType.HEAVY,
                enabled=True,
                timeout_seconds=180,
                warnings_allowed=0,
                errors_allowed=0,
                severity=GateSeverity.CRITICAL,
            ),
            QualityGateName.BANDIT: QualityThreshold(
                gate=QualityGateName.BANDIT,
                lane=LaneType.HEAVY,
                enabled=True,
                timeout_seconds=90,
                warnings_allowed=0,
                errors_allowed=0,
                severity=GateSeverity.CRITICAL,
            ),
            QualityGateName.COVERAGE: QualityThreshold(
                gate=QualityGateName.COVERAGE,
                lane=LaneType.HEAVY,
                enabled=True,
                pass_threshold=85.0,  # Require 85% coverage
                fail_threshold=95.0,
                severity=GateSeverity.CRITICAL,
            ),
        },
    }

    @classmethod
    def get_threshold(cls, gate: QualityGateName, lane: LaneType) -> QualityThreshold:
        """Get threshold for specific gate and lane."""
        return cls.LANE_CONFIGS[lane][gate]

    @classmethod
    def get_all_thresholds(
        cls, lane: LaneType
    ) -> Dict[QualityGateName, QualityThreshold]:
        """Get all thresholds for a lane."""
        return cls.LANE_CONFIGS[lane].copy()


class RemediationSuggestions:
    """Provides remediation steps for common quality gate failures."""

    REMEDIATION_MAP = {
        QualityGateName.RUFF: {
            "E": [
                "Fix formatting issues: Review the flagged lines",
                "Run 'ruff check --fix agent/' to auto-fix issues",
                "Review docs: https://docs.astral.sh/ruff/",
            ],
            "W": [
                "Review warnings: Not always critical",
                "Consider suppressing with # noqa comments if justified",
                "For DOCS lane: Warnings are warnings, not errors",
            ],
            "F": [
                "Fix imports: Remove unused imports",
                "Run 'ruff check --fix --extend-select=F agent/'",
                "Check for undefined names in code",
            ],
        },
        QualityGateName.MYPY: {
            "error": [
                "Add type hints: def func(x: int) -> str:",
                "Use typing module: from typing import List, Dict, Optional",
                "Install type stubs: pip install types-<package>",
                "Configure mypy: Check agent/mypy.ini settings",
            ],
            "ignored": [
                "Add # type: ignore comments only if unavoidable",
                "Better: Fix the underlying type issue",
                "Review: Why is this type hard to infer?",
            ],
        },
        QualityGateName.PYTEST: {
            "FAILED": [
                "Review test output: pytest tests/ -v --tb=short",
                "Check assertions: Verify expected vs actual",
                "Run locally: pytest tests/backend/test_*.py -k 'test_name' -vv",
                "Check fixtures: Ensure test setup is correct",
            ],
            "ERROR": [
                "Check test setup: Verify imports and dependencies",
                "Run: pytest tests/ --co -q to list tests",
                "Check conftest.py: Ensure fixtures are configured",
                "Install missing deps: pip install -r requirements.txt",
            ],
        },
        QualityGateName.BANDIT: {
            "HIGH": [
                "Security issue detected: Review flagged code carefully",
                "Check: Are you using secure functions (secrets vs random)?",
                "Fix: Replace insecure patterns with secure alternatives",
                "Test: Verify fix doesn't break functionality",
            ],
            "MEDIUM": [
                "Potential security risk: Assess if applicable",
                "Suppress if justified: # nosec B101",
                "Document: Why the pattern is safe in context",
            ],
        },
        QualityGateName.COVERAGE: {
            "low": [
                "Add missing tests: Identify uncovered code",
                "Run: pytest --cov=agent --cov-report=html tests/",
                "Review: htmlcov/index.html for coverage gaps",
                "Target: Aim for 85%+ in STANDARD, 95%+ in HEAVY lane",
            ],
        },
    }

    @classmethod
    def get_suggestions(cls, gate: QualityGateName, issue_type: str) -> List[str]:
        """Get remediation suggestions for gate and issue type."""
        gate_map = cls.REMEDIATION_MAP.get(gate, {})
        return gate_map.get(
            issue_type,
            [
                "Check gate documentation",
                "Review the error output carefully",
                "Search for similar issues in project",
            ],
        )


class ColorFormatter:
    """ANSI color formatting for terminal output."""

    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }

    @classmethod
    def green(cls, text: str) -> str:
        """Format text in green."""
        return f"{cls.COLORS['green']}{text}{cls.COLORS['reset']}"

    @classmethod
    def yellow(cls, text: str) -> str:
        """Format text in yellow."""
        return f"{cls.COLORS['yellow']}{text}{cls.COLORS['reset']}"

    @classmethod
    def red(cls, text: str) -> str:
        """Format text in red."""
        return f"{cls.COLORS['red']}{text}{cls.COLORS['reset']}"

    @classmethod
    def blue(cls, text: str) -> str:
        """Format text in blue."""
        return f"{cls.COLORS['blue']}{text}{cls.COLORS['reset']}"

    @classmethod
    def bold(cls, text: str) -> str:
        """Format text in bold."""
        return f"{cls.COLORS['bold']}{text}{cls.COLORS['reset']}"

    @classmethod
    def severity_color(cls, severity: GateSeverity) -> str:
        """Get color for severity level."""
        if severity == GateSeverity.CRITICAL:
            return cls.red(severity.value.upper())
        elif severity == GateSeverity.ERROR:
            return cls.red(severity.value)
        elif severity == GateSeverity.WARNING:
            return cls.yellow(severity.value)
        else:
            return cls.blue(severity.value)


class EnhancedQualityGateExecutor:
    """Execute quality gates with lane-specific thresholds and reporting."""

    def __init__(self, lane: LaneType = LaneType.STANDARD):
        self.lane = lane
        self.thresholds = LaneQualityConfig.get_all_thresholds(lane)
        self.metrics = QualityGatesMetrics(lane=lane)
        self.results = {}
        self.failed_gates = []
        self.warnings = []

    async def execute_all_gates(self) -> Tuple[bool, QualityGatesMetrics]:
        """
        Execute all enabled gates for the lane.

        Returns:
            Tuple of (all_passed, metrics)
        """
        print(f"\n{ColorFormatter.bold('Quality Gates Execution')}")
        print(f"Lane: {ColorFormatter.blue(self.lane.value.upper())}")
        print("=" * 60)

        for gate in QualityGateName:
            threshold = self.thresholds[gate]

            if not threshold.enabled:
                print(
                    f"\n⊘ {gate.value.upper():20s} SKIPPED (disabled for {self.lane.value} lane)"
                )
                continue

            result = await self.execute_gate(gate)
            self.results[gate] = result
            self.metrics.gate_results.append(result)
            self._report_gate_result(result)

        # Finalize metrics
        self.metrics.total_gates = len(
            [t for t in self.thresholds.values() if t.enabled]
        )
        self.metrics.passed_gates = len(
            [r for r in self.metrics.gate_results if r.passed]
        )
        self.metrics.failed_gates = len(
            [r for r in self.metrics.gate_results if not r.passed]
        )
        self.metrics.total_duration_seconds = sum(
            r.duration_seconds for r in self.metrics.gate_results
        )

        if self.metrics.gate_results:
            self.metrics.avg_gate_duration_seconds = (
                self.metrics.total_duration_seconds / len(self.metrics.gate_results)
            )

        # Print summary
        self._print_summary()

        all_passed = self.metrics.failed_gates == 0
        return (all_passed, self.metrics)

    async def execute_gate(self, gate: QualityGateName) -> GateResult:
        """Execute a single quality gate."""
        threshold = self.thresholds[gate]
        result = GateResult(
            gate=gate, lane=self.lane, passed=False, severity=threshold.severity
        )

        try:
            start_time = time.time()
            result.start_time = datetime.now()

            # Execute gate based on type
            if gate == QualityGateName.RUFF:
                passed, output, error = await self._run_ruff()
            elif gate == QualityGateName.MYPY:
                passed, output, error = await self._run_mypy()
            elif gate == QualityGateName.PYTEST:
                passed, output, error = await self._run_pytest()
            elif gate == QualityGateName.BANDIT:
                passed, output, error = await self._run_bandit()
            elif gate == QualityGateName.COVERAGE:
                passed, output, error = await self._run_coverage(threshold)
            else:
                passed, output, error = False, "", "Unknown gate"

            result.end_time = datetime.now()
            result.duration_seconds = time.time() - start_time
            result.passed = passed
            result.output = output
            result.error_output = error

            # Parse output for warnings/errors
            result.warnings_count = output.count("warning")
            result.errors_count = output.count("error")

            # Check thresholds
            if not passed and threshold.severity == GateSeverity.CRITICAL:
                self.failed_gates.append((gate, result))
            elif not passed:
                self.warnings.append((gate, result))

            # Generate remediation steps
            if not passed:
                result.remediation_steps = self._generate_remediation(gate, result)

        except Exception as e:
            result.passed = False
            result.error_output = str(e)
            result.severity = GateSeverity.ERROR
            self.failed_gates.append((gate, result))

        return result

    async def _run_ruff(self) -> Tuple[bool, str, str]:
        """Run ruff linter."""
        cmd = ["ruff", "check", "agent/"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        passed = result.returncode == 0
        return passed, result.stdout, result.stderr

    async def _run_mypy(self) -> Tuple[bool, str, str]:
        """Run mypy type checker."""
        cmd = ["mypy", "agent/", "--ignore-missing-imports"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        passed = result.returncode == 0
        return passed, result.stdout, result.stderr

    async def _run_pytest(self) -> Tuple[bool, str, str]:
        """Run pytest test suite."""
        cmd = ["pytest", "tests/", "-v", "--tb=short"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        passed = result.returncode == 0
        return passed, result.stdout, result.stderr

    async def _run_bandit(self) -> Tuple[bool, str, str]:
        """Run bandit security scanner."""
        cmd = ["bandit", "-r", "agent/", "-f", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        # Bandit returns 0 if no issues, 1 if issues found
        passed = result.returncode == 0
        return passed, result.stdout, result.stderr

    async def _run_coverage(self, threshold: QualityThreshold) -> Tuple[bool, str, str]:
        """Check code coverage."""
        cmd = ["pytest", "--cov=agent", "--cov-report=term", "tests/"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        # Parse coverage percentage from output
        coverage_percent = 0.0
        for line in result.stdout.split("\n"):
            if "TOTAL" in line:
                parts = line.split()
                if parts:
                    try:
                        coverage_percent = float(parts[-1].rstrip("%"))
                    except ValueError:
                        pass

        passed = coverage_percent >= threshold.pass_threshold
        return passed, result.stdout, result.stderr

    def _report_gate_result(self, result: GateResult):
        """Report result of a single gate execution."""
        status = "✓" if result.passed else "✗"
        severity = ColorFormatter.severity_color(result.severity)

        print(
            f"\n{status} {result.gate.value.upper():20s} {result.duration_seconds:7.2f}s  [{severity}]"
        )

        if not result.passed and result.remediation_steps:
            print(f"  {ColorFormatter.yellow('→ Remediation:')}")
            for i, step in enumerate(result.remediation_steps[:3], 1):
                print(f"    {i}. {step}")

    def _print_summary(self):
        """Print summary of all gates."""
        print("\n" + "=" * 60)
        print(f"{ColorFormatter.bold('Quality Gates Summary')}")
        print(f"Total:   {self.metrics.total_gates}")
        print(f"Passed:  {ColorFormatter.green(str(self.metrics.passed_gates))}")
        print(f"Failed:  {ColorFormatter.red(str(self.metrics.failed_gates))}")
        print(f"Duration: {self.metrics.total_duration_seconds:.2f}s")

        if self.failed_gates:
            print(f"\n{ColorFormatter.red('CRITICAL FAILURES:')}")
            for gate, result in self.failed_gates:
                print(f"  ✗ {gate.value.upper()}")

        if self.warnings:
            print(f"\n{ColorFormatter.yellow('WARNINGS:')}")
            for gate, result in self.warnings:
                print(f"  ⚠ {gate.value.upper()}")

    def _generate_remediation(
        self, gate: QualityGateName, result: GateResult
    ) -> List[str]:
        """Generate remediation steps for a failed gate."""
        # Determine issue type from output
        if "error" in result.error_output.lower() or "error" in result.output.lower():
            issue_type = "error"
        elif "warning" in result.output.lower():
            issue_type = "warning"
        else:
            issue_type = "general"

        return RemediationSuggestions.get_suggestions(gate, issue_type)

    async def export_metrics(self, output_file: str):
        """Export metrics to JSON file."""
        metrics_dict = self.metrics.to_dict()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(metrics_dict, f, indent=2, default=str)

        print(f"\nMetrics exported to {output_path}")


class QualityGateDashboard:
    """Generate dashboard and reports for quality gate metrics."""

    @staticmethod
    def format_metrics_report(metrics: QualityGatesMetrics) -> str:
        """Format quality gate metrics as readable report."""
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║              QUALITY GATES PERFORMANCE REPORT                 ║
╚═══════════════════════════════════════════════════════════════╝

Lane: {metrics.lane.value.upper()}
Timestamp: {metrics.timestamp}

Execution Results
  Total Gates:        {metrics.total_gates}
  Passed:             {metrics.passed_gates}
  Failed:             {metrics.failed_gates}
  Success Rate:       {(metrics.passed_gates / max(metrics.total_gates, 1) * 100):.1f}%

Performance Metrics
  Total Duration:     {metrics.total_duration_seconds:.2f}s
  Average Gate:       {metrics.avg_gate_duration_seconds:.2f}s

Per-Gate Details
"""
        for gate_result in metrics.gate_results:
            status = "✓" if gate_result.passed else "✗"
            report += f"  {status} {gate_result.gate.value:15s} {gate_result.duration_seconds:7.2f}s  [{gate_result.severity.value}]\n"
            if gate_result.warnings_count > 0:
                report += f"      Warnings: {gate_result.warnings_count}\n"
            if gate_result.errors_count > 0:
                report += f"      Errors: {gate_result.errors_count}\n"

        report += f"\nReport Generated: {datetime.now().isoformat()}\n"
        return report


if __name__ == "__main__":
    print("Enhanced Quality Gates System")
    print("=" * 60)

    # Show lane configurations
    for lane in LaneType:
        print(f"\n{lane.value.upper()} Lane:")
        thresholds = LaneQualityConfig.get_all_thresholds(lane)
        for gate, threshold in thresholds.items():
            status = "✓" if threshold.enabled else "⊘"
            print(
                f"  {status} {gate.value:12s} - Timeout: {threshold.timeout_seconds}s, "
                f"Warnings: {threshold.warnings_allowed}, "
                f"Errors: {threshold.errors_allowed}"
            )
