"""
Logging Management API

Provides REST endpoints for logging configuration, monitoring, and analysis.
Integrates with the comprehensive logging framework to provide:
- Dynamic log level configuration
- Log file access and streaming
- Log statistics and metrics
- Log filtering and search
- Log export and archiving
- Real-time log monitoring
"""

import asyncio
import gzip
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from .error_handling import ConfigurationError, ValidationError, error_context
from .logging_framework import (
    LogCategory,
    get_log_manager,
    get_logger,
    log_audit,
    log_security,
)

# Create logger for this module
logger = get_logger(__name__, LogCategory.API)

# Create router
router = APIRouter(prefix="/api/logs", tags=["logging"])


class LogLevelUpdate(BaseModel):
    """Request model for log level updates"""

    level: str = Field(
        ...,
        description="New log level",
        pattern=r"^(TRACE|DEBUG|INFO|WARNING|ERROR|CRITICAL|AUDIT)$",
    )


class LogFilter(BaseModel):
    """Request model for log filtering"""

    level: Optional[str] = Field(None, description="Filter by log level")
    category: Optional[str] = Field(None, description="Filter by log category")
    logger_name: Optional[str] = Field(None, description="Filter by logger name")
    start_time: Optional[datetime] = Field(None, description="Filter from start time")
    end_time: Optional[datetime] = Field(None, description="Filter to end time")
    search_term: Optional[str] = Field(None, description="Search term in log messages")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    request_id: Optional[str] = Field(None, description="Filter by request ID")


class LogExportFormat(str, Enum):
    """Supported log export formats"""

    JSON = "json"
    CSV = "csv"
    TEXT = "text"


class LogStreamOptions(BaseModel):
    """Options for log streaming"""

    follow: bool = Field(False, description="Follow log file (tail -f behavior)")
    lines: int = Field(100, description="Number of lines to return", ge=1, le=10000)
    level_filter: Optional[str] = Field(None, description="Filter by minimum log level")


@router.get("/status")
async def get_logging_status():
    """Get current logging system status and configuration"""
    with error_context("get_logging_status", reraise=False):
        log_manager = get_log_manager()
        stats = log_manager.get_log_stats()

        return {
            "status": "active",
            "configuration": {
                "level": log_manager.config["level"],
                "format": log_manager.config["format"],
                "log_directory": log_manager.config["log_dir"],
                "console_enabled": log_manager.config["console_enabled"],
                "file_enabled": log_manager.config["file_enabled"],
                "audit_enabled": log_manager.config["audit_enabled"],
                "security_enabled": log_manager.config["security_enabled"],
                "performance_enabled": log_manager.config["performance_enabled"],
            },
            "statistics": stats,
            "handlers": list(log_manager._handlers.keys()),
            "specialized_loggers": list(log_manager._loggers.keys()),
        }


@router.post("/level")
async def update_log_level(level_update: LogLevelUpdate):
    """Update the system log level dynamically"""
    with error_context("update_log_level", reraise=False):
        log_manager = get_log_manager()

        try:
            old_level = log_manager.config["level"]
            log_manager.update_log_level(level_update.level)

            # Log the change for audit
            log_audit(
                "log_level_changed",
                action="update_log_level",
                old_level=old_level,
                new_level=level_update.level,
                outcome="success",
            )

            logger.info(f"Log level updated from {old_level} to {level_update.level}")

            return {
                "message": "Log level updated successfully",
                "old_level": old_level,
                "new_level": level_update.level,
            }

        except ValueError as e:
            raise ValidationError(
                str(e),
                field="level",
                suggestion="Use valid log level: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL, AUDIT",
            )


@router.get("/files")
async def list_log_files():
    """List available log files with metadata"""
    with error_context("list_log_files", reraise=False):
        log_manager = get_log_manager()
        log_dir = Path(log_manager.config["log_dir"])

        if not log_dir.exists():
            raise ConfigurationError(
                "Log directory does not exist", config_key="log_dir"
            )

        files = []
        for log_file in log_dir.glob("*.log*"):
            if log_file.is_file():
                stat = log_file.stat()
                files.append(
                    {
                        "name": log_file.name,
                        "path": str(log_file),
                        "size": stat.st_size,
                        "size_human": _format_file_size(stat.st_size),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": _get_log_file_type(log_file.name),
                    }
                )

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)

        return {
            "log_directory": str(log_dir),
            "total_files": len(files),
            "total_size": sum(f["size"] for f in files),
            "total_size_human": _format_file_size(sum(f["size"] for f in files)),
            "files": files,
        }


@router.get("/files/{filename}")
async def get_log_file(
    filename: str,
    lines: int = Query(1000, description="Number of lines to return", ge=1, le=50000),
    offset: int = Query(0, description="Line offset to start from", ge=0),
    format_output: bool = Query(False, description="Format JSON logs for readability"),
):
    """Get contents of a specific log file"""
    with error_context("get_log_file", reraise=False):
        log_manager = get_log_manager()
        log_dir = Path(log_manager.config["log_dir"])
        log_file = log_dir / filename

        # Security check: ensure file is within log directory
        if not log_file.resolve().is_relative_to(log_dir.resolve()):
            raise ValidationError(
                "Invalid file path",
                field="filename",
                suggestion="Provide a valid log file name",
            )

        if not log_file.exists():
            raise HTTPException(status_code=404, detail="Log file not found")

        try:
            # Read file content
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()

            # Apply offset and limit
            start_idx = offset
            end_idx = min(offset + lines, len(all_lines))
            selected_lines = all_lines[start_idx:end_idx]

            # Format JSON logs if requested
            if format_output and filename.endswith(".log"):
                formatted_lines = []
                for line in selected_lines:
                    line = line.strip()
                    if line:
                        try:
                            # Try to parse as JSON and format
                            json_obj = json.loads(line)
                            formatted_lines.append(json.dumps(json_obj, indent=2))
                        except json.JSONDecodeError:
                            # Not JSON, keep as is
                            formatted_lines.append(line)
                content = "\n".join(formatted_lines)
            else:
                content = "".join(selected_lines)

            return {
                "filename": filename,
                "total_lines": len(all_lines),
                "returned_lines": len(selected_lines),
                "offset": offset,
                "content": content,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error reading log file: {str(e)}"
            )


@router.get("/stream/{filename}")
async def stream_log_file(
    filename: str,
    follow: bool = Query(False, description="Follow file (tail -f behavior)"),
    lines: int = Query(100, description="Initial number of lines", ge=1, le=1000),
):
    """Stream log file contents with optional follow mode"""
    with error_context("stream_log_file", reraise=False):
        log_manager = get_log_manager()
        log_dir = Path(log_manager.config["log_dir"])
        log_file = log_dir / filename

        # Security check
        if not log_file.resolve().is_relative_to(log_dir.resolve()):
            raise ValidationError("Invalid file path", field="filename")

        if not log_file.exists():
            raise HTTPException(status_code=404, detail="Log file not found")

        async def generate_stream():
            try:
                # Read initial lines
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    all_lines = f.readlines()
                    if len(all_lines) > lines:
                        initial_lines = all_lines[-lines:]
                    else:
                        initial_lines = all_lines

                    for line in initial_lines:
                        yield f"data: {json.dumps({'line': line.rstrip()})}\n\n"

                if follow:
                    # Follow mode: watch for new lines
                    last_size = log_file.stat().st_size

                    while True:
                        await asyncio.sleep(1)  # Check every second

                        try:
                            current_size = log_file.stat().st_size
                            if current_size > last_size:
                                with open(
                                    log_file, "r", encoding="utf-8", errors="ignore"
                                ) as f:
                                    f.seek(last_size)
                                    new_content = f.read()
                                    for line in new_content.splitlines():
                                        yield f"data: {json.dumps({'line': line})}\n\n"
                                last_size = current_size
                        except FileNotFoundError:
                            # File was removed/rotated
                            break
                        except Exception as e:
                            yield f"data: {json.dumps({'error': str(e)})}\n\n"
                            break

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable Nginx buffering
            },
        )


@router.post("/search")
async def search_logs(filter_params: LogFilter):
    """Search logs with advanced filtering"""
    with error_context("search_logs", reraise=False):
        log_manager = get_log_manager()
        log_dir = Path(log_manager.config["log_dir"])

        if not log_dir.exists():
            raise ConfigurationError("Log directory does not exist")

        results = []

        # Search through log files
        for log_file in log_dir.glob("*.log"):
            if not log_file.is_file():
                continue

            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue

                        # Try to parse as JSON for structured filtering
                        try:
                            log_entry = json.loads(line)
                            if _matches_filter(log_entry, filter_params, line):
                                results.append(
                                    {
                                        "file": log_file.name,
                                        "line_number": line_num,
                                        "timestamp": log_entry.get("timestamp", ""),
                                        "level": log_entry.get("level", ""),
                                        "logger": log_entry.get("logger", ""),
                                        "message": log_entry.get("message", ""),
                                        "category": log_entry.get("category", ""),
                                        "raw_line": line,
                                    }
                                )
                        except json.JSONDecodeError:
                            # Plain text log, search in content
                            if (
                                filter_params.search_term
                                and filter_params.search_term.lower() in line.lower()
                            ):
                                results.append(
                                    {
                                        "file": log_file.name,
                                        "line_number": line_num,
                                        "timestamp": "",
                                        "level": "",
                                        "logger": "",
                                        "message": line,
                                        "category": "",
                                        "raw_line": line,
                                    }
                                )

                        # Limit results to prevent memory issues
                        if len(results) >= 10000:
                            break

            except Exception as e:
                logger.warning(f"Error searching log file {log_file}: {e}")
                continue

        # Sort results by timestamp if available
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "total_results": len(results),
            "results": results[:1000],  # Limit to 1000 results for API response
            "truncated": len(results) > 1000,
        }


@router.post("/export")
async def export_logs(
    background_tasks: BackgroundTasks,
    format_type: LogExportFormat = LogExportFormat.JSON,
    filter_params: Optional[LogFilter] = None,
    compress: bool = Query(True, description="Compress exported file"),
):
    """Export logs in various formats"""
    with error_context("export_logs", reraise=False):
        log_manager = get_log_manager()
        log_dir = Path(log_manager.config["log_dir"])

        if not log_dir.exists():
            raise ConfigurationError("Log directory does not exist")

        # Create export filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"logs_export_{timestamp}"

        if format_type == LogExportFormat.JSON:
            filename = f"{base_filename}.json"
            media_type = "application/json"
        elif format_type == LogExportFormat.CSV:
            filename = f"{base_filename}.csv"
            media_type = "text/csv"
        else:  # TEXT
            filename = f"{base_filename}.txt"
            media_type = "text/plain"

        if compress:
            filename += ".gz"
            media_type = "application/gzip"

        # Create temporary export file
        export_path = log_dir / filename

        try:
            if compress:
                with gzip.open(export_path, "wt", encoding="utf-8") as export_file:
                    _write_export_data(export_file, log_dir, format_type, filter_params)
            else:
                with open(export_path, "w", encoding="utf-8") as export_file:
                    _write_export_data(export_file, log_dir, format_type, filter_params)

            # Log the export
            log_audit(
                "logs_exported",
                action="export_logs",
                format=format_type.value,
                compressed=compress,
                file_size=export_path.stat().st_size,
                outcome="success",
            )

            # Schedule cleanup of export file after 1 hour
            background_tasks.add_task(_cleanup_export_file, export_path)

            return FileResponse(
                path=export_path,
                media_type=media_type,
                filename=filename,
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )

        except Exception as e:
            if export_path.exists():
                export_path.unlink()
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.delete("/files/{filename}")
async def delete_log_file(filename: str):
    """Delete a specific log file"""
    with error_context("delete_log_file", reraise=False):
        log_manager = get_log_manager()
        log_dir = Path(log_manager.config["log_dir"])
        log_file = log_dir / filename

        # Security check
        if not log_file.resolve().is_relative_to(log_dir.resolve()):
            raise ValidationError("Invalid file path", field="filename")

        if not log_file.exists():
            raise HTTPException(status_code=404, detail="Log file not found")

        # Prevent deletion of active log files
        active_files = [
            "app.log",
            "error.log",
            "audit.log",
            "security.log",
            "performance.log",
        ]
        if filename in active_files:
            raise ValidationError("Cannot delete active log file", field="filename")

        try:
            file_size = log_file.stat().st_size
            log_file.unlink()

            # Log the deletion
            log_audit(
                "log_file_deleted",
                action="delete_log_file",
                filename=filename,
                file_size=file_size,
                outcome="success",
            )

            log_security(
                "log_file_deleted",
                severity="low",
                filename=filename,
                file_size=file_size,
            )

            logger.info(f"Log file deleted: {filename}")

            return {"message": f"Log file {filename} deleted successfully"}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete log file: {str(e)}"
            )


@router.post("/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, description="Delete logs older than N days", ge=1, le=365),
):
    """Clean up old log files"""
    with error_context("cleanup_old_logs", reraise=False):
        log_manager = get_log_manager()
        log_dir = Path(log_manager.config["log_dir"])

        if not log_dir.exists():
            raise ConfigurationError("Log directory does not exist")

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_files = []
        total_size_freed = 0

        for log_file in log_dir.glob("*.log*"):
            if not log_file.is_file():
                continue

            try:
                file_stat = log_file.stat()
                file_date = datetime.fromtimestamp(file_stat.st_mtime)

                if file_date < cutoff_date:
                    # Don't delete active log files
                    active_files = [
                        "app.log",
                        "error.log",
                        "audit.log",
                        "security.log",
                        "performance.log",
                    ]
                    if log_file.name in active_files:
                        continue

                    file_size = file_stat.st_size
                    log_file.unlink()

                    deleted_files.append(
                        {
                            "name": log_file.name,
                            "size": file_size,
                            "modified": file_date.isoformat(),
                        }
                    )
                    total_size_freed += file_size

            except Exception as e:
                logger.warning(f"Error deleting log file {log_file}: {e}")

        # Log the cleanup
        log_audit(
            "log_cleanup_performed",
            action="cleanup_old_logs",
            cutoff_days=days,
            files_deleted=len(deleted_files),
            size_freed=total_size_freed,
            outcome="success",
        )

        logger.info(
            f"Log cleanup completed: {len(deleted_files)} files deleted, {_format_file_size(total_size_freed)} freed"
        )

        return {
            "message": "Log cleanup completed",
            "files_deleted": len(deleted_files),
            "total_size_freed": total_size_freed,
            "total_size_freed_human": _format_file_size(total_size_freed),
            "deleted_files": deleted_files,
        }


@router.get("/metrics")
async def get_log_metrics():
    """Get logging metrics and statistics"""
    with error_context("get_log_metrics", reraise=False):
        log_manager = get_log_manager()

        return {
            "performance_metrics": log_manager.performance_tracker.get_metrics(),
            "system_stats": log_manager.get_log_stats(),
            "request_context": log_manager.request_tracker.get_context(),
        }


# Helper functions


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def _get_log_file_type(filename: str) -> str:
    """Determine log file type from filename"""
    if "audit" in filename:
        return "audit"
    elif "security" in filename:
        return "security"
    elif "performance" in filename:
        return "performance"
    elif "error" in filename:
        return "error"
    elif filename.startswith("app"):
        return "application"
    else:
        return "unknown"


def _matches_filter(
    log_entry: Dict[str, Any], filter_params: LogFilter, raw_line: str
) -> bool:
    """Check if log entry matches filter parameters"""
    if not filter_params:
        return True

    # Level filter
    if filter_params.level:
        entry_level = log_entry.get("level", "").upper()
        if entry_level != filter_params.level.upper():
            return False

    # Category filter
    if filter_params.category:
        entry_category = log_entry.get("category", "").lower()
        if entry_category != filter_params.category.lower():
            return False

    # Logger name filter
    if filter_params.logger_name:
        entry_logger = log_entry.get("logger", "").lower()
        if filter_params.logger_name.lower() not in entry_logger:
            return False

    # Time range filter
    if filter_params.start_time or filter_params.end_time:
        timestamp_str = log_entry.get("timestamp", "")
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                if filter_params.start_time and timestamp < filter_params.start_time:
                    return False
                if filter_params.end_time and timestamp > filter_params.end_time:
                    return False
            except ValueError:
                pass

    # Search term filter
    if filter_params.search_term:
        search_term = filter_params.search_term.lower()
        message = log_entry.get("message", "").lower()
        if search_term not in message and search_term not in raw_line.lower():
            return False

    # User ID filter
    if filter_params.user_id:
        entry_user_id = log_entry.get("user_id", "")
        if entry_user_id != filter_params.user_id:
            return False

    # Request ID filter
    if filter_params.request_id:
        entry_request_id = log_entry.get("request_id", "")
        if entry_request_id != filter_params.request_id:
            return False

    return True


def _write_export_data(
    export_file,
    log_dir: Path,
    format_type: LogExportFormat,
    filter_params: Optional[LogFilter],
):
    """Write log data to export file in specified format"""
    entries = []

    # Collect log entries
    for log_file in log_dir.glob("*.log"):
        if not log_file.is_file():
            continue

        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        log_entry = json.loads(line)
                        if _matches_filter(log_entry, filter_params, line):
                            log_entry["source_file"] = log_file.name
                            entries.append(log_entry)
                    except json.JSONDecodeError:
                        if (
                            not filter_params
                            or not filter_params.search_term
                            or filter_params.search_term.lower() in line.lower()
                        ):
                            entries.append(
                                {
                                    "source_file": log_file.name,
                                    "message": line,
                                    "timestamp": "",
                                    "level": "",
                                    "logger": "",
                                }
                            )
        except Exception:
            continue

    # Sort by timestamp
    entries.sort(key=lambda x: x.get("timestamp", ""))

    # Write in requested format
    if format_type == LogExportFormat.JSON:
        json.dump(entries, export_file, indent=2, default=str)
    elif format_type == LogExportFormat.CSV:
        import csv

        if entries:
            fieldnames = set()
            for entry in entries:
                fieldnames.update(entry.keys())
            fieldnames = sorted(fieldnames)

            writer = csv.DictWriter(export_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries)
    else:  # TEXT
        for entry in entries:
            export_file.write(
                f"{entry.get('timestamp', '')} [{entry.get('level', '')}] {entry.get('logger', '')}: {entry.get('message', '')}\n"
            )


async def _cleanup_export_file(file_path: Path):
    """Clean up export file after delay"""
    await asyncio.sleep(3600)  # Wait 1 hour
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass  # Ignore cleanup errors
