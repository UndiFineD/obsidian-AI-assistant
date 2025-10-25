"""
Lane Selection System Enhancements for v0.1.45

Improvements:
  1. Auto-lane detection based on changed files
  2. Enhanced error messaging with remediation hints
  3. Performance metrics per lane (collected in status.json)
  4. Lane recommendation engine
  5. Lane compatibility checking

Author: @kdejo
Date: 2025-10-24
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LaneType(Enum):
    """Enumeration of available workflow lanes."""

    DOCS = "docs"
    STANDARD = "standard"
    HEAVY = "heavy"


@dataclass
class LaneConfig:
    """Configuration for a workflow lane."""

    name: str
    description: str
    stages: List[int]
    quality_gates_enabled: bool
    parallelization_enabled: bool
    code_change_check: bool
    max_duration_seconds: int
    min_duration_seconds: int = 0
    recommended_for: List[str] = None
    blocked_for: List[str] = None

    def __post_init__(self):
        if self.recommended_for is None:
            self.recommended_for = []
        if self.blocked_for is None:
            self.blocked_for = []


@dataclass
class LaneMetrics:
    """Performance metrics for a lane execution."""

    lane: str
    start_time: str
    end_time: str
    duration_seconds: float
    stages_executed: int
    stages_skipped: int
    quality_gates_passed: bool
    parallelization_used: bool
    code_changes_detected: bool
    warnings: List[str] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for JSON serialization."""
        return asdict(self)


class LaneAutoDetector:
    """Automatically detect appropriate lane based on file changes."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.git_changes = self._get_git_changes()

    def _get_git_changes(self) -> Dict[str, List[str]]:
        """Get modified, added, and deleted files from git."""
        changes = {"modified": [], "added": [], "deleted": [], "all": []}

        try:
            # Get modified files
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                changes["modified"] = (
                    result.stdout.strip().split("\n") if result.stdout else []
                )

            # Get added/untracked files
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                changes["added"] = (
                    result.stdout.strip().split("\n") if result.stdout else []
                )

            # Combine all changes
            changes["all"] = [f for f in changes["modified"] + changes["added"] if f]

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Failed to get git changes: {e}")

        return changes

    def detect_lane(self) -> Tuple[LaneType, str]:
        """
        Detect appropriate lane based on file changes.

        Returns:
            Tuple of (recommended_lane, reasoning)
        """
        if not self.git_changes["all"]:
            return LaneType.STANDARD, "No changes detected, using standard lane"

        # Categorize changes
        code_files = []
        doc_files = []
        config_files = []
        test_files = []

        for file_path in self.git_changes["all"]:
            if not file_path:
                continue

            file_lower = file_path.lower()

            # Categorize by file type
            if any(
                file_lower.endswith(ext)
                for ext in [".py", ".js", ".ts", ".jsx", ".tsx"]
            ):
                code_files.append(file_path)
            elif any(file_lower.endswith(ext) for ext in [".md", ".txt", ".rst"]):
                doc_files.append(file_path)
            elif "test" in file_lower or file_lower.endswith(".test.js"):
                test_files.append(file_path)
            elif any(
                file_lower.endswith(name)
                for name in [".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"]
            ):
                config_files.append(file_path)
            else:
                # Uncertain - treat conservatively
                code_files.append(file_path)

        # Determine lane based on file categories
        if code_files or test_files or config_files:
            # Code changes detected
            if len(code_files) > 5 or len(test_files) > 3:
                return LaneType.HEAVY, (
                    f"Multiple code/test changes detected ({len(code_files)} code, "
                    f"{len(test_files)} test files). Using heavy lane for strict validation."
                )
            else:
                return LaneType.STANDARD, (
                    f"Code changes detected ({len(code_files)} code, {len(config_files)} config). "
                    f"Using standard lane with quality gates."
                )
        elif doc_files:
            return LaneType.DOCS, (
                f"Only documentation changes detected ({len(doc_files)} files). "
                f"Using fast docs lane (<5 min)."
            )
        else:
            return (
                LaneType.STANDARD,
                "Unknown file types detected. Using standard lane.",
            )

    def is_suitable_for_lane(self, lane: LaneType) -> Tuple[bool, str]:
        """
        Check if detected changes are suitable for a specific lane.

        Returns:
            Tuple of (is_suitable, reasoning)
        """
        code_files = [
            f
            for f in self.git_changes["all"]
            if f
            and any(
                f.lower().endswith(ext) for ext in [".py", ".js", ".ts", ".jsx", ".tsx"]
            )
        ]

        if lane == LaneType.DOCS:
            if code_files:
                return (
                    False,
                    f"Code changes detected ({len(code_files)} files), docs lane not suitable",
                )
            return True, "Only documentation changes - suitable for docs lane"

        elif lane == LaneType.STANDARD:
            return True, "Standard lane suitable for all change types"

        elif lane == LaneType.HEAVY:
            if len(code_files) > 5 or len(self.git_changes["all"]) > 10:
                return True, "Large change set suitable for heavy lane validation"
            return True, "Heavy lane can be used for any change"

        return True, "Lane compatibility check passed"


class LaneErrorHandler:
    """Enhanced error handling with remediation hints for lane issues."""

    ERROR_REMEDIATION = {
        "invalid_lane": {
            "message": "Invalid lane specified",
            "remediation": [
                "Use one of: docs, standard, heavy",
                "docs: For documentation-only changes (<5 min)",
                "standard: For regular code/config changes (~15 min, default)",
                "heavy: For critical changes with strict validation (~20 min)",
            ],
        },
        "code_in_docs_lane": {
            "message": "Code changes detected but docs lane selected",
            "remediation": [
                "Switch to standard lane: --lane standard",
                "Or switch to heavy lane for strict validation: --lane heavy",
                "Run workflow with auto-detection: python scripts/workflow.py --auto-detect-lane",
            ],
        },
        "lane_not_compatible": {
            "message": "Selected lane may not be compatible with changes",
            "remediation": [
                "Check your file changes with: git diff --name-only",
                "Use auto-detect: python scripts/workflow.py --auto-detect-lane",
                "Override with --lane standard or --lane heavy if you're sure",
            ],
        },
        "stage_not_available": {
            "message": "Requested stage not available in selected lane",
            "remediation": [
                "Some stages are skipped in docs lane for speed",
                "Switch to standard lane to execute all stages",
                "Or switch to heavy lane for comprehensive validation",
            ],
        },
    }

    @classmethod
    def get_error_message(cls, error_code: str, **kwargs) -> str:
        """
        Get formatted error message with remediation steps.

        Args:
            error_code: Error type identifier
            **kwargs: Additional context for formatting

        Returns:
            Formatted error message with remediation hints
        """
        error_info = cls.ERROR_REMEDIATION.get(
            error_code,
            {
                "message": "Unknown error",
                "remediation": ["Contact @kdejo for assistance"],
            },
        )

        message = f"\n❌ ERROR: {error_info['message']}\n"

        if kwargs:
            for key, value in kwargs.items():
                message += f"   {key}: {value}\n"

        message += "\n📋 REMEDIATION STEPS:\n"
        for i, step in enumerate(error_info["remediation"], 1):
            message += f"   {i}. {step}\n"

        return message

    @classmethod
    def warn_code_in_docs_lane(
        cls, code_files: List[str], user_confirmed: bool = False
    ) -> bool:
        """
        Warn user if code changes detected in docs lane.

        Returns:
            True if user wants to continue, False to cancel
        """
        message = f"\n⚠️  WARNING: Code changes detected in docs lane\n"
        message += f"   Files: {', '.join(code_files[:3])}"
        if len(code_files) > 3:
            message += f" ... and {len(code_files) - 3} more"
        message += "\n\n"
        message += "   Docs lane skips testing and quality gates.\n"
        message += "   Consider switching to standard lane: --lane standard\n"

        if user_confirmed:
            message += "\n✓ Proceeding as confirmed.\n"
            return True

        print(message)
        response = input("Continue with docs lane? (y/N): ").strip().lower()
        return response == "y"


class LaneRecommendationEngine:
    """Recommend optimal lane based on project context and history."""

    def __init__(self, stats_file: Optional[str] = None):
        self.stats_file = stats_file or "./.workflow_stats/lane_usage.json"
        self.stats = self._load_stats()

    def _load_stats(self) -> dict:
        """Load historical lane usage and performance statistics."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "docs": {"usage_count": 0, "avg_duration": 0, "success_rate": 100},
            "standard": {"usage_count": 0, "avg_duration": 0, "success_rate": 100},
            "heavy": {"usage_count": 0, "avg_duration": 0, "success_rate": 100},
        }

    def recommend(self, detected_lane: LaneType) -> Tuple[LaneType, float]:
        """
        Recommend lane based on detection and historical performance.

        Returns:
            Tuple of (recommended_lane, confidence_score 0-1)
        """
        # Start with detected lane
        recommendation = detected_lane
        confidence = 0.7

        # Adjust based on success rates
        detected_stats = self.stats.get(detected_lane.value, {})
        if detected_stats.get("success_rate", 100) < 90:
            # If detected lane has low success rate, recommend standard
            recommendation = LaneType.STANDARD
            confidence = 0.5
        else:
            confidence = min(
                0.95, 0.7 + (detected_stats.get("success_rate", 100) - 90) / 100
            )

        return recommendation, confidence

    def update_stats(self, lane: str, duration_seconds: float, success: bool):
        """Update statistics with new lane execution data."""
        if lane not in self.stats:
            self.stats[lane] = {
                "usage_count": 0,
                "avg_duration": 0,
                "success_rate": 100,
            }

        stats = self.stats[lane]
        stats["usage_count"] += 1

        # Update average duration
        old_avg = stats["avg_duration"]
        count = stats["usage_count"]
        stats["avg_duration"] = (old_avg * (count - 1) + duration_seconds) / count

        # Update success rate
        old_success_count = int(stats.get("success_rate", 100) * (count - 1) / 100)
        new_success_count = old_success_count + (1 if success else 0)
        stats["success_rate"] = (new_success_count / count) * 100

        # Save updated stats
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)


class LanePerformanceTracker:
    """Track and analyze performance metrics for each lane."""

    def __init__(self, metrics_file: Optional[str] = None):
        self.metrics_file = metrics_file or "./.workflow_stats/lane_metrics.json"
        self.current_metrics: Optional[LaneMetrics] = None

    def start_tracking(self, lane: str):
        """Start tracking metrics for a lane execution."""
        self.current_metrics = LaneMetrics(
            lane=lane,
            start_time=datetime.now().isoformat(),
            end_time="",
            duration_seconds=0,
            stages_executed=0,
            stages_skipped=0,
            quality_gates_passed=False,
            parallelization_used=False,
            code_changes_detected=False,
        )

    def end_tracking(
        self,
        stages_executed: int,
        stages_skipped: int,
        quality_gates_passed: bool,
        parallelization_used: bool,
    ):
        """End tracking and record metrics."""
        if not self.current_metrics:
            return

        self.current_metrics.end_time = datetime.now().isoformat()
        start = datetime.fromisoformat(self.current_metrics.start_time)
        end = datetime.fromisoformat(self.current_metrics.end_time)
        self.current_metrics.duration_seconds = (end - start).total_seconds()

        self.current_metrics.stages_executed = stages_executed
        self.current_metrics.stages_skipped = stages_skipped
        self.current_metrics.quality_gates_passed = quality_gates_passed
        self.current_metrics.parallelization_used = parallelization_used

        self._save_metrics()

    def _save_metrics(self):
        """Save metrics to file."""
        if not self.current_metrics:
            return

        # Load existing metrics
        metrics_list = []
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, "r") as f:
                    metrics_list = json.load(f)
            except (json.JSONDecodeError, IOError):
                metrics_list = []

        # Append new metrics
        metrics_list.append(self.current_metrics.to_dict())

        # Keep last 100 entries
        metrics_list = metrics_list[-100:]

        # Save
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        with open(self.metrics_file, "w") as f:
            json.dump(metrics_list, f, indent=2)

    def get_lane_stats(self, lane: str) -> dict:
        """Get aggregated statistics for a lane."""
        if not os.path.exists(self.metrics_file):
            return {}

        try:
            with open(self.metrics_file, "r") as f:
                all_metrics = json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

        lane_metrics = [m for m in all_metrics if m.get("lane") == lane]
        if not lane_metrics:
            return {}

        durations = [m.get("duration_seconds", 0) for m in lane_metrics]
        quality_passes = sum(1 for m in lane_metrics if m.get("quality_gates_passed"))

        return {
            "executions": len(lane_metrics),
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "quality_gate_pass_rate": (quality_passes / len(lane_metrics)) * 100,
        }


# Enhanced lane configuration with better structure
ENHANCED_LANE_CONFIG: Dict[str, LaneConfig] = {
    "docs": LaneConfig(
        name="Documentation-Only Lane",
        description="Fast docs-only workflow (<5 min)",
        stages=[0, 1, 2, 3, 4, 5, 7, 9, 10, 12],
        quality_gates_enabled=False,
        parallelization_enabled=False,
        code_change_check=True,
        max_duration_seconds=300,
        min_duration_seconds=60,
        recommended_for=["*.md", "*.rst", "*.txt", "docs/"],
        blocked_for=["*.py", "*.js", "*.ts"],
    ),
    "standard": LaneConfig(
        name="Standard Lane",
        description="Standard workflow with basic validation (~15 min)",
        stages=list(range(0, 13)),
        quality_gates_enabled=True,
        parallelization_enabled=True,
        code_change_check=False,
        max_duration_seconds=900,
        min_duration_seconds=300,
        recommended_for=["*.py", "*.js", "*.json", "*.yaml"],
        blocked_for=[],
    ),
    "heavy": LaneConfig(
        name="Heavy Lane",
        description="Strict validation workflow (~20 min)",
        stages=list(range(0, 13)),
        quality_gates_enabled=True,
        parallelization_enabled=True,
        code_change_check=False,
        max_duration_seconds=1200,
        min_duration_seconds=600,
        recommended_for=["scripts/", "agent/", "critical/"],
        blocked_for=[],
    ),
}


if __name__ == "__main__":
    # Example usage
    print("Lane Selection Enhancements Module")
    print("=" * 50)

    # Test auto-detection
    detector = LaneAutoDetector(".")
    detected_lane, reasoning = detector.detect_lane()
    print(f"\n🎯 Detected Lane: {detected_lane.value}")
    print(f"   Reasoning: {reasoning}")

    # Check suitability for each lane
    for lane_type in LaneType:
        suitable, reason = detector.is_suitable_for_lane(lane_type)
        status = "✓" if suitable else "✗"
        print(f"   {status} {lane_type.value}: {reason}")

    # Test recommendation engine
    rec_engine = LaneRecommendationEngine()
    recommended_lane, confidence = rec_engine.recommend(detected_lane)
    print(
        f"\n💡 Recommended Lane: {recommended_lane.value} (confidence: {confidence:.1%})"
    )

    # Test error handling
    print(
        f"\n{LaneErrorHandler.get_error_message('code_in_docs_lane', files='app.py, config.yaml')}"
    )
