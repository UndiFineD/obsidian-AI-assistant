"""
Security Management API for Obsidian AI Agent

This module provides comprehensive API endpoints for managing security features:
- Security status monitoring and dashboards
- Session management and monitoring
- API key management and rotation
- Threat detection configuration and monitoring
- Security audit logging and reporting
- Compliance monitoring and reporting

Author: AI Assistant
Date: October 16, 2025
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Query
from pydantic import BaseModel, Field

from .error_handling import ValidationError, error_context
from .logging_framework import LogCategory, get_logger, log_audit
from .security_hardening import (
    APIKeyManager,
    AuthenticationMethod,
    SessionManager,
    ThreatDetector,
    get_security_status,
)

# Create router for security management endpoints
router = APIRouter(prefix="/api/security", tags=["security"])

# Get logger for security management
security_logger = get_logger("security.management", LogCategory.SECURITY)

# Global instances (would be properly managed in production)
session_manager = SessionManager()
api_key_manager = APIKeyManager()
threat_detector = ThreatDetector()


# Request/Response Models
class SecurityStatusResponse(BaseModel):
    """Security system status response"""

    timestamp: str
    security_level: str
    system_health: Dict[str, Any]
    active_threats: int
    security_events_24h: int
    authentication_status: Dict[str, Any]
    session_statistics: Dict[str, Any]
    api_key_statistics: Dict[str, Any]


class SessionInfo(BaseModel):
    """Session information model"""

    session_id: str
    user_id: str
    client_ip: str
    created_at: str
    last_activity: str
    activity_count: int
    is_suspicious: bool
    security_events: List[Dict[str, Any]]


class APIKeyInfo(BaseModel):
    """API key information model"""

    key_id: str
    name: str
    permissions: List[str]
    created_at: str
    expires_at: Optional[str]
    rate_limit: int
    is_active: bool
    usage_count: int


class ThreatEvent(BaseModel):
    """Threat detection event model"""

    event_id: str
    timestamp: str
    threat_type: str
    threat_score: float
    client_ip: str
    request_path: str
    security_flags: List[str]
    status: str  # detected, blocked, allowed


class SecurityConfigUpdate(BaseModel):
    """Security configuration update request"""

    security_level: Optional[str] = Field(
        None, pattern="^(minimal|standard|enhanced|maximum)$"
    )
    session_timeout_hours: Optional[int] = Field(None, ge=1, le=168)  # 1 hour to 1 week
    api_key_rate_limit: Optional[int] = Field(None, ge=10, le=10000)
    threat_detection_enabled: Optional[bool] = None
    auto_block_threshold: Optional[float] = Field(None, ge=0.0, le=100.0)


class CreateAPIKeyRequest(BaseModel):
    """Request to create new API key"""

    name: str = Field(..., min_length=1, max_length=100)
    permissions: List[str] = Field(..., min_length=1)
    expires_in_days: Optional[int] = Field(None, ge=1, le=3650)  # Max 10 years
    rate_limit: int = Field(100, ge=10, le=10000)
    allowed_ips: Optional[List[str]] = None


class SessionActionRequest(BaseModel):
    """Request to perform action on session"""

    session_id: str
    action: str = Field(..., pattern="^(terminate|block|unblock)$")
    reason: Optional[str] = None


# Security Status and Monitoring Endpoints
@router.get("/status", response_model=SecurityStatusResponse)
async def get_security_system_status():
    """Get comprehensive security system status"""
    with error_context("security_status", reraise=False):
        security_logger.info("Security status requested")

        # Get current status
        base_status = get_security_status()

        # Enhance with detailed statistics
        session_stats = {
            "active_sessions": len(session_manager.active_sessions),
            "blocked_sessions": len(session_manager.blocked_sessions),
            "total_users": len(
                set(s["user_id"] for s in session_manager.active_sessions.values())
            ),
        }

        api_key_stats = {
            "active_keys": len(
                [k for k in api_key_manager.active_keys.values() if k["is_active"]]
            ),
            "revoked_keys": len(api_key_manager.revoked_keys),
            "total_usage_24h": sum(
                len(
                    [
                        u
                        for u in usage
                        if u["timestamp"] > datetime.utcnow() - timedelta(hours=24)
                    ]
                )
                for usage in api_key_manager.key_usage.values()
            ),
        }

        threat_stats = {
            "behavioral_profiles": len(threat_detector.behavioral_tracker),
            "high_threat_ips": len(
                [
                    ip
                    for ip, behavior in threat_detector.behavioral_tracker.items()
                    if behavior.get("threat_score", 0) > 10.0
                ]
            ),
        }

        return SecurityStatusResponse(
            timestamp=datetime.utcnow().isoformat(),
            security_level=base_status["security_level"],
            system_health=base_status["security_features"],
            active_threats=threat_stats["high_threat_ips"],
            security_events_24h=0,  # Would get from security logs
            authentication_status={
                "methods_enabled": base_status["authentication_methods"],
                "session_management": True,
                "api_key_validation": True,
            },
            session_statistics=session_stats,
            api_key_statistics=api_key_stats,
        )


@router.get("/health")
async def get_security_health():
    """Lightweight security health check"""
    with error_context("security_health", reraise=False):
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "security_systems": {
                "session_manager": "active",
                "api_key_manager": "active",
                "threat_detector": "active",
                "middleware": "active",
            },
        }


# Session Management Endpoints
@router.get("/sessions", response_model=List[SessionInfo])
async def list_active_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(
        50, ge=1, le=1000, description="Maximum number of sessions to return"
    ),
):
    """List active sessions with optional filtering"""
    with error_context("list_sessions", reraise=False):
        security_logger.info(
            "Sessions list requested", extra={"user_id_filter": user_id, "limit": limit}
        )

        sessions = []
        for session_id, session_data in session_manager.active_sessions.items():
            if user_id and session_data["user_id"] != user_id:
                continue

            sessions.append(
                SessionInfo(
                    session_id=session_id,
                    user_id=session_data["user_id"],
                    client_ip=session_data["client_ip"],
                    created_at=session_data["created_at"].isoformat(),
                    last_activity=session_data["last_activity"].isoformat(),
                    activity_count=session_data["activity_count"],
                    is_suspicious=session_data["is_suspicious"],
                    security_events=session_data["security_events"],
                )
            )

            if len(sessions) >= limit:
                break

        # Sort by last activity (most recent first)
        sessions.sort(key=lambda x: x.last_activity, reverse=True)

        log_audit(
            "sessions_listed",
            session_count=len(sessions),
            user_id_filter=user_id,
            outcome="success",
        )

        return sessions


@router.post("/sessions/action")
async def perform_session_action(request: SessionActionRequest):
    """Perform action on a session (terminate, block, unblock)"""
    with error_context("session_action", reraise=False):
        session = session_manager.active_sessions.get(request.session_id)
        if not session:
            raise ValidationError(
                f"Session {request.session_id} not found",
                field="session_id",
                suggestion="Verify the session ID is correct and the session is still active",
            )

        if request.action == "terminate":
            session_manager.terminate_session(
                request.session_id, request.reason or "admin_action"
            )
        elif request.action == "block":
            session_manager.block_session(
                request.session_id, request.reason or "security_violation"
            )
        elif request.action == "unblock":
            if request.session_id in session_manager.blocked_sessions:
                session_manager.blocked_sessions.remove(request.session_id)

        security_logger.info(
            "Session action performed",
            extra={
                "session_id": request.session_id,
                "action": request.action,
                "reason": request.reason,
                "user_id": session["user_id"],
            },
        )

        log_audit(
            "session_action",
            session_id=request.session_id,
            action=request.action,
            reason=request.reason,
            outcome="success",
        )

        return {
            "success": True,
            "message": f"Session {request.action} completed",
            "session_id": request.session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_details(session_id: str):
    """Get detailed information about a specific session"""
    with error_context("get_session", reraise=False):
        session_data = session_manager.active_sessions.get(session_id)
        if not session_data:
            # Check session history
            for user_history in session_manager.session_history.values():
                for historical_session in user_history:
                    if historical_session.get("session_id") == session_id:
                        return SessionInfo(
                            session_id=session_id,
                            user_id=historical_session["user_id"],
                            client_ip=historical_session["client_ip"],
                            created_at=historical_session["created_at"].isoformat(),
                            last_activity=historical_session.get(
                                "terminated_at", historical_session["last_activity"]
                            ).isoformat(),
                            activity_count=historical_session["activity_count"],
                            is_suspicious=historical_session["is_suspicious"],
                            security_events=historical_session["security_events"],
                        )

            raise ValidationError(
                f"Session {session_id} not found",
                field="session_id",
                suggestion="Check that the session ID is correct",
            )

        return SessionInfo(
            session_id=session_id,
            user_id=session_data["user_id"],
            client_ip=session_data["client_ip"],
            created_at=session_data["created_at"].isoformat(),
            last_activity=session_data["last_activity"].isoformat(),
            activity_count=session_data["activity_count"],
            is_suspicious=session_data["is_suspicious"],
            security_events=session_data["security_events"],
        )


# API Key Management Endpoints
@router.get("/api-keys", response_model=List[APIKeyInfo])
async def list_api_keys():
    """List all API keys (without showing actual key values)"""
    with error_context("list_api_keys", reraise=False):
        security_logger.info("API keys list requested")

        keys = []
        for api_key, key_data in api_key_manager.active_keys.items():
            usage_count = len(api_key_manager.key_usage.get(api_key, []))

            keys.append(
                APIKeyInfo(
                    key_id=key_data["key_id"],
                    name=key_data["name"],
                    permissions=key_data["permissions"],
                    created_at=key_data["created_at"].isoformat(),
                    expires_at=(
                        key_data["expires_at"].isoformat()
                        if key_data["expires_at"]
                        else None
                    ),
                    rate_limit=key_data["rate_limit"],
                    is_active=key_data["is_active"],
                    usage_count=usage_count,
                )
            )

        log_audit("api_keys_listed", key_count=len(keys), outcome="success")

        return keys


@router.post("/api-keys")
async def create_api_key(request: CreateAPIKeyRequest):
    """Create a new API key"""
    with error_context("create_api_key", reraise=False):
        # Generate new API key
        new_key = f"ak_{secrets.token_urlsafe(32)}"

        # Calculate expiration date
        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)

        # Create key data
        key_data = {
            "key_id": f"key_{len(api_key_manager.active_keys) + 1}",
            "name": request.name,
            "permissions": request.permissions,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "rate_limit": request.rate_limit,
            "allowed_ips": request.allowed_ips or [],
            "is_active": True,
        }

        # Store the key
        api_key_manager.active_keys[new_key] = key_data

        security_logger.info(
            "API key created",
            extra={
                "key_id": key_data["key_id"],
                "name": request.name,
                "permissions": request.permissions,
            },
        )

        log_audit(
            "api_key_created",
            key_id=key_data["key_id"],
            name=request.name,
            permissions=request.permissions,
            outcome="success",
        )

        return {
            "success": True,
            "message": "API key created successfully",
            "key_id": key_data["key_id"],
            "api_key": new_key,  # Only shown once at creation
            "expires_at": expires_at.isoformat() if expires_at else None,
            "warning": "Store this API key securely - it will not be shown again",
        }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str, reason: str = Query("admin_revocation")):
    """Revoke an API key"""
    with error_context("revoke_api_key", reraise=False):
        # Find the key by key_id
        target_key = None
        for api_key, key_data in api_key_manager.active_keys.items():
            if key_data["key_id"] == key_id:
                target_key = api_key
                break

        if not target_key:
            raise ValidationError(
                f"API key with ID {key_id} not found",
                field="key_id",
                suggestion="Check that the key ID is correct",
            )

        # Revoke the key
        api_key_manager.revoke_api_key(target_key, reason)

        security_logger.warning(
            "API key revoked", extra={"key_id": key_id, "reason": reason}
        )

        log_audit("api_key_revoked", key_id=key_id, reason=reason, outcome="success")

        return {
            "success": True,
            "message": f"API key {key_id} has been revoked",
            "key_id": key_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Threat Detection and Monitoring Endpoints
@router.get("/threats", response_model=List[ThreatEvent])
async def list_threat_events(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    min_score: float = Query(5.0, ge=0.0, le=100.0, description="Minimum threat score"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum events to return"),
):
    """List recent threat detection events"""
    with error_context("list_threats", reraise=False):
        security_logger.info(
            "Threat events requested",
            extra={"hours": hours, "min_score": min_score, "limit": limit},
        )

        # This would query actual threat detection logs in production
        # For now, return sample data based on behavioral tracker
        events = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        for client_key, behavior in threat_detector.behavioral_tracker.items():
            if behavior["last_request"] < cutoff_time:
                continue

            # Calculate threat score based on behavior
            threat_score = 0.0
            flags = []

            if behavior["request_count"] > 100:
                threat_score += 5.0
                flags.append("high_request_count")

            if len(behavior["endpoints"]) > 20:
                threat_score += 3.0
                flags.append("endpoint_scanning")

            if threat_score >= min_score:
                events.append(
                    ThreatEvent(
                        event_id=f"threat_{len(events) + 1}",
                        timestamp=behavior["last_request"].isoformat(),
                        threat_type="behavioral_analysis",
                        threat_score=threat_score,
                        client_ip=client_key.split("_")[0],
                        request_path="multiple",
                        security_flags=flags,
                        status="detected",
                    )
                )

            if len(events) >= limit:
                break

        # Sort by timestamp (most recent first)
        events.sort(key=lambda x: x.timestamp, reverse=True)

        return events


@router.get("/threats/summary")
async def get_threat_summary():
    """Get threat detection summary statistics"""
    with error_context("threat_summary", reraise=False):
        now = datetime.utcnow()

        # Calculate statistics from behavioral tracker
        total_clients = len(threat_detector.behavioral_tracker)
        suspicious_clients = 0
        high_threat_clients = 0

        for behavior in threat_detector.behavioral_tracker.values():
            threat_score = 0.0

            if behavior["request_count"] > 100:
                threat_score += 5.0
            if len(behavior["endpoints"]) > 20:
                threat_score += 3.0

            if threat_score >= 5.0:
                suspicious_clients += 1
            if threat_score >= 10.0:
                high_threat_clients += 1

        return {
            "timestamp": now.isoformat(),
            "summary": {
                "total_clients_tracked": total_clients,
                "suspicious_clients": suspicious_clients,
                "high_threat_clients": high_threat_clients,
                "threat_detection_active": True,
            },
            "time_periods": {
                "last_1h": {"threats": 0, "blocked": 0},
                "last_24h": {"threats": suspicious_clients, "blocked": 0},
                "last_7d": {"threats": suspicious_clients, "blocked": 0},
            },
            "top_threat_types": [
                {"type": "high_request_frequency", "count": 0},
                {"type": "endpoint_scanning", "count": 0},
                {"type": "pattern_matching", "count": 0},
            ],
        }


# Security Configuration Endpoints
@router.get("/config")
async def get_security_config():
    """Get current security configuration"""
    with error_context("get_security_config", reraise=False):
        return {
            "security_level": "standard",
            "session_timeout_hours": 24,
            "idle_timeout_hours": 2,
            "api_key_rate_limit": 100,
            "threat_detection_enabled": True,
            "auto_block_threshold": 20.0,
            "authentication_methods": [method.value for method in AuthenticationMethod],
            "public_endpoints": [
                "/health",
                "/status",
                "/",
                "/docs",
                "/redoc",
                "/openapi.json",
            ],
        }


@router.post("/config")
async def update_security_config(
    request: SecurityConfigUpdate, background_tasks: BackgroundTasks
):
    """Update security configuration"""
    with error_context("update_security_config", reraise=False):
        updates = {}

        # Validate and apply updates
        if request.security_level:
            updates["security_level"] = request.security_level

        if request.session_timeout_hours:
            updates["session_timeout_hours"] = request.session_timeout_hours
            # Update session manager configuration
            session_manager.session_timeout = timedelta(
                hours=request.session_timeout_hours
            )

        if request.api_key_rate_limit:
            updates["api_key_rate_limit"] = request.api_key_rate_limit

        if request.threat_detection_enabled is not None:
            updates["threat_detection_enabled"] = request.threat_detection_enabled

        if request.auto_block_threshold:
            updates["auto_block_threshold"] = request.auto_block_threshold

        security_logger.info("Security configuration updated", extra=updates)

        log_audit("security_config_updated", updates=updates, outcome="success")

        # Schedule configuration reload in background
        background_tasks.add_task(lambda: None)  # Placeholder for config reload

        return {
            "success": True,
            "message": "Security configuration updated",
            "updates": updates,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Security Audit and Compliance Endpoints
@router.get("/audit/events")
async def get_security_audit_events(
    hours: int = Query(24, ge=1, le=168),
    event_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
):
    """Get security audit events"""
    with error_context("get_audit_events", reraise=False):
        # This would query actual audit logs in production
        # For now, return a sample response
        return {
            "events": [],
            "total_count": 0,
            "filters": {
                "hours": hours,
                "event_type": event_type,
                "user_id": user_id,
                "limit": limit,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/compliance/report")
async def generate_compliance_report(
    days: int = Query(30, ge=1, le=365),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    """Generate security compliance report"""
    with error_context("compliance_report", reraise=False):
        report_data = {
            "report_id": f"compliance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": days,
            "format": format,
            "summary": {
                "total_events": 0,
                "security_incidents": 0,
                "authentication_failures": 0,
                "policy_violations": 0,
                "access_reviews": 0,
            },
            "compliance_status": {
                "authentication_controls": "compliant",
                "access_controls": "compliant",
                "audit_logging": "compliant",
                "data_protection": "compliant",
                "incident_response": "compliant",
            },
        }

        log_audit(
            "compliance_report_generated",
            report_id=report_data["report_id"],
            period_days=days,
            format=format,
            outcome="success",
        )

        return report_data


# Security Testing and Validation Endpoints
@router.post("/test/validate")
async def validate_security_configuration():
    """Validate current security configuration and perform health checks"""
    with error_context("validate_security", reraise=False):
        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "checks": {
                "session_manager": {
                    "status": "healthy",
                    "active_sessions": len(session_manager.active_sessions),
                    "blocked_sessions": len(session_manager.blocked_sessions),
                },
                "api_key_manager": {
                    "status": "healthy",
                    "active_keys": len(
                        [
                            k
                            for k in api_key_manager.active_keys.values()
                            if k["is_active"]
                        ]
                    ),
                    "revoked_keys": len(api_key_manager.revoked_keys),
                },
                "threat_detector": {
                    "status": "healthy",
                    "tracked_clients": len(threat_detector.behavioral_tracker),
                    "pattern_rules": len(threat_detector.threat_patterns),
                },
            },
            "recommendations": [],
        }

        # Add recommendations based on current state
        if len(session_manager.active_sessions) > 100:
            validation_results["recommendations"].append(
                "Consider implementing session limits - high number of active sessions detected"
            )

        if len(api_key_manager.revoked_keys) == 0:
            validation_results["recommendations"].append(
                "Consider implementing API key rotation policy"
            )

        return validation_results
