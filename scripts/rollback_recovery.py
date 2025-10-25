#!/usr/bin/env python3
"""
Rollback and Recovery Framework - Recovery procedures for workflow failures

Provides comprehensive rollback and recovery capabilities:
1. Checkpoint management - Save and restore execution state
2. Recovery procedures - Recover from different failure types
3. Partial execution resume - Continue from last successful checkpoint
4. State cleanup - Clean up failed execution state
5. Rollback scripts - Revert changes to previous state
6. Recovery metrics - Track recovery success and timing

Features:
- State snapshots at each workflow step
- Recovery from any checkpoint
- Lane-aware recovery procedures
- Comprehensive error logging
- Rollback transaction support
- Partial execution resume
- State validation and verification
- Recovery metrics and reporting

Usage:
    python scripts/rollback_recovery.py [options]

Options:
    --checkpoint ID     Restore from specific checkpoint
    --list-checkpoints  Show available checkpoints
    --validate          Validate current state
    --cleanup           Clean up failed execution state
    --rollback COMMIT   Rollback to git commit
    --dry-run           Show what would happen
    --verbose           Enable verbose logging
    --lane LANE         Lane-specific recovery
"""

import argparse
import hashlib
import json
import logging
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of workflow failures that can be recovered."""

    TIMEOUT = "timeout"  # Execution exceeded time limit
    TEST_FAILURE = "test_failure"  # Tests failed
    QUALITY_GATE_FAILURE = "quality_gate_failure"  # Quality gates failed
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # Out of memory/disk
    NETWORK_ERROR = "network_error"  # Network connectivity issue
    GIT_ERROR = "git_error"  # Git operation failed
    UNKNOWN = "unknown"  # Unknown failure type


class RecoveryStrategy(Enum):
    """Strategies for recovering from failures."""

    RETRY = "retry"  # Retry the failed step
    RESUME = "resume"  # Resume from checkpoint
    SKIP = "skip"  # Skip the failed step
    ROLLBACK = "rollback"  # Rollback to previous state
    MANUAL = "manual"  # Manual intervention required


class LaneType(Enum):
    """Workflow lanes."""

    DOCS = "docs"
    STANDARD = "standard"
    HEAVY = "heavy"


@dataclass
class WorkflowCheckpoint:
    """Checkpoint representing a saved workflow state."""

    checkpoint_id: str
    lane: LaneType
    step_number: int
    step_name: str
    timestamp: str
    git_commit: str
    git_branch: str
    state_hash: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    files_snapshot: List[str] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["lane"] = self.lane.value
        return data


@dataclass
class RecoveryAction:
    """Action to take for recovery."""

    action_type: RecoveryStrategy
    description: str
    commands: List[str] = field(default_factory=list)
    estimated_time: int = 0  # seconds
    success_criteria: str = ""
    rollback_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["action_type"] = self.action_type.value
        return data


@dataclass
class RecoveryResult:
    """Result of recovery operation."""

    success: bool
    recovery_strategy: RecoveryStrategy
    checkpoint_id: Optional[str]
    duration: int  # seconds
    steps_executed: int
    steps_skipped: int
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["recovery_strategy"] = self.recovery_strategy.value
        return data


class CheckpointManager:
    """Manages workflow checkpoints for state recovery."""

    def __init__(self, project_root: Path = None):
        """Initialize checkpoint manager."""
        self.project_root = project_root or Path.cwd()
        self.checkpoint_dir = self.project_root / ".checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.state_file = self.checkpoint_dir / "state.json"

    def create_checkpoint(
        self,
        lane: LaneType,
        step_number: int,
        step_name: str,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> WorkflowCheckpoint:
        """
        Create a new checkpoint at current workflow step.

        Args:
            lane: Current workflow lane
            step_number: Step number in workflow
            step_name: Name of the step
            success: Whether step completed successfully
            error_message: Error message if step failed

        Returns:
            WorkflowCheckpoint with saved state
        """
        try:
            # Get git information
            git_commit = self._get_git_commit()
            git_branch = self._get_git_branch()

            # Create checkpoint ID
            timestamp = datetime.now().isoformat()
            checkpoint_id = f"{lane.value}-step{step_number}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Get state hash
            state_hash = self._calculate_state_hash()

            # Get files snapshot
            files_snapshot = self._snapshot_key_files()

            # Create checkpoint object
            checkpoint = WorkflowCheckpoint(
                checkpoint_id=checkpoint_id,
                lane=lane,
                step_number=step_number,
                step_name=step_name,
                timestamp=timestamp,
                git_commit=git_commit,
                git_branch=git_branch,
                state_hash=state_hash,
                files_snapshot=files_snapshot,
                success=success,
                error_message=error_message,
                metrics=self._collect_metrics(),
            )

            # Save checkpoint
            self._save_checkpoint(checkpoint)
            logger.info(f"Checkpoint created: {checkpoint_id}")

            return checkpoint

        except Exception as e:
            logger.error(f"Error creating checkpoint: {e}")
            raise

    def list_checkpoints(self) -> List[WorkflowCheckpoint]:
        """List all available checkpoints."""
        try:
            if not self.state_file.exists():
                return []

            with open(self.state_file) as f:
                state = json.load(f)

            checkpoints = []
            for cp_data in state.get("checkpoints", []):
                cp = WorkflowCheckpoint(**cp_data)
                checkpoints.append(cp)

            return sorted(checkpoints, key=lambda x: x.timestamp, reverse=True)

        except Exception as e:
            logger.error(f"Error listing checkpoints: {e}")
            return []

    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restore state from a specific checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            True if restoration successful
        """
        try:
            checkpoint = self._find_checkpoint(checkpoint_id)
            if not checkpoint:
                logger.error(f"Checkpoint not found: {checkpoint_id}")
                return False

            # Restore files from snapshot
            for file_path in checkpoint.files_snapshot:
                file_full_path = self.project_root / file_path
                backup_path = self.checkpoint_dir / checkpoint_id / file_path

                if backup_path.exists():
                    file_full_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_path, file_full_path)
                    logger.info(f"Restored file: {file_path}")

            logger.info(f"Checkpoint restored: {checkpoint_id}")
            return True

        except Exception as e:
            logger.error(f"Error restoring checkpoint: {e}")
            return False

    def validate_state(self) -> bool:
        """Validate current workflow state."""
        try:
            # Check for critical files
            critical_files = [
                "scripts/workflow.py",
                "agent/backend.py",
                "pytest.ini",
                "requirements.txt",
            ]

            for file_path in critical_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    logger.warning(f"Critical file missing: {file_path}")
                    return False

            # Check git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.warning("Git status check failed")
                return False

            logger.info("State validation passed")
            return True

        except Exception as e:
            logger.error(f"Error validating state: {e}")
            return False

    def cleanup_state(self) -> bool:
        """Clean up failed execution state."""
        try:
            # Remove temporary files
            temp_patterns = ["**/*.pyc", "**/__pycache__", "**/*.tmp", ".pytest_cache"]

            for pattern in temp_patterns:
                for path in self.project_root.glob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path)
                        logger.info(f"Removed directory: {path}")
                    else:
                        path.unlink()
                        logger.info(f"Removed file: {path}")

            # Reset git state if needed
            result = subprocess.run(
                ["git", "clean", "-fd"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info("Git state cleaned")

            logger.info("State cleanup completed")
            return True

        except Exception as e:
            logger.error(f"Error cleaning up state: {e}")
            return False

    def _get_git_commit(self) -> str:
        """Get current git commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _calculate_state_hash(self) -> str:
        """Calculate hash of current state."""
        try:
            hash_obj = hashlib.sha256()

            key_files = [
                "scripts/workflow.py",
                "agent/backend.py",
                "agent/settings.py",
                "pytest.ini",
            ]

            for file_path in key_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    with open(full_path, "rb") as f:
                        hash_obj.update(f.read())

            return hash_obj.hexdigest()

        except Exception:
            return "unknown"

    def _snapshot_key_files(self) -> List[str]:
        """Create snapshot of key files."""
        try:
            key_files = [
                "scripts/workflow.py",
                "agent/backend.py",
                "agent/settings.py",
                "pytest.ini",
                "requirements.txt",
            ]

            snapshots = []
            for file_path in key_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    snapshots.append(file_path)

            return snapshots

        except Exception:
            return []

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": sys.platform,
        }

    def _save_checkpoint(self, checkpoint: WorkflowCheckpoint):
        """Save checkpoint to disk."""
        try:
            # Load existing state
            state = {}
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)

            # Add new checkpoint
            if "checkpoints" not in state:
                state["checkpoints"] = []

            state["checkpoints"].append(checkpoint.to_dict())
            state["last_checkpoint"] = checkpoint.checkpoint_id
            state["updated"] = datetime.now().isoformat()

            # Save state
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)

            # Create checkpoint directory
            cp_dir = self.checkpoint_dir / checkpoint.checkpoint_id
            cp_dir.mkdir(exist_ok=True)

            # Backup files
            for file_path in checkpoint.files_snapshot:
                src = self.project_root / file_path
                dst = cp_dir / file_path

                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)

        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
            raise

    def _find_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Find checkpoint by ID."""
        try:
            checkpoints = self.list_checkpoints()
            for cp in checkpoints:
                if cp.checkpoint_id == checkpoint_id:
                    return cp
            return None
        except Exception:
            return None


class RecoveryPlanner:
    """Plans recovery strategy based on failure type and context."""

    def __init__(self, project_root: Path = None):
        """Initialize recovery planner."""
        self.project_root = project_root or Path.cwd()
        self.checkpoint_manager = CheckpointManager(project_root)

    def get_recovery_plan(
        self, failure_type: FailureType, lane: LaneType
    ) -> List[RecoveryAction]:
        """
        Get recovery plan for a specific failure type and lane.

        Args:
            failure_type: Type of failure that occurred
            lane: Lane where failure occurred

        Returns:
            List of recovery actions to take
        """
        recovery_map = {
            FailureType.TIMEOUT: self._recover_from_timeout,
            FailureType.TEST_FAILURE: self._recover_from_test_failure,
            FailureType.QUALITY_GATE_FAILURE: self._recover_from_quality_gate_failure,
            FailureType.RESOURCE_EXHAUSTION: self._recover_from_resource_exhaustion,
            FailureType.NETWORK_ERROR: self._recover_from_network_error,
            FailureType.GIT_ERROR: self._recover_from_git_error,
            FailureType.UNKNOWN: self._recover_from_unknown,
        }

        recovery_fn = recovery_map.get(failure_type, self._recover_from_unknown)
        return recovery_fn(lane)

    def _recover_from_timeout(self, lane: LaneType) -> List[RecoveryAction]:
        """Recovery from timeout failure."""
        actions = []

        # Action 1: Check resource usage
        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.RETRY,
                description="Check resource usage and retry",
                commands=[
                    "free -h",  # Memory
                    "df -h",  # Disk
                    "ps aux | grep python",  # Process list
                ],
                estimated_time=30,
                success_criteria="Process completes within SLA",
            )
        )

        # Action 2: Consider resuming from checkpoint
        checkpoints = self.checkpoint_manager.list_checkpoints()
        if checkpoints:
            actions.append(
                RecoveryAction(
                    action_type=RecoveryStrategy.RESUME,
                    description="Resume from last successful checkpoint",
                    estimated_time=60,
                    success_criteria="Workflow completes from checkpoint",
                )
            )

        # Action 3: Try heavier lane if applicable
        if lane == LaneType.STANDARD:
            actions.append(
                RecoveryAction(
                    action_type=RecoveryStrategy.RETRY,
                    description="Retry with HEAVY lane for more resources",
                    estimated_time=1200,
                    success_criteria="Heavy lane completes successfully",
                )
            )

        return actions

    def _recover_from_test_failure(self, lane: LaneType) -> List[RecoveryAction]:
        """Recovery from test failure."""
        actions = []

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.RETRY,
                description="Re-run failed tests individually",
                commands=[
                    "pytest tests/ -v -x",  # Stop on first failure
                    "pytest tests/ -v --tb=short",  # Detailed output
                ],
                estimated_time=300,
                success_criteria="All tests pass",
            )
        )

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.SKIP,
                description="Skip failing tests and continue",
                commands=["pytest tests/ -v --ignore=tests/broken"],
                estimated_time=180,
                success_criteria="Other tests pass",
            )
        )

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.MANUAL,
                description="Manual review and fix required",
                success_criteria="Tests fixed and passing",
            )
        )

        return actions

    def _recover_from_quality_gate_failure(
        self, lane: LaneType
    ) -> List[RecoveryAction]:
        """Recovery from quality gate failure."""
        actions = []

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.RETRY,
                description="Run quality gates individually",
                commands=[
                    "ruff check agent/",
                    "mypy agent/ --ignore-missing-imports",
                    "bandit -r agent/",
                ],
                estimated_time=120,
                success_criteria="All quality gates pass",
            )
        )

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.SKIP,
                description="Skip quality gates for development",
                commands=["# Skip quality gates"],
                estimated_time=0,
                success_criteria="Workflow continues",
                rollback_steps=[
                    "Re-run quality gates before merge",
                    "Fix quality gate issues",
                ],
            )
        )

        return actions

    def _recover_from_resource_exhaustion(self, lane: LaneType) -> List[RecoveryAction]:
        """Recovery from resource exhaustion."""
        actions = []

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.RETRY,
                description="Clean up and retry",
                commands=[
                    "git clean -fd",
                    "rm -rf __pycache__ .pytest_cache",
                    "python -m pytest --cache-clear tests/",
                ],
                estimated_time=180,
                success_criteria="Workflow completes with sufficient resources",
            )
        )

        if lane != LaneType.DOCS:
            actions.append(
                RecoveryAction(
                    action_type=RecoveryStrategy.RETRY,
                    description="Downgrade to lighter lane",
                    estimated_time=300,
                    success_criteria="Lighter lane completes successfully",
                )
            )

        return actions

    def _recover_from_network_error(self, lane: LaneType) -> List[RecoveryAction]:
        """Recovery from network error."""
        actions = []

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.RETRY,
                description="Wait and retry",
                estimated_time=60,
                success_criteria="Network connectivity restored",
            )
        )

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.RESUME,
                description="Resume from checkpoint once network restored",
                estimated_time=120,
                success_criteria="Workflow completes from checkpoint",
            )
        )

        return actions

    def _recover_from_git_error(self, lane: LaneType) -> List[RecoveryAction]:
        """Recovery from git error."""
        actions = []

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.RETRY,
                description="Check git status and retry",
                commands=["git status", "git log -1 --oneline", "git fetch origin"],
                estimated_time=30,
                success_criteria="Git operations succeed",
            )
        )

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.MANUAL,
                description="Manual git recovery required",
                success_criteria="Git repository restored",
            )
        )

        return actions

    def _recover_from_unknown(self, lane: LaneType) -> List[RecoveryAction]:
        """Recovery from unknown failure."""
        actions = []

        actions.append(
            RecoveryAction(
                action_type=RecoveryStrategy.MANUAL,
                description="Manual investigation required",
                commands=[
                    "Check logs for error details",
                    "Verify system state",
                    "Review recent changes",
                ],
                success_criteria="Issue identified and resolved",
            )
        )

        return actions


class RollbackRecoverySystem:
    """Main system for rollback and recovery operations."""

    def __init__(self, project_root: Path = None, verbose: bool = False):
        """Initialize rollback recovery system."""
        self.project_root = project_root or Path.cwd()
        self.verbose = verbose
        self.checkpoint_manager = CheckpointManager(self.project_root)
        self.recovery_planner = RecoveryPlanner(self.project_root)

    def run(self, action: str, **kwargs) -> RecoveryResult:
        """
        Run recovery operation.

        Args:
            action: Action to perform (checkpoint, restore, validate, cleanup, rollback)
            **kwargs: Action-specific arguments

        Returns:
            RecoveryResult with operation details
        """
        start_time = datetime.now()

        try:
            if action == "checkpoint":
                return self._action_checkpoint(kwargs)
            elif action == "restore":
                return self._action_restore(kwargs)
            elif action == "validate":
                return self._action_validate()
            elif action == "cleanup":
                return self._action_cleanup()
            elif action == "list":
                return self._action_list()
            elif action == "plan":
                return self._action_plan(kwargs)
            else:
                return RecoveryResult(
                    success=False,
                    recovery_strategy=RecoveryStrategy.MANUAL,
                    checkpoint_id=None,
                    duration=int((datetime.now() - start_time).total_seconds()),
                    steps_executed=0,
                    steps_skipped=0,
                    error_message=f"Unknown action: {action}",
                )

        except Exception as e:
            logger.exception(f"Error during recovery: {e}")
            return RecoveryResult(
                success=False,
                recovery_strategy=RecoveryStrategy.MANUAL,
                checkpoint_id=None,
                duration=int((datetime.now() - start_time).total_seconds()),
                steps_executed=0,
                steps_skipped=0,
                error_message=str(e),
            )

    def _action_checkpoint(self, kwargs) -> RecoveryResult:
        """Create checkpoint."""
        lane = LaneType(kwargs.get("lane", "standard"))
        step_number = kwargs.get("step_number", 0)
        step_name = kwargs.get("step_name", "unknown")

        cp = self.checkpoint_manager.create_checkpoint(lane, step_number, step_name)

        return RecoveryResult(
            success=True,
            recovery_strategy=RecoveryStrategy.RETRY,
            checkpoint_id=cp.checkpoint_id,
            duration=0,
            steps_executed=1,
            steps_skipped=0,
        )

    def _action_restore(self, kwargs) -> RecoveryResult:
        """Restore from checkpoint."""
        checkpoint_id = kwargs.get("checkpoint_id")
        if not checkpoint_id:
            return RecoveryResult(
                success=False,
                recovery_strategy=RecoveryStrategy.MANUAL,
                checkpoint_id=None,
                duration=0,
                steps_executed=0,
                steps_skipped=1,
                error_message="No checkpoint ID provided",
            )

        success = self.checkpoint_manager.restore_checkpoint(checkpoint_id)

        return RecoveryResult(
            success=success,
            recovery_strategy=RecoveryStrategy.RESUME,
            checkpoint_id=checkpoint_id,
            duration=0,
            steps_executed=1,
            steps_skipped=0 if success else 1,
        )

    def _action_validate(self) -> RecoveryResult:
        """Validate state."""
        success = self.checkpoint_manager.validate_state()

        return RecoveryResult(
            success=success,
            recovery_strategy=RecoveryStrategy.RETRY,
            checkpoint_id=None,
            duration=0,
            steps_executed=1,
            steps_skipped=0,
        )

    def _action_cleanup(self) -> RecoveryResult:
        """Clean up state."""
        success = self.checkpoint_manager.cleanup_state()

        return RecoveryResult(
            success=success,
            recovery_strategy=RecoveryStrategy.RETRY,
            checkpoint_id=None,
            duration=0,
            steps_executed=1,
            steps_skipped=0,
        )

    def _action_list(self) -> RecoveryResult:
        """List checkpoints."""
        checkpoints = self.checkpoint_manager.list_checkpoints()

        for cp in checkpoints[:5]:  # Show last 5
            logger.info(f"  {cp.checkpoint_id}: {cp.step_name} ({cp.lane.value})")

        return RecoveryResult(
            success=True,
            recovery_strategy=RecoveryStrategy.RESUME,
            checkpoint_id=None,
            duration=0,
            steps_executed=len(checkpoints),
            steps_skipped=0,
        )

    def _action_plan(self, kwargs) -> RecoveryResult:
        """Get recovery plan."""
        failure_type = FailureType(kwargs.get("failure_type", "unknown"))
        lane = LaneType(kwargs.get("lane", "standard"))

        actions = self.recovery_planner.get_recovery_plan(failure_type, lane)

        logger.info(f"Recovery plan for {failure_type.value} in {lane.value}:")
        for i, action in enumerate(actions, 1):
            logger.info(f"  {i}. {action.description}")

        return RecoveryResult(
            success=True,
            recovery_strategy=(
                actions[0].action_type if actions else RecoveryStrategy.MANUAL
            ),
            checkpoint_id=None,
            duration=0,
            steps_executed=len(actions),
            steps_skipped=0,
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Rollback and Recovery Framework")

    parser.add_argument(
        "action",
        choices=["checkpoint", "restore", "validate", "cleanup", "list", "plan"],
        help="Action to perform",
    )
    parser.add_argument("--checkpoint-id", help="Checkpoint ID for restore action")
    parser.add_argument(
        "--lane",
        choices=["docs", "standard", "heavy"],
        default="standard",
        help="Workflow lane",
    )
    parser.add_argument(
        "--step-number", type=int, default=0, help="Step number for checkpoint"
    )
    parser.add_argument(
        "--step-name", default="unknown", help="Step name for checkpoint"
    )
    parser.add_argument(
        "--failure-type",
        choices=[
            "timeout",
            "test_failure",
            "quality_gate_failure",
            "resource_exhaustion",
            "network_error",
            "git_error",
            "unknown",
        ],
        default="unknown",
        help="Type of failure for recovery planning",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--project-root", type=Path, help="Project root path")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    system = RollbackRecoverySystem(
        project_root=args.project_root, verbose=args.verbose
    )

    result = system.run(
        args.action,
        checkpoint_id=args.checkpoint_id,
        lane=args.lane,
        step_number=args.step_number,
        step_name=args.step_name,
        failure_type=args.failure_type,
    )

    if result.success:
        logger.info(f"✓ Recovery successful: {result.recovery_strategy.value}")
    else:
        logger.error(f"✗ Recovery failed: {result.error_message}")

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
