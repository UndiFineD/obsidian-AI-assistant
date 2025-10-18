"""
Comprehensive Logging Framework for Obsidian AI Assistant

This module provides:
- Structured logging with JSON output
- PII redaction and data sanitization
- Log rotation and cleanup
- Performance metrics logging
- Request tracing and correlation
- Security event logging
- Audit trail logging
- Multi-level log filtering
- Dynamic log level configuration
- Log aggregation and analysis
"""

import json
import logging
import logging.handlers
import os
import re
import sys
import threading
import time
import traceback
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    structlog = None
    STRUCTLOG_AVAILABLE = False


class LogLevel(Enum):
    """Enhanced log levels with semantic meanings"""

    TRACE = 5  # Very detailed diagnostic information
    DEBUG = 10  # Detailed information for diagnosing problems
    INFO = 20  # General operational information
    WARNING = 30  # Warning of potential issues
    ERROR = 40  # Error conditions
    CRITICAL = 50  # Critical errors that may cause system failure
    AUDIT = 60  # Audit trail events (highest priority)


class LogCategory(Enum):
    """Log event categories for filtering and analysis"""

    SYSTEM = "system"  # System startup, shutdown, configuration
    API = "api"  # API requests and responses
    AUTH = "auth"  # Authentication and authorization
    SECURITY = "security"  # Security events and threats
    PERFORMANCE = "performance"  # Performance metrics and monitoring
    ERROR = "error"  # Errors and exceptions
    AUDIT = "audit"  # Audit trail and compliance
    USER = "user"  # User interactions and behavior
    CACHE = "cache"  # Caching operations
    MODEL = "model"  # AI model operations
    DATABASE = "database"  # Database operations
    NETWORK = "network"  # Network operations
    FILE = "file"  # File system operations


@dataclass
class LogContext:
    """Enhanced logging context for structured logging"""

    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    operation: Optional[str] = None
    resource: Optional[str] = None
    category: LogCategory = LogCategory.SYSTEM
    tags: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PIIRedactor:
    """PII data redaction for secure logging"""

    def __init__(self):
        self.pii_patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(
                r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
            ),
            "ssn": re.compile(r"\b(?:\d{3}[-.\s]?\d{2}[-.\s]?\d{4}|\d{9})\b"),
            "credit_card": re.compile(r"\b(?:\d{4}[-.\s]?){3}\d{4}\b"),
            "api_key": re.compile(r"\b[A-Za-z0-9]{32,}\b"),
            "jwt_token": re.compile(
                r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
            ),
            "password": re.compile(
                r'(?i)(password|pwd|pass)["\']?\s*[:=]\s*["\']?([^"\s,}]+)'
            ),
            "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
            "file_path": re.compile(r'(?i)(C:\\|/)[^\s<>"]*'),
        }

    def redact_pii(self, text: str) -> str:
        """Redact PII data from text"""
        if not isinstance(text, str):
            return str(text)

        redacted = text
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type == "password":
                redacted = pattern.sub(r"\1: [REDACTED]", redacted)
            else:
                redacted = pattern.sub("[REDACTED]", redacted)

        return redacted

    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact PII data from dictionary"""
        if not isinstance(data, dict):
            return data

        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = self.redact_pii(value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [
                    self.redact_pii(str(item)) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                redacted[key] = value

        return redacted


class PerformanceTracker:
    """Performance metrics tracking for logging"""

    def __init__(self):
        self._start_times: Dict[str, float] = {}
        self._metrics: Dict[str, List[float]] = {}

    def start_timer(self, operation: str) -> str:
        """Start timing an operation"""
        timer_id = f"{operation}_{uuid.uuid4().hex[:8]}"
        self._start_times[timer_id] = time.time()
        return timer_id

    def end_timer(self, timer_id: str) -> float:
        """End timing and return elapsed time"""
        if timer_id not in self._start_times:
            return 0.0

        elapsed = time.time() - self._start_times[timer_id]
        del self._start_times[timer_id]

        # Extract operation name from timer_id
        operation = timer_id.rsplit("_", 1)[0]
        if operation not in self._metrics:
            self._metrics[operation] = []

        self._metrics[operation].append(elapsed)
        return elapsed

    def get_metrics(self, operation: str = None) -> Dict[str, Any]:
        """Get performance metrics"""
        if operation:
            times = self._metrics.get(operation, [])
            if not times:
                return {}

            return {
                "operation": operation,
                "count": len(times),
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "total_time": sum(times),
            }

        return {op: self.get_metrics(op) for op in self._metrics.keys()}


class RequestTracker:
    """Request correlation and tracing"""

    def __init__(self):
        self._local = threading.local()

    def start_request(self, request_id: str = None, user_id: str = None) -> str:
        """Start tracking a request"""
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:12]}"

        self._local.request_id = request_id
        self._local.user_id = user_id
        self._local.start_time = time.time()
        self._local.trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        return request_id

    def get_context(self) -> Dict[str, Any]:
        """Get current request context"""
        return {
            "request_id": getattr(self._local, "request_id", None),
            "user_id": getattr(self._local, "user_id", None),
            "trace_id": getattr(self._local, "trace_id", None),
            "elapsed_time": time.time()
            - getattr(self._local, "start_time", time.time()),
        }

    def end_request(self) -> Dict[str, Any]:
        """End request tracking and return summary"""
        context = self.get_context()

        # Clear local storage
        for attr in ["request_id", "user_id", "start_time", "trace_id"]:
            if hasattr(self._local, attr):
                delattr(self._local, attr)

        return context


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""

    def __init__(self, include_pii: bool = False):
        super().__init__()
        self.pii_redactor = PIIRedactor()
        self.include_pii = include_pii

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        # Create base structured log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
        }

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add custom fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_entry[key] = value

        # Redact PII unless explicitly allowed
        if not self.include_pii:
            log_entry = self.pii_redactor.redact_dict(log_entry)

        return json.dumps(log_entry, default=str, separators=(",", ":"))


class LogManager:
    """Comprehensive logging management system"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.pii_redactor = PIIRedactor()
        self.performance_tracker = PerformanceTracker()
        self.request_tracker = RequestTracker()
        self._loggers: Dict[str, logging.Logger] = {}
        self._handlers: Dict[str, logging.Handler] = {}
        self._initialized = False

        # Default configuration
        self.default_config = {
            "level": "INFO",
            "format": "structured",  # 'structured' or 'text'
            "include_pii": False,
            "log_dir": "./backend/logs",
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "backup_count": 5,
            "rotation_when": "midnight",
            "rotation_interval": 1,
            "console_enabled": True,
            "file_enabled": True,
            "audit_enabled": True,
            "security_enabled": True,
            "performance_enabled": True,
            "cleanup_days": 30,
        }

        # Merge with provided config
        self.config = {**self.default_config, **self.config}

        self._setup_logging()

    def _setup_logging(self):
        """Setup comprehensive logging configuration"""
        if self._initialized:
            return

        # Create log directory
        log_dir = Path(self.config["log_dir"])
        log_dir.mkdir(parents=True, exist_ok=True)

        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(LogLevel, self.config["level"].upper()).value)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Setup console handler
        if self.config["console_enabled"]:
            self._setup_console_handler()

        # Setup file handlers
        if self.config["file_enabled"]:
            self._setup_file_handlers()

        # Setup specialized handlers
        if self.config["audit_enabled"]:
            self._setup_audit_handler()

        if self.config["security_enabled"]:
            self._setup_security_handler()

        if self.config["performance_enabled"]:
            self._setup_performance_handler()

        self._initialized = True

    def _setup_console_handler(self):
        """Setup console logging handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        if self.config["format"] == "structured":
            formatter = StructuredFormatter(include_pii=self.config["include_pii"])
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        self._handlers["console"] = console_handler

    def _setup_file_handlers(self):
        """Setup rotating file handlers"""
        log_dir = Path(self.config["log_dir"])

        # Main application log
        app_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=self.config["max_file_size"],
            backupCount=self.config["backup_count"],
        )
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(
            StructuredFormatter(include_pii=self.config["include_pii"])
        )
        logging.getLogger().addHandler(app_handler)
        self._handlers["app"] = app_handler

        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=self.config["max_file_size"],
            backupCount=self.config["backup_count"],
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            StructuredFormatter(include_pii=self.config["include_pii"])
        )
        logging.getLogger().addHandler(error_handler)
        self._handlers["error"] = error_handler

    def _setup_audit_handler(self):
        """Setup audit logging handler"""
        log_dir = Path(self.config["log_dir"])

        audit_handler = logging.handlers.TimedRotatingFileHandler(
            log_dir / "audit.log",
            when=self.config["rotation_when"],
            interval=self.config["rotation_interval"],
            backupCount=365,  # Keep audit logs for 1 year
        )
        audit_handler.setLevel(LogLevel.AUDIT.value)
        audit_handler.setFormatter(
            StructuredFormatter(include_pii=False)
        )  # Never include PII in audit logs

        # Create audit logger
        audit_logger = logging.getLogger("audit")
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(LogLevel.AUDIT.value)
        audit_logger.propagate = False

        self._loggers["audit"] = audit_logger
        self._handlers["audit"] = audit_handler

    def _setup_security_handler(self):
        """Setup security event logging handler"""
        log_dir = Path(self.config["log_dir"])

        security_handler = logging.handlers.TimedRotatingFileHandler(
            log_dir / "security.log",
            when=self.config["rotation_when"],
            interval=self.config["rotation_interval"],
            backupCount=365,  # Keep security logs for 1 year
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(StructuredFormatter(include_pii=False))

        # Create security logger
        security_logger = logging.getLogger("security")
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.WARNING)
        security_logger.propagate = False

        self._loggers["security"] = security_logger
        self._handlers["security"] = security_handler

    def _setup_performance_handler(self):
        """Setup performance metrics logging handler"""
        log_dir = Path(self.config["log_dir"])

        performance_handler = logging.handlers.TimedRotatingFileHandler(
            log_dir / "performance.log",
            when="H",  # Hourly rotation for performance logs
            interval=1,
            backupCount=48,  # Keep 48 hours of performance logs
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(StructuredFormatter(include_pii=False))

        # Create performance logger
        performance_logger = logging.getLogger("performance")
        performance_logger.addHandler(performance_handler)
        performance_logger.setLevel(logging.INFO)
        performance_logger.propagate = False

        self._loggers["performance"] = performance_logger
        self._handlers["performance"] = performance_handler

    def get_logger(
        self, name: str, category: LogCategory = LogCategory.SYSTEM
    ) -> logging.Logger:
        """Get or create a logger with specified category"""
        logger = logging.getLogger(name)

        # Add category as a filter
        if not hasattr(logger, "_category_filter_added"):
            logger.addFilter(
                lambda record: setattr(record, "category", category.value) or True
            )
            logger._category_filter_added = True

        return logger

    def log_audit_event(
        self,
        event_type: str,
        user_id: str = None,
        resource: str = None,
        action: str = None,
        outcome: str = None,
        **kwargs,
    ):
        """Log audit event for compliance"""
        if "audit" not in self._loggers:
            return

        audit_data = {
            "event_type": event_type,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }

        # Add request context
        audit_data.update(self.request_tracker.get_context())

        self._loggers["audit"].log(
            LogLevel.AUDIT.value, "Audit event", extra=audit_data
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str = "medium",
        threat_level: str = "low",
        **kwargs,
    ):
        """Log security event"""
        if "security" not in self._loggers:
            return

        security_data = {
            "event_type": event_type,
            "severity": severity,
            "threat_level": threat_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }

        # Add request context
        security_data.update(self.request_tracker.get_context())

        level = logging.ERROR if severity == "high" else logging.WARNING
        self._loggers["security"].log(
            level, f"Security event: {event_type}", extra=security_data
        )

    def log_performance_metric(self, operation: str, duration: float, **kwargs):
        """Log performance metric"""
        if "performance" not in self._loggers:
            return

        performance_data = {
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }

        # Add request context
        performance_data.update(self.request_tracker.get_context())

        self._loggers["performance"].info(
            f"Performance: {operation}", extra=performance_data
        )

    @contextmanager
    def performance_timer(self, operation: str, **kwargs):
        """Context manager for timing operations"""
        timer_id = self.performance_tracker.start_timer(operation)
        start_time = time.time()

        try:
            yield timer_id
        finally:
            duration = self.performance_tracker.end_timer(timer_id)
            self.log_performance_metric(operation, duration, **kwargs)

    @contextmanager
    def request_context(self, request_id: str = None, user_id: str = None):
        """Context manager for request tracking"""
        request_id = self.request_tracker.start_request(request_id, user_id)

        try:
            yield request_id
        finally:
            context = self.request_tracker.end_request()
            self.log_audit_event(
                "request_completed",
                user_id=context.get("user_id"),
                request_id=context.get("request_id"),
                duration=context.get("elapsed_time"),
            )

    def cleanup_old_logs(self):
        """Cleanup old log files"""
        log_dir = Path(self.config["log_dir"])
        if not log_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=self.config["cleanup_days"])

        for log_file in log_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
            except OSError:
                pass  # Ignore errors during cleanup

    def update_log_level(self, level: str):
        """Dynamically update log level"""
        try:
            log_level = getattr(LogLevel, level.upper())
            logging.getLogger().setLevel(log_level.value)
            self.config["level"] = level.upper()
        except AttributeError:
            raise ValueError(f"Invalid log level: {level}")

    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        log_dir = Path(self.config["log_dir"])
        stats = {
            "log_directory": str(log_dir),
            "current_level": self.config["level"],
            "handlers": list(self._handlers.keys()),
            "loggers": list(self._loggers.keys()),
        }

        if log_dir.exists():
            log_files = list(log_dir.glob("*.log*"))
            stats["log_files"] = {
                "count": len(log_files),
                "total_size": sum(f.stat().st_size for f in log_files if f.is_file()),
                "files": [
                    {
                        "name": f.name,
                        "size": f.stat().st_size,
                        "modified": datetime.fromtimestamp(
                            f.stat().st_mtime
                        ).isoformat(),
                    }
                    for f in log_files
                    if f.is_file()
                ],
            }

        # Add performance metrics
        stats["performance"] = self.performance_tracker.get_metrics()

        return stats


# Global logging manager instance
_log_manager: Optional[LogManager] = None


def initialize_logging(config: Dict[str, Any] = None) -> LogManager:
    """Initialize the global logging manager"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager(config)
    return _log_manager


def get_log_manager() -> LogManager:
    """Get the global logging manager instance"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


def get_logger(name: str, category: LogCategory = LogCategory.SYSTEM) -> logging.Logger:
    """Get a logger with specified category"""
    return get_log_manager().get_logger(name, category)


# Convenience functions for common logging operations
def log_audit(event_type: str, **kwargs):
    """Log audit event"""
    get_log_manager().log_audit_event(event_type, **kwargs)


def log_security(event_type: str, **kwargs):
    """Log security event"""
    get_log_manager().log_security_event(event_type, **kwargs)


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metric"""
    get_log_manager().log_performance_metric(operation, duration, **kwargs)


def performance_timer(operation: str, **kwargs):
    """Performance timing context manager"""
    return get_log_manager().performance_timer(operation, **kwargs)


def request_context(request_id: str = None, user_id: str = None):
    """Request tracking context manager"""
    return get_log_manager().request_context(request_id, user_id)


# Integration with existing error handling
def setup_error_logging_integration():
    """Setup integration with error handling system"""
    try:
        from .error_handling import ErrorContext

        # Patch ErrorContext to use our logging system
        original_log_error = ErrorContext.log_error

        def enhanced_log_error(self, error: Exception, context: Dict[str, Any] = None):
            # Call original logging
            original_log_error(self, error, context)

            # Add structured logging
            log_manager = get_log_manager()
            logger = log_manager.get_logger("error_handling", LogCategory.ERROR)

            error_data = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
                "traceback": traceback.format_exc(),
            }

            logger.error(f"Error in {self.operation}: {error}", extra=error_data)

            # Log as security event if it's a security-related error
            if "security" in str(error).lower() or "auth" in str(error).lower():
                log_manager.log_security_event(
                    "error_occurred",
                    severity="medium",
                    error_type=type(error).__name__,
                    error_message=str(error),
                    context=context,
                )

        ErrorContext.log_error = enhanced_log_error

    except ImportError:
        pass  # Error handling module not available


# Auto-initialize with default configuration
def _auto_initialize():
    """Auto-initialize logging with environment-based configuration"""
    config = {}

    # Read configuration from environment
    if "LOG_LEVEL" in os.environ:
        config["level"] = os.environ["LOG_LEVEL"]

    if "LOG_DIR" in os.environ:
        config["log_dir"] = os.environ["LOG_DIR"]

    if "LOG_FORMAT" in os.environ:
        config["format"] = os.environ["LOG_FORMAT"]

    if "LOG_INCLUDE_PII" in os.environ:
        config["include_pii"] = os.environ["LOG_INCLUDE_PII"].lower() in (
            "true",
            "1",
            "yes",
        )

    initialize_logging(config)
    setup_error_logging_integration()


# Auto-initialize when module is imported
_auto_initialize()
