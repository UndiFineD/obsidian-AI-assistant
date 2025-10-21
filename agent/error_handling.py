"""
Standardized Error Handling System for Obsidian AI Agent

This module provides a comprehensive, consistent error handling framework with:
- Centralized error classification and response formatting
- Structured logging with context preservation
- User-friendly error messages with security considerations
- Graceful degradation patterns
- Integration with FastAPI exception handling
"""

import logging
import sys
import traceback
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover - fallback for older pydantic
    ConfigDict = dict  # type: ignore

try:
    from .utils import redact_data
except ImportError:
    from agent.utils import redact_data


# Error severity levels
class ErrorSeverity(str, Enum):
    """Error severity classification."""

    CRITICAL = "critical"  # System failure, immediate attention required
    HIGH = "high"  # Major functionality impacted, urgent fix needed
    MEDIUM = "medium"  # Feature degradation, should be fixed soon
    LOW = "low"  # Minor issues, cosmetic problems
    INFO = "info"  # Informational, not actually an error


# Error categories for better organization
class ErrorCategory(str, Enum):
    """Error category classification."""

    AUTHENTICATION = "authentication"  # Auth, authorization, access control
    VALIDATION = "validation"  # Input validation, data format errors
    BUSINESS_LOGIC = "business_logic"  # Application logic errors
    EXTERNAL_SERVICE = "external_service"  # Third-party service failures
    SYSTEM = "system"  # System-level errors (file I/O, network)
    SECURITY = "security"  # Security-related errors
    PERFORMANCE = "performance"  # Performance degradation, timeouts
    DATA = "data"  # Database, data consistency errors
    CONFIGURATION = "configuration"  # Configuration, setup errors
    UNKNOWN = "unknown"  # Unclassified errors


# Standardized error response model
class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    severity: ErrorSeverity = Field(default=ErrorSeverity.MEDIUM)
    category: ErrorCategory = Field(default=ErrorCategory.UNKNOWN)
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context"
    )
    suggestion: Optional[str] = Field(default=None, description="Suggested resolution")
    documentation_url: Optional[str] = Field(
        default=None, description="Link to relevant documentation"
    )


class ErrorResponse(BaseModel):
    """Standardized API error response."""

    error: ErrorDetail
    request_id: str = Field(..., description="Unique request identifier for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    debug_info: Optional[Dict[str, Any]] = Field(
        default=None, description="Debug information (dev mode only)"
    )

    # Pydantic v2 serializer for datetime
    @staticmethod
    def _serialize_datetime(value: datetime) -> str:
        return value.isoformat()

    model_config = ConfigDict(ser_json_timedelta="iso8601")


# Custom exception classes
class ObsidianAIError(Exception):
    """Base exception for all Obsidian AI Agent errors."""

    def __init__(
        self,
        message: str,
        code: str = "OBSIDIAN_AI_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        documentation_url: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.suggestion = suggestion
        self.documentation_url = documentation_url
        self.original_exception = original_exception
        self.request_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)


class ValidationError(ObsidianAIError):
    """Input validation errors."""

    def __init__(self, message: str, field: str = None, **kwargs):
        combined_context: Dict[str, Any] = {}
        extra_context = kwargs.pop("context", None) or {}
        if isinstance(extra_context, dict):
            combined_context.update(extra_context)
        if field is not None:
            combined_context.setdefault("field", field)
        context_value = combined_context or None
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            context=context_value,
            **kwargs,
        )


class AuthenticationError(ObsidianAIError):
    """Authentication and authorization errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            code="AUTH_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            **kwargs,
        )


class ExternalServiceError(ObsidianAIError):
    """External service integration errors."""

    def __init__(self, message: str, service: str = None, **kwargs):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.EXTERNAL_SERVICE,
            context={"service": service} if service else None,
            **kwargs,
        )


class ModelError(ObsidianAIError):
    """AI model related errors."""

    def __init__(self, message: str, model_name: str = None, **kwargs):
        super().__init__(
            message=message,
            code="MODEL_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            context={"model": model_name} if model_name else None,
            **kwargs,
        )


class ConfigurationError(ObsidianAIError):
    """Configuration and setup errors."""

    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(
            message=message,
            code="CONFIG_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            context={"config_key": config_key} if config_key else None,
            **kwargs,
        )


class SecurityError(ObsidianAIError):
    """Security-related errors."""

    def __init__(self, message: str, **kwargs):
        # Extract known ObsidianAIError parameters
        context = kwargs.pop("context", None) or {}
        suggestion = kwargs.pop("suggestion", None)
        documentation_url = kwargs.pop("documentation_url", None)
        original_exception = kwargs.pop("original_exception", None)

        # Add any extra kwargs to context instead of passing them to parent
        for key, value in kwargs.items():
            context[key] = value

        super().__init__(
            message=message,
            code="SECURITY_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            context=context if context else None,
            suggestion=suggestion,
            documentation_url=documentation_url,
            original_exception=original_exception,
        )


class PerformanceError(ObsidianAIError):
    """Performance and timeout errors."""

    def __init__(
        self, message: str, operation: str = None, duration: float = None, **kwargs
    ):
        context = {}
        if operation:
            context["operation"] = operation
        if duration:
            context["duration_seconds"] = duration

        super().__init__(
            message=message,
            code="PERFORMANCE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            context=context if context else None,
            **kwargs,
        )


class DataError(ObsidianAIError):
    """Data integrity and database errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            code="DATA_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATA,
            **kwargs,
        )


# Error handler singleton
class ErrorHandler:
    """Centralized error handling and logging."""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(__name__)

        # Error message templates for common scenarios
        self.error_templates = {
            "MODEL_LOADING_FAILED": "Failed to load AI model '{model}'. Please check the model file exists and is valid.",
            "VALIDATION_FAILED": "Invalid input for field '{field}': {details}",
            "AUTH_TOKEN_INVALID": "Authentication token is invalid or expired. Please authenticate again.",
            "EXTERNAL_SERVICE_TIMEOUT": "External service '{service}' timed out. Please try again later.",
            "CONFIGURATION_MISSING": "Required configuration '{config}' is missing. Please check your settings.",
            "PERMISSION_DENIED": "You don't have permission to perform this action.",
            "RATE_LIMIT_EXCEEDED": "Too many requests. Please wait before trying again.",
            "SYSTEM_OVERLOADED": "System is currently overloaded. Please try again in a few minutes.",
        }

        # Default suggestions for common error patterns
        self.default_suggestions = {
            ErrorCategory.AUTHENTICATION: "Please verify your credentials and try again.",
            ErrorCategory.VALIDATION: "Please check your input format and try again.",
            ErrorCategory.EXTERNAL_SERVICE: "This appears to be a temporary issue. Please try again later.",
            ErrorCategory.CONFIGURATION: "Please check your configuration settings and restart the service.",
            ErrorCategory.SYSTEM: "Please check system resources and try again.",
            ErrorCategory.PERFORMANCE: "Please try reducing the request size or wait before retrying.",
        }

    def create_error_detail(
        self,
        error: Union[Exception, ObsidianAIError],
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
    ) -> ErrorDetail:
        """Create standardized error detail from an exception."""

        if isinstance(error, ObsidianAIError):
            # Use the structured error information
            return ErrorDetail(
                code=error.code,
                message=user_message or error.message,
                severity=error.severity,
                category=error.category,
                context=redact_data({**(error.context or {}), **(context or {})}),
                suggestion=error.suggestion
                or self.default_suggestions.get(error.category),
                documentation_url=error.documentation_url,
            )
        else:
            # Handle generic exceptions
            error_type = type(error).__name__
            message = (
                user_message or str(error) or f"An unexpected {error_type} occurred"
            )

            # Classify common exception types
            category = self._classify_exception(error)
            severity = self._determine_severity(error, category)

            return ErrorDetail(
                code=f"GENERIC_{error_type.upper()}",
                message=message,
                severity=severity,
                category=category,
                context=redact_data(context or {}),
                suggestion=self.default_suggestions.get(category),
            )

    def _classify_exception(self, error: Exception) -> ErrorCategory:
        """Classify generic exceptions into categories."""
        error_type = type(error).__name__.lower()

        if any(
            auth_term in error_type
            for auth_term in ["auth", "permission", "forbidden", "unauthorized"]
        ):
            return ErrorCategory.AUTHENTICATION
        elif any(
            val_term in error_type
            for val_term in ["validation", "value", "type", "format"]
        ):
            return ErrorCategory.VALIDATION
        elif any(
            net_term in error_type
            for net_term in ["connection", "timeout", "network", "http"]
        ):
            return ErrorCategory.EXTERNAL_SERVICE
        elif any(
            io_term in error_type for io_term in ["io", "file", "path", "directory"]
        ):
            return ErrorCategory.SYSTEM
        elif any(
            data_term in error_type for data_term in ["database", "sql", "integrity"]
        ):
            return ErrorCategory.DATA
        else:
            return ErrorCategory.UNKNOWN

    def _determine_severity(
        self, error: Exception, category: ErrorCategory
    ) -> ErrorSeverity:
        """Determine error severity based on exception type and category."""
        error_type = type(error).__name__.lower()

        # Critical errors that require immediate attention
        if any(
            critical_term in error_type
            for critical_term in ["security", "corrupt", "fatal"]
        ):
            return ErrorSeverity.CRITICAL

        # High severity errors
        if category in [
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.DATA,
            ErrorCategory.CONFIGURATION,
        ]:
            return ErrorSeverity.HIGH

        # Low severity for validation and formatting issues
        if category in [ErrorCategory.VALIDATION]:
            return ErrorSeverity.LOW

        # Default to medium severity
        return ErrorSeverity.MEDIUM

    def log_error(
        self,
        error: Union[Exception, ObsidianAIError],
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log error with structured information."""

        log_context = {
            "request_id": request_id,
            "user_id": user_id,
            "operation": operation,
            "error_type": type(error).__name__,
            **(context or {}),
        }

        # Redact sensitive information
        log_context = redact_data(log_context)

        if isinstance(error, ObsidianAIError):
            self.logger.error(
                f"[{error.severity.upper()}] {error.category}: {error.message}",
                extra={
                    "error_code": error.code,
                    "severity": error.severity,
                    "category": error.category,
                    **log_context,
                },
                exc_info=error.original_exception,
            )
        else:
            self.logger.error(
                f"Unhandled exception: {error}", extra=log_context, exc_info=True
            )

    def create_http_exception(
        self,
        error: Union[Exception, ObsidianAIError],
        status_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> HTTPException:
        """Create FastAPI HTTPException from error."""

        error_detail = self.create_error_detail(error, context)

        # Determine HTTP status code
        if status_code is None:
            if isinstance(error, ObsidianAIError):
                status_code = self._get_http_status_code(error.category, error.severity)
            else:
                status_code = self._get_http_status_code_from_exception(error)

        response = ErrorResponse(
            error=error_detail,
            request_id=getattr(error, "request_id", str(uuid.uuid4())),
            debug_info=self._get_debug_info(error) if self.debug_mode else None,
        )

        return HTTPException(
            status_code=status_code, detail=response.model_dump(mode="json")
        )

    def _get_http_status_code(
        self, category: ErrorCategory, severity: ErrorSeverity
    ) -> int:
        """Map error category and severity to HTTP status code."""

        if category == ErrorCategory.AUTHENTICATION:
            return status.HTTP_401_UNAUTHORIZED
        elif category == ErrorCategory.VALIDATION:
            return status.HTTP_422_UNPROCESSABLE_CONTENT
        elif category == ErrorCategory.SECURITY:
            return status.HTTP_403_FORBIDDEN
        elif category == ErrorCategory.EXTERNAL_SERVICE:
            return status.HTTP_502_BAD_GATEWAY
        elif category == ErrorCategory.PERFORMANCE:
            return status.HTTP_504_GATEWAY_TIMEOUT
        elif severity == ErrorSeverity.CRITICAL:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR

    def _get_http_status_code_from_exception(self, error: Exception) -> int:
        """Determine HTTP status code from exception type."""
        error_type = type(error).__name__.lower()

        if "permission" in error_type or "forbidden" in error_type:
            return status.HTTP_403_FORBIDDEN
        elif "auth" in error_type or "unauthorized" in error_type:
            return status.HTTP_401_UNAUTHORIZED
        elif "validation" in error_type or "value" in error_type:
            return status.HTTP_422_UNPROCESSABLE_CONTENT
        elif "timeout" in error_type:
            return status.HTTP_504_GATEWAY_TIMEOUT
        elif "notfound" in error_type or "filenotfound" in error_type:
            return status.HTTP_404_NOT_FOUND
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR

    def _get_debug_info(self, error: Exception) -> Dict[str, Any]:
        """Get debug information for development mode."""
        debug_info = {
            "exception_type": type(error).__name__,
            "exception_args": list(error.args),
            "traceback": (
                traceback.format_tb(error.__traceback__)
                if error.__traceback__
                else None
            ),
        }

        if isinstance(error, ObsidianAIError) and error.original_exception:
            debug_info["original_exception"] = {
                "type": type(error.original_exception).__name__,
                "args": list(error.original_exception.args),
            }

        return debug_info


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        # Check if we're in debug mode
        debug_mode = "pytest" in sys.modules or any(
            arg.startswith("--debug") for arg in sys.argv
        )
        _error_handler = ErrorHandler(debug_mode=debug_mode)
    return _error_handler


# Decorator for consistent error handling
def handle_errors(
    operation: str = None,
    reraise: bool = False,
    default_return: Any = None,
    log_errors: bool = True,
):
    """Decorator for consistent error handling in functions."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()

                if log_errors:
                    handler.log_error(
                        error=e,
                        operation=operation or func.__name__,
                        context={"args": str(args)[:100], "kwargs": str(kwargs)[:100]},
                    )

                if reraise:
                    raise

                return default_return

        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


# Context manager for error handling
@contextmanager
def error_context(
    operation: str,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    reraise: bool = True,
    context: Optional[Dict[str, Any]] = None,
):
    """Context manager for comprehensive error handling."""
    handler = get_error_handler()

    try:
        yield
    except Exception as e:
        handler.log_error(
            error=e,
            operation=operation,
            user_id=user_id,
            request_id=request_id,
            context=context,
        )

        if reraise:
            raise


# Utility functions for common error scenarios
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that required fields are present and non-empty."""
    missing_fields = []
    empty_fields = []

    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field]:
            empty_fields.append(field)

    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            context={"missing_fields": missing_fields},
        )

    if empty_fields:
        raise ValidationError(
            f"Empty required fields: {', '.join(empty_fields)}",
            context={"empty_fields": empty_fields},
        )


def require_authentication(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure user is authenticated."""
    if not user:
        raise AuthenticationError("Authentication required")
    return user


def check_rate_limit(identifier: str, limit: int, window_seconds: int) -> None:
    """Check if rate limit is exceeded (placeholder - implement with Redis/cache)."""
    # This would typically check against a rate limiting store
    # For now, just a placeholder that always passes
    pass


def graceful_shutdown(reason: str = "System shutdown requested") -> None:
    """Initiate graceful shutdown with proper error logging."""
    handler = get_error_handler()
    handler.logger.info(f"Graceful shutdown initiated: {reason}")

    # Add cleanup logic here as needed
    sys.exit(0)
