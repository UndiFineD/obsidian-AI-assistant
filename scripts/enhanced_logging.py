#!/usr/bin/env python3
"""
Enhanced Logging Module for Workflow Troubleshooting

Provides structured logging, context tracking, and diagnostic information
for workflow execution and debugging.

Features:
- Structured JSON logging
- Context-aware logging with workflow state
- Performance metrics tracking
- Diagnostic data collection
- Log rotation and archival
- Real-time troubleshooting suggestions

Author: Obsidian AI Agent Team
License: MIT
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import asdict, dataclass, field


@dataclass
class LogContext:
    """Context information for logging"""
    workflow_id: str
    lane: str
    stage_id: Optional[int] = None
    stage_name: Optional[str] = None
    user: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    additional: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = {
            "workflow_id": self.workflow_id,
            "lane": self.lane,
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "user": self.user,
            "environment": self.environment,
            "version": self.version,
        }
        data.update(self.additional)
        return {k: v for k, v in data.items() if v is not None}


class StructuredLogger:
    """Provides structured logging with context"""

    def __init__(self, name: str, log_dir: Path):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.context: Optional[LogContext] = None
        self.logger = logging.getLogger(name)
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers"""
        # JSON file handler
        json_handler = logging.FileHandler(
            self.log_dir / f"{self.name}-structured.jsonl"
        )
        json_handler.setFormatter(
            logging.Formatter("%(message)s")
        )

        # Text file handler
        text_handler = logging.FileHandler(
            self.log_dir / f"{self.name}-details.log"
        )
        text_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        text_handler.setFormatter(text_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(levelname)s: %(message)s"
        )
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(json_handler)
        self.logger.addHandler(text_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

        self.json_handler = json_handler

    def set_context(self, context: LogContext):
        """Set logging context"""
        self.context = context

    def _create_log_entry(
        self,
        level: str,
        message: str,
        **kwargs
    ) -> str:
        """Create a structured log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        }

        if self.context:
            entry["context"] = self.context.to_dict()

        entry.update(kwargs)

        return json.dumps(entry)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(
            self._create_log_entry("DEBUG", message, **kwargs),
            extra={"skip_json": True}
        )

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(
            self._create_log_entry("INFO", message, **kwargs),
            extra={"skip_json": True}
        )

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(
            self._create_log_entry("WARNING", message, **kwargs),
            extra={"skip_json": True}
        )

    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message"""
        entry_kwargs = kwargs.copy()
        if exception:
            entry_kwargs["exception"] = str(exception)
            entry_kwargs["exception_type"] = type(exception).__name__

        self.logger.error(
            self._create_log_entry("ERROR", message, **entry_kwargs),
            extra={"skip_json": True}
        )

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(
            self._create_log_entry("CRITICAL", message, **kwargs),
            extra={"skip_json": True}
        )

    def log_performance(
        self,
        operation: str,
        duration_seconds: float,
        status: str = "completed",
        **kwargs
    ):
        """Log performance metrics"""
        self.info(
            f"Performance: {operation}",
            operation=operation,
            duration_seconds=duration_seconds,
            status=status,
            **kwargs
        )

    def log_stage_execution(
        self,
        stage_id: int,
        stage_name: str,
        result: str,
        duration_seconds: float,
        details: Optional[Dict] = None
    ):
        """Log stage execution details"""
        self.info(
            f"Stage execution: {stage_name}",
            stage_id=stage_id,
            stage_name=stage_name,
            result=result,
            duration_seconds=duration_seconds,
            details=details or {}
        )

    def get_diagnostic_summary(self) -> Dict:
        """Get diagnostic summary of recent logs"""
        return {
            "log_directory": str(self.log_dir),
            "context": self.context.to_dict() if self.context else None,
            "handlers": [
                {
                    "type": type(h).__name__,
                    "level": logging.getLevelName(h.level)
                }
                for h in self.logger.handlers
            ]
        }


class DiagnosticCollector:
    """Collects diagnostic information for troubleshooting"""

    @staticmethod
    def collect_environment_info() -> Dict:
        """Collect environment information"""
        import platform
        import os

        return {
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "processor": platform.processor(),
            "user": os.getenv("USER") or os.getenv("USERNAME"),
            "cwd": os.getcwd(),
        }

    @staticmethod
    def collect_workflow_state(status_file: Path) -> Dict:
        """Collect workflow state from status file"""
        if not status_file.exists():
            return {"status": "no_status_file"}

        try:
            with open(status_file) as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def collect_system_resources() -> Dict:
        """Collect system resource information"""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "cpu_count": os.cpu_count(),
            }
        except Exception:
            return {"status": "unavailable"}

    @staticmethod
    def generate_diagnostic_report(
        log_dir: Path,
        status_file: Path
    ) -> Dict:
        """Generate comprehensive diagnostic report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "environment": DiagnosticCollector.collect_environment_info(),
            "workflow_state": DiagnosticCollector.collect_workflow_state(status_file),
            "system_resources": DiagnosticCollector.collect_system_resources(),
            "log_files": [
                str(f) for f in log_dir.glob("*.log")
            ] if log_dir.exists() else [],
        }


class TroubleshootingSuggestions:
    """Provides troubleshooting suggestions based on common issues"""

    SUGGESTIONS = {
        "timeout": "Check if the operation is taking longer than expected. "
                  "Try increasing the timeout or splitting the operation.",
        "module_not_found": "Install missing module: pip install -r requirements.txt",
        "permission_denied": "Check file permissions or run with appropriate privileges",
        "network_error": "Check network connectivity and retry",
        "git_error": "Verify git is installed and repository is accessible",
        "github_cli_error": "Install GitHub CLI (gh) or use manual PR creation",
    }

    @staticmethod
    def get_suggestion(error_message: str) -> Optional[str]:
        """Get troubleshooting suggestion for an error"""
        error_lower = error_message.lower()

        for error_type, suggestion in TroubleshootingSuggestions.SUGGESTIONS.items():
            if error_type in error_lower:
                return suggestion

        return None

    @staticmethod
    def format_diagnostic_help(diagnostic_report: Dict) -> str:
        """Format diagnostic report for user display"""
        output = "=== Workflow Diagnostic Report ===\n"
        output += f"Generated: {diagnostic_report.get('timestamp')}\n\n"

        output += "Environment:\n"
        env = diagnostic_report.get("environment", {})
        for key, value in env.items():
            output += f"  {key}: {value}\n"

        output += "\nSystem Resources:\n"
        resources = diagnostic_report.get("system_resources", {})
        for key, value in resources.items():
            output += f"  {key}: {value}\n"

        return output
