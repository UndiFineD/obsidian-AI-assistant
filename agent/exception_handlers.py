"""
FastAPI Exception Handlers for Obsidian AI Agent

This module provides FastAPI-specific exception handlers that integrate with
our standardized error handling system to ensure consistent API responses.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from .error_handling import (
        ErrorHandler,
        ErrorResponse,
        ObsidianAIError,
        ValidationError,
        get_error_handler,
    )
except ImportError:
    from agent.error_handling import (
        ErrorResponse,
        ObsidianAIError,
        ValidationError,
        get_error_handler,
    )


logger = logging.getLogger(__name__)


async def obsidian_ai_exception_handler(
    request: Request, exc: ObsidianAIError
) -> JSONResponse:
    """Handle custom ObsidianAI exceptions."""
    handler = get_error_handler()

    # Log the error with request context
    handler.log_error(
        error=exc,
        request_id=getattr(request.state, "request_id", None),
        user_id=getattr(request.state, "user_id", None),
        operation=f"{request.method} {request.url.path}",
        context={
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host if request.client else None,
        },
    )

    # Create error response
    error_detail = handler.create_error_detail(exc)
    response = ErrorResponse(
        error=error_detail,
        request_id=exc.request_id,
        debug_info=handler._get_debug_info(exc) if handler.debug_mode else None,
    )

    # Determine HTTP status code
    status_code = handler._get_http_status_code(exc.category, exc.severity)

    return JSONResponse(
        status_code=status_code, content=response.model_dump(mode="json")
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException with our standardized format."""
    handler = get_error_handler()

    # If the HTTPException already contains our error format, use it
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    # Otherwise, wrap it in our standard format
    error_detail = handler.create_error_detail(
        exc,
        context={"http_status": exc.status_code},
        user_message=str(exc.detail) if exc.detail else None,
    )

    response = ErrorResponse(
        error=error_detail,
        request_id=getattr(request.state, "request_id", str(exc.__hash__())),
    )

    return JSONResponse(
        status_code=exc.status_code, content=response.model_dump(mode="json")
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with detailed field information."""
    handler = get_error_handler()

    # Extract validation error details
    validation_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        validation_errors.append(
            {
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input"),
            }
        )

    # Create a ValidationError with detailed context
    validation_error = ValidationError(
        message=f"Validation failed for {len(validation_errors)} field(s)",
        context={
            "validation_errors": validation_errors,
            "error_count": len(validation_errors),
        },
        suggestion="Please check the request format and ensure all required fields are provided with correct data types.",
    )

    # Log the validation error
    handler.log_error(
        error=validation_error,
        request_id=getattr(request.state, "request_id", None),
        operation=f"{request.method} {request.url.path}",
        context={"body": str(exc.body)[:500] if hasattr(exc, "body") else None},
    )

    # Create response
    error_detail = handler.create_error_detail(validation_error)
    response = ErrorResponse(error=error_detail, request_id=validation_error.request_id)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(mode="json"),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    handler = get_error_handler()

    # Log the unexpected error
    handler.log_error(
        error=exc,
        request_id=getattr(request.state, "request_id", None),
        user_id=getattr(request.state, "user_id", None),
        operation=f"{request.method} {request.url.path}",
        context={
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host if request.client else None,
        },
    )

    # Create standardized error response
    error_detail = handler.create_error_detail(
        exc, user_message="An unexpected error occurred. Please try again later."
    )

    response = ErrorResponse(
        error=error_detail,
        request_id=str(hash(str(exc))),
        debug_info=handler._get_debug_info(exc) if handler.debug_mode else None,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the FastAPI application."""

    # Custom ObsidianAI exceptions
    app.add_exception_handler(ObsidianAIError, obsidian_ai_exception_handler)

    # FastAPI built-in exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers configured successfully")


# Middleware for request tracking
class RequestTrackingMiddleware:
    """Middleware to add request tracking information."""

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Generate request ID and add to state
            import uuid

            request_id = str(uuid.uuid4())

            # Add request ID to scope for handlers to access
            if "state" not in scope:
                scope["state"] = {}
            scope["state"]["request_id"] = request_id

            # Add response header with request ID
            async def send_with_request_id(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-request-id", request_id.encode()))
                    message["headers"] = headers
                await send(message)

            await self.app(scope, receive, send_with_request_id)
        else:
            await self.app(scope, receive, send)


# Health check with error handling
async def health_check_with_error_handling() -> Dict[str, Any]:
    """Enhanced health check that demonstrates error handling."""
    try:
        try:
            from .settings import get_settings
        except ImportError:
            from agent.settings import get_settings
        settings = get_settings()

        health_status = {
            "status": "healthy",
            "timestamp": str(datetime.utcnow()),
            "version": "1.0.0",  # Should come from actual version
            "services": {
                "api": "healthy",
                "database": "unknown",  # Would check actual DB
                "models": "unknown",  # Would check model availability
            },
        }

        return health_status

    except Exception as e:
        handler = get_error_handler()

        # Log the health check failure
        handler.log_error(
            error=e, operation="health_check", context={"component": "health_check"}
        )

        # Return degraded status instead of failing
        return {
            "status": "degraded",
            "timestamp": str(datetime.utcnow()),
            "error": "Health check partially failed",
            "services": {
                "api": "healthy",
                "database": "error",
                "models": "error",
            },
        }


# Error reporting endpoint for frontend
async def report_client_error(
    request: Request, error_data: Dict[str, Any]
) -> Dict[str, str]:
    """Allow frontend to report client-side errors."""
    handler = get_error_handler()

    try:
        # Validate required fields
        required_fields = ["message", "type"]
        missing_fields = [field for field in required_fields if field not in error_data]

        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                context={"missing_fields": missing_fields},
            )

        # Create client error for logging
        client_error = ObsidianAIError(
            message=f"Client Error: {error_data['message']}",
            code="CLIENT_ERROR",
            context={
                "error_type": error_data.get("type"),
                "url": error_data.get("url"),
                "user_agent": request.headers.get("user-agent"),
                "timestamp": error_data.get("timestamp"),
                "stack_trace": error_data.get("stackTrace", "")[:1000],  # Limit size
            },
        )

        # Log the client error
        handler.log_error(
            error=client_error,
            request_id=getattr(request.state, "request_id", None),
            operation="client_error_report",
        )

        return {"status": "logged", "request_id": client_error.request_id}

    except Exception as e:
        # If we can't even log the client error, log that fact
        handler.log_error(
            error=e,
            operation="client_error_report_failed",
            context={"original_error_data": str(error_data)[:500]},
        )

        raise ObsidianAIError(
            message="Failed to process error report", code="ERROR_REPORTING_FAILED"
        )
