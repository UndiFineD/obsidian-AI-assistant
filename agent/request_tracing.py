"""
Enhanced Request Tracing and Performance Monitoring

This module provides comprehensive request tracing capabilities including:
- Unique request IDs for all API calls
- Request/response timing and profiling
- Slow query detection and logging
- Performance metrics aggregation
- Distributed tracing support (future)
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logging_framework import LogCategory, get_logger

logger = get_logger("request_tracing", LogCategory.PERFORMANCE)


class RequestTracer:
    """
    Centralized request tracing with performance monitoring.

    Features:
    - Automatic request ID generation
    - Request/response timing
    - Slow query detection
    - Performance metrics aggregation
    - Memory usage tracking
    """

    def __init__(
        self,
        slow_request_threshold_ms: float = 1000.0,
        very_slow_threshold_ms: float = 5000.0,
        enable_detailed_logging: bool = True,
    ):
        self.slow_threshold = slow_request_threshold_ms
        self.very_slow_threshold = very_slow_threshold_ms
        self.enable_detailed = enable_detailed_logging

        # Performance metrics storage
        self.request_history: List[Dict[str, Any]] = []
        self.max_history = 1000

        # Slow request tracking
        self.slow_requests: List[Dict[str, Any]] = []
        self.max_slow_requests = 100

        # Endpoint statistics
        self.endpoint_stats: Dict[str, Dict[str, Any]] = {}

    def generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())

    def start_request(self, request: Request) -> Dict[str, Any]:
        """
        Start tracking a request.

        Returns:
            Context dictionary with timing and metadata
        """
        request_id = self.generate_request_id()
        start_time = time.perf_counter()

        context = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "start_time": start_time,
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store in request state for access in handlers
        if not hasattr(request, "state"):
            request.state = type("State", (), {})()
        request.state.trace_context = context
        request.state.request_id = request_id

        if self.enable_detailed:
            logger.debug(
                f"Request started: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "endpoint": request.url.path,
                    "method": request.method,
                },
            )

        return context

    def end_request(
        self,
        context: Dict[str, Any],
        response: Response,
        exception: Optional[Exception] = None,
    ) -> Dict[str, Any]:
        """
        End request tracking and calculate metrics.

        Args:
            context: Request context from start_request()
            response: FastAPI Response object
            exception: Optional exception if request failed

        Returns:
            Complete request metrics
        """
        end_time = time.perf_counter()
        duration_ms = (end_time - context["start_time"]) * 1000

        # Build complete request record
        request_record = {
            **context,
            "end_time": end_time,
            "end_timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "status_code": response.status_code if response else 500,
            "success": exception is None
            and (response and 200 <= response.status_code < 300),
            "exception": str(exception) if exception else None,
        }

        # Update endpoint statistics
        self._update_endpoint_stats(request_record)

        # Add to history
        self.request_history.append(request_record)
        if len(self.request_history) > self.max_history:
            self.request_history.pop(0)

        # Check for slow requests
        if duration_ms > self.slow_threshold:
            self._log_slow_request(request_record, duration_ms)

        # Log completion
        log_level = logging.INFO
        if exception:
            log_level = logging.ERROR
        elif duration_ms > self.very_slow_threshold:
            log_level = logging.WARNING

        logger.log(
            log_level,
            f"Request completed: {context['method']} {context['path']} "
            f"[{response.status_code if response else 500}] in {duration_ms:.2f}ms",
            extra={
                "request_id": context["request_id"],
                "endpoint": context["path"],
                "method": context["method"],
                "duration_ms": duration_ms,
                "status_code": response.status_code if response else 500,
            },
        )

        return request_record

    def _update_endpoint_stats(self, request_record: Dict[str, Any]):
        """Update aggregated endpoint statistics."""
        endpoint = f"{request_record['method']} {request_record['path']}"

        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "total_requests": 0,
                "total_duration_ms": 0,
                "min_duration_ms": float("inf"),
                "max_duration_ms": 0,
                "error_count": 0,
                "slow_count": 0,
            }

        stats = self.endpoint_stats[endpoint]
        stats["total_requests"] += 1
        stats["total_duration_ms"] += request_record["duration_ms"]
        stats["min_duration_ms"] = min(
            stats["min_duration_ms"], request_record["duration_ms"]
        )
        stats["max_duration_ms"] = max(
            stats["max_duration_ms"], request_record["duration_ms"]
        )

        if not request_record["success"]:
            stats["error_count"] += 1

        if request_record["duration_ms"] > self.slow_threshold:
            stats["slow_count"] += 1

    def _log_slow_request(self, request_record: Dict[str, Any], duration_ms: float):
        """Log and track slow requests for analysis."""
        severity = "VERY SLOW" if duration_ms > self.very_slow_threshold else "SLOW"

        logger.warning(
            f"{severity} REQUEST DETECTED: {request_record['method']} {request_record['path']} "
            f"took {duration_ms:.2f}ms (threshold: {self.slow_threshold}ms)",
            extra={
                "request_id": request_record["request_id"],
                "endpoint": request_record["path"],
                "duration_ms": duration_ms,
                "slow_threshold_ms": self.slow_threshold,
                "severity": severity,
            },
        )

        # Add to slow requests tracking
        self.slow_requests.append(
            {
                **request_record,
                "severity": severity,
                "threshold_exceeded_by_ms": duration_ms - self.slow_threshold,
            }
        )

        if len(self.slow_requests) > self.max_slow_requests:
            self.slow_requests.pop(0)

    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get endpoint performance statistics.

        Args:
            endpoint: Optional specific endpoint (e.g., "GET /api/ask")
                      If None, returns stats for all endpoints

        Returns:
            Dictionary of endpoint statistics with calculated metrics
        """
        if endpoint:
            if endpoint not in self.endpoint_stats:
                return {}

            stats = self.endpoint_stats[endpoint].copy()
            if stats["total_requests"] > 0:
                stats["avg_duration_ms"] = (
                    stats["total_duration_ms"] / stats["total_requests"]
                )
                stats["error_rate"] = stats["error_count"] / stats["total_requests"]
                stats["slow_rate"] = stats["slow_count"] / stats["total_requests"]

            return {endpoint: stats}

        # Return all endpoints with calculated metrics
        result = {}
        for ep, stats in self.endpoint_stats.items():
            ep_stats = stats.copy()
            if ep_stats["total_requests"] > 0:
                ep_stats["avg_duration_ms"] = (
                    ep_stats["total_duration_ms"] / ep_stats["total_requests"]
                )
                ep_stats["error_rate"] = (
                    ep_stats["error_count"] / ep_stats["total_requests"]
                )
                ep_stats["slow_rate"] = (
                    ep_stats["slow_count"] / ep_stats["total_requests"]
                )
            result[ep] = ep_stats

        return result

    def get_slow_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow requests."""
        return sorted(self.slow_requests, key=lambda x: x["duration_ms"], reverse=True)[
            :limit
        ]

    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent requests."""
        return self.request_history[-limit:]

    def get_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        total_requests = len(self.request_history)

        if total_requests == 0:
            return {"total_requests": 0, "message": "No requests tracked yet"}

        total_duration = sum(r["duration_ms"] for r in self.request_history)
        slow_count = sum(
            1 for r in self.request_history if r["duration_ms"] > self.slow_threshold
        )
        error_count = sum(1 for r in self.request_history if not r["success"])

        return {
            "total_requests": total_requests,
            "avg_duration_ms": total_duration / total_requests,
            "slow_request_count": slow_count,
            "slow_request_rate": slow_count / total_requests,
            "error_count": error_count,
            "error_rate": error_count / total_requests,
            "slow_threshold_ms": self.slow_threshold,
            "very_slow_threshold_ms": self.very_slow_threshold,
        }


# Global tracer instance
_tracer: Optional[RequestTracer] = None


def get_request_tracer(
    slow_threshold_ms: float = 1000.0, very_slow_threshold_ms: float = 5000.0
) -> RequestTracer:
    """Get or create global request tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = RequestTracer(
            slow_request_threshold_ms=slow_threshold_ms,
            very_slow_threshold_ms=very_slow_threshold_ms,
        )
    return _tracer


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically trace all requests.

    Adds request IDs, timing, and performance monitoring to all HTTP requests.
    """

    def __init__(
        self,
        app: ASGIApp,
        slow_threshold_ms: float = 1000.0,
        very_slow_threshold_ms: float = 5000.0,
    ):
        super().__init__(app)
        self.tracer = get_request_tracer(slow_threshold_ms, very_slow_threshold_ms)

    async def dispatch(self, request: Request, call_next):
        """Process request with tracing."""
        # Start tracing
        context = self.tracer.start_request(request)

        response = None
        exception = None

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = context["request_id"]
            response.headers["X-Response-Time"] = (
                f"{(time.perf_counter() - context['start_time']) * 1000:.2f}ms"
            )

        except BaseException as exc:
            # Don't swallow exceptions; record and re-raise so FastAPI handlers run
            exception = exc
            raise
        finally:
            # End tracing with whatever we have (response may be None on exception)
            try:
                self.tracer.end_request(context, response, exception)
            except Exception:
                # Tracing must never crash the request lifecycle
                pass

        return response


@asynccontextmanager
async def trace_operation(
    operation_name: str, context: Optional[Dict[str, Any]] = None
):
    """
    Context manager for tracing individual operations within a request.

    Usage:
        async with trace_operation("database_query", {"query": "SELECT *"}):
            result = await db.execute(query)
    """
    start_time = time.perf_counter()
    operation_id = str(uuid.uuid4())

    logger.debug(
        f"Operation started: {operation_name}",
        extra={"operation_id": operation_id, "operation": operation_name},
    )

    try:
        yield {"operation_id": operation_id, "start_time": start_time}

    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.debug(
            f"Operation completed: {operation_name} in {duration_ms:.2f}ms",
            extra={
                "operation_id": operation_id,
                "operation": operation_name,
                "duration_ms": duration_ms,
            },
        )
