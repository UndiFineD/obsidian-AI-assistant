"""
HTTPS/SSL utilities for FastAPI backend
"""

import os

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware to redirect HTTP requests to HTTPS"""
    async def dispatch(self, request: Request, call_next):
        if request.url.scheme == "http":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(url), status_code=307)
        return await call_next(request)


def get_ssl_config():
    """Get SSL config from environment variables"""
    certfile = os.getenv("SSL_CERTFILE", None)
    keyfile = os.getenv("SSL_KEYFILE", None)
    ca_certs = os.getenv("SSL_CA_CERTS", None)
    if certfile and keyfile:
        return {
            "ssl_certfile": certfile,
            "ssl_keyfile": keyfile,
            "ssl_ca_certs": ca_certs,
        }
    return None
