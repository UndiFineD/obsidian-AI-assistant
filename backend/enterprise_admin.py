# Enterprise Admin Dashboard Module
# Comprehensive administrative interface for enterprise features

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging
from fastapi import HTTPException
from .enterprise_auth import SSOManager
from .enterprise_tenant import TenantManager
from .enterprise_rbac import RBACManager
from .enterprise_gdpr import GDPRComplianceManager
from .enterprise_soc2 import SOC2ComplianceManager

logger = logging.getLogger(__name__)

@dataclass
class DashboardMetrics:
    """Dashboard metrics summary"""
    total_users: int
    active_users_30d: int
    total_tenants: int
    active_tenants: int
    total_queries_30d: int
    avg_response_time_ms: float
    system_availability: float
    storage_used_gb: float
    storage_limit_gb: float
    
@dataclass
class UserActivity:
    """User activity summary"""
    user_id: str
    tenant_id: str
    last_login: datetime
    total_queries: int
    queries_30d: int
    avg_session_duration_min: float
    
@dataclass
class TenantUsage:
    """Tenant usage summary"""
    tenant_id: str
    tenant_name: str
    user_count: int
    active_users_30d: int
    queries_30d: int
    storage_used_gb: float
    api_calls_30d: int
    billing_amount: float

@dataclass
class SystemAlert:
    """System alert definition"""
    alert_id: str
    severity: str  # info, warning, error, critical
    title: str
    description: str
    component: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
class EnterpriseAdminDashboard:
    """Enterprise admin dashboard and management interface"""
    
    def __init__(self, sso_manager: SSOManager, tenant_manager: TenantManager,
                 rbac_manager: RBACManager, gdpr_manager: GDPRComplianceManager,
                 soc2_manager: SOC2ComplianceManager):
        self.sso_manager = sso_manager
        self.tenant_manager = tenant_manager
        self.rbac_manager = rbac_manager
        self.gdpr_manager = gdpr_manager
        self.soc2_manager = soc2_manager
        self.system_alerts: Dict[str, SystemAlert] = {}
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Initialize system monitoring and alerts"""
        # This would integrate with actual monitoring systems
        pass
    
    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get comprehensive dashboard overview"""
        try:
            # Get metrics from various systems
            user_metrics = await self._get_user_metrics()
            tenant_metrics = await self._get_tenant_metrics()
            system_metrics = await self._get_system_metrics()
            security_metrics = await self._get_security_metrics()
            compliance_metrics = await self._get_compliance_metrics()
            
            return {
                "overview": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "healthy",
                    "version": "1.0.0"
                },
                "users": user_metrics,
                "tenants": tenant_metrics,
                "system": system_metrics,
                "security": security_metrics,
                "compliance": compliance_metrics,
                "alerts": await self._get_active_alerts()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard overview: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to load dashboard")
    
    async def _get_user_metrics(self) -> Dict[str, Any]:
        """Get user-related metrics"""
        # In production, this would query actual user database
        return {
            "total_users": 150,
            "active_users_30d": 125,
            "new_users_30d": 25,
            "user_growth_rate": 20.0,
            "avg_sessions_per_user": 8.5,
            "top_users_by_activity": [
                {"user_id": "user1", "queries": 450},
                {"user_id": "user2", "queries": 380},
                {"user_id": "user3", "queries": 320}
            ]
        }
    
    async def _get_tenant_metrics(self) -> Dict[str, Any]:
        """Get tenant-related metrics"""
        tenants = self.tenant_manager.list_tenants()
        
        total_tenants = len(tenants)
        active_tenants = len([t for t in tenants if t.status == "active"])
        
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "tenant_types": {
                "enterprise": len([t for t in tenants if t.tier == "enterprise"]),
                "professional": len([t for t in tenants if t.tier == "professional"]),
                "basic": len([t for t in tenants if t.tier == "basic"])
            },
            "total_revenue_monthly": sum(t.billing_info.get("monthly_cost", 0) for t in tenants),
            "avg_users_per_tenant": 12.5,
            "top_tenants_by_usage": [
                {"tenant_id": "tenant1", "monthly_queries": 15000},
                {"tenant_id": "tenant2", "monthly_queries": 12000},
                {"tenant_id": "tenant3", "monthly_queries": 8500}
            ]
        }
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            "uptime_percentage": 99.95,
            "avg_response_time_ms": 245,
            "requests_per_minute": 1250,
            "error_rate_percentage": 0.15,
            "cpu_usage_percentage": 68.5,
            "memory_usage_percentage": 74.2,
            "disk_usage_percentage": 45.8,
            "active_connections": 425,
            "cache_hit_rate": 0.89,
            "database_connections": 28
        }
    
    async def _get_security_metrics(self) -> Dict[str, Any]:
        """Get security-related metrics"""
        incident_metrics = self.soc2_manager.get_incident_metrics()
        
        return {
            "security_incidents_30d": incident_metrics["monthly_incident_count"],
            "critical_incidents_30d": incident_metrics["critical_incident_count"],
            "avg_resolution_time_hours": incident_metrics["avg_resolution_time_hours"],
            "failed_login_attempts_24h": 45,
            "suspicious_activities_24h": 8,
            "mfa_adoption_rate": 0.92,
            "password_policy_compliance": 0.98,
            "vulnerability_scan_score": 8.7,
            "last_security_assessment": "2024-01-15T10:30:00Z"
        }
    
    async def _get_compliance_metrics(self) -> Dict[str, Any]:
        """Get compliance-related metrics"""
        soc2_report = self.soc2_manager.generate_soc2_report()
        gdpr_records = self.gdpr_manager.generate_processing_record_report()
        
        return {
            "soc2_compliance_score": soc2_report["overall_compliance_score"],
            "effective_controls": soc2_report["control_testing"]["effective_controls"],
            "total_controls": soc2_report["control_testing"]["total_controls"],
            "gdpr_processing_activities": len(gdpr_records["processing_activities"]),
            "data_subject_requests_30d": len([
                req for req in self.gdpr_manager.data_subject_requests.values()
                if req.submitted_at > datetime.utcnow() - timedelta(days=30)
            ]),
            "consent_rate": 0.94,
            "audit_log_coverage": 0.99,
            "last_compliance_audit": "2024-01-10T14:00:00Z"
        }
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        active_alerts = [
            alert for alert in self.system_alerts.values()
            if alert.resolved_at is None
        ]
        
        return [
            {
                "alert_id": alert.alert_id,
                "severity": alert.severity,
                "title": alert.title,
                "component": alert.component,
                "created_at": alert.created_at.isoformat()
            }
            for alert in active_alerts
        ]
    
    async def get_user_management(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get user management data"""
        try:
            # In production, this would query actual user database with pagination
            users = [
                {
                    "user_id": f"user{i}",
                    "email": f"user{i}@company.com",
                    "tenant_id": f"tenant{(i-1)//10 + 1}",
                    "roles": ["user", "analyst"] if i % 3 == 0 else ["user"],
                    "last_login": (datetime.utcnow() - timedelta(days=i%30)).isoformat(),
                    "status": "active" if i % 10 != 0 else "inactive",
                    "mfa_enabled": i % 4 != 0,
                    "created_at": (datetime.utcnow() - timedelta(days=i*10)).isoformat()
                }
                for i in range((page-1)*limit + 1, page*limit + 1)
            ]
            
            return {
                "users": users,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": 500,  # Mock total
                    "pages": 10
                },
                "filters": {
                    "available_roles": list(self.rbac_manager.roles.keys()),
                    "available_tenants": [t.tenant_id for t in self.tenant_manager.list_tenants()]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user management data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to load user management")
    
    async def get_tenant_management(self) -> Dict[str, Any]:
        """Get tenant management data"""
        try:
            tenants = self.tenant_manager.list_tenants()
            
            tenant_data = []
            for tenant in tenants:
                usage = self.tenant_manager.get_usage_stats(tenant.tenant_id)
                
                tenant_data.append({
                    "tenant_id": tenant.tenant_id,
                    "name": tenant.name,
                    "tier": tenant.tier,
                    "status": tenant.status,
                    "created_at": tenant.created_at.isoformat(),
                    "user_count": usage.get("user_count", 0),
                    "storage_used_gb": usage.get("storage_used_gb", 0),
                    "api_calls_30d": usage.get("api_calls_30d", 0),
                    "monthly_cost": tenant.billing_info.get("monthly_cost", 0),
                    "limits": {
                        "max_users": tenant.limits.get("max_users", 0),
                        "max_storage_gb": tenant.limits.get("max_storage_gb", 0),
                        "max_api_calls_monthly": tenant.limits.get("max_api_calls_monthly", 0)
                    }
                })
            
            return {
                "tenants": tenant_data,
                "summary": {
                    "total_tenants": len(tenants),
                    "active_tenants": len([t for t in tenants if t.status == "active"]),
                    "total_monthly_revenue": sum(t.billing_info.get("monthly_cost", 0) for t in tenants)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get tenant management data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to load tenant management")
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        try:
            soc2_report = self.soc2_manager.generate_soc2_report()
            
            return {
                "incidents": {
                    "recent_incidents": [
                        {
                            "incident_id": inc.incident_id,
                            "title": inc.title,
                            "severity": inc.severity.value,
                            "status": inc.status,
                            "reported_at": inc.reported_at.isoformat()
                        }
                        for inc in list(self.soc2_manager.incidents.values())[-10:]
                    ],
                    "metrics": self.soc2_manager.get_incident_metrics()
                },
                "access_controls": {
                    "recent_reviews": [
                        {
                            "review_id": review.review_id,
                            "user_id": review.user_id,
                            "reviewer": review.reviewer,
                            "review_date": review.review_date.isoformat(),
                            "access_appropriate": review.access_appropriate
                        }
                        for review in list(self.soc2_manager.access_reviews.values())[-10:]
                    ],
                    "overdue_reviews": len([
                        r for r in self.soc2_manager.access_reviews.values()
                        if r.next_review_date and r.next_review_date < datetime.utcnow()
                    ])
                },
                "vulnerabilities": {
                    "recent_assessments": [
                        {
                            "assessment_id": va.assessment_id,
                            "type": va.assessment_type,
                            "risk_score": va.risk_score,
                            "findings_count": len(va.findings),
                            "assessment_date": va.assessment_date.isoformat()
                        }
                        for va in list(self.soc2_manager.vulnerability_assessments.values())[-5:]
                    ]
                },
                "compliance": {
                    "soc2_score": soc2_report["overall_compliance_score"],
                    "control_effectiveness": soc2_report["control_testing"]["effectiveness_rate"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get security dashboard: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to load security dashboard")
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        try:
            gdpr_report = self.gdpr_manager.generate_processing_record_report()
            soc2_report = self.soc2_manager.generate_soc2_report()
            
            return {
                "gdpr": {
                    "processing_activities": len(gdpr_report["processing_activities"]),
                    "data_subject_requests": {
                        "total": len(self.gdpr_manager.data_subject_requests),
                        "pending": len([
                            req for req in self.gdpr_manager.data_subject_requests.values()
                            if req.status == "pending"
                        ]),
                        "completed_30d": len([
                            req for req in self.gdpr_manager.data_subject_requests.values()
                            if req.completed_at and req.completed_at > datetime.utcnow() - timedelta(days=30)
                        ])
                    },
                    "consent_metrics": {
                        "total_consents": len(self.gdpr_manager.consent_records),
                        "active_consents": len([
                            c for c in self.gdpr_manager.consent_records.values()
                            if c.granted and c.withdrawn_at is None
                        ])
                    }
                },
                "soc2": {
                    "compliance_score": soc2_report["overall_compliance_score"],
                    "controls": soc2_report["control_testing"],
                    "incidents": soc2_report["security_incidents"]
                },
                "audit_logs": {
                    "total_entries_30d": 15420,  # Mock data
                    "coverage_percentage": 99.2,
                    "retention_compliance": True
                },
                "recommendations": soc2_report["recommendations"] + [
                    "Complete overdue GDPR data subject requests",
                    "Update privacy policy to reflect new processing activities",
                    "Conduct quarterly compliance training"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get compliance dashboard: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to load compliance dashboard")
    
    async def create_system_alert(self, severity: str, title: str, description: str,
                                component: str) -> SystemAlert:
        """Create a system alert"""
        alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        alert = SystemAlert(
            alert_id=alert_id,
            severity=severity,
            title=title,
            description=description,
            component=component,
            created_at=datetime.utcnow()
        )
        
        self.system_alerts[alert_id] = alert
        logger.info(f"System alert created: {title} ({severity})")
        return alert
    
    async def resolve_system_alert(self, alert_id: str) -> bool:
        """Resolve a system alert"""
        if alert_id in self.system_alerts:
            self.system_alerts[alert_id].resolved_at = datetime.utcnow()
            logger.info(f"System alert resolved: {alert_id}")
            return True
        return False
    
    async def bulk_user_action(self, action: str, user_ids: List[str],
                             parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform bulk actions on users"""
        if not parameters:
            parameters = {}
        
        success_count = 0
        failed_count = 0
        results = []
        
        for user_id in user_ids:
            try:
                if action == "deactivate":
                    # Would integrate with actual user management system
                    success_count += 1
                    results.append({"user_id": user_id, "status": "deactivated"})
                    
                elif action == "reset_password":
                    # Would integrate with actual auth system
                    success_count += 1
                    results.append({"user_id": user_id, "status": "password_reset_sent"})
                    
                elif action == "assign_role":
                    role = parameters.get("role")
                    if role and role in self.rbac_manager.roles:
                        # Would integrate with RBAC system
                        success_count += 1
                        results.append({"user_id": user_id, "status": f"role_{role}_assigned"})
                    else:
                        failed_count += 1
                        results.append({"user_id": user_id, "error": "Invalid role"})
                        
                else:
                    failed_count += 1
                    results.append({"user_id": user_id, "error": "Unknown action"})
                    
            except Exception as e:
                failed_count += 1
                results.append({"user_id": user_id, "error": str(e)})
        
        return {
            "action": action,
            "total_users": len(user_ids),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }

# FastAPI endpoints for admin dashboard
class AdminDashboardEndpoints:
    """Admin dashboard API endpoints"""
    
    def __init__(self, app, admin_dashboard: EnterpriseAdminDashboard):
        self.app = app
        self.admin_dashboard = admin_dashboard
        self._register_endpoints()
    
    def _register_endpoints(self):
        """Register admin dashboard endpoints with FastAPI"""
        
        @self.app.get("/admin/dashboard")
        async def get_dashboard_overview(request):
            """Get comprehensive dashboard overview"""
            # Verify admin permissions
            user_roles = request.state.user.get("roles", [])
            if "admin" not in user_roles and "super_admin" not in user_roles:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return await self.admin_dashboard.get_dashboard_overview()
        
        @self.app.get("/admin/users")
        async def get_user_management(page: int = 1, limit: int = 50, request=None):
            """Get user management interface"""
            user_roles = request.state.user.get("roles", [])
            if "admin" not in user_roles:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return await self.admin_dashboard.get_user_management(page, limit)
        
        @self.app.get("/admin/tenants")
        async def get_tenant_management(request):
            """Get tenant management interface"""
            user_roles = request.state.user.get("roles", [])
            if "admin" not in user_roles:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return await self.admin_dashboard.get_tenant_management()
        
        @self.app.get("/admin/security")
        async def get_security_dashboard(request):
            """Get security dashboard"""
            user_roles = request.state.user.get("roles", [])
            if "admin" not in user_roles and "security_admin" not in user_roles:
                raise HTTPException(status_code=403, detail="Security admin access required")
            
            return await self.admin_dashboard.get_security_dashboard()
        
        @self.app.get("/admin/compliance")
        async def get_compliance_dashboard(request):
            """Get compliance dashboard"""
            user_roles = request.state.user.get("roles", [])
            if "admin" not in user_roles and "compliance_admin" not in user_roles:
                raise HTTPException(status_code=403, detail="Compliance admin access required")
            
            return await self.admin_dashboard.get_compliance_dashboard()
        
        @self.app.post("/admin/alerts")
        async def create_alert(alert_data: Dict[str, Any], request):
            """Create system alert"""
            user_roles = request.state.user.get("roles", [])
            if "admin" not in user_roles:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            severity = alert_data.get("severity", "info")
            title = alert_data.get("title", "")
            description = alert_data.get("description", "")
            component = alert_data.get("component", "system")
            
            alert = await self.admin_dashboard.create_system_alert(
                severity, title, description, component
            )
            
            return {
                "alert_id": alert.alert_id,
                "created_at": alert.created_at.isoformat()
            }
        
        @self.app.post("/admin/users/bulk-action")
        async def bulk_user_action(action_data: Dict[str, Any], request):
            """Perform bulk actions on users"""
            user_roles = request.state.user.get("roles", [])
            if "admin" not in user_roles:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            action = action_data.get("action")
            user_ids = action_data.get("user_ids", [])
            parameters = action_data.get("parameters", {})
            
            if not action or not user_ids:
                raise HTTPException(status_code=400, detail="Action and user_ids required")
            
            return await self.admin_dashboard.bulk_user_action(action, user_ids, parameters)