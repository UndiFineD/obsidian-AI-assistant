#!/usr/bin/env python3
"""
Status Tracking Module - Workflow State Persistence

Tracks workflow progress with atomic status.json updates at each stage.
Records timing, metrics, and results for workflow resumption and monitoring.

Status JSON Structure:
{
  "workflow_id": "unique-change-id",
  "stage": 8,
  "lane": "standard",
  "status": "RUNNING|COMPLETED|FAILED",
  "started_at": "2025-10-26T10:30:00",
  "updated_at": "2025-10-26T10:35:00",
  "stages": [
    {
      "stage_num": 0,
      "name": "Create TODOs",
      "status": "COMPLETED",
      "started_at": "2025-10-26T10:30:00",
      "completed_at": "2025-10-26T10:30:05",
      "duration_seconds": 5,
      "metrics": {}
    },
    ...
  ],
  "timing": {
    "total_elapsed_seconds": 125,
    "estimated_remaining_seconds": 300,
    "sla_target_seconds": 900,
    "within_sla": true
  },
  "metrics": {
    "files_modified": 5,
    "files_created": 2,
    "tests_passed": 45,
    "tests_failed": 0,
    "coverage_percent": 87
  }
}
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class StageStatus(Enum):
    """Stage execution status"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class StageInfo:
    """Information about a single workflow stage"""

    stage_num: int
    name: str
    status: str = StageStatus.PENDING.value
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

    def to_dict(self) -> Dict:
        return {
            "stage_num": self.stage_num,
            "name": self.name,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
        }


class StatusTracker:
    """Track and persist workflow status across stages"""

    # SLA targets per lane (in seconds)
    SLA_TARGETS = {
        "docs": 300,  # 5 minutes
        "standard": 900,  # 15 minutes
        "heavy": 1200,  # 20 minutes
    }

    def __init__(
        self,
        workflow_id: str,
        lane: str = "standard",
        status_file: Optional[Path] = None,
    ):
        """
        Initialize status tracker.

        Args:
            workflow_id: Unique workflow identifier (change-id)
            lane: Workflow lane (docs, standard, heavy)
            status_file: Path to status.json file (default: .checkpoints/status.json)
        """
        self.workflow_id = workflow_id
        self.lane = lane
        self.status_file = status_file or Path.cwd() / ".checkpoints" / "status.json"

        # Initialize or load existing status
        self.status = self._load_or_create_status()

    def _load_or_create_status(self) -> Dict[str, Any]:
        """Load existing status or create new one"""
        if self.status_file.exists():
            try:
                return json.loads(self.status_file.read_text(encoding="utf-8"))
            except Exception:
                pass  # Fall through to create new

        # Create new status
        return {
            "workflow_id": self.workflow_id,
            "lane": self.lane,
            "status": "RUNNING",
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "stages": [],
            "timing": {
                "total_elapsed_seconds": 0,
                "estimated_remaining_seconds": 0,
                "sla_target_seconds": self.SLA_TARGETS.get(self.lane, 900),
                "within_sla": True,
            },
            "metrics": {
                "files_modified": 0,
                "files_created": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "coverage_percent": 0,
            },
        }

    def start_stage(self, stage_num: int, stage_name: str) -> None:
        """Record stage start"""
        now = datetime.now().isoformat()

        # Find or create stage entry
        stage_entry = None
        for stage in self.status["stages"]:
            if stage["stage_num"] == stage_num:
                stage_entry = stage
                break

        if stage_entry is None:
            stage_entry = {
                "stage_num": stage_num,
                "name": stage_name,
                "status": StageStatus.PENDING.value,
                "started_at": None,
                "completed_at": None,
                "duration_seconds": 0.0,
                "metrics": {},
            }
            self.status["stages"].append(stage_entry)

        stage_entry["status"] = StageStatus.RUNNING.value
        stage_entry["started_at"] = now
        self.status["updated_at"] = now

        self._save_status()

    def complete_stage(
        self,
        stage_num: int,
        success: bool = True,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record stage completion"""
        now = datetime.now().isoformat()

        # Find stage entry
        for stage in self.status["stages"]:
            if stage["stage_num"] == stage_num:
                stage["status"] = (
                    StageStatus.COMPLETED.value if success else StageStatus.FAILED.value
                )
                stage["completed_at"] = now

                # Calculate duration
                if stage.get("started_at"):
                    start = datetime.fromisoformat(stage["started_at"])
                    end = datetime.fromisoformat(now)
                    stage["duration_seconds"] = (end - start).total_seconds()

                # Add metrics
                if metrics:
                    stage["metrics"] = metrics

                break

        self.status["status"] = "FAILED" if not success else "RUNNING"
        self.status["updated_at"] = now
        self._update_timing()
        self._save_status()

    def skip_stage(
        self, stage_num: int, stage_name: str, reason: str = "Not applicable for lane"
    ) -> None:
        """Record stage skip"""
        now = datetime.now().isoformat()

        # Find or create stage entry
        stage_entry = None
        for stage in self.status["stages"]:
            if stage["stage_num"] == stage_num:
                stage_entry = stage
                break

        if stage_entry is None:
            stage_entry = {
                "stage_num": stage_num,
                "name": stage_name,
                "status": StageStatus.SKIPPED.value,
                "started_at": now,
                "completed_at": now,
                "duration_seconds": 0.0,
                "metrics": {"reason": reason},
            }
            self.status["stages"].append(stage_entry)
        else:
            stage_entry["status"] = StageStatus.SKIPPED.value
            stage_entry["metrics"]["reason"] = reason

        self.status["updated_at"] = now
        self._save_status()

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update overall workflow metrics"""
        self.status["metrics"].update(metrics)
        self.status["updated_at"] = datetime.now().isoformat()
        self._update_timing()
        self._save_status()

    def _update_timing(self) -> None:
        """Update timing information"""
        start = datetime.fromisoformat(self.status["started_at"])
        now = datetime.now()
        elapsed = (now - start).total_seconds()

        self.status["timing"]["total_elapsed_seconds"] = elapsed

        # Calculate SLA metrics
        sla_target = self.status["timing"]["sla_target_seconds"]
        self.status["timing"]["within_sla"] = elapsed <= sla_target

        # Estimate remaining time (simple linear extrapolation)
        completed_stages = sum(
            1
            for s in self.status["stages"]
            if s["status"]
            in (
                StageStatus.COMPLETED.value,
                StageStatus.FAILED.value,
                StageStatus.SKIPPED.value,
            )
        )
        total_stages = 13  # Total workflow stages
        if completed_stages > 0:
            avg_time_per_stage = elapsed / completed_stages
            remaining_stages = total_stages - completed_stages
            self.status["timing"]["estimated_remaining_seconds"] = (
                avg_time_per_stage * remaining_stages
            )
        else:
            self.status["timing"]["estimated_remaining_seconds"] = sla_target - elapsed

    def complete_workflow(self, success: bool = True) -> None:
        """Mark workflow as completed"""
        self.status["status"] = "COMPLETED" if success else "FAILED"
        self.status["updated_at"] = datetime.now().isoformat()
        self._update_timing()
        self._save_status()

    def _save_status(self) -> None:
        """Save status to JSON file (atomic write)"""
        # Create directory if needed
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first
        temp_file = self.status_file.with_suffix(".tmp")
        try:
            temp_file.write_text(
                json.dumps(self.status, indent=2),
                encoding="utf-8",
            )
            # Atomic rename
            temp_file.replace(self.status_file)
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise RuntimeError(f"Failed to save status: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get human-readable summary"""
        stages_completed = sum(
            1
            for s in self.status["stages"]
            if s["status"] in (StageStatus.COMPLETED.value, StageStatus.FAILED.value)
        )
        stages_total = len(self.status["stages"])

        elapsed = self.status["timing"]["total_elapsed_seconds"]
        remaining = self.status["timing"]["estimated_remaining_seconds"]
        sla = self.status["timing"]["sla_target_seconds"]

        return {
            "workflow_id": self.workflow_id,
            "status": self.status["status"],
            "lane": self.lane,
            "stages": f"{stages_completed}/{stages_total} completed",
            "elapsed_seconds": elapsed,
            "elapsed_formatted": self._format_duration(elapsed),
            "remaining_formatted": self._format_duration(remaining),
            "sla_status": "✅ On SLA"
            if self.status["timing"]["within_sla"]
            else "⚠️ Behind SLA",
            "sla_target": self._format_duration(sla),
        }

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format seconds as human-readable duration"""
        if seconds < 0:
            seconds = 0
        delta = timedelta(seconds=int(seconds))
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours > 0:
            parts.append(f"{int(hours)}h")
        if minutes > 0:
            parts.append(f"{int(minutes)}m")
        if seconds > 0 or not parts:
            parts.append(f"{int(seconds)}s")

        return " ".join(parts)


def create_tracker(
    workflow_id: str,
    lane: str = "standard",
    status_file: Optional[Path] = None,
) -> StatusTracker:
    """Factory function to create a status tracker"""
    return StatusTracker(workflow_id, lane, status_file)


if __name__ == "__main__":
    # Example usage
    tracker = create_tracker("test-workflow", "standard")

    # Simulate workflow
    tracker.start_stage(0, "Create TODOs")
    tracker.complete_stage(0, success=True, metrics={"todos_created": 5})

    tracker.start_stage(1, "Version Bump")
    tracker.complete_stage(1, success=True, metrics={"version": "0.1.44"})

    tracker.skip_stage(2, "Skip Example", "Not applicable")

    tracker.start_stage(3, "Some Task")
    tracker.complete_stage(3, success=True)

    tracker.update_metrics(
        {
            "files_modified": 3,
            "files_created": 2,
        }
    )

    # Print summary
    summary = tracker.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
