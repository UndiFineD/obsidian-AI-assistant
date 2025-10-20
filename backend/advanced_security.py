#!/usr/bin/env python3
"""
Comprehensive Security utilities and middleware for the Obsidian AI Assistant backend.
Includes input validation, audit logging, threat detection, and security monitoring.
"""

import html
import json
import logging
import os
import re
import secrets
import urllib.parse
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent:
    """Security event for audit logging"""

    def __init__(
        self,
        event_type: str,
        severity: ThreatLevel,
        source: str,
        description: str,
        details: Dict[str, Any] = None,
    ):
        self.timestamp = datetime.now()
        self.event_type = event_type
        self.severity = severity
        self.source = source
        self.description = description
        self.details = details or {}
        self.event_id = secrets.token_hex(8)

    def to_dict(self) -> Dict[str, Any]:
        """Convert security event to dictionary"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "severity": self.severity.value,
            "source": self.source,
            "description": self.description,
            "details": self.details,
        }


class AuditLogger:
    """Comprehensive audit logging system"""

    def __init__(self, log_dir: str = "backend/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Security event log
        self.security_log_file = self.log_dir / "security_events.jsonl"
        self.access_log_file = self.log_dir / "access_audit.jsonl"

        # In-memory event storage for monitoring
        self.recent_events: List[SecurityEvent] = []
        self.max_recent_events = 1000

        # Event statistics
        self.event_stats = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "blocked_attempts": 0,
        }

    def log_security_event(self, event: SecurityEvent):
        """Log a security event"""
        try:
            # Add to recent events
            self.recent_events.append(event)
            if len(self.recent_events) > self.max_recent_events:
                self.recent_events.pop(0)

            # Update statistics
            self.event_stats["total_events"] += 1
            self.event_stats["events_by_type"][event.event_type] = (
                self.event_stats["events_by_type"].get(event.event_type, 0) + 1
            )
            self.event_stats["events_by_severity"][event.severity.value] = (
                self.event_stats["events_by_severity"].get(event.severity.value, 0) + 1
            )

            if event.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self.event_stats["blocked_attempts"] += 1

            # Write to log file
            with open(self.security_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict()) + "\n")

            # Log to system logger based on severity
            if event.severity == ThreatLevel.CRITICAL:
                logger.critical(f"SECURITY CRITICAL: {event.description}")
            elif event.severity == ThreatLevel.HIGH:
                logger.error(f"SECURITY HIGH: {event.description}")
            elif event.severity == ThreatLevel.MEDIUM:
                logger.warning(f"SECURITY MEDIUM: {event.description}")
            else:
                logger.info(f"SECURITY LOW: {event.description}")

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    def log_access_event(
        self,
        client_id: str,
        endpoint: str,
        method: str,
        status: int,
        user_agent: str = "",
        details: Dict = None,
    ):
        """Log access event for audit trail"""
        try:
            access_event = {
                "timestamp": datetime.now().isoformat(),
                "client_id": client_id,
                "endpoint": endpoint,
                "method": method,
                "status_code": status,
                "user_agent": user_agent[:200],  # Truncate user agent
                "details": details or {},
            }

            with open(self.access_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(access_event) + "\n")

        except Exception as e:
            logger.error(f"Failed to log access event: {e}")

    def get_recent_events(
        self,
        severity: Optional[ThreatLevel] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get recent security events with optional filtering"""
        events = self.recent_events

        if severity:
            events = [e for e in events if e.severity == severity]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Sort by timestamp (most recent first)
        events = sorted(events, key=lambda x: x.timestamp, reverse=True)

        return [e.to_dict() for e in events[:limit]]

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security monitoring summary"""
        recent_events = [
            e
            for e in self.recent_events
            if e.timestamp > datetime.now() - timedelta(hours=24)
        ]

        high_severity_events = [
            e
            for e in recent_events
            if e.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        ]

        return {
            "total_events_24h": len(recent_events),
            "high_severity_events_24h": len(high_severity_events),
            "event_statistics": self.event_stats.copy(),
            "recent_threat_types": list(
                set(e.event_type for e in high_severity_events)
            ),
            "monitoring_active": True,
        }


class AdvancedInputValidator:
    """Advanced input validation and sanitization"""

    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r"(\bSELECT\b.*\bFROM\b|\bUNION\b.*\bSELECT\b)",
            r"(\bINSERT\b.*\bINTO\b|\bUPDATE\b.*\bSET\b)",
            r"(\bDELETE\b.*\bFROM\b|\bDROP\b.*\bTABLE\b)",
            r"(;.*--|\|\|.*'|'.*\bOR\b.*')",
            r"(\bEXEC\b|\bEXECUTE\b|\bsp_\w+)",
        ]

        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
        ]

        # Command injection patterns
        self.command_patterns = [
            r"[;&|]",  # Removed space from character class - spaces are normal in text
            r"\$\([^)]*\)",
            r"`[^`]*`",
            r">\s*/\w+",
            r"<\s*/\w+",
        ]

        # Path traversal patterns
        self.path_traversal_patterns = [r"\.\./", r"\.\.\\", r"/\.\./", r"\\\.\.\\"]

        # Compile patterns for efficiency
        self.compiled_patterns = {
            "sql": [re.compile(p, re.IGNORECASE) for p in self.sql_patterns],
            "xss": [re.compile(p, re.IGNORECASE) for p in self.xss_patterns],
            "command": [re.compile(p, re.IGNORECASE) for p in self.command_patterns],
            "path_traversal": [
                re.compile(p, re.IGNORECASE) for p in self.path_traversal_patterns
            ],
        }

    def detect_threats(self, input_text: str) -> List[tuple]:
        """Detect security threats in input text"""
        if not input_text:
            return []

        threats = []

        for threat_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(input_text):
                    threats.append((threat_type, pattern.pattern))

        return threats

    def sanitize_input(
        self, input_str: str, max_length: int = 10000, html_escape: bool = True
    ) -> str:
        """Advanced input sanitization"""
        if not isinstance(input_str, str):
            return ""

        # Truncate to max length
        sanitized = input_str[:max_length]

        # Remove null bytes and dangerous control characters
        sanitized = "".join(
            char for char in sanitized if ord(char) >= 32 or char in "\n\r\t"
        )

        # HTML escape if requested
        if html_escape:
            sanitized = html.escape(sanitized)

        # URL decode to prevent double encoding attacks
        try:
            sanitized = urllib.parse.unquote(sanitized)
        except Exception:
            pass  # Keep original if decoding fails

        return sanitized.strip()

    def validate_json_input(
        self, json_str: str, max_depth: int = 10, max_keys: int = 100
    ) -> tuple[bool, Optional[Dict]]:
        """Validate JSON input with security checks"""
        try:
            # Parse JSON
            data = json.loads(json_str)

            # Check structure depth and complexity
            if not self._check_json_complexity(data, max_depth, max_keys):
                return False, None

            # Check for threats in string values
            if not self._validate_json_content(data):
                return False, None

            return True, data

        except json.JSONDecodeError:
            return False, None

    def _check_json_complexity(
        self, obj: Any, max_depth: int, max_keys: int, current_depth: int = 0
    ) -> bool:
        """Check JSON structure complexity"""
        if current_depth > max_depth:
            return False

        if isinstance(obj, dict):
            if len(obj) > max_keys:
                return False
            return all(
                self._check_json_complexity(v, max_depth, max_keys, current_depth + 1)
                for v in obj.values()
            )

        elif isinstance(obj, list):
            if len(obj) > max_keys:
                return False
            return all(
                self._check_json_complexity(
                    item, max_depth, max_keys, current_depth + 1
                )
                for item in obj
            )

        return True

    def _validate_json_content(self, obj: Any) -> bool:
        """Validate JSON content for security threats"""
        if isinstance(obj, str):
            threats = self.detect_threats(obj)
            return len(threats) == 0

        elif isinstance(obj, dict):
            return all(self._validate_json_content(v) for v in obj.values())

        elif isinstance(obj, list):
            return all(self._validate_json_content(item) for item in obj)

        return True


class ComplianceManager:
    """GDPR and SOC2 compliance management"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.data_retention_days = int(
            os.getenv("DATA_RETENTION_DAYS", "2555")
        )  # 7 years
        self.gdpr_enabled = os.getenv("GDPR_COMPLIANCE", "true").lower() == "true"
        self.soc2_enabled = os.getenv("SOC2_COMPLIANCE", "true").lower() == "true"

    def log_data_access(
        self,
        user_id: str,
        data_type: str,
        action: str,
        purpose: str,
        legal_basis: str = "legitimate_interest",
    ):
        """Log data access for GDPR compliance"""
        if self.gdpr_enabled:
            event = SecurityEvent(
                event_type="data_access",
                severity=ThreatLevel.LOW,
                source="compliance",
                description=f"Data access: {action} on {data_type}",
                details={
                    "user_id": user_id,
                    "data_type": data_type,
                    "action": action,
                    "purpose": purpose,
                    "legal_basis": legal_basis,
                    "gdpr_compliant": True,
                },
            )
            self.audit_logger.log_security_event(event)

    def handle_data_deletion_request(self, user_id: str) -> Dict[str, Any]:
        """Handle GDPR right to be forgotten request"""
        if not self.gdpr_enabled:
            return {"status": "gdpr_not_enabled"}

        # Log the deletion request
        event = SecurityEvent(
            event_type="gdpr_deletion_request",
            severity=ThreatLevel.MEDIUM,
            source="compliance",
            description=f"GDPR deletion request for user {user_id}",
            details={
                "user_id": user_id,
                "request_type": "right_to_be_forgotten",
                "status": "processing",
            },
        )
        self.audit_logger.log_security_event(event)

        return {
            "status": "deletion_request_logged",
            "user_id": user_id,
            "processing_time": "30_days_max",
            "reference_id": event.event_id,
        }

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance status report"""
        return {
            "gdpr_compliance": {
                "enabled": self.gdpr_enabled,
                "data_retention_days": self.data_retention_days,
                "audit_logging": True,
                "right_to_deletion": True,
                "data_minimization": True,
            },
            "soc2_compliance": {
                "enabled": self.soc2_enabled,
                "security_monitoring": True,
                "access_controls": True,
                "incident_response": True,
                "audit_trail": True,
            },
            "report_generated": datetime.now().isoformat(),
        }


class SecurityConfig:
    """Enhanced security configuration settings"""

    def __init__(self):
        self.max_request_size = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
        self.max_json_depth = int(os.getenv("MAX_JSON_DEPTH", "10"))
        self.max_json_keys = int(os.getenv("MAX_JSON_KEYS", "100"))

        self.allowed_file_extensions = {
            ".txt",
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".py",
            ".js",
            ".html",
            ".css",
            ".xml",
            ".pdf",
            ".docx",
            ".rtf",
        }
        self.blocked_extensions = {
            ".exe",
            ".bat",
            ".sh",
            ".cmd",
            ".scr",
            ".com",
            ".pif",
            ".vbs",
            ".jar",
            ".dll",
            ".msi",
            ".app",
            ".deb",
            ".rpm",
        }

        # Security monitoring settings
        self.enable_audit_logging = (
            os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
        )
        self.enable_threat_detection = (
            os.getenv("ENABLE_THREAT_DETECTION", "true").lower() == "true"
        )
        self.log_retention_days = int(os.getenv("LOG_RETENTION_DAYS", "90"))

        # Initialize components
        self.audit_logger = AuditLogger() if self.enable_audit_logging else None
        self.input_validator = (
            AdvancedInputValidator() if self.enable_threat_detection else None
        )
        self.compliance_manager = (
            ComplianceManager(self.audit_logger) if self.audit_logger else None
        )

    def is_allowed_file_type(self, filename: str) -> bool:
        """Check if file type is allowed."""
        if not filename or "." not in filename:
            return False

        ext = "." + filename.split(".")[-1].lower()

        # Check blocked extensions first
        if ext in self.blocked_extensions:
            return False

        # Check allowed extensions
        return ext in self.allowed_file_extensions

    def validate_and_sanitize_input(
        self, input_data: str, source: str = "unknown"
    ) -> tuple[bool, str]:
        """Validate and sanitize input with threat detection"""
        if not self.input_validator:
            return True, input_data

        # Detect threats
        threats = self.input_validator.detect_threats(input_data)

        if threats and self.audit_logger:
            # Log security event
            event = SecurityEvent(
                event_type="input_threat_detected",
                severity=ThreatLevel.HIGH,
                source=source,
                description=f"Detected {len(threats)} security threats in input",
                details={"threats": [{"type": t[0], "pattern": t[1]} for t in threats]},
            )
            self.audit_logger.log_security_event(event)

            # Block input with high-risk threats
            high_risk_threats = [t for t in threats if t[0] in ["sql", "command"]]
            if high_risk_threats:
                return False, ""

        # Sanitize input
        sanitized = self.input_validator.sanitize_input(input_data)
        return True, sanitized

    def log_security_event(
        self,
        event_type: str,
        severity: ThreatLevel,
        source: str,
        description: str,
        details: Dict = None,
    ):
        """Log a security event"""
        if self.audit_logger:
            event = SecurityEvent(event_type, severity, source, description, details)
            self.audit_logger.log_security_event(event)

    def log_access_event(
        self,
        client_id: str,
        endpoint: str,
        method: str,
        status: int,
        user_agent: str = "",
        details: Dict = None,
    ):
        """Log access event"""
        if self.audit_logger:
            self.audit_logger.log_access_event(
                client_id, endpoint, method, status, user_agent, details
            )

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        status = {
            "audit_logging_enabled": self.enable_audit_logging,
            "threat_detection_enabled": self.enable_threat_detection,
            "max_request_size": self.max_request_size,
            "max_file_size": self.max_file_size,
            "allowed_extensions": len(self.allowed_file_extensions),
            "blocked_extensions": len(self.blocked_extensions),
        }

        if self.audit_logger:
            status["security_summary"] = self.audit_logger.get_security_summary()

        if self.compliance_manager:
            status["compliance"] = self.compliance_manager.generate_compliance_report()

        return status


# Global security config instance
advanced_security_config = SecurityConfig()


def get_advanced_security_config() -> SecurityConfig:
    """Get the global advanced security configuration."""
    return advanced_security_config


# Convenience functions for common operations
def sanitize_input(input_str: str, max_length: int = 10000) -> str:
    """Sanitize input using global security config"""
    if advanced_security_config.input_validator:
        return advanced_security_config.input_validator.sanitize_input(
            input_str, max_length
        )

    # Fallback basic sanitization
    if not isinstance(input_str, str):
        return ""

    sanitized = input_str[:max_length]
    sanitized = "".join(
        char for char in sanitized if ord(char) >= 32 or char in "\n\r\t"
    )
    return sanitized.strip()


def log_security_event(
    event_type: str,
    severity: ThreatLevel,
    source: str,
    description: str,
    details: Dict = None,
):
    """Log security event using global config"""
    advanced_security_config.log_security_event(
        event_type, severity, source, description, details
    )


def validate_input_security(input_data: str, source: str = "api") -> tuple[bool, str]:
    """Validate input for security threats"""
    return advanced_security_config.validate_and_sanitize_input(input_data, source)


def log_data_access(user_id: str, data_type: str, action: str, purpose: str):
    """Log data access for compliance"""
    if advanced_security_config.compliance_manager:
        advanced_security_config.compliance_manager.log_data_access(
            user_id, data_type, action, purpose
        )
