"""
Error Recovery Module for Obsidian AI Assistant Workflow

Provides state validation, auto-repair mechanisms, and checkpoint rollback
for workflow error recovery and resilience.

Classes:
    StateValidator: Validates workflow state integrity
    StateRepair: Auto-repairs workflow state issues
    CheckpointRollback: Manages checkpoint recovery
    ResourceCleaner: Cleans up workflow resources

Functions:
    validate_state(status_file): Full state validation
    repair_state(status_file): Automated state repair
    rollback_to_checkpoint(checkpoint_path): Checkpoint recovery
    cleanup_resources(workflow_dir): Resource cleanup
"""

import json
import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a state validation error"""

    error_type: str
    message: str
    severity: str  # "warning", "error", "critical"
    location: str
    timestamp: datetime = field(default_factory=datetime.now)
    repair_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "repair_suggestion": self.repair_suggestion,
        }


@dataclass
class RepairResult:
    """Represents a state repair operation result"""

    success: bool
    repairs_applied: int
    errors_remaining: int
    details: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "repairs_applied": self.repairs_applied,
            "errors_remaining": self.errors_remaining,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class StateValidator:
    """Validates workflow state integrity"""

    def __init__(self, status_file: Path):
        """
        Initialize StateValidator

        Args:
            status_file: Path to status.json file
        """
        self.status_file = Path(status_file)
        self.errors: List[ValidationError] = []

    def validate(self) -> Tuple[bool, List[ValidationError]]:
        """
        Perform complete state validation

        Returns:
            Tuple of (is_valid, errors_list)
        """
        self.errors = []

        # Check file exists
        if not self._validate_file_exists():
            return False, self.errors

        # Check file is readable
        if not self._validate_file_readable():
            return False, self.errors

        # Check JSON validity
        if not self._validate_json_format():
            return False, self.errors

        # Check required fields
        if not self._validate_required_fields():
            return False, self.errors

        # Check field types
        if not self._validate_field_types():
            return False, self.errors

        # Check stage consistency
        if not self._validate_stage_consistency():
            return False, self.errors

        # Check git state
        if not self._validate_git_state():
            return False, self.errors

        return len(self.errors) == 0, self.errors

    def _validate_file_exists(self) -> bool:
        """Check if status file exists"""
        if not self.status_file.exists():
            error = ValidationError(
                error_type="missing_file",
                message=f"Status file not found: {self.status_file}",
                severity="critical",
                location=str(self.status_file),
                repair_suggestion="Create status.json with default structure",
            )
            self.errors.append(error)
            return False
        return True

    def _validate_file_readable(self) -> bool:
        """Check if status file is readable"""
        if not os.access(self.status_file, os.R_OK):
            error = ValidationError(
                error_type="permission_error",
                message=f"Status file not readable: {self.status_file}",
                severity="critical",
                location=str(self.status_file),
                repair_suggestion="Fix file permissions (chmod 644 on Unix)",
            )
            self.errors.append(error)
            return False
        return True

    def _validate_json_format(self) -> bool:
        """Check if file contains valid JSON"""
        try:
            with open(self.status_file, "r") as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            error = ValidationError(
                error_type="invalid_json",
                message=f"Invalid JSON format: {str(e)}",
                severity="critical",
                location=f"{self.status_file}:{e.lineno}",
                repair_suggestion="Manual JSON repair or restore from checkpoint",
            )
            self.errors.append(error)
            return False
        except Exception as e:
            error = ValidationError(
                error_type="read_error",
                message=f"Error reading file: {str(e)}",
                severity="critical",
                location=str(self.status_file),
                repair_suggestion="Restore from backup",
            )
            self.errors.append(error)
            return False

    def _validate_required_fields(self) -> bool:
        """Check if all required fields are present"""
        try:
            with open(self.status_file, "r") as f:
                data = json.load(f)

            required_fields = {
                "change_id": str,
                "status": str,
                "stage": int,
                "timestamp": str,
            }

            all_valid = True
            for field_name, field_type in required_fields.items():
                if field_name not in data:
                    error = ValidationError(
                        error_type="missing_field",
                        message=f"Required field missing: {field_name}",
                        severity="error",
                        location=f"{self.status_file}:{field_name}",
                        repair_suggestion="Add missing field with default value",
                    )
                    self.errors.append(error)
                    all_valid = False

            return all_valid
        except Exception as e:
            logger.error(f"Error validating fields: {e}")
            return False

    def _validate_field_types(self) -> bool:
        """Check if field types are correct"""
        try:
            with open(self.status_file, "r") as f:
                data = json.load(f)

            field_validators = {
                "change_id": lambda x: isinstance(x, str) and len(x) > 0,
                "status": lambda x: isinstance(x, str)
                and x in ["pending", "running", "completed", "failed", "cancelled"],
                "stage": lambda x: isinstance(x, int) and 0 <= x <= 12,
                "timestamp": lambda x: isinstance(x, str),
            }

            all_valid = True
            for field_name, validator in field_validators.items():
                if field_name in data:
                    if not validator(data[field_name]):
                        error = ValidationError(
                            error_type="invalid_type",
                            message=f"Invalid type for field {field_name}: {type(data[field_name]).__name__}",
                            severity="error",
                            location=f"{self.status_file}:{field_name}",
                            repair_suggestion="Correct field type or use default value",
                        )
                        self.errors.append(error)
                        all_valid = False

            return all_valid
        except Exception as e:
            logger.error(f"Error validating types: {e}")
            return False

    def _validate_stage_consistency(self) -> bool:
        """Check if stage sequence is valid"""
        try:
            with open(self.status_file, "r") as f:
                data = json.load(f)

            stage = data.get("stage", 0)
            completed_stages = data.get("completed_stages", [])

            # Check stage range
            if not isinstance(stage, int) or stage < 0 or stage > 12:
                error = ValidationError(
                    error_type="invalid_stage",
                    message=f"Invalid stage number: {stage}",
                    severity="error",
                    location=f"{self.status_file}:stage",
                    repair_suggestion="Reset to valid stage (0-12)",
                )
                self.errors.append(error)
                return False

            # Check completed stages are all valid
            if isinstance(completed_stages, list):
                all_valid = True
                for i, s in enumerate(completed_stages):
                    if not isinstance(s, int) or s < 0 or s > 12:
                        error = ValidationError(
                            error_type="invalid_completed_stage",
                            message=f"Invalid completed stage at index {i}: {s}",
                            severity="warning",
                            location=f"{self.status_file}:completed_stages[{i}]",
                            repair_suggestion="Remove invalid stage from completed list",
                        )
                        self.errors.append(error)
                        all_valid = False
                return all_valid

            return True
        except Exception as e:
            logger.error(f"Error validating stage consistency: {e}")
            return False

    def _validate_git_state(self) -> bool:
        """Check if git state is valid"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                error = ValidationError(
                    error_type="git_error",
                    message="Not in a git repository or git error",
                    severity="warning",
                    location="git status",
                    repair_suggestion="Initialize git repository",
                )
                self.errors.append(error)
                return False

            return True
        except subprocess.TimeoutExpired:
            error = ValidationError(
                error_type="git_timeout",
                message="Git status check timed out",
                severity="warning",
                location="git status",
                repair_suggestion="Check git repository status manually",
            )
            self.errors.append(error)
            return False
        except FileNotFoundError:
            error = ValidationError(
                error_type="git_not_found",
                message="Git executable not found",
                severity="warning",
                location="git",
                repair_suggestion="Install git or add to PATH",
            )
            self.errors.append(error)
            return False


class StateRepair:
    """Auto-repairs workflow state issues"""

    def __init__(self, status_file: Path):
        """
        Initialize StateRepair

        Args:
            status_file: Path to status.json file
        """
        self.status_file = Path(status_file)
        self.repairs_applied: List[str] = []

    def repair(self) -> RepairResult:
        """
        Perform automatic state repair

        Returns:
            RepairResult with details of repairs applied
        """
        # Validate state first
        validator = StateValidator(self.status_file)
        is_valid, errors = validator.validate()

        if is_valid:
            return RepairResult(success=True, repairs_applied=0, errors_remaining=0)

        self.repairs_applied = []

        # Try to repair each error
        for error in errors:
            if error.error_type == "invalid_json":
                # Handle JSON errors at any severity
                self._repair_invalid_json()
            elif error.severity == "critical":
                if error.error_type == "missing_file":
                    self._repair_missing_file()
            elif error.severity == "error":
                if error.error_type == "missing_field":
                    self._repair_missing_field(error)
                elif error.error_type == "invalid_type":
                    self._repair_invalid_type(error)

        # Validate again to count remaining errors
        validator = StateValidator(self.status_file)
        is_valid, remaining_errors = validator.validate()

        return RepairResult(
            success=is_valid,
            repairs_applied=len(self.repairs_applied),
            errors_remaining=len(remaining_errors),
            details=self.repairs_applied,
        )

    def _repair_missing_file(self) -> None:
        """Create missing status.json file"""
        default_status = {
            "change_id": "unknown",
            "status": "unknown",
            "stage": 0,
            "timestamp": datetime.now().isoformat(),
            "completed_stages": [],
            "errors": [],
        }

        try:
            self.status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.status_file, "w") as f:
                json.dump(default_status, f, indent=2)
            self.repairs_applied.append(
                f"Created missing status.json at {self.status_file}"
            )
            logger.info(f"Created missing status.json: {self.status_file}")
        except Exception as e:
            logger.error(f"Failed to create status.json: {e}")

    def _repair_invalid_json(self) -> None:
        """Attempt to repair invalid JSON"""
        try:
            with open(self.status_file, "r") as f:
                content = f.read()

            # Try to fix common JSON issues
            fixed_content = content

            # Remove trailing commas before closing braces/brackets
            fixed_content = re.sub(r",(\s*[}\]])", r"\1", fixed_content)

            # Try to parse
            json.loads(fixed_content)

            # If successful, write back
            with open(self.status_file, "w") as f:
                f.write(fixed_content)

            self.repairs_applied.append("Fixed JSON formatting issues")
            logger.info("Fixed JSON formatting in status.json")

        except json.JSONDecodeError:
            # If JSON repair fails, restore to default
            self._repair_missing_file()
            self.repairs_applied.append("JSON repair failed, restored to default")
            logger.error("JSON repair failed, restored to default")

        except Exception as e:
            # If repair fails, restore to default
            self._repair_missing_file()
            self.repairs_applied.append(
                f"JSON repair failed, restored to default: {str(e)}"
            )
            logger.error(f"JSON repair failed, restored to default: {e}")

    def _repair_missing_field(self, error: ValidationError) -> None:
        """Repair missing field"""
        try:
            with open(self.status_file, "r") as f:
                data = json.load(f)

            # Extract field name from location (format: file:field)
            if ":" in error.location:
                field_name = error.location.split(":")[-1]

                # Add missing field with default value
                defaults = {
                    "change_id": "unknown",
                    "status": "unknown",
                    "stage": 0,
                    "timestamp": datetime.now().isoformat(),
                    "completed_stages": [],
                    "errors": [],
                }

                if field_name in defaults:
                    data[field_name] = defaults[field_name]

                    with open(self.status_file, "w") as f:
                        json.dump(data, f, indent=2)

                    self.repairs_applied.append(f"Added missing field: {field_name}")
                    logger.info(f"Added missing field: {field_name}")

        except Exception as e:
            logger.error(f"Failed to repair missing field: {e}")

    def _repair_invalid_type(self, error: ValidationError) -> None:
        """Repair field with invalid type"""
        try:
            with open(self.status_file, "r") as f:
                data = json.load(f)

            # Extract field name
            if ":" in error.location:
                field_name = error.location.split(":")[-1]

                # Convert to correct type
                defaults = {
                    "change_id": "unknown",
                    "status": "unknown",
                    "stage": 0,
                    "timestamp": datetime.now().isoformat(),
                    "completed_stages": [],
                    "errors": [],
                }

                if field_name in defaults and field_name in data:
                    data[field_name] = defaults[field_name]

                    with open(self.status_file, "w") as f:
                        json.dump(data, f, indent=2)

                    self.repairs_applied.append(f"Fixed type for field: {field_name}")
                    logger.info(f"Fixed type for field: {field_name}")

        except Exception as e:
            logger.error(f"Failed to repair invalid type: {e}")


class CheckpointRollback:
    """Manages checkpoint recovery"""

    def __init__(self, checkpoint_dir: Path):
        """
        Initialize CheckpointRollback

        Args:
            checkpoint_dir: Path to checkpoints directory
        """
        self.checkpoint_dir = Path(checkpoint_dir)

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List available checkpoints

        Returns:
            List of checkpoint info dictionaries
        """
        checkpoints: List[Dict[str, Any]] = []

        if not self.checkpoint_dir.exists():
            return checkpoints

        for checkpoint_path in sorted(self.checkpoint_dir.glob("checkpoint-*")):
            if checkpoint_path.is_dir():
                state_file = checkpoint_path / "state.json"
                if state_file.exists():
                    try:
                        with open(state_file, "r") as f:
                            state = json.load(f)
                        checkpoints.append(
                            {
                                "path": str(checkpoint_path),
                                "name": checkpoint_path.name,
                                "stage": state.get("stage", 0),
                                "timestamp": state.get("timestamp", "unknown"),
                                "change_id": state.get("change_id", "unknown"),
                            }
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to read checkpoint {checkpoint_path}: {e}"
                        )

        return checkpoints

    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent checkpoint

        Returns:
            Latest checkpoint info or None if no checkpoints exist
        """
        checkpoints = self.list_checkpoints()
        return checkpoints[-1] if checkpoints else None

    def rollback_to_checkpoint(
        self, checkpoint_name: str, target_dir: Path
    ) -> Tuple[bool, str]:
        """
        Restore workflow state from checkpoint

        Args:
            checkpoint_name: Name of checkpoint to restore
            target_dir: Directory to restore files to

        Returns:
            Tuple of (success, message)
        """
        checkpoint_path = self.checkpoint_dir / checkpoint_name

        if not checkpoint_path.exists():
            return False, f"Checkpoint not found: {checkpoint_name}"

        try:
            state_file = checkpoint_path / "state.json"
            if state_file.exists():
                # Ensure target directory exists
                target_dir.mkdir(parents=True, exist_ok=True)

                # Copy state.json
                target_status = target_dir / "state.json"
                shutil.copy2(str(state_file), str(target_status))

                # Copy any other checkpoint data
                for file in checkpoint_path.glob("*"):
                    if file.name != "state.json":
                        target_file = target_dir / file.name
                        if file.is_file():
                            shutil.copy2(str(file), str(target_file))
                        elif file.is_dir():
                            if target_file.exists():
                                shutil.rmtree(str(target_file))
                            shutil.copytree(str(file), str(target_file))

                logger.info(f"Restored from checkpoint: {checkpoint_name}")
                return True, f"Successfully restored from checkpoint: {checkpoint_name}"

            return False, f"Checkpoint state.json not found: {checkpoint_name}"

        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            return False, f"Checkpoint restoration failed: {str(e)}"

    def rollback_to_latest(self, target_dir: Path) -> Tuple[bool, str]:
        """
        Restore workflow state from latest checkpoint

        Args:
            target_dir: Directory to restore files to

        Returns:
            Tuple of (success, message)
        """
        latest = self.get_latest_checkpoint()

        if not latest:
            return False, "No checkpoints available"

        return self.rollback_to_checkpoint(latest["name"], target_dir)


class ResourceCleaner:
    """Cleans up workflow resources"""

    def __init__(self, workflow_dir: Path):
        """
        Initialize ResourceCleaner

        Args:
            workflow_dir: Path to workflow directory
        """
        self.workflow_dir = Path(workflow_dir)

    def cleanup_temp_files(self) -> int:
        """
        Remove temporary files

        Returns:
            Number of files removed
        """
        removed_count = 0
        temp_patterns = ["*.tmp", "*.lock", ".tmp*", "~*"]

        try:
            for pattern in temp_patterns:
                for file_path in self.workflow_dir.rglob(pattern):
                    try:
                        if file_path.is_file():
                            file_path.unlink()
                            removed_count += 1
                            logger.info(f"Removed temp file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")

        return removed_count

    def cleanup_lock_files(self) -> int:
        """
        Remove lock files

        Returns:
            Number of lock files removed
        """
        removed_count = 0

        try:
            for lock_file in self.workflow_dir.rglob(".gitlock"):
                try:
                    if lock_file.is_file():
                        lock_file.unlink()
                        removed_count += 1
                        logger.info(f"Removed lock file: {lock_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove lock file {lock_file}: {e}")

        except Exception as e:
            logger.error(f"Error cleaning lock files: {e}")

        return removed_count

    def cleanup_orphaned_directories(self) -> int:
        """
        Remove empty directories

        Returns:
            Number of directories removed
        """
        removed_count = 0

        try:
            for dir_path in sorted(
                self.workflow_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True
            ):
                try:
                    if dir_path.is_dir() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        removed_count += 1
                        logger.info(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    logger.debug(f"Could not remove directory {dir_path}: {e}")

        except Exception as e:
            logger.error(f"Error cleaning orphaned directories: {e}")

        return removed_count

    def cleanup_all(self) -> Dict[str, int]:
        """
        Perform comprehensive cleanup

        Returns:
            Dictionary with cleanup statistics
        """
        return {
            "temp_files": self.cleanup_temp_files(),
            "lock_files": self.cleanup_lock_files(),
            "empty_directories": self.cleanup_orphaned_directories(),
        }


# Public API functions


def validate_state(status_file: Path) -> Tuple[bool, List[ValidationError]]:
    """
    Validate workflow state

    Args:
        status_file: Path to status.json file

    Returns:
        Tuple of (is_valid, errors_list)
    """
    validator = StateValidator(status_file)
    return validator.validate()


def repair_state(status_file: Path) -> RepairResult:
    """
    Repair workflow state

    Args:
        status_file: Path to status.json file

    Returns:
        RepairResult with repair details
    """
    repairer = StateRepair(status_file)
    return repairer.repair()


def rollback_to_checkpoint(checkpoint_path: Path, target_dir: Path) -> Tuple[bool, str]:
    """
    Restore workflow from checkpoint

    Args:
        checkpoint_path: Path to checkpoint
        target_dir: Directory to restore to

    Returns:
        Tuple of (success, message)
    """
    checkpoint_name = checkpoint_path.name
    checkpoint_dir = checkpoint_path.parent
    rollback = CheckpointRollback(checkpoint_dir)
    return rollback.rollback_to_checkpoint(checkpoint_name, target_dir)


def cleanup_resources(workflow_dir: Path) -> Dict[str, int]:
    """
    Clean up workflow resources

    Args:
        workflow_dir: Path to workflow directory

    Returns:
        Dictionary with cleanup statistics
    """
    cleaner = ResourceCleaner(workflow_dir)
    return cleaner.cleanup_all()
