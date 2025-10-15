import os
import sys

from fastapi import FastAPI

#!/usr/bin/env python3
"""
Simple test server to verify security features work independently
"""


# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Import our security modules
try:
    pass
    from advanced_security import (
        ThreatLevel,
        get_advanced_security_config,
        log_security_event,
    )
    from rate_limiting import get_security_status

    SECURITY_AVAILABLE = True
except ImportError:
    pass
    SECURITY_AVAILABLE = False

# Create minimal FastAPI app
app = FastAPI(title="Security Test Server")


@app.get("/")
async def root():
    return {"message": "Security test server is running"}


@app.get("/test-security")
async def test_security_endpoint():
    """Test security functionality"""
    if not SECURITY_AVAILABLE:
        pass
        return {"error": "Security modules not available"}

    try:
        pass
        # Test advanced security config
        security_config = get_advanced_security_config()
        security_status = security_config.get_security_status()

        # Test rate limiting
        rate_limit_status = get_security_status()

        # Log a test security event
        log_security_event(
            event_type="test_event",
            severity=ThreatLevel.LOW,
            source="test_server",
            description="Testing security functionality",
            details={"test": True},
        )

        return {
            "success": True,
            "security_config": security_status,
            "rate_limiting": rate_limit_status,
            "timestamp": "2025-10-13T00:00:00Z",
        }
    except Exception as e:
        pass
        return {"error": f"Security test failed: {str(e)}"}


if __name__ == "__main__":
    pass
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
