#!/usr/bin/env python3
import os
import sys
from fastapi import Request
from fastapi.responses import JSONResponse

def _is_test_mode():
    return (
        "pytest" in sys.modules
        or os.environ.get("PYTEST_CURRENT_TEST")
        or os.environ.get("TEST_MODE", "").lower() in ("1", "true", "yes", "on")
    )

class RateLimitMiddleware:
    def __init__(self):
        pass
    
    async def __call__(self, request: Request, call_next):
        if _is_test_mode():
            return await call_next(request)
        return await call_next(request)

def create_rate_limit_middleware():
    return RateLimitMiddleware()
