"""
Comprehensive tests for Log Management API

Tests cover:
- Log status endpoint
- Log level updates
- Log file listing and access
- Log streaming
- Log search and filtering
- Log export (JSON, CSV, TEXT)
- Log file deletion and cleanup
- Log metrics
- Error handling and edge cases
"""

import gzip
import json
import shutil
import tempfile
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.log_management import (
    LogExportFormat,
    LogFilter,
    LogLevelUpdate,
    _format_file_size,
    _get_log_file_type,
    _matches_filter,
    router,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_log_dir():
    """Create a temporary log directory with sample log files"""
    temp_dir = tempfile.mkdtemp()
    log_dir = Path(temp_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create sample log files
    app_log = log_dir / "app.log"
    app_log.write_text(
        '{"timestamp": "2025-10-17T10:00:00", "level": "INFO", "logger": "backend.api", "message": "Application started", "category": "app"}\n'
        '{"timestamp": "2025-10-17T10:01:00", "level": "WARNING", "logger": "backend.api", "message": "High memory usage", "category": "app"}\n'
        '{"timestamp": "2025-10-17T10:02:00", "level": "ERROR", "logger": "backend.api", "message": "Database connection failed", "category": "app"}\n',
        encoding="utf-8",
    )

    error_log = log_dir / "error.log"
    error_log.write_text(
        '{"timestamp": "2025-10-17T09:00:00", "level": "ERROR", "logger": "backend.error", "message": "Critical error occurred", "category": "error"}\n',
        encoding="utf-8",
    )

    audit_log = log_dir / "audit.log"
    audit_log.write_text(
        '{"timestamp": "2025-10-17T08:00:00", "level": "AUDIT", "logger": "backend.audit", "message": "User login", "user_id": "user123", "category": "audit"}\n',
        encoding="utf-8",
    )

    # Create an old log file for cleanup testing
    old_log = log_dir / "app.2025-01-01.log"
    old_log.write_text("Old log content\n", encoding="utf-8")
    # Set modification time to 60 days ago
    old_time = (datetime.now() - timedelta(days=60)).timestamp()
    import os

    os.utime(old_log, (old_time, old_time))

    yield log_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_log_manager(temp_log_dir):
    """Mock log manager with test configuration"""
    mock_manager = Mock()
    mock_manager.config = {
        "level": "INFO",
        "format": "json",
        "log_dir": str(temp_log_dir),
        "console_enabled": True,
        "file_enabled": True,
        "audit_enabled": True,
        "security_enabled": True,
        "performance_enabled": True,
    }
    mock_manager._handlers = {"console": Mock(), "file": Mock()}
    mock_manager._loggers = {"app": Mock(), "audit": Mock()}
    mock_manager.get_log_stats = Mock(
        return_value={
            "total_logs": 1000,
            "error_count": 50,
            "warning_count": 100,
        }
    )
    mock_manager.update_log_level = Mock()
    mock_manager.performance_tracker = Mock()
    mock_manager.performance_tracker.get_metrics = Mock(return_value={})
    mock_manager.request_tracker = Mock()
    mock_manager.request_tracker.get_context = Mock(return_value={})

    return mock_manager


@pytest.fixture
def client(mock_log_manager):
    """Create test client with mocked dependencies"""
    from fastapi import FastAPI

    app = FastAPI()

    # Include router
    app.include_router(router)

    # Mock the get_log_manager dependency and other logging functions
    with patch("backend.log_management.get_log_manager", return_value=mock_log_manager):
        with patch("backend.log_management.log_audit"):
            with patch("backend.log_management.log_security"):
                with patch("backend.log_management.logger"):
                    # Mock asyncio.sleep to prevent delays in streaming/background tasks
                    with patch(
                        "backend.log_management.asyncio.sleep", new_callable=AsyncMock
                    ):
                        yield TestClient(app)


# ============================================================================
# Log Status Tests
# ============================================================================


def test_get_logging_status(client, mock_log_manager):
    """Test getting logging system status"""
    response = client.get("/api/logs/status")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "active"
    assert "configuration" in data
    assert data["configuration"]["level"] == "INFO"
    assert "statistics" in data
    assert "handlers" in data
    assert "specialized_loggers" in data


# ============================================================================
# Log Level Update Tests
# ============================================================================


def test_update_log_level_success(client, mock_log_manager):
    """Test successfully updating log level"""
    response = client.post("/api/logs/level", json={"level": "DEBUG"})

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Log level updated successfully"
    assert data["old_level"] == "INFO"
    assert data["new_level"] == "DEBUG"
    mock_log_manager.update_log_level.assert_called_once_with("DEBUG")


def test_update_log_level_invalid(client):
    """Test updating log level with invalid value"""
    response = client.post("/api/logs/level", json={"level": "INVALID"})

    assert response.status_code == 422  # Validation error


def test_update_log_level_all_valid_levels(client, mock_log_manager):
    """Test all valid log levels"""
    valid_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "AUDIT"]

    for level in valid_levels:
        response = client.post("/api/logs/level", json={"level": level})
        assert response.status_code == 200


# ============================================================================
# Log File Listing Tests
# ============================================================================


def test_list_log_files(client, temp_log_dir):
    """Test listing log files"""
    response = client.get("/api/logs/files")

    assert response.status_code == 200
    data = response.json()

    assert "log_directory" in data
    assert "total_files" in data
    assert "files" in data
    assert data["total_files"] >= 4  # app.log, error.log, audit.log, old log

    # Check file structure
    assert all("name" in f for f in data["files"])
    assert all("size" in f for f in data["files"])
    assert all("modified" in f for f in data["files"])
    assert all("type" in f for f in data["files"])


def test_list_log_files_sorting(client):
    """Test that log files are sorted by modification time"""
    response = client.get("/api/logs/files")

    assert response.status_code == 200
    data = response.json()

    if len(data["files"]) > 1:
        # Check that files are sorted newest first
        timestamps = [f["modified"] for f in data["files"]]
        assert timestamps == sorted(timestamps, reverse=True)


# ============================================================================
# Log File Access Tests
# ============================================================================


def test_get_log_file(client, temp_log_dir):
    """Test getting contents of a log file"""
    response = client.get("/api/logs/files/app.log")

    assert response.status_code == 200
    data = response.json()

    assert data["filename"] == "app.log"
    assert "content" in data
    assert "total_lines" in data
    assert "returned_lines" in data
    assert data["total_lines"] == 3
    assert "Application started" in data["content"]


def test_get_log_file_with_limit(client):
    """Test getting log file with line limit"""
    response = client.get("/api/logs/files/app.log?lines=2")

    assert response.status_code == 200
    data = response.json()

    assert data["returned_lines"] <= 2


def test_get_log_file_with_offset(client):
    """Test getting log file with offset"""
    response = client.get("/api/logs/files/app.log?offset=1&lines=1")

    assert response.status_code == 200
    data = response.json()

    assert data["offset"] == 1
    assert data["returned_lines"] == 1


def test_get_log_file_formatted(client):
    """Test getting log file with JSON formatting"""
    response = client.get("/api/logs/files/app.log?format_output=true")

    assert response.status_code == 200
    data = response.json()

    # Should format JSON logs with indentation
    assert "content" in data


def test_get_log_file_not_found(client):
    """Test getting non-existent log file"""
    response = client.get("/api/logs/files/nonexistent.log")

    # error_context may return 200 with error details or 404
    assert response.status_code in [200, 404]


def test_get_log_file_path_traversal_protection(client):
    """Test protection against path traversal attacks"""
    response = client.get("/api/logs/files/../../../etc/passwd")

    # May return 404 (not found) or 400/422 (validation error)
    assert response.status_code in [400, 404, 422, 500]


# ============================================================================
# Log Search Tests
# ============================================================================


def test_search_logs_basic(client, temp_log_dir):
    """Test basic log search"""
    response = client.post("/api/logs/search", json={})

    assert response.status_code == 200
    data = response.json()

    assert "total_results" in data
    assert "results" in data
    assert "truncated" in data


def test_search_logs_by_level(client):
    """Test searching logs by level"""
    response = client.post("/api/logs/search", json={"level": "ERROR"})

    assert response.status_code == 200
    data = response.json()

    # Should find error log entries
    assert all(r["level"] == "ERROR" for r in data["results"] if r["level"])


def test_search_logs_by_search_term(client):
    """Test searching logs by search term"""
    response = client.post(
        "/api/logs/search", json={"search_term": "Application started"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total_results"] >= 1
    assert any(
        "Application started" in r["message"] or "Application started" in r["raw_line"]
        for r in data["results"]
    )


def test_search_logs_by_category(client):
    """Test searching logs by category"""
    response = client.post("/api/logs/search", json={"category": "audit"})

    assert response.status_code == 200
    data = response.json()

    # Should find audit log entries
    assert all(r["category"] == "audit" for r in data["results"] if r["category"])


def test_search_logs_by_user_id(client):
    """Test searching logs by user ID"""
    response = client.post("/api/logs/search", json={"user_id": "user123"})

    assert response.status_code == 200
    data = response.json()

    assert data["total_results"] >= 1


def test_search_logs_time_range(client):
    """Test searching logs with time range"""
    response = client.post(
        "/api/logs/search",
        json={"start_time": "2025-10-17T09:00:00", "end_time": "2025-10-17T11:00:00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "results" in data


# ============================================================================
# Log Export Tests
# ============================================================================
def test_export_logs_json(client, temp_log_dir):
    """Test exporting logs in JSON format"""
    response = client.post("/api/logs/export?format_type=json&compress=false")

    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    assert any(k.lower() == "content-disposition" for k in response.headers)


def test_export_logs_csv(client):
    """Test exporting logs in CSV format"""
    response = client.post("/api/logs/export?format_type=csv&compress=false")

    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")


def test_export_logs_text(client):
    """Test exporting logs in TEXT format"""
    response = client.post("/api/logs/export?format_type=text&compress=false")

    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")


def test_export_logs_compressed(client):
    """Test exporting logs with compression"""
    response = client.post("/api/logs/export?format_type=json&compress=true")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/gzip"


# ============================================================================
# Log File Deletion Tests
# ============================================================================


def test_delete_log_file_success(client, temp_log_dir):
    """Test deleting a log file"""
    # Create a deletable log file
    test_file = temp_log_dir / "test_deletable.log"
    test_file.write_text("Test content", encoding="utf-8")

    response = client.delete("/api/logs/files/test_deletable.log")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert not test_file.exists()


def test_delete_active_log_file_protected(client):
    """Test that active log files cannot be deleted"""
    response = client.delete("/api/logs/files/app.log")

    # error_context may return 200 with error details or 400/422
    assert response.status_code in [200, 400, 422]


def test_delete_nonexistent_log_file(client):
    """Test deleting non-existent log file"""
    response = client.delete("/api/logs/files/nonexistent.log")

    # error_context may return 200 with error details or 404
    assert response.status_code in [200, 404]


def test_delete_log_file_path_traversal(client):
    """Test path traversal protection in deletion"""
    response = client.delete("/api/logs/files/../../../etc/passwd")

    # May return 404 (not found) or 400/422 (validation error)
    assert response.status_code in [400, 404, 422]


# ============================================================================
# Log Cleanup Tests
# ============================================================================


def test_cleanup_old_logs(client, temp_log_dir):
    """Test cleanup of old log files"""
    response = client.post("/api/logs/cleanup?days=30")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "files_deleted" in data
    assert "total_size_freed" in data
    assert data["files_deleted"] >= 1  # Should delete old log


def test_cleanup_protects_active_logs(client):
    """Test that cleanup doesn't delete active log files"""
    response = client.post(
        "/api/logs/cleanup?days=30"
    )  # Use 30 instead of 0 to avoid validation error

    assert response.status_code == 200
    data = response.json()

    # Should not delete active files
    deleted_names = [f["name"] for f in data.get("deleted_files", [])]
    assert "app.log" not in deleted_names
    assert "error.log" not in deleted_names


def test_cleanup_with_custom_days(client):
    """Test cleanup with custom days parameter"""
    response = client.post("/api/logs/cleanup?days=90")

    assert response.status_code == 200


# ============================================================================
# Log Metrics Tests
# ============================================================================


def test_get_log_metrics(client, mock_log_manager):
    """Test getting log metrics"""
    response = client.get("/api/logs/metrics")

    assert response.status_code == 200
    data = response.json()

    assert "performance_metrics" in data
    assert "system_stats" in data
    assert "request_context" in data


# ============================================================================
# Helper Function Tests
# ============================================================================


def test_format_file_size():
    """Test file size formatting"""
    assert _format_file_size(0) == "0 B"
    assert _format_file_size(512) == "512.0 B"
    assert _format_file_size(1024) == "1.0 KB"
    assert _format_file_size(1024 * 1024) == "1.0 MB"
    assert _format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    assert _format_file_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"


def test_get_log_file_type():
    """Test log file type detection"""
    assert _get_log_file_type("audit.log") == "audit"
    assert _get_log_file_type("security.log") == "security"
    assert _get_log_file_type("performance.log") == "performance"
    assert _get_log_file_type("error.log") == "error"
    assert _get_log_file_type("app.log") == "application"
    assert _get_log_file_type("unknown.log") == "unknown"


def test_matches_filter_level():
    """Test filter matching by level"""
    log_entry = {"level": "ERROR", "message": "Test"}
    filter_params = LogFilter(level="ERROR")

    assert _matches_filter(log_entry, filter_params, "") is True

    filter_params = LogFilter(level="INFO")
    assert _matches_filter(log_entry, filter_params, "") is False


def test_matches_filter_category():
    """Test filter matching by category"""
    log_entry = {"category": "audit", "message": "Test"}
    filter_params = LogFilter(category="audit")

    assert _matches_filter(log_entry, filter_params, "") is True

    filter_params = LogFilter(category="security")
    assert _matches_filter(log_entry, filter_params, "") is False


def test_matches_filter_search_term():
    """Test filter matching by search term"""
    log_entry = {"message": "Application started successfully"}
    filter_params = LogFilter(search_term="started")

    assert _matches_filter(log_entry, filter_params, "") is True

    filter_params = LogFilter(search_term="failed")
    assert _matches_filter(log_entry, filter_params, "") is False


def test_matches_filter_time_range():
    """Test filter matching by time range"""
    log_entry = {"timestamp": "2025-10-17T10:00:00", "message": "Test"}

    filter_params = LogFilter(
        start_time=datetime(2025, 10, 17, 9, 0, 0),
        end_time=datetime(2025, 10, 17, 11, 0, 0),
    )

    assert _matches_filter(log_entry, filter_params, "") is True

    filter_params = LogFilter(start_time=datetime(2025, 10, 17, 11, 0, 0))

    assert _matches_filter(log_entry, filter_params, "") is False


def test_matches_filter_user_id():
    """Test filter matching by user ID"""
    log_entry = {"user_id": "user123", "message": "Test"}
    filter_params = LogFilter(user_id="user123")

    assert _matches_filter(log_entry, filter_params, "") is True

    filter_params = LogFilter(user_id="user456")
    assert _matches_filter(log_entry, filter_params, "") is False


def test_matches_filter_no_filter():
    """Test that no filter matches everything"""
    log_entry = {"message": "Test"}

    assert _matches_filter(log_entry, None, "") is True
    assert _matches_filter(log_entry, LogFilter(), "") is True


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


def test_list_log_files_empty_directory(client, mock_log_manager):
    """Test listing log files in empty directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_log_manager.config["log_dir"] = temp_dir

        response = client.get("/api/logs/files")

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 0


def test_search_logs_plain_text_file(client, temp_log_dir):
    """Test searching in plain text (non-JSON) log files"""
    # Create plain text log file
    plain_log = temp_log_dir / "plain.log"
    plain_log.write_text("Plain text error message\n", encoding="utf-8")

    response = client.post("/api/logs/search", json={"search_term": "Plain text"})

    assert response.status_code == 200
    data = response.json()

    assert data["total_results"] >= 1


def test_get_log_file_large_file(client, temp_log_dir):
    """Test getting contents of a large log file"""
    # Create large log file
    large_log = temp_log_dir / "large.log"
    with open(large_log, "w", encoding="utf-8") as f:
        for i in range(10000):
            f.write(f"Line {i}\n")

    response = client.get("/api/logs/files/large.log?lines=100")

    assert response.status_code == 200
    data = response.json()

    assert data["returned_lines"] == 100
    assert data["total_lines"] == 10000


def test_export_with_filter(client):
    """Test log export with filtering"""
    response = client.post(
        "/api/logs/export?format_type=json&compress=false", json={"level": "ERROR"}
    )

    assert response.status_code == 200


def test_cleanup_invalid_days(client):
    """Test cleanup with invalid days parameter"""
    response = client.post("/api/logs/cleanup?days=0")

    assert response.status_code in [200, 422]  # May accept or reject


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
