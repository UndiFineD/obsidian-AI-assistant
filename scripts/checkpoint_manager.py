#!/usr/bin/env python3
"""
Checkpoint and Rollback System for OpenSpec Workflow

Provides automatic state snapshots before each step execution, allowing users to
rollback to previous checkpoints if a step fails or produces unexpected results.

Key Features:
- Automatic checkpoint creation before each step
- File-level snapshots with minimal storage overhead
- Easy rollback to any previous checkpoint
- State preservation across workflow runs
- Checkpoint listing and inspection

Author: Obsidian AI Agent Team
License: MIT
"""

import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class CheckpointMetadata:
    """Metadata for a workflow checkpoint."""

    checkpoint_id: str  # Format: checkpoint-YYYYMMDD-HHMMSS-step{N}
    step_num: int
    step_name: str
    timestamp: str  # ISO 8601 format
    files_snapshot: List[str]  # List of files in change directory
    git_commit: Optional[str] = None  # Git commit hash if available
    notes: str = ""


@dataclass
class CheckpointState:
    """Complete state of all checkpoints for a change."""

    change_id: str
    checkpoints: List[CheckpointMetadata] = field(default_factory=list)
    last_successful_step: int = -1

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "change_id": self.change_id,
            "checkpoints": [asdict(cp) for cp in self.checkpoints],
            "last_successful_step": self.last_successful_step,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CheckpointState":
        """Create from dictionary (JSON deserialization)."""
        checkpoints = [CheckpointMetadata(**cp) for cp in data.get("checkpoints", [])]
        return cls(
            change_id=data["change_id"],
            checkpoints=checkpoints,
            last_successful_step=data.get("last_successful_step", -1),
        )


class CheckpointManager:
    """
    Manages checkpoints for workflow state recovery.

    Checkpoints are stored in: openspec/changes/<change-id>/.checkpoints/
    - checkpoint-YYYYMMDD-HHMMSS-step{N}/ (snapshot directories)
    - state.json (checkpoint metadata)
    """

    def __init__(self, change_path):
        """
        Initialize checkpoint manager for a change.

        Args:
            change_path: Path to change directory (str or Path)
        """
        self.change_path = (
            Path(change_path) if not isinstance(change_path, Path) else change_path
        )
        self.checkpoints_dir = self.change_path / ".checkpoints"
        self.state_file = self.checkpoints_dir / "state.json"
        self.state: Optional[CheckpointState] = None

        # Ensure checkpoints directory exists
        self.checkpoints_dir.mkdir(exist_ok=True)

        # Load existing state
        self._load_state()

    def _load_state(self) -> None:
        """Load checkpoint state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.state = CheckpointState.from_dict(data)
            except Exception as e:
                print(f"Warning: Could not load checkpoint state: {e}")
                self.state = CheckpointState(change_id=self.change_path.name)
        else:
            self.state = CheckpointState(change_id=self.change_path.name)

    def _save_state(self) -> None:
        """Save checkpoint state to disk."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save checkpoint state: {e}")

    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash if in a git repository."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.change_path.parent.parent,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _list_files(self) -> List[str]:
        """List all non-checkpoint files in change directory."""
        files = []
        for item in self.change_path.iterdir():
            if item.name == ".checkpoints":
                continue
            if item.is_file():
                files.append(item.name)
        return sorted(files)

    def _generate_checkpoint_id(self, step_num: int) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return f"checkpoint-{timestamp}-step{step_num:02d}"

    def create_checkpoint(self, step_num: int, step_name: str, notes: str = "") -> str:
        """
        Create a checkpoint before executing a step.

        Args:
            step_num: Step number being executed
            step_name: Human-readable step name
            notes: Optional notes about this checkpoint

        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id(step_num)
        checkpoint_dir = self.checkpoints_dir / checkpoint_id
        checkpoint_dir.mkdir(exist_ok=True)

        # Snapshot all files in change directory
        files = self._list_files()
        for filename in files:
            src = self.change_path / filename
            dst = checkpoint_dir / filename
            shutil.copy2(src, dst)

        # Create checkpoint metadata
        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            step_num=step_num,
            step_name=step_name,
            timestamp=datetime.utcnow().isoformat(),
            files_snapshot=files,
            git_commit=self._get_git_commit(),
            notes=notes,
        )

        # Update state
        self.state.checkpoints.append(metadata)
        self._save_state()

        return checkpoint_id

    def mark_step_success(self, step_num: int) -> None:
        """Mark a step as successfully completed."""
        if step_num > self.state.last_successful_step:
            self.state.last_successful_step = step_num
            self._save_state()

    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Rollback change directory to a specific checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            True if successful, False otherwise
        """
        # Find checkpoint
        checkpoint = None
        for cp in self.state.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                checkpoint = cp
                break

        if not checkpoint:
            print(f"Error: Checkpoint '{checkpoint_id}' not found")
            return False

        checkpoint_dir = self.checkpoints_dir / checkpoint_id
        if not checkpoint_dir.exists():
            print(f"Error: Checkpoint directory not found: {checkpoint_dir}")
            return False

        # Create backup of current state (before rollback)
        backup_id = self._generate_checkpoint_id(
            99
        )  # Special step number for rollback backups
        backup_dir = self.checkpoints_dir / backup_id
        backup_dir.mkdir(exist_ok=True)

        current_files = self._list_files()
        for filename in current_files:
            src = self.change_path / filename
            dst = backup_dir / filename
            shutil.copy2(src, dst)

        # Rollback: Delete current files and restore from checkpoint
        for filename in current_files:
            (self.change_path / filename).unlink()

        for filename in checkpoint.files_snapshot:
            src = checkpoint_dir / filename
            dst = self.change_path / filename
            if src.exists():
                shutil.copy2(src, dst)

        # Update state
        self.state.last_successful_step = checkpoint.step_num - 1
        self._save_state()

        print(f"✓ Rolled back to checkpoint: {checkpoint_id}")
        print(f"  Step: {checkpoint.step_num} - {checkpoint.step_name}")
        print(f"  Time: {checkpoint.timestamp}")
        print(f"✓ Created backup of current state: {backup_id}")

        return True

    def list_checkpoints(self) -> List[CheckpointMetadata]:
        """Get list of all checkpoints."""
        return self.state.checkpoints

    def get_latest_checkpoint(self) -> Optional[CheckpointMetadata]:
        """Get the most recent checkpoint."""
        if self.state.checkpoints:
            return self.state.checkpoints[-1]
        return None

    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Get checkpoint by ID."""
        for cp in self.state.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                return cp
        return None

    def get_last_successful_step(self) -> int:
        """Get the last successfully completed step number."""
        return self.state.last_successful_step

    def cleanup_old_checkpoints(self, keep_count: int = 10) -> int:
        """
        Remove old checkpoints, keeping only the most recent ones.

        Args:
            keep_count: Number of recent checkpoints to keep

        Returns:
            Number of checkpoints removed
        """
        if len(self.state.checkpoints) <= keep_count:
            return 0

        # Sort by timestamp (oldest first)
        sorted_cps = sorted(self.state.checkpoints, key=lambda cp: cp.timestamp)

        # Determine which to remove
        to_remove = sorted_cps[:-keep_count]
        removed_count = 0

        for cp in to_remove:
            checkpoint_dir = self.checkpoints_dir / cp.checkpoint_id
            if checkpoint_dir.exists():
                shutil.rmtree(checkpoint_dir)
                removed_count += 1

            # Remove from state
            self.state.checkpoints.remove(cp)

        self._save_state()
        return removed_count


def format_checkpoint_list(checkpoints: List[CheckpointMetadata]) -> str:
    """Format checkpoint list for display."""
    if not checkpoints:
        return "No checkpoints found."

    lines = []
    lines.append("\nAvailable Checkpoints:")
    lines.append("=" * 80)

    for i, cp in enumerate(checkpoints, 1):
        # Parse timestamp for readable format
        try:
            dt = datetime.fromisoformat(cp.timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            time_str = cp.timestamp

        lines.append(f"\n{i}. Checkpoint: {cp.checkpoint_id}")
        lines.append(f"   Step: {cp.step_num} - {cp.step_name}")
        lines.append(f"   Time: {time_str}")
        lines.append(
            f"   Files: {len(cp.files_snapshot)} file(s) - {', '.join(cp.files_snapshot[:5])}"
        )
        if len(cp.files_snapshot) > 5:
            lines.append(f"          ... and {len(cp.files_snapshot) - 5} more")
        if cp.notes:
            lines.append(f"   Notes: {cp.notes}")
        if cp.git_commit:
            lines.append(f"   Git: {cp.git_commit[:8]}")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)
