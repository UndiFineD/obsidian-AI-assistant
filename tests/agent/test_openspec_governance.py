"""
Comprehensive tests for OpenSpec Governance Module

Tests cover:
- OpenSpecChange class (parsing, validation, status)
- OpenSpecGovernance class (listing, details, validation, application, archiving)
- Bulk operations (bulk validation, metrics)
- Error handling and edge cases
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from agent.openspec_governance import (
    OpenSpecChange,
    OpenSpecGovernance,
    get_openspec_governance,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_openspec_dir():
    """Create a temporary OpenSpec directory structure"""
    temp_dir = tempfile.mkdtemp()
    base_path = Path(temp_dir)

    # Create directory structure
    changes_path = base_path / "openspec" / "changes"
    specs_path = base_path / "openspec" / "specs"
    changes_path.mkdir(parents=True, exist_ok=True)
    specs_path.mkdir(parents=True, exist_ok=True)

    yield base_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_change_dir(temp_openspec_dir):
    """Create a sample change directory with proposal and tasks"""
    change_id = "test-change-001"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    # Create proposal.md
    proposal_content = """# Test Change Proposal

## Why

This is a test change to improve the system.

## What Changes

- Update documentation
- Add new features
- Fix bugs

## Impact

Positive impact on system reliability.

## Implementation Plan

1. Step one
2. Step two
3. Step three

## Acceptance Criteria

- [ ] Documentation updated
- [x] Tests passing
- [ ] Code reviewed

## Security Considerations

No security concerns.
"""
    (change_path / "proposal.md").write_text(proposal_content, encoding="utf-8")

    # Create tasks.md
    tasks_content = """# Tasks for test-change-001

## Documentation Tasks

- [x] Update README.md
- [ ] Update API docs
- [x] Add examples

## Implementation Tasks

- [x] Implement feature A
- [ ] Implement feature B
- [ ] Write tests

## Review Tasks

- [ ] Code review
- [ ] Security review
"""
    (change_path / "tasks.md").write_text(tasks_content, encoding="utf-8")

    return change_path, change_id


# ============================================================================
# OpenSpecChange Tests
# ============================================================================


def test_openspec_change_initialization(temp_openspec_dir):
    """Test OpenSpecChange initialization"""
    change = OpenSpecChange("test-001", temp_openspec_dir)

    assert change.change_id == "test-001"
    assert change.base_path == temp_openspec_dir
    assert "openspec" in str(change.change_path)
    assert "changes" in str(change.change_path)
    assert "test-001" in str(change.change_path)


def test_openspec_change_exists_true(sample_change_dir):
    """Test exists() returns True for existing change"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    change = OpenSpecChange(change_id, base_path)
    assert change.exists() is True


def test_openspec_change_exists_false(temp_openspec_dir):
    """Test exists() returns False for non-existent change"""
    change = OpenSpecChange("nonexistent-change", temp_openspec_dir)
    assert change.exists() is False


def test_get_proposal_success(sample_change_dir):
    """Test successful proposal parsing"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    change = OpenSpecChange(change_id, base_path)
    proposal = change.get_proposal()

    assert "error" not in proposal
    assert proposal["title"] == "Test Change Proposal"
    assert "test change" in proposal["why"].lower()
    assert "documentation" in proposal["what_changes"].lower()
    assert "positive impact" in proposal["impact"].lower()


def test_get_proposal_missing_file(temp_openspec_dir):
    """Test get_proposal() with missing file"""
    change = OpenSpecChange("missing-proposal", temp_openspec_dir)
    proposal = change.get_proposal()

    assert "error" in proposal
    assert "not found" in proposal["error"].lower()


def test_get_proposal_acceptance_criteria(sample_change_dir):
    """Test proposal acceptance criteria parsing"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    change = OpenSpecChange(change_id, base_path)
    proposal = change.get_proposal()

    assert "acceptance_criteria" in proposal
    criteria = proposal["acceptance_criteria"]
    assert len(criteria) == 3
    assert criteria[0]["text"] == "Documentation updated"
    assert criteria[0]["completed"] is False
    assert criteria[1]["completed"] is True  # Tests passing


def test_get_tasks_success(sample_change_dir):
    """Test successful tasks parsing"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    change = OpenSpecChange(change_id, base_path)
    tasks = change.get_tasks()

    assert "error" not in tasks
    assert tasks["total_tasks"] > 0
    assert tasks["completed_tasks"] > 0
    assert 0 <= tasks["completion_rate"] <= 100


def test_get_tasks_completion_calculation(sample_change_dir):
    """Test tasks completion rate calculation"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    change = OpenSpecChange(change_id, base_path)
    tasks = change.get_tasks()

    # Based on sample: 3 completed out of 8 total
    assert tasks["total_tasks"] == 8
    assert tasks["completed_tasks"] == 3
    assert tasks["completion_rate"] == pytest.approx(37.5, rel=0.1)


def test_get_tasks_sections(sample_change_dir):
    """Test tasks section parsing"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    change = OpenSpecChange(change_id, base_path)
    tasks = change.get_tasks()

    assert "task_sections" in tasks
    sections = tasks["task_sections"]
    assert len(sections) == 3  # Documentation, Implementation, Review

    section_names = [s["name"] for s in sections]
    assert "Documentation Tasks" in section_names
    assert "Implementation Tasks" in section_names
    assert "Review Tasks" in section_names


def test_get_tasks_missing_file(temp_openspec_dir):
    """Test get_tasks() with missing file"""
    change = OpenSpecChange("missing-tasks", temp_openspec_dir)
    tasks = change.get_tasks()

    assert "error" in tasks
    assert "not found" in tasks["error"].lower()


def test_validate_success(sample_change_dir):
    """Test successful validation"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    change = OpenSpecChange(change_id, base_path)
    validation = change.validate()

    assert validation["valid"] is True
    assert len(validation["errors"]) == 0
    assert "info" in validation


def test_validate_missing_required_files(temp_openspec_dir):
    """Test validation with missing required files"""
    change_id = "incomplete-change"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    change = OpenSpecChange(change_id, temp_openspec_dir)
    validation = change.validate()

    assert validation["valid"] is False
    assert len(validation["errors"]) > 0
    assert any("proposal.md" in err for err in validation["errors"])
    assert any("tasks.md" in err for err in validation["errors"])


def test_validate_warnings_for_incomplete_proposal(temp_openspec_dir):
    """Test validation warnings for incomplete proposal"""
    change_id = "incomplete-proposal"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    # Create minimal proposal
    (change_path / "proposal.md").write_text("# Title Only", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [ ] Task 1", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    validation = change.validate()

    assert len(validation["warnings"]) > 0


def test_get_status_pending(temp_openspec_dir):
    """Test status determination for pending change"""
    change_id = "pending-change"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [ ] Task 1\n- [ ] Task 2", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    assert change.get_status() == "pending"


def test_get_status_in_progress(temp_openspec_dir):
    """Test status determination for in-progress change"""
    change_id = "progress-change"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [x] Task 1\n- [ ] Task 2", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    assert change.get_status() == "in_progress"


def test_get_status_completed(temp_openspec_dir):
    """Test status determination for completed change"""
    change_id = "completed-change"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [x] Task 1\n- [x] Task 2", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    assert change.get_status() == "completed"


def test_get_status_not_found(temp_openspec_dir):
    """Test status determination for non-existent change"""
    change = OpenSpecChange("not-exist", temp_openspec_dir)
    assert change.get_status() == "not_found"


# ============================================================================
# OpenSpecGovernance Tests
# ============================================================================


def test_governance_initialization(temp_openspec_dir):
    """Test OpenSpecGovernance initialization"""
    gov = OpenSpecGovernance(str(temp_openspec_dir))

    assert gov.base_path == temp_openspec_dir
    assert "openspec" in str(gov.changes_path)
    assert "changes" in str(gov.changes_path)
    assert "openspec" in str(gov.specs_path)
    assert "specs" in str(gov.specs_path)


def test_list_changes_empty(temp_openspec_dir):
    """Test list_changes with no changes"""
    gov = OpenSpecGovernance(str(temp_openspec_dir))
    changes = gov.list_changes()

    assert isinstance(changes, list)
    assert len(changes) == 0


def test_list_changes_with_changes(sample_change_dir):
    """Test list_changes with existing changes"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    changes = gov.list_changes()

    assert len(changes) >= 1
    assert any(c["change_id"] == change_id for c in changes)

    # Check structure
    first_change = changes[0]
    assert "change_id" in first_change
    assert "status" in first_change
    assert "path" in first_change
    assert "modified" in first_change


def test_list_changes_excludes_archive_by_default(temp_openspec_dir):
    """Test that archive directory is excluded by default"""
    # Create archive directory with a change
    archive_path = temp_openspec_dir / "openspec" / "changes" / "archive"
    archive_path.mkdir(parents=True, exist_ok=True)
    archived_change = archive_path / "old-change"
    archived_change.mkdir()

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    changes = gov.list_changes(include_archived=False)

    # Should not include archived changes
    assert not any(c["change_id"] == "old-change" for c in changes)


def test_list_changes_includes_archive_when_requested(temp_openspec_dir):
    """Test including archived changes"""
    # Create archive directory with a change
    archive_path = temp_openspec_dir / "openspec" / "changes" / "archive"
    archive_path.mkdir(parents=True, exist_ok=True)
    archived_change = archive_path / "old-change"
    archived_change.mkdir()
    (archived_change / "proposal.md").write_text("# Old", encoding="utf-8")

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    changes = gov.list_changes(include_archived=True)

    # Should include archived changes
    archived = [c for c in changes if c.get("archived", False)]
    assert len(archived) > 0
    assert any(c["change_id"] == "old-change" for c in archived)


def test_get_change_details_success(sample_change_dir):
    """Test getting change details"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    details = gov.get_change_details(change_id)

    assert "error" not in details
    assert details["change_id"] == change_id
    assert "status" in details
    assert "proposal" in details
    assert "tasks" in details
    assert "validation" in details


def test_get_change_details_not_found(temp_openspec_dir):
    """Test getting details for non-existent change"""
    gov = OpenSpecGovernance(str(temp_openspec_dir))
    details = gov.get_change_details("nonexistent")

    assert "error" in details
    assert "not found" in details["error"].lower()


def test_validate_change_success(sample_change_dir):
    """Test validating a change"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    validation = gov.validate_change(change_id)

    assert "error" not in validation
    assert "valid" in validation
    assert "errors" in validation
    assert "warnings" in validation


def test_validate_change_not_found(temp_openspec_dir):
    """Test validating non-existent change"""
    gov = OpenSpecGovernance(str(temp_openspec_dir))
    validation = gov.validate_change("nonexistent")

    assert "error" in validation


def test_apply_change_dry_run(sample_change_dir):
    """Test applying change in dry-run mode"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    # Make all tasks completed
    tasks_content = "- [x] Task 1\n- [x] Task 2\n- [x] Task 3"
    (change_path / "tasks.md").write_text(tasks_content, encoding="utf-8")

    gov = OpenSpecGovernance(str(base_path))
    result = gov.apply_change(change_id, dry_run=True)

    assert "error" not in result
    assert result["dry_run"] is True
    assert result["success"] is False  # Because dry_run=True
    assert len(result["actions_taken"]) > 0


def test_apply_change_incomplete_tasks(sample_change_dir):
    """Test applying change with incomplete tasks"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    result = gov.apply_change(change_id, dry_run=True)

    assert "error" in result
    assert "incomplete" in result["error"].lower()


def test_apply_change_invalid(temp_openspec_dir):
    """Test applying invalid change"""
    change_id = "invalid-change"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)
    # Missing required files

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    result = gov.apply_change(change_id, dry_run=True)

    assert "error" in result
    assert "validation" in result["error"].lower()


def test_archive_change_success(temp_openspec_dir):
    """Test archiving a completed change"""
    change_id = "completed-archive-test"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [x] Task 1", encoding="utf-8")

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    result = gov.archive_change(change_id, create_timestamp=True)

    assert "error" not in result
    assert result["success"] is True
    assert "archived_to" in result

    # Verify change was moved
    assert not change_path.exists()
    assert gov.archive_path.exists()


def test_archive_change_not_completed(sample_change_dir):
    """Test archiving non-completed change fails"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    result = gov.archive_change(change_id)

    assert "error" in result
    assert "completed" in result["error"].lower()


def test_archive_change_not_found(temp_openspec_dir):
    """Test archiving non-existent change"""
    gov = OpenSpecGovernance(str(temp_openspec_dir))
    result = gov.archive_change("nonexistent")

    assert "error" in result
    assert "not found" in result["error"].lower()


def test_bulk_validate_all_changes(sample_change_dir):
    """Test bulk validation of all changes"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    result = gov.bulk_validate()

    assert "summary" in result
    assert "results" in result
    assert result["summary"]["total"] > 0
    assert change_id in result["results"]


def test_bulk_validate_specific_changes(sample_change_dir):
    """Test bulk validation of specific changes"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    result = gov.bulk_validate([change_id])

    assert result["summary"]["total"] == 1
    assert change_id in result["results"]


def test_get_governance_metrics(sample_change_dir):
    """Test getting governance metrics"""
    change_path, change_id = sample_change_dir
    base_path = change_path.parent.parent.parent

    gov = OpenSpecGovernance(str(base_path))
    metrics = gov.get_governance_metrics()

    assert "total_changes" in metrics
    assert "status_distribution" in metrics
    assert "active_changes" in metrics
    assert "archived_changes" in metrics
    assert "overall_task_completion" in metrics
    assert "total_tasks" in metrics
    assert "completed_tasks" in metrics

    assert metrics["total_changes"] >= 1
    assert metrics["total_tasks"] > 0


def test_get_openspec_governance_factory(temp_openspec_dir):
    """Test factory function"""
    gov = get_openspec_governance(str(temp_openspec_dir))

    assert isinstance(gov, OpenSpecGovernance)
    assert gov.base_path == temp_openspec_dir


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


def test_parse_proposal_with_malformed_content(temp_openspec_dir):
    """Test parsing malformed proposal content"""
    change_id = "malformed"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    # Create malformed proposal
    (change_path / "proposal.md").write_text("Random text without structure", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [ ] Task", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    proposal = change.get_proposal()

    # Should not crash, but may have empty sections
    assert "error" not in proposal


def test_parse_tasks_with_empty_file(temp_openspec_dir):
    """Test parsing empty tasks file"""
    change_id = "empty-tasks"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")
    (change_path / "tasks.md").write_text("", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    tasks = change.get_tasks()

    assert tasks["total_tasks"] == 0
    assert tasks["completed_tasks"] == 0
    assert tasks["completion_rate"] == 0


def test_list_changes_with_non_directory_files(temp_openspec_dir):
    """Test list_changes ignores non-directory files"""
    changes_path = temp_openspec_dir / "openspec" / "changes"

    # Create a file (not a directory) in changes
    (changes_path / "readme.txt").write_text("Not a change directory", encoding="utf-8")

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    changes = gov.list_changes()

    # Should not include the file
    assert not any(c["change_id"] == "readme.txt" for c in changes)


# ============================================================================
# Additional Coverage Tests - Exception Handling and Edge Cases
# ============================================================================


def test_get_proposal_parse_exception(temp_openspec_dir):
    """Test get_proposal with file read exception"""
    change_id = "bad-encoding"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    # Create a file that might cause parsing issues
    with open(change_path / "proposal.md", "wb") as f:
        f.write(b"\xff\xfe\x00\x00")  # Invalid UTF-8

    (change_path / "tasks.md").write_text("- [ ] Task", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    proposal = change.get_proposal()

    # Should return error dict
    assert "error" in proposal


def test_get_tasks_parse_exception(temp_openspec_dir):
    """Test get_tasks with file read exception"""
    change_id = "bad-tasks"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")

    # Create a file that might cause parsing issues
    with open(change_path / "tasks.md", "wb") as f:
        f.write(b"\xff\xfe\x00\x00")  # Invalid UTF-8

    change = OpenSpecChange(change_id, temp_openspec_dir)
    tasks = change.get_tasks()

    # Should return error dict
    assert "error" in tasks


def test_validate_with_exception_during_validation(temp_openspec_dir):
    """Test validation when an exception occurs"""
    change_id = "validation-error"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    # Create proposal and tasks files
    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")

    # Create tasks file with invalid encoding
    with open(change_path / "tasks.md", "wb") as f:
        f.write(b"\xff\xfe\x00\x00")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    validation = change.validate()

    # Should still return a result, possibly with errors
    assert "valid" in validation or "error" in validation


def test_list_changes_sorting(temp_openspec_dir):
    """Test list_changes returns sorted results"""
    # Create multiple changes with different names
    for change_id in ["change-003", "change-001", "change-002"]:
        change_path = temp_openspec_dir / "openspec" / "changes" / change_id
        change_path.mkdir(parents=True, exist_ok=True)
        (change_path / "proposal.md").write_text("# Test", encoding="utf-8")

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    changes = gov.list_changes()

    # Should be sorted by change_id
    change_ids = [c["change_id"] for c in changes]
    assert change_ids == sorted(change_ids)


def test_archive_change_with_timestamp(temp_openspec_dir):
    """Test archiving with timestamp in directory name"""
    change_id = "timestamped-archive"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [x] Task 1", encoding="utf-8")

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    result = gov.archive_change(change_id, create_timestamp=True)

    assert result["success"] is True
    assert "archived_to" in result

    # Verify timestamp in archived path
    archived_path = result["archived_to"]
    assert change_id in archived_path
    # Check for timestamp format (YYYYMMDD_HHMMSS)
    assert any(char.isdigit() for char in archived_path)


def test_apply_change_with_actual_execution(temp_openspec_dir):
    """Test apply_change in non-dry-run mode"""
    change_id = "apply-test"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test\n\n## Why\nReason", encoding="utf-8")
    (change_path / "tasks.md").write_text("- [x] Task 1\n- [x] Task 2", encoding="utf-8")

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    result = gov.apply_change(change_id, dry_run=False)

    # Should succeed with completed tasks
    assert result["success"] is True
    assert result["dry_run"] is False
    assert len(result["actions_taken"]) > 0


def test_get_governance_metrics_empty(temp_openspec_dir):
    """Test metrics calculation with no changes"""
    gov = OpenSpecGovernance(str(temp_openspec_dir))
    metrics = gov.get_governance_metrics()

    assert metrics["total_changes"] == 0
    assert metrics["active_changes"] == 0
    assert metrics["archived_changes"] == 0
    assert metrics["total_tasks"] == 0
    assert metrics["completed_tasks"] == 0
    assert metrics["overall_task_completion"] == 0


def test_parse_checklist_items_with_nested_content(temp_openspec_dir):
    """Test parsing checklist items with nested content"""
    change_id = "nested-tasks"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    (change_path / "proposal.md").write_text("# Test", encoding="utf-8")
    tasks_content = """
## Main Tasks

- [x] Task 1
  - Subtask A
  - Subtask B
- [ ] Task 2
  - Subtask C

## Other Tasks

- [x] Task 3
"""
    (change_path / "tasks.md").write_text(tasks_content, encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    tasks = change.get_tasks()

    assert tasks["total_tasks"] == 3
    assert tasks["completed_tasks"] == 2


def test_proposal_sections_with_special_characters(temp_openspec_dir):
    """Test proposal parsing with special characters"""
    change_id = "special-chars"
    change_path = temp_openspec_dir / "openspec" / "changes" / change_id
    change_path.mkdir(parents=True, exist_ok=True)

    proposal_content = """# Test with Special Characters: @#$%

## Why

Reason with symbols: & < > "quotes"

## What Changes

- Change 1 with *asterisk*
- Change 2 with [link](url)

## Impact

Impact with `code` and **bold**
"""
    (change_path / "proposal.md").write_text(proposal_content, encoding="utf-8")
    (change_path / "tasks.md").write_text("- [ ] Task", encoding="utf-8")

    change = OpenSpecChange(change_id, temp_openspec_dir)
    proposal = change.get_proposal()

    assert "error" not in proposal
    assert "Special Characters" in proposal["title"]


def test_bulk_validate_with_mixed_results(temp_openspec_dir):
    """Test bulk validation with valid and invalid changes"""
    # Create valid change
    valid_path = temp_openspec_dir / "openspec" / "changes" / "valid-change"
    valid_path.mkdir(parents=True, exist_ok=True)
    (valid_path / "proposal.md").write_text("# Valid", encoding="utf-8")
    (valid_path / "tasks.md").write_text("- [ ] Task", encoding="utf-8")

    # Create invalid change (missing files)
    invalid_path = temp_openspec_dir / "openspec" / "changes" / "invalid-change"
    invalid_path.mkdir(parents=True, exist_ok=True)

    gov = OpenSpecGovernance(str(temp_openspec_dir))
    result = gov.bulk_validate()

    assert result["summary"]["total"] == 2
    assert result["summary"]["valid"] == 1
    assert result["summary"]["invalid"] == 1
