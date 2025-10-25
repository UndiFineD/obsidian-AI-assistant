"""
Test suite for security headers in backend responses
"""

import pytest
from fastapi.testclient import TestClient

from agent.backend import app

client = TestClient(app)

SECURITY_HEADERS = [
    ("Strict-Transport-Security", None),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("X-XSS-Protection", "1; mode=block"),
    ("Referrer-Policy", "no-referrer"),
    ("Content-Security-Policy", None),
]


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/health",
        "/status",
        "/api/config",
        "/api/auth/token",
    ],
)
def test_security_headers_present(endpoint):
    response = client.get(endpoint)
    for header, expected_value in SECURITY_HEADERS:
        assert header in response.headers, f"Missing header: {header}"
        if expected_value:
            assert response.headers[header] == expected_value, f"Header {header} value mismatch"


def test_security_headers_options():
    response = client.options("/api/health")
    for header, _ in SECURITY_HEADERS:
        assert header in response.headers, f"Missing header: {header} in OPTIONS"
