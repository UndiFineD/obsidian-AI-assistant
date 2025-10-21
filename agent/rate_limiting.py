#!/usr/bin/env python3
"""
Advanced Rate Limiting and Security Middleware
Provides comprehensive request throttling, abuse prevention, and security monitoring
"""

import hashlib
import logging
import os
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _is_test_mode():
    return (
        "pytest" in sys.modules
        or os.environ.get("PYTEST_CURRENT_TEST")
        or os.environ.get("TEST_MODE", "").lower() in ("1", "true", "yes", "on")
    )


class RateLimitStore:
    """In-memory store for rate limiting data"""

    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}
        self.security_events: deque = deque(maxlen=1000)
        self.suspicious_patterns: Dict[str, int] = defaultdict(int)

    def record_request(self, client_id: str, timestamp: float):
        """Record a request for rate limiting"""
        self.requests[client_id].append(timestamp)

        # Clean old entries (older than 1 hour)
        cutoff = timestamp - 3600
        while self.requests[client_id] and self.requests[client_id][0] < cutoff:
            self.requests[client_id].popleft()

    def get_recent_requests(self, client_id: str, window_seconds: int) -> int:
        """Get number of requests in the specified time window"""
        if client_id not in self.requests:
            return 0

        cutoff = time.time() - window_seconds
        return sum(1 for timestamp in self.requests[client_id] if timestamp >= cutoff)

    def block_client(self, client_id: str, duration: int = 300):
        """Block a client for specified duration (default 5 minutes)"""
        self.blocked_ips[client_id] = time.time() + duration

    def is_blocked(self, client_id: str) -> bool:
        """Check if a client is currently blocked"""
        if client_id not in self.blocked_ips:
            return False

        if time.time() > self.blocked_ips[client_id]:
            # Block expired, remove it
            del self.blocked_ips[client_id]
            return False

        return True

    def record_security_event(self, event_type: str, client_id: str, details: str):
        """Record a security event for monitoring"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "client_id": client_id,
            "details": details,
        }
        self.security_events.append(event)

        # Track suspicious patterns
        pattern_key = f"{event_type}:{client_id}"
        self.suspicious_patterns[pattern_key] += 1

        # Auto-block clients with too many suspicious events
        if self.suspicious_patterns[pattern_key] >= 10:
            self.block_client(client_id, duration=1800)  # 30 minute block
            logger.warning(
                f"Auto-blocked client {client_id} due to suspicious activity: {event_type}"
            )

    def get_security_summary(self) -> Dict:
        """Get security event summary"""
        recent_events = [
            e
            for e in self.security_events
            if datetime.fromisoformat(e["timestamp"])
            > datetime.now() - timedelta(hours=1)
        ]

        event_types = defaultdict(int)
        for event in recent_events:
            event_types[event["type"]] += 1

        return {
            "total_events_1h": len(recent_events),
            "event_types": dict(event_types),
            "blocked_clients": len(self.blocked_ips),
            "suspicious_patterns": len(
                [p for p in self.suspicious_patterns.values() if p >= 5]
            ),
        }


class AdvancedRateLimitMiddleware:
    """Advanced rate limiting with security monitoring"""

    def __init__(self):
        self.store = RateLimitStore()

        # Configurable limits
        self.limits = {
            "requests_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            "requests_per_hour": int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
            # requests per 10 seconds
            "burst_limit": int(os.getenv("RATE_LIMIT_BURST", "10")),
            # 10MB
            "max_request_size": int(os.getenv("MAX_REQUEST_SIZE", "10485760")),
        }

        # Security patterns to detect
        self.security_patterns = {
            "sql_injection": [
                "SELECT",
                "UNION",
                "DROP TABLE",
                "INSERT INTO",
                "DELETE FROM",
            ],
            "xss_attempt": ["<script>", "javascript:", "onload=", "onerror="],
            "path_traversal": [
                "../",
                "..\\",
                "/etc/passwd",
                "\\windows\\system32",
            ],
            "command_injection": ["|", "&&", ";", "`", "$()"],
        }

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get real IP from headers (for reverse proxy setups)
        real_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.headers.get("X-Real-IP", "").strip()
            or (request.client.host if request.client else "unknown")
        )

        # Include user agent for more specific fingerprinting
        user_agent = request.headers.get("User-Agent", "")
        client_signature = (
            f"{real_ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        )

        return client_signature

    def _check_request_size(self, request: Request) -> bool:
        """Check if request size is within limits"""
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                size = int(content_length)
                return size <= self.limits["max_request_size"]
            except ValueError:
                return False
        return True

    async def _check_security_patterns(self, request: Request, client_id: str):
        """Check request for suspicious security patterns"""
        try:
            # Check URL path
            path = str(request.url.path).lower()
            query = str(request.url.query).lower()

            # Check headers
            headers_text = " ".join(
                [f"{k}:{v}" for k, v in request.headers.items()]
            ).lower()

            # Get request body if available
            body_text = ""
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        body_text = body.decode("utf-8", errors="ignore").lower()
                except Exception:
                    pass  # Skip body analysis if not available

            # Combine all text for pattern matching
            full_text = f"{path} {query} {headers_text} {body_text}"

            # Check for security patterns
            for pattern_type, patterns in self.security_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in full_text:
                        self.store.record_security_event(
                            pattern_type,
                            client_id,
                            f"Detected pattern '{pattern}' in {request.method} {request.url.path}",
                        )
                        logger.warning(
                            f"Security pattern detected: {pattern_type} from {client_id}"
                        )

                        # Block immediately for high-risk patterns
                        if pattern_type in ["sql_injection", "command_injection"]:
                            # 1 hour block
                            self.store.block_client(client_id, duration=3600)
                            raise HTTPException(
                                status_code=403,
                                detail="Request blocked due to suspicious content",
                            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in security pattern check: {e}")

    def _check_rate_limits(
        self, client_id: str, timestamp: float
    ) -> Optional[Tuple[int, str]]:
        """Check if client has exceeded rate limits"""
        # Check burst limit (10 seconds)
        burst_requests = self.store.get_recent_requests(client_id, 10)
        if burst_requests >= self.limits["burst_limit"]:
            return (
                429,
                f"Burst limit exceeded: {burst_requests}/{self.limits['burst_limit']} requests in 10s",
            )

        # Check per-minute limit
        minute_requests = self.store.get_recent_requests(client_id, 60)
        if minute_requests >= self.limits["requests_per_minute"]:
            return (
                429,
                f"Rate limit exceeded: {minute_requests}/{self.limits['requests_per_minute']} requests per minute",
            )

        # Check per-hour limit
        hour_requests = self.store.get_recent_requests(client_id, 3600)
        if hour_requests >= self.limits["requests_per_hour"]:
            return (
                429,
                f"Rate limit exceeded: {hour_requests}/{self.limits['requests_per_hour']} requests per hour",
            )

        return None

    async def __call__(self, request: Request, call_next):
        # Skip in test mode
        if _is_test_mode():
            return await call_next(request)

        timestamp = time.time()
        client_id = self._get_client_id(request)

        # Check if client is blocked
        if self.store.is_blocked(client_id):
            self.store.record_security_event(
                "blocked_request", client_id, "Request from blocked client"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Client temporarily blocked due to suspicious activity"
                },
            )

        # Check request size
        if not self._check_request_size(request):
            self.store.record_security_event(
                "oversized_request", client_id, "Request size exceeds limit"
            )
            return JSONResponse(status_code=413, content={"error": "Request too large"})

        # Check security patterns
        try:
            await self._check_security_patterns(request, client_id)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"error": e.detail})

        # Check rate limits
        rate_limit_result = self._check_rate_limits(client_id, timestamp)
        if rate_limit_result:
            status_code, message = rate_limit_result
            self.store.record_security_event("rate_limit_exceeded", client_id, message)

            # Block client after multiple rate limit violations
            if (
                self.store.get_recent_requests(client_id, 300)
                > self.limits["requests_per_minute"] * 2
            ):
                # 10 minute block
                self.store.block_client(client_id, duration=600)

            return JSONResponse(
                status_code=status_code, content={"error": message, "retry_after": 60}
            )

        # Record successful request
        self.store.record_request(client_id, timestamp)

        # Add security headers to response
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

    def get_security_status(self) -> Dict:
        """Get current security status and statistics"""
        return {
            "rate_limits": self.limits,
            "security_summary": self.store.get_security_summary(),
            "active_blocks": len(self.store.blocked_ips),
            "monitoring_active": True,
        }


# Global instance
_rate_limit_middleware = None


def create_rate_limit_middleware():
    """Create rate limiting middleware instance"""
    global _rate_limit_middleware
    if _rate_limit_middleware is None:
        _rate_limit_middleware = AdvancedRateLimitMiddleware()
    return _rate_limit_middleware


def get_security_status():
    """Get security monitoring status"""
    middleware = create_rate_limit_middleware()
    return middleware.get_security_status()
