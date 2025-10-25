"""
Comprehensive test suite for error_recovery module

Tests cover:
- State validation (file integrity, JSON format, field validation)
- Auto-repair mechanisms (missing files, JSON corruption, invalid fields)
- Checkpoint recovery (listing, rollback, recovery)
- Resource cleanup (temp files, lock files, orphaned directories)
"""

import pytest
import json
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from scripts.error_recovery import (
    StateValidator,
    StateRepair,
    CheckpointRollback,
    ResourceCleaner,
    ValidationError,
    RepairResult,
    validate_state,
    repair_state,
    rollback_to_checkpoint,
    cleanup_resources,
)


# ==================== Fixtures ====================


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def valid_status_file(temp_dir):
    """Create valid status.json file"""
    status_data = {
        "change_id": "test-change-001",
        "status": "running",
        "stage": 5,
        "timestamp": datetime.now().isoformat(),
        "completed_stages": [0, 1, 2, 3, 4],
        "errors": [],
    }
    status_file = temp_dir / "status.json"
    with open(status_file, "w") as f:
        json.dump(status_data, f)
    return status_file


@pytest.fixture
def corrupted_json_file(temp_dir):
    """Create file with corrupted JSON"""
    corrupted_file = temp_dir / "corrupted.json"
    with open(corrupted_file, "w") as f:
        f.write('{"change_id": "test",\n"status": "running",\n}')
    return corrupted_file


@pytest.fixture
def checkpoint_dir(temp_dir):
    """Create checkpoint directory structure"""
    checkpoints_dir = temp_dir / "checkpoints"
    checkpoints_dir.mkdir()

    # Create checkpoint 1
    cp1 = checkpoints_dir / "checkpoint-001"
    cp1.mkdir()
    cp1_state = {
        "change_id": "test-001",
        "stage": 3,
        "timestamp": "2025-10-24T10:00:00",
    }
    with open(cp1 / "state.json", "w") as f:
        json.dump(cp1_state, f)

    # Create checkpoint 2
    cp2 = checkpoints_dir / "checkpoint-002"
    cp2.mkdir()
    cp2_state = {
        "change_id": "test-001",
        "stage": 6,
        "timestamp": "2025-10-24T10:30:00",
    }
    with open(cp2 / "state.json", "w") as f:
        json.dump(cp2_state, f)

    return checkpoints_dir


# ==================== Test StateValidator ====================


class TestStateValidator:
    """Tests for StateValidator class"""

    def test_validate_missing_file(self, temp_dir):
        """Test validation of missing file"""
        status_file = temp_dir / "nonexistent.json"
        validator = StateValidator(status_file)
        is_valid, errors = validator.validate()

        assert not is_valid
        assert len(errors) > 0
        assert errors[0].error_type == "missing_file"
        assert errors[0].severity == "critical"

    def test_validate_valid_file(self, valid_status_file):
        """Test validation of valid status file"""
        validator = StateValidator(valid_status_file)
        is_valid, errors = validator.validate()

        assert is_valid
        assert len(errors) == 0

    def test_validate_corrupted_json(self, corrupted_json_file):
        """Test validation of corrupted JSON"""
        validator = StateValidator(corrupted_json_file)
        is_valid, errors = validator.validate()

        assert not is_valid
        assert any(e.error_type == "invalid_json" for e in errors)

    def test_validate_missing_required_fields(self, temp_dir):
        """Test validation of missing required fields"""
        incomplete_file = temp_dir / "incomplete.json"
        with open(incomplete_file, "w") as f:
            json.dump({"change_id": "test"}, f)

        validator = StateValidator(incomplete_file)
        is_valid, errors = validator.validate()

        assert not is_valid
        assert any(e.error_type == "missing_field" for e in errors)

    def test_validate_invalid_field_types(self, temp_dir):
        """Test validation of invalid field types"""
        invalid_file = temp_dir / "invalid_types.json"
        with open(invalid_file, "w") as f:
            json.dump(
                {
                    "change_id": 123,  # Should be string
                    "status": "running",
                    "stage": "5",  # Should be int
                    "timestamp": datetime.now().isoformat(),
                },
                f,
            )

        validator = StateValidator(invalid_file)
        is_valid, errors = validator.validate()

        assert not is_valid
        assert any(e.error_type == "invalid_type" for e in errors)

    def test_validate_invalid_stage_number(self, temp_dir):
        """Test validation of invalid stage number"""
        invalid_file = temp_dir / "invalid_stage.json"
        with open(invalid_file, "w") as f:
            json.dump(
                {
                    "change_id": "test",
                    "status": "running",
                    "stage": 99,  # Invalid: > 12
                    "timestamp": datetime.now().isoformat(),
                },
                f,
            )

        validator = StateValidator(invalid_file)
        is_valid, errors = validator.validate()

        assert not is_valid
        # Stage error should be detected (may be caught in JSON validation)
        assert len(errors) > 0

    def test_validate_invalid_status_value(self, temp_dir):
        """Test validation of invalid status value"""
        invalid_file = temp_dir / "invalid_status.json"
        with open(invalid_file, "w") as f:
            json.dump(
                {
                    "change_id": "test",
                    "status": "invalid_status",  # Not in valid values
                    "stage": 5,
                    "timestamp": datetime.now().isoformat(),
                },
                f,
            )

        validator = StateValidator(invalid_file)
        is_valid, errors = validator.validate()

        assert not is_valid
        assert any(e.error_type == "invalid_type" for e in errors)

    def test_validation_error_to_dict(self):
        """Test ValidationError to_dict conversion"""
        error = ValidationError(
            error_type="test_error",
            message="Test message",
            severity="warning",
            location="test_location",
        )
        error_dict = error.to_dict()

        assert error_dict["error_type"] == "test_error"
        assert error_dict["message"] == "Test message"
        assert error_dict["severity"] == "warning"
        assert "timestamp" in error_dict

    @pytest.mark.skipif(
        sys.platform == "win32", reason="File permissions work differently on Windows"
    )
    def test_validate_file_permission_error(self, temp_dir):
        """Test validation when file is not readable"""
        status_file = temp_dir / "unreadable.json"
        with open(status_file, "w") as f:
            json.dump({"change_id": "test", "status": "running", "stage": 0}, f)

        # Remove read permissions
        status_file.chmod(0o000)

        try:
            validator = StateValidator(status_file)
            is_valid, errors = validator.validate()

            assert not is_valid
            assert any(e.error_type == "permission_error" for e in errors)
        finally:
            # Restore permissions for cleanup
            status_file.chmod(0o644)


# ==================== Test StateRepair ====================


class TestStateRepair:
    """Tests for StateRepair class"""

    def test_repair_missing_file(self, temp_dir):
        """Test repair of missing status.json"""
        status_file = temp_dir / "status.json"
        repairer = StateRepair(status_file)
        result = repairer.repair()

        # File should be created
        assert status_file.exists()
        assert result.repairs_applied > 0
        # After repair, file may still fail git validation if not in repo, so just check created
        assert len(result.details) > 0

    def test_repair_invalid_json(self, corrupted_json_file):
        """Test repair of corrupted JSON"""
        repairer = StateRepair(corrupted_json_file)
        result = repairer.repair()

        # Should attempt to repair or restore
        assert isinstance(result, RepairResult)
        # File should still exist after repair
        assert corrupted_json_file.exists()
        # Check file is now valid JSON (either repaired or restored)
        with open(corrupted_json_file, "r") as f:
            data = json.load(f)
        # Should have some structure
        assert isinstance(data, dict)

    def test_repair_missing_fields(self, temp_dir):
        """Test repair of missing required fields"""
        incomplete_file = temp_dir / "incomplete.json"
        with open(incomplete_file, "w") as f:
            json.dump({"change_id": "test"}, f)

        repairer = StateRepair(incomplete_file)
        result = repairer.repair()

        # Should repair the missing fields
        assert result.repairs_applied > 0
        # Verify fields were added
        with open(incomplete_file, "r") as f:
            data = json.load(f)
        assert "status" in data
        assert "stage" in data
        assert "timestamp" in data

    def test_repair_invalid_types(self, temp_dir):
        """Test repair of invalid field types"""
        invalid_file = temp_dir / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(
                {
                    "change_id": 123,  # Should be string
                    "status": "running",
                    "stage": "5",  # Should be int
                    "timestamp": datetime.now().isoformat(),
                },
                f,
            )

        repairer = StateRepair(invalid_file)
        result = repairer.repair()

        assert result.success
        assert result.repairs_applied > 0

    def test_repair_result_to_dict(self):
        """Test RepairResult to_dict conversion"""
        result = RepairResult(
            success=True,
            repairs_applied=3,
            errors_remaining=0,
            details=["Fixed field 1", "Fixed field 2"],
        )
        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["repairs_applied"] == 3
        assert result_dict["errors_remaining"] == 0
        assert len(result_dict["details"]) == 2
        assert "timestamp" in result_dict

    def test_repair_no_errors(self, valid_status_file):
        """Test repair when no errors exist"""
        repairer = StateRepair(valid_status_file)
        result = repairer.repair()

        assert result.success
        assert result.repairs_applied == 0
        assert result.errors_remaining == 0


# ==================== Test CheckpointRollback ====================


class TestCheckpointRollback:
    """Tests for CheckpointRollback class"""

    def test_list_checkpoints(self, checkpoint_dir):
        """Test listing available checkpoints"""
        rollback = CheckpointRollback(checkpoint_dir)
        checkpoints = rollback.list_checkpoints()

        assert len(checkpoints) == 2
        assert checkpoints[0]["name"] == "checkpoint-001"
        assert checkpoints[1]["name"] == "checkpoint-002"
        assert checkpoints[0]["stage"] == 3
        assert checkpoints[1]["stage"] == 6

    def test_get_latest_checkpoint(self, checkpoint_dir):
        """Test getting latest checkpoint"""
        rollback = CheckpointRollback(checkpoint_dir)
        latest = rollback.get_latest_checkpoint()

        assert latest is not None
        assert latest["name"] == "checkpoint-002"
        assert latest["stage"] == 6

    def test_get_latest_checkpoint_empty(self, temp_dir):
        """Test getting latest checkpoint when none exist"""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        rollback = CheckpointRollback(empty_dir)
        latest = rollback.get_latest_checkpoint()

        assert latest is None

    def test_rollback_to_checkpoint(self, checkpoint_dir, temp_dir):
        """Test restoring from checkpoint"""
        restore_dir = temp_dir / "restore"
        restore_dir.mkdir()

        rollback = CheckpointRollback(checkpoint_dir)
        success, message = rollback.rollback_to_checkpoint("checkpoint-001", restore_dir)

        assert success
        assert (restore_dir / "state.json").exists()
        with open(restore_dir / "state.json", "r") as f:
            state = json.load(f)
        assert state["stage"] == 3

    def test_rollback_to_checkpoint_not_found(self, checkpoint_dir, temp_dir):
        """Test rollback when checkpoint doesn't exist"""
        restore_dir = temp_dir / "restore"
        restore_dir.mkdir()

        rollback = CheckpointRollback(checkpoint_dir)
        success, message = rollback.rollback_to_checkpoint("checkpoint-999", restore_dir)

        assert not success
        assert "not found" in message.lower()

    def test_rollback_to_latest(self, checkpoint_dir, temp_dir):
        """Test restoring from latest checkpoint"""
        restore_dir = temp_dir / "restore"

        rollback = CheckpointRollback(checkpoint_dir)
        success, message = rollback.rollback_to_latest(restore_dir)

        assert success
        assert (restore_dir / "state.json").exists()
        with open(restore_dir / "state.json", "r") as f:
            state = json.load(f)
        assert state["stage"] == 6  # Latest checkpoint


# ==================== Test ResourceCleaner ====================


class TestResourceCleaner:
    """Tests for ResourceCleaner class"""

    def test_cleanup_temp_files(self, temp_dir):
        """Test removal of temporary files"""
        # Create temp files
        (temp_dir / "file1.tmp").touch()
        (temp_dir / "file2.tmp").touch()
        (temp_dir / "test.lock").touch()

        cleaner = ResourceCleaner(temp_dir)
        removed = cleaner.cleanup_temp_files()

        assert removed > 0
        assert not (temp_dir / "file1.tmp").exists()
        assert not (temp_dir / "file2.tmp").exists()

    def test_cleanup_lock_files(self, temp_dir):
        """Test removal of lock files"""
        # Create lock file
        lock_file = temp_dir / ".gitlock"
        lock_file.touch()

        cleaner = ResourceCleaner(temp_dir)
        removed = cleaner.cleanup_lock_files()

        assert removed > 0
        assert not lock_file.exists()

    def test_cleanup_orphaned_directories(self, temp_dir):
        """Test removal of empty directories"""
        # Create nested empty directories
        empty1 = temp_dir / "empty1"
        empty2 = empty1 / "empty2"
        empty2.mkdir(parents=True)

        cleaner = ResourceCleaner(temp_dir)
        removed = cleaner.cleanup_orphaned_directories()

        assert removed > 0
        assert not empty1.exists()

    def test_cleanup_all(self, temp_dir):
        """Test comprehensive cleanup"""
        # Create various files and directories
        (temp_dir / "file.tmp").touch()
        (temp_dir / ".gitlock").touch()
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        cleaner = ResourceCleaner(temp_dir)
        stats = cleaner.cleanup_all()

        assert "temp_files" in stats
        assert "lock_files" in stats
        assert "empty_directories" in stats

    def test_cleanup_preserves_important_files(self, temp_dir):
        """Test that cleanup doesn't remove important files"""
        # Create important file
        important = temp_dir / "important.txt"
        important.write_text("important data")

        cleaner = ResourceCleaner(temp_dir)
        cleaner.cleanup_all()

        assert important.exists()
        assert important.read_text() == "important data"


# ==================== Test Public API Functions ====================


class TestPublicAPI:
    """Tests for public API functions"""

    def test_validate_state_function(self, valid_status_file):
        """Test validate_state function"""
        is_valid, errors = validate_state(valid_status_file)

        assert is_valid
        assert len(errors) == 0

    def test_repair_state_function(self, temp_dir):
        """Test repair_state function"""
        status_file = temp_dir / "status.json"
        result = repair_state(status_file)

        assert isinstance(result, RepairResult)
        assert result.repairs_applied > 0

    def test_rollback_to_checkpoint_function(self, checkpoint_dir, temp_dir):
        """Test rollback_to_checkpoint function"""
        restore_dir = temp_dir / "restore"
        restore_dir.mkdir()

        checkpoint_path = checkpoint_dir / "checkpoint-001"
        success, message = rollback_to_checkpoint(checkpoint_path, restore_dir)

        assert success

    def test_cleanup_resources_function(self, temp_dir):
        """Test cleanup_resources function"""
        (temp_dir / "file.tmp").touch()
        stats = cleanup_resources(temp_dir)

        assert isinstance(stats, dict)
        assert "temp_files" in stats


# ==================== Integration Tests ====================


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_validate_repair_workflow(self, temp_dir):
        """Test complete validate and repair workflow"""
        # Create corrupted file
        corrupted_file = temp_dir / "status.json"
        with open(corrupted_file, "w") as f:
            f.write('{"change_id": "test",}')  # Invalid JSON

        # Validate
        validator = StateValidator(corrupted_file)
        is_valid, errors = validator.validate()
        assert not is_valid

        # Repair
        repairer = StateRepair(corrupted_file)
        result = repairer.repair()
        # Repair should process the file
        assert isinstance(result, RepairResult)

        # Verify file is now valid JSON
        assert corrupted_file.exists()
        with open(corrupted_file, "r") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_checkpoint_and_recovery_workflow(self, checkpoint_dir, temp_dir):
        """Test complete checkpoint and recovery workflow"""
        restore_dir = temp_dir / "restored"

        # List checkpoints
        rollback = CheckpointRollback(checkpoint_dir)
        checkpoints = rollback.list_checkpoints()
        assert len(checkpoints) > 0

        # Get latest
        latest = rollback.get_latest_checkpoint()
        assert latest is not None

        # Rollback
        success, _ = rollback.rollback_to_latest(restore_dir)
        assert success

        # Verify restoration
        restored_state = restore_dir / "state.json"
        assert restored_state.exists()
        with open(restored_state, "r") as f:
            state = json.load(f)
        assert state["stage"] == 6  # Latest checkpoint

    def test_cleanup_workflow(self, temp_dir):
        """Test complete cleanup workflow"""
        # Create messy structure
        (temp_dir / "work1.tmp").touch()
        (temp_dir / ".gitlock").touch()
        empty = temp_dir / "empty"
        empty.mkdir()
        (temp_dir / "important.txt").write_text("keep this")

        # Cleanup
        stats = cleanup_resources(temp_dir)

        # Verify
        assert not (temp_dir / "work1.tmp").exists()
        assert not (temp_dir / ".gitlock").exists()
        assert not empty.exists()
        assert (temp_dir / "important.txt").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
