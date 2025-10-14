#!/usr/bin/env python3
"""
Security middleware integration test
Tests advanced security features, rate limiting, and audit logging
"""

from unittest.mock import patch

import pytest


def test_advanced_security_config():
    """Test advanced security configuration"""
    from backend.advanced_security import SecurityConfig

    config = SecurityConfig()

    # Test basic configuration
    assert config.max_request_size > 0
    assert config.max_file_size > 0
    assert len(config.allowed_file_extensions) > 0
    assert len(config.blocked_extensions) > 0

    # Test file type validation
    assert config.is_allowed_file_type("test.txt")
    assert config.is_allowed_file_type("document.pdf")
    assert not config.is_allowed_file_type("malware.exe")
    assert not config.is_allowed_file_type("script.bat")

def test_input_validator():
    """Test advanced input validation"""
    from backend.advanced_security import AdvancedInputValidator

    validator = AdvancedInputValidator()

    # Test SQL injection detection
    sql_threats = validator.detect_threats("SELECT * FROM users WHERE id = 1")
    assert len(sql_threats) > 0
    assert any(t[0] == "sql" for t in sql_threats)

    # Test XSS detection
    xss_threats = validator.detect_threats("<script>alert('xss')</script>")
    assert len(xss_threats) > 0
    assert any(t[0] == "xss" for t in xss_threats)

    # Test command injection detection
    cmd_threats = validator.detect_threats("ls -la; rm -rf /")
    assert len(cmd_threats) > 0
    assert any(t[0] == "command" for t in cmd_threats)

    # Test path traversal detection
    path_threats = validator.detect_threats("../../../etc/passwd")
    assert len(path_threats) > 0
    assert any(t[0] == "path_traversal" for t in path_threats)

    # Test safe input
    safe_threats = validator.detect_threats("This is a normal text input")
    assert len(safe_threats) == 0

def test_input_sanitization():
    """Test input sanitization"""
    from backend.advanced_security import AdvancedInputValidator

    validator = AdvancedInputValidator()

    # Test basic sanitization
    sanitized = validator.sanitize_input("Normal text input")
    assert sanitized == "Normal text input"

    # Test HTML escaping
    sanitized = validator.sanitize_input("<script>alert('test')</script>")
    assert "&lt;" in sanitized and "&gt;" in sanitized

    # Test length truncation
    long_input = "a" * 20000
    sanitized = validator.sanitize_input(long_input, max_length=1000)
    assert len(sanitized) <= 1000

    # Test control character removal
    bad_input = "text\x00with\x01bad\x02chars"
    sanitized = validator.sanitize_input(bad_input)
    assert "\x00" not in sanitized
    assert "\x01" not in sanitized
    assert "\x02" not in sanitized

def test_audit_logger():
    """Test audit logging functionality"""
    from backend.advanced_security import AuditLogger, SecurityEvent, ThreatLevel

    logger = AuditLogger(log_dir="backend/logs/test")

    # Create test security event
    event = SecurityEvent(
        event_type="test_event",
        severity=ThreatLevel.MEDIUM,
        source="test",
        description="Test security event",
        details={"test": "data"}
    )

    # Log the event
    logger.log_security_event(event)

    # Check event was recorded
    assert len(logger.recent_events) > 0
    assert logger.event_stats["total_events"] > 0
    assert "test_event" in logger.event_stats["events_by_type"]

    # Test event filtering
    events = logger.get_recent_events(severity=ThreatLevel.MEDIUM)
    assert len(events) > 0
    assert all(e["severity"] == "medium" for e in events)

def test_rate_limiting_store():
    """Test rate limiting store functionality"""
    import time

    from backend.rate_limiting import RateLimitStore

    store = RateLimitStore()

    # Test request recording with current timestamp
    current_time = time.time()
    store.record_request("test_client", current_time)
    assert len(store.requests["test_client"]) == 1

    # Test recent request counting
    count = store.get_recent_requests("test_client", 60)
    assert count >= 1

    # Test client blocking
    store.block_client("bad_client", 300)
    assert store.is_blocked("bad_client")

    # Test security event recording
    store.record_security_event("test_threat", "bad_client", "Test threat detected")
    assert len(store.security_events) > 0

def test_json_validation():
    """Test JSON input validation"""
    from backend.advanced_security import AdvancedInputValidator

    validator = AdvancedInputValidator()

    # Test valid JSON
    valid_json = '{"key": "value", "number": 42}'
    is_valid, data = validator.validate_json_input(valid_json)
    assert is_valid
    assert data["key"] == "value"
    assert data["number"] == 42

    # Test invalid JSON
    invalid_json = '{"invalid": json}'
    is_valid, data = validator.validate_json_input(invalid_json)
    assert not is_valid
    assert data is None

    # Test JSON with threats
    threat_json = '{"script": "<script>alert()</script>"}'
    is_valid, data = validator.validate_json_input(threat_json)
    assert not is_valid  # Should be blocked due to XSS content

    # Test overly complex JSON
    complex_json = '{"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": ' \
                   '{"i": {"j": {}}}}}}}}}}'
    is_valid, data = validator.validate_json_input(complex_json, max_depth=5)
    assert not is_valid  # Should be blocked due to depth

def test_compliance_manager():
    """Test GDPR/SOC2 compliance management"""
    from backend.advanced_security import AuditLogger, ComplianceManager

    audit_logger = AuditLogger(log_dir="backend/logs/test")
    compliance = ComplianceManager(audit_logger)

    # Test data access logging
    compliance.log_data_access("user123", "personal_data", "read", "service_provision")
    assert len(audit_logger.recent_events) > 0

    # Test deletion request handling
    result = compliance.handle_data_deletion_request("user123")
    assert result["status"] in ["deletion_request_logged", "gdpr_not_enabled"]

    # Test compliance report generation
    report = compliance.generate_compliance_report()
    assert "gdpr_compliance" in report
    assert "soc2_compliance" in report
    assert "report_generated" in report

@pytest.mark.asyncio
async def test_security_integration():
    """Test integration of security components"""
    from backend.advanced_security import (
        get_advanced_security_config,
        validate_input_security,
    )

    # Test global security config
    config = get_advanced_security_config()
    assert config is not None

    # Test input validation integration
    is_safe, sanitized = validate_input_security("Normal input", "test")
    assert is_safe
    assert sanitized == "Normal input"

    # Test threat detection integration
    is_safe, sanitized = validate_input_security(
        "<script>alert('xss')</script>", "test"
    )
    # Should be sanitized even if not completely blocked
    assert "&lt;" in sanitized or not is_safe

def test_security_configuration_env_vars():
    """Test security configuration with environment variables"""
    import os

    from backend.advanced_security import SecurityConfig

    # Mock environment variables
    with patch.dict(os.environ, {
        'MAX_REQUEST_SIZE': '5242880',  # 5MB
        'MAX_FILE_SIZE': '26214400',    # 25MB
        'ENABLE_AUDIT_LOGGING': 'false',
        'ENABLE_THREAT_DETECTION': 'false'
    }):
        config = SecurityConfig()
        assert config.max_request_size == 5242880
        assert config.max_file_size == 26214400
        assert not config.enable_audit_logging
        assert not config.enable_threat_detection

def test_security_status_endpoint():
    """Test security status reporting"""
    from backend.advanced_security import get_advanced_security_config

    config = get_advanced_security_config()
    status = config.get_security_status()

    # Check required fields
    assert "audit_logging_enabled" in status
    assert "threat_detection_enabled" in status
    assert "max_request_size" in status
    assert "max_file_size" in status
    assert "allowed_extensions" in status
    assert "blocked_extensions" in status

    # Check security summary if audit logging is enabled
    if config.audit_logger:
        assert "security_summary" in status

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
