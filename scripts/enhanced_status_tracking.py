#!/usr/bin/env python3
"""
Enhanced Status Tracking System for OpenSpec Workflow

Provides timeline visualization, improved resumption logic, and checkpoint cleanup
policies for the workflow execution pipeline.

Key Features:
    - Timeline visualization with ASCII art and timestamps
    - Improved resumption logic with state recovery
    - Checkpoint cleanup policies (retention, archival)
    - Performance metrics per stage
    - Execution history tracking
    - JSON state persistence with atomic writes

Classes:
    EnhancedStatusTracker: Main status tracking coordinator
    TimelineVisualizer: ASCII timeline rendering
    CheckpointManager: Checkpoint lifecycle management
    ExecutionHistory: Historical execution tracking

Usage:
    tracker = EnhancedStatusTracker(change_id="my-change")
    tracker.mark_stage_start(2, "Generate Docs")
    tracker.mark_stage_complete(2, {"files_generated": 5})
    timeline = tracker.visualize_timeline()
    print(timeline)

Author: Obsidian AI Agent Team
License: MIT
Version: 0.1.45
"""

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class StageExecution:
    """Represents a single stage execution."""

    stage_num: int
    stage_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: str = "running"  # running, completed, failed, skipped
    metrics: Dict[str, Any] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ExecutionSnapshot:
    """Represents a complete execution snapshot."""

    change_id: str
    execution_id: str
    lane: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    status: str = "in-progress"  # in-progress, completed, failed, resumed
    stages: List[StageExecution] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.stages is None:
            self.stages = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["stages"] = [
            s.to_dict() if isinstance(s, StageExecution) else s for s in data["stages"]
        ]
        return data


class TimelineVisualizer:
    """Visualizes workflow execution timeline."""

    COLORS = {
        "completed": "\033[92m",  # Green
        "running": "\033[93m",  # Yellow
        "failed": "\033[91m",  # Red
        "skipped": "\033[94m",  # Blue
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    def __init__(self, use_colors: bool = True):
        """
        Initialize timeline visualizer.

        Args:
            use_colors: Whether to use ANSI color codes
        """
        self.use_colors = use_colors

    def _color(self, text: str, color_name: str) -> str:
        """Apply color to text if colors enabled."""
        if not self.use_colors:
            return text
        color = self.COLORS.get(color_name, "")
        reset = self.COLORS["reset"]
        return f"{color}{text}{reset}"

    def visualize_stages(
        self, stages: List[StageExecution], max_width: int = 80
    ) -> str:
        """
        Create ASCII visualization of stages.

        Args:
            stages: List of stage executions
            max_width: Maximum line width

        Returns:
            ASCII art timeline
        """
        lines = []
        lines.append(self._color("═" * max_width, "bold"))
        lines.append(self._color("WORKFLOW EXECUTION TIMELINE", "bold"))
        lines.append(self._color("═" * max_width, "bold"))
        lines.append("")

        # Find max duration for scaling
        max_duration = max((s.duration or 0) for s in stages) or 1

        for stage in stages:
            status = stage.status
            duration = stage.duration or 0

            # Build stage line
            status_symbol = self._get_status_symbol(status)
            status_text = self._color(f"[{status_symbol}]", status)

            # Progress bar
            if duration > 0:
                bar_width = int((duration / max_duration) * 30)
                bar = "█" * bar_width + "░" * (30 - bar_width)
            else:
                bar = "░" * 30

            stage_line = (
                f"{status_text} Stage {stage.stage_num:2d}: {stage.stage_name:30s} "
                f"{bar} {duration:6.2f}s"
            )
            lines.append(stage_line)

            # Metrics if present
            if stage.metrics:
                metrics_str = ", ".join(f"{k}={v}" for k, v in stage.metrics.items())
                lines.append(f"              └─ {metrics_str}")

        lines.append("")
        lines.append(self._color("═" * max_width, "bold"))
        return "\n".join(lines)

    def visualize_timeline_compact(self, stages: List[StageExecution]) -> str:
        """
        Create compact single-line timeline.

        Args:
            stages: List of stage executions

        Returns:
            Compact timeline string
        """
        timeline = []
        for stage in stages:
            symbol = self._get_status_symbol(stage.status)
            colored_symbol = self._color(symbol, stage.status)
            timeline.append(colored_symbol)

        return f"Timeline: {' → '.join(timeline)}"

    @staticmethod
    def _get_status_symbol(status: str) -> str:
        """Get symbol for status."""
        symbols = {
            "completed": "✓",
            "running": "→",
            "failed": "✗",
            "skipped": "⊘",
        }
        return symbols.get(status, "?")


class CheckpointManager:
    """Manages checkpoint lifecycle (creation, cleanup, archival)."""

    def __init__(
        self,
        checkpoint_dir: Path,
        retention_days: int = 7,
        archive_dir: Optional[Path] = None,
    ):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory for active checkpoints
            retention_days: Days to keep checkpoints before cleanup
            archive_dir: Optional directory for archived checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.retention_days = retention_days
        self.archive_dir = Path(archive_dir) if archive_dir else None

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        if self.archive_dir:
            self.archive_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(
        self, change_id: str, execution_id: str, data: Dict[str, Any]
    ) -> Path:
        """
        Create a new checkpoint.

        Args:
            change_id: Change identifier
            execution_id: Execution identifier
            data: Checkpoint data to save

        Returns:
            Path to created checkpoint
        """
        checkpoint_file = self.checkpoint_dir / f"{change_id}_{execution_id}.json"

        checkpoint_data = {
            "change_id": change_id,
            "execution_id": execution_id,
            "created_at": datetime.now().isoformat(),
            "data": data,
        }

        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

        return checkpoint_file

    def load_checkpoint(self, checkpoint_file: Path) -> Dict[str, Any]:
        """Load checkpoint data."""
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_file}")

        with open(checkpoint_file, "r") as f:
            return json.load(f)

    def cleanup_old_checkpoints(self, dry_run: bool = False) -> Tuple[int, int]:
        """
        Clean up old checkpoints.

        Args:
            dry_run: If True, don't actually delete, just report

        Returns:
            Tuple of (deleted_count, archived_count)
        """
        deleted_count = 0
        archived_count = 0

        cutoff_time = time.time() - (self.retention_days * 86400)

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            if checkpoint_file.stat().st_mtime < cutoff_time:
                if self.archive_dir:
                    # Archive instead of delete
                    archive_path = self.archive_dir / checkpoint_file.name
                    if not dry_run:
                        checkpoint_file.rename(archive_path)
                    archived_count += 1
                else:
                    # Delete
                    if not dry_run:
                        checkpoint_file.unlink()
                    deleted_count += 1

        return deleted_count, archived_count


class EnhancedStatusTracker:
    """Enhanced status tracking with timeline, resumption, and cleanup."""

    def __init__(
        self, change_id: str, lane: str = "standard", status_dir: Optional[Path] = None
    ):
        """
        Initialize enhanced status tracker.

        Args:
            change_id: Change identifier
            lane: Workflow lane (docs, standard, heavy)
            status_dir: Directory for status files (default: .workflow_state/)
        """
        self.change_id = change_id
        self.lane = lane
        self.status_dir = Path(status_dir or ".workflow_state")
        self.status_dir.mkdir(parents=True, exist_ok=True)

        # Generate execution ID
        self.execution_id = self._generate_execution_id()

        # Initialize snapshot
        self.snapshot = ExecutionSnapshot(
            change_id=change_id,
            execution_id=self.execution_id,
            lane=lane,
            start_time=time.time(),
            metadata={"hostname": os.getenv("HOSTNAME", "unknown")},
        )

        # Visualizer and checkpoint manager
        self.visualizer = TimelineVisualizer(use_colors=True)
        self.checkpoint_manager = CheckpointManager(
            self.status_dir / "checkpoints",
            retention_days=7,
            archive_dir=self.status_dir / "archive",
        )

    @staticmethod
    def _generate_execution_id() -> str:
        """Generate unique execution ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}{os.getpid()}".encode()
        return hashlib.md5(hash_input).hexdigest()[:8]

    def mark_stage_start(self, stage_num: int, stage_name: str) -> None:
        """Mark stage as started."""
        execution = StageExecution(
            stage_num=stage_num,
            stage_name=stage_name,
            start_time=time.time(),
            status="running",
        )
        self.snapshot.stages.append(execution)
        self._save_state()

    def mark_stage_complete(
        self,
        stage_num: int,
        metrics: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Mark stage as complete."""
        # Find stage
        stage = next(
            (s for s in self.snapshot.stages if s.stage_num == stage_num), None
        )

        if stage:
            stage.end_time = time.time()
            stage.duration = stage.end_time - stage.start_time
            stage.status = "failed" if error else "completed"
            stage.metrics = metrics or {}
            stage.error_message = error
            self._save_state()

    def mark_stage_skipped(self, stage_num: int, reason: str) -> None:
        """Mark stage as skipped."""
        stage = next(
            (s for s in self.snapshot.stages if s.stage_num == stage_num), None
        )

        if stage:
            stage.status = "skipped"
            stage.end_time = stage.start_time  # No duration
            stage.duration = 0
            stage.metrics = {"reason": reason}
            self._save_state()

    def get_timeline_visualization(self) -> str:
        """Get timeline visualization."""
        return self.visualizer.visualize_stages(self.snapshot.stages)

    def get_compact_timeline(self) -> str:
        """Get compact timeline."""
        return self.visualizer.visualize_timeline_compact(self.snapshot.stages)

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        completed = [s for s in self.snapshot.stages if s.status == "completed"]
        failed = [s for s in self.snapshot.stages if s.status == "failed"]
        skipped = [s for s in self.snapshot.stages if s.status == "skipped"]

        total_duration = sum(s.duration or 0 for s in self.snapshot.stages)

        return {
            "total_stages": len(self.snapshot.stages),
            "completed": len(completed),
            "failed": len(failed),
            "skipped": len(skipped),
            "total_duration": total_duration,
            "average_stage_duration": (
                total_duration / len(completed) if completed else 0
            ),
            "success_rate": (
                len(completed) / len(self.snapshot.stages) * 100
                if self.snapshot.stages
                else 0
            ),
        }

    def can_resume(self) -> bool:
        """Check if execution can be resumed."""
        if not self.snapshot.stages:
            return False

        # Can resume if last stage is not completed
        last_stage = self.snapshot.stages[-1]
        return last_stage.status in ("running", "failed")

    def get_resume_point(self) -> Optional[int]:
        """Get stage number to resume from."""
        if not self.can_resume():
            return None

        # Resume from first non-completed stage
        for stage in self.snapshot.stages:
            if stage.status != "completed":
                return stage.stage_num

        return None

    def create_checkpoint(self) -> Path:
        """Create checkpoint for current state."""
        checkpoint_data = {
            "snapshot": self.snapshot.to_dict(),
            "statistics": self.get_statistics(),
        }

        return self.checkpoint_manager.create_checkpoint(
            self.change_id, self.execution_id, checkpoint_data
        )

    def cleanup_checkpoints(self, dry_run: bool = False) -> Dict[str, int]:
        """Clean up old checkpoints."""
        deleted, archived = self.checkpoint_manager.cleanup_old_checkpoints(dry_run)
        return {"deleted": deleted, "archived": archived}

    def _save_state(self) -> None:
        """Save current state to file."""
        state_file = self.status_dir / f"{self.change_id}_status.json"

        state_data = {
            "execution_id": self.execution_id,
            "change_id": self.change_id,
            "lane": self.lane,
            "snapshot": self.snapshot.to_dict(),
            "statistics": self.get_statistics(),
            "saved_at": datetime.now().isoformat(),
        }

        # Atomic write
        temp_file = state_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(state_data, f, indent=2)
        temp_file.replace(state_file)

    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load state from file."""
        state_file = self.status_dir / f"{self.change_id}_status.json"

        if not state_file.exists():
            return None

        with open(state_file, "r") as f:
            return json.load(f)


class ExecutionHistory:
    """Tracks execution history for analytics and learning."""

    def __init__(self, history_dir: Path):
        """
        Initialize execution history.

        Args:
            history_dir: Directory for history files
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def record_execution(self, snapshot: ExecutionSnapshot) -> Path:
        """
        Record execution for history.

        Args:
            snapshot: Execution snapshot to record

        Returns:
            Path to history file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = (
            self.history_dir
            / f"{snapshot.change_id}_{timestamp}_{snapshot.execution_id}.json"
        )

        with open(history_file, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2)

        return history_file

    def get_execution_trends(
        self, change_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trends for a specific change.

        Args:
            change_id: Change identifier
            limit: Maximum number of executions to return

        Returns:
            List of execution summaries
        """
        files = sorted(self.history_dir.glob(f"{change_id}_*.json"), reverse=True)[
            :limit
        ]

        trends = []
        for history_file in files:
            with open(history_file, "r") as f:
                data = json.load(f)

                total_duration = sum(
                    (s["duration"] or 0) for s in data.get("stages", [])
                )

                trends.append(
                    {
                        "execution_id": data["execution_id"],
                        "timestamp": data["start_time"],
                        "total_duration": total_duration,
                        "stage_count": len(data.get("stages", [])),
                        "success": all(
                            s["status"] in ("completed", "skipped")
                            for s in data.get("stages", [])
                        ),
                    }
                )

        return trends


if __name__ == "__main__":
    # Example usage
    tracker = EnhancedStatusTracker("test-change", lane="standard")

    # Simulate workflow execution
    tracker.mark_stage_start(0, "Setup")
    time.sleep(0.1)
    tracker.mark_stage_complete(0, {"time": 0.1})

    tracker.mark_stage_start(1, "Generate Docs")
    time.sleep(0.2)
    tracker.mark_stage_complete(1, {"files": 5, "lines": 1000})

    tracker.mark_stage_start(2, "Run Tests")
    time.sleep(0.05)
    tracker.mark_stage_complete(2, {"passed": 45, "failed": 0})

    # Display timeline
    print(tracker.get_timeline_visualization())
    print()
    print(tracker.get_compact_timeline())
    print()

    # Display statistics
    stats = tracker.get_statistics()
    print("Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Create checkpoint
    checkpoint_path = tracker.create_checkpoint()
    print(f"\nCheckpoint created: {checkpoint_path}")
