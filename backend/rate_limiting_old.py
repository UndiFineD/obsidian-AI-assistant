#!/usr/bin/env python3
"""
Rate limiting middleware implementation for FastAPI backend.

Provides configurable rate limiting for different endpoint categories:
- Public endpoints: More restrictive
- Authenticated endpoints: Less restrictive  
- Admin endpoints: Minimal restrictions
"""

import time
import os
import sys as _sysmod
from typing import Dict, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse
import threading


def _is_test_mode() -> bool:
    """Check if running in test mode using multiple detection methods"""
    try:
        if (
            "pytest" in _sysmod.modules
            or os.environ.get("PYTEST_CURRENT_TEST")
            or os.environ.get("PYTEST_RUNNING", "").lower()
            in ("1", "true", "yes", "on")
            or os.environ.get("TEST_MODE", "").lower() in ("1", "true", "yes", "on")
        ):
            return True
    except Exception:
        pass
    return False

class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, max_tokens: int, refill_rate: float, window_seconds: int = 60):
        """
        Initialize rate limiter with token bucket algorithm
        
        Args:
            max_tokens: Maximum number of tokens in bucket
            refill_rate: Tokens added per second
            window_seconds: Time window for rate limiting
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.window_seconds = window_seconds
        self.buckets: Dict[str, Tuple[float, float]] = {}  # client_id -> (tokens, last_refill)
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed for client
        
        Returns:
            Tuple of (allowed: bool, headers: dict with rate limit info)
        """
        with self.lock:
            now = time.time()
            
            if client_id not in self.buckets:
                self.buckets[client_id] = (self.max_tokens - 1, now)
                return True, self._get_headers(self.max_tokens - 1, now)
            
            tokens, last_refill = self.buckets[client_id]
            
            # Calculate tokens to add based on time elapsed
            time_elapsed = now - last_refill
            tokens_to_add = time_elapsed * self.refill_rate
            tokens = min(self.max_tokens, tokens + tokens_to_add)
            
            if tokens >= 1:
                # Allow request and consume token
                self.buckets[client_id] = (tokens - 1, now)
                return True, self._get_headers(tokens - 1, now)
            else:
                # Request denied
                self.buckets[client_id] = (tokens, now)
                return False, self._get_headers(tokens, now)
    
    def _get_headers(self, remaining_tokens: float, timestamp: float) -> Dict[str, str]:
        """Get rate limit headers for response"""
        return {
            "X-RateLimit-Limit": str(self.max_tokens),
            "X-RateLimit-Remaining": str(int(remaining_tokens)),
            "X-RateLimit-Reset": str(int(timestamp + self.window_seconds)),
            "X-RateLimit-Window": str(self.window_seconds)
        }
    
    def cleanup_expired(self):
        """Clean up expired client entries"""
        with self.lock:
            now = time.time()
            expired_clients = [
                client_id for client_id, (_, last_refill) in self.buckets.items()
                if now - last_refill > self.window_seconds * 2
            ]
            for client_id in expired_clients:
                del self.buckets[client_id]


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self):
        # Different rate limits for different endpoint categories
        self.limiters = {
            "public": TokenBucketRateLimiter(max_tokens=30, refill_rate=0.5, window_seconds=60),  # 30 requests/min
            "authenticated": TokenBucketRateLimiter(max_tokens=100, refill_rate=2.0, window_seconds=60),  # 100 requests/min
            "admin": TokenBucketRateLimiter(max_tokens=200, refill_rate=4.0, window_seconds=60),  # 200 requests/min
        }
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task to clean up expired entries"""
        def cleanup_loop():
            while True:
                try:
                    for limiter in self.limiters.values():
                        limiter.cleanup_expired()
                    time.sleep(300)  # Clean up every 5 minutes
                except Exception as e:
                    print(f"[RateLimit] Cleanup error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def get_client_id(self, request: Request) -> str:
        """Extract client identifier from request"""
        # Use X-Forwarded-For if behind proxy, otherwise client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # For authenticated requests, could also use user ID
        # This is a basic implementation using IP
        return client_ip
    
    def get_endpoint_category(self, path: str, has_auth: bool = False) -> str:
        """Determine rate limit category based on endpoint path"""
        
        # Admin endpoints (require admin role)
        admin_endpoints = [
            "/api/scan_vault",
            "/api/reindex", "/reindex",
            "/api/index_pdf",
            "/api/enterprise/status",
            "/api/enterprise/demo"
        ]
        
        # Public endpoints (no auth required)
        public_endpoints = [
            "/health", "/status", "/api/health",
            "/docs", "/redoc", "/openapi.json"
        ]
        
        if any(path.startswith(endpoint) for endpoint in admin_endpoints):
            return "admin"
        elif any(path.startswith(endpoint) for endpoint in public_endpoints):
            return "public"
        elif has_auth:
            return "authenticated"
        else:
            return "public"  # Default to most restrictive
    
    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting in test mode
        if _is_test_mode():
            return await call_next(request)
        
        # Skip rate limiting for certain paths
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Get client identifier
        client_id = self.get_client_id(request)
        
        # Determine if request has authentication
        has_auth = request.headers.get("Authorization") is not None
        
        # Get endpoint category for rate limiting
        category = self.get_endpoint_category(request.url.path, has_auth)
        
        # Check rate limit
        limiter = self.limiters[category]
        allowed, headers = limiter.is_allowed(f"{category}:{client_id}")
        
        if not allowed:
            # Return rate limit exceeded response
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests for {category} endpoints. Please try again later.",
                    "category": category,
                    "retry_after": int(headers.get("X-RateLimit-Reset", "60"))
                },
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


# Factory function for easy integration
def create_rate_limit_middleware():
    """Create and return rate limit middleware instance"""
    return RateLimitMiddleware()


# Configuration constants
RATE_LIMIT_CONFIG = {
    "public": {
        "max_tokens": 30,  # 30 requests per window
        "refill_rate": 0.5,  # 0.5 tokens per second = 30/min
        "window_seconds": 60
    },
    "authenticated": {
        "max_tokens": 100,  # 100 requests per window
        "refill_rate": 2.0,  # 2 tokens per second = 120/min
        "window_seconds": 60
    },
    "admin": {
        "max_tokens": 200,  # 200 requests per window
        "refill_rate": 4.0,  # 4 tokens per second = 240/min
        "window_seconds": 60
    }
}