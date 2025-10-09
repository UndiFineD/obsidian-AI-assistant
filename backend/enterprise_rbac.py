# Enterprise Role-Based Access Control (RBAC)
# Provides granular permission management for enterprise deployments

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum

import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

class Permission(Enum):
    # Configuration permissions
    READ_CONFIG = "read_config"
    WRITE_CONFIG = "write_config"
    RELOAD_CONFIG = "reload_config"
    
    # AI operations
    ASK_QUESTIONS = "ask_questions"
    VOICE_PROCESSING = "voice_processing"
    CUSTOM_MODELS = "custom_models"
    
    # Document management
    READ_DOCUMENTS = "read_documents"
    WRITE_DOCUMENTS = "write_documents"
    DELETE_DOCUMENTS = "delete_documents"
    MANAGE_VAULT = "manage_vault"
    REINDEX_VAULT = "reindex_vault"
    
    # User management
    VIEW_USERS = "view_users"
    MANAGE_USERS = "manage_users"
    ASSIGN_ROLES = "assign_roles"
    
    # Analytics and monitoring
    VIEW_ANALYTICS = "view_analytics"
    VIEW_LOGS = "view_logs"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    EXPORT_DATA = "export_data"
    
    # System administration
    SYSTEM_ADMIN = "system_admin"
    TENANT_ADMIN = "tenant_admin"
    BILLING_ACCESS = "billing_access"

class UserRole(Enum):
    # Standard user roles
    READONLY = "readonly"           # Read-only access to documents and basic AI
    USER = "user"                  # Standard user with document management
    POWER_USER = "power_user"      # Advanced AI features and analytics
    
    # Administrative roles
    TEAM_ADMIN = "team_admin"      # Manage team users and settings
    TENANT_ADMIN = "tenant_admin"  # Full tenant management
    SYSTEM_ADMIN = "system_admin"  # Cross-tenant system administration

@dataclass
class Role:
    """Role definition with permissions"""
    name: UserRole
    display_name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[UserRole] = None

@dataclass
class UserPermissions:
    """User's effective permissions"""
    user_id: str
    tenant_id: str
    roles: List[UserRole]
    effective_permissions: Set[Permission]
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None

class RBACManager:
    """Role-Based Access Control manager"""
    
    def __init__(self):
        self.roles = self._initialize_default_roles()
        self.user_permissions: Dict[str, UserPermissions] = {}
        self.custom_roles: Dict[str, Role] = {}
    
    def _initialize_default_roles(self) -> Dict[UserRole, Role]:
        """Initialize default role definitions"""
        return {
            UserRole.READONLY: Role(
                name=UserRole.READONLY,
                display_name="Read-Only User",
                description="Can read documents and use basic AI features",
                permissions={
                    Permission.READ_CONFIG,
                    Permission.ASK_QUESTIONS,
                    Permission.READ_DOCUMENTS,
                    Permission.VIEW_ANALYTICS
                }
            ),
            
            UserRole.USER: Role(
                name=UserRole.USER,
                display_name="Standard User",
                description="Can manage documents and use AI features",
                permissions={
                    Permission.READ_CONFIG,
                    Permission.ASK_QUESTIONS,
                    Permission.VOICE_PROCESSING,
                    Permission.READ_DOCUMENTS,
                    Permission.WRITE_DOCUMENTS,
                    Permission.MANAGE_VAULT,
                    Permission.VIEW_ANALYTICS
                }
            ),
            
            UserRole.POWER_USER: Role(
                name=UserRole.POWER_USER,
                display_name="Power User",
                description="Advanced AI features and analytics access",
                permissions={
                    Permission.READ_CONFIG,
                    Permission.ASK_QUESTIONS,
                    Permission.VOICE_PROCESSING,
                    Permission.CUSTOM_MODELS,
                    Permission.READ_DOCUMENTS,
                    Permission.WRITE_DOCUMENTS,
                    Permission.DELETE_DOCUMENTS,
                    Permission.MANAGE_VAULT,
                    Permission.REINDEX_VAULT,
                    Permission.VIEW_ANALYTICS,
                    Permission.VIEW_LOGS,
                    Permission.EXPORT_DATA
                }
            ),
            
            UserRole.TEAM_ADMIN: Role(
                name=UserRole.TEAM_ADMIN,
                display_name="Team Administrator",
                description="Can manage team users and configuration",
                permissions={
                    Permission.READ_CONFIG,
                    Permission.WRITE_CONFIG,
                    Permission.RELOAD_CONFIG,
                    Permission.ASK_QUESTIONS,
                    Permission.VOICE_PROCESSING,
                    Permission.CUSTOM_MODELS,
                    Permission.READ_DOCUMENTS,
                    Permission.WRITE_DOCUMENTS,
                    Permission.DELETE_DOCUMENTS,
                    Permission.MANAGE_VAULT,
                    Permission.REINDEX_VAULT,
                    Permission.VIEW_USERS,
                    Permission.MANAGE_USERS,
                    Permission.VIEW_ANALYTICS,
                    Permission.VIEW_LOGS,
                    Permission.EXPORT_DATA
                }
            ),
            
            UserRole.TENANT_ADMIN: Role(
                name=UserRole.TENANT_ADMIN,
                display_name="Tenant Administrator",
                description="Full tenant management capabilities",
                permissions={
                    Permission.READ_CONFIG,
                    Permission.WRITE_CONFIG,
                    Permission.RELOAD_CONFIG,
                    Permission.ASK_QUESTIONS,
                    Permission.VOICE_PROCESSING,
                    Permission.CUSTOM_MODELS,
                    Permission.READ_DOCUMENTS,
                    Permission.WRITE_DOCUMENTS,
                    Permission.DELETE_DOCUMENTS,
                    Permission.MANAGE_VAULT,
                    Permission.REINDEX_VAULT,
                    Permission.VIEW_USERS,
                    Permission.MANAGE_USERS,
                    Permission.ASSIGN_ROLES,
                    Permission.VIEW_ANALYTICS,
                    Permission.VIEW_LOGS,
                    Permission.VIEW_AUDIT_LOGS,
                    Permission.EXPORT_DATA,
                    Permission.TENANT_ADMIN,
                    Permission.BILLING_ACCESS
                }
            ),
            
            UserRole.SYSTEM_ADMIN: Role(
                name=UserRole.SYSTEM_ADMIN,
                display_name="System Administrator",
                description="System-wide administration privileges",
                permissions=set(Permission)  # All permissions
            )
        }
    
    def assign_role(self, user_id: str, tenant_id: str, role: UserRole, 
        granted_by: str, expires_at: Optional[datetime] = None) -> bool:
        """Assign a role to a user"""
        key = f"{user_id}:{tenant_id}"
        
        # Get existing permissions or create new
        if key in self.user_permissions:
            user_perms = self.user_permissions[key]
            if role not in user_perms.roles:
                user_perms.roles.append(role)
        else:
            user_perms = UserPermissions(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=[role],
                effective_permissions=set(),
                granted_by=granted_by,
                granted_at=datetime.utcnow(),
                expires_at=expires_at
            )
            self.user_permissions[key] = user_perms
        
        # Recalculate effective permissions
        self._calculate_effective_permissions(user_perms)
        
        logger.info(f"Assigned role {role.value} to user {user_id} in tenant {tenant_id}")
        return True
    
    def remove_role(self, user_id: str, tenant_id: str, role: UserRole) -> bool:
        """Remove a role from a user"""
        key = f"{user_id}:{tenant_id}"
        
        if key not in self.user_permissions:
            return False
        
        user_perms = self.user_permissions[key]
        if role in user_perms.roles:
            user_perms.roles.remove(role)
            self._calculate_effective_permissions(user_perms)
            logger.info(f"Removed role {role.value} from user {user_id} in tenant {tenant_id}")
            return True
        
        return False
    
    def has_permission(self, user_id: str, tenant_id: str, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        key = f"{user_id}:{tenant_id}"
        user_perms = self.user_permissions.get(key)
        
        if not user_perms:
            return False
        
        # Check if permissions have expired
        if user_perms.expires_at and datetime.utcnow() > user_perms.expires_at:
            logger.warning(f"Permissions expired for user {user_id}")
            return False
        
        return permission in user_perms.effective_permissions
    
    def get_user_permissions(self, user_id: str, tenant_id: str) -> Optional[UserPermissions]:
        """Get user's permission details"""
        key = f"{user_id}:{tenant_id}"
        return self.user_permissions.get(key)
    
    def is_valid_role(self, role_name: str) -> bool:
        """Check if a role name string is a valid UserRole."""
        try:
            UserRole(role_name)
            return True
        except ValueError:
            return False
    def _calculate_effective_permissions(self, user_perms: UserPermissions):
        """Calculate effective permissions from all assigned roles"""
        effective_perms = set()
        
        for role in user_perms.roles:
            if role in self.roles:
                role_perms = self.roles[role].permissions
                effective_perms.update(role_perms)
                
                # Handle role inheritance
                inherited_role = self.roles[role].inherits_from
                if inherited_role and inherited_role in self.roles:
                    inherited_perms = self.roles[inherited_role].permissions
                    effective_perms.update(inherited_perms)
        
        user_perms.effective_permissions = effective_perms
    
    def create_custom_role(self, role_name: str, display_name: str, 
        description: str, permissions: List[Permission]) -> bool:
        """Create a custom role"""
        if role_name in self.custom_roles:
            return False
        
        custom_role = Role(
            name=role_name,
            display_name=display_name,
            description=description,
            permissions=set(permissions)
        )
        
        self.custom_roles[role_name] = custom_role
        logger.info(f"Created custom role: {role_name}")
        return True
    
    def list_available_roles(self) -> List[Dict[str, Any]]:
        """List all available roles"""
        roles_list = []
        
        # Standard roles
        for role in self.roles.values():
            roles_list.append({
                "name": role.name.value,
                "display_name": role.display_name,
                "description": role.description,
                "permission_count": len(role.permissions),
                "type": "standard"
            })
        
        # Custom roles
        for role in self.custom_roles.values():
            roles_list.append({
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "permission_count": len(role.permissions),
                "type": "custom"
            })
        
        return roles_list

def require_permission(permission: Permission):
    """Decorator to enforce permission requirements"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object (assumes FastAPI)
            request = None
            for arg in args:
                if hasattr(arg, 'state'):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'user'):
                raise PermissionError("Authentication required")
            
            user = request.state.user
            user_id = user.get('user_id')
            tenant_id = user.get('tenant_id')
            
            if not user_id or not tenant_id:
                raise PermissionError("User or tenant identification missing")
            
            # Get RBAC manager from app state (would be injected in real implementation)
            rbac_manager = getattr(request.app.state, 'rbac_manager', None)
            if not rbac_manager:
                raise PermissionError("RBAC system not available")
            
            if not rbac_manager.has_permission(user_id, tenant_id, permission):
                raise PermissionError(f"Permission {permission.value} required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class AuditLogger:
    """Audit logging for RBAC operations"""
    
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
    
    def log_permission_check(self, user_id: str, tenant_id: str, 
        permission: Permission, granted: bool, resource: str = ""):
        """Log permission check events"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "permission_check",
            "user_id": user_id,
            "tenant_id": tenant_id,
            "permission": permission.value,
            "granted": granted,
            "resource": resource
        }
        
        self.audit_log.append(audit_entry)
        logger.info(f"Permission check: {user_id} -> {permission.value} = {granted}")
    
    def log_role_assignment(self, user_id: str, tenant_id: str, 
        role: UserRole, granted_by: str, action: str):
        """Log role assignment/removal events"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "role_assignment",
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": role.value,
            "granted_by": granted_by,
            "action": action  # "assigned" or "removed"
        }
        
        self.audit_log.append(audit_entry)
        logger.info(f"Role {action}: {user_id} -> {role.value} by {granted_by}")
    
    def get_audit_log(self, user_id: Optional[str] = None, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve audit log entries"""
        filtered_log = self.audit_log
        
        if user_id:
            filtered_log = [entry for entry in filtered_log if entry.get("user_id") == user_id]
        
        if start_date:
            filtered_log = [entry for entry in filtered_log 
                if datetime.fromisoformat(entry["timestamp"]) >= start_date]
        
        if end_date:
            filtered_log = [entry for entry in filtered_log 
                if datetime.fromisoformat(entry["timestamp"]) <= end_date]
        
        return filtered_log

# FastAPI endpoints for RBAC management
class RBACEndpoints:
    """RBAC management API endpoints"""
    
    def __init__(self, app, rbac_manager: RBACManager, audit_logger: AuditLogger):
        self.app = app
        self.rbac_manager = rbac_manager
        self.audit_logger = audit_logger
        self._register_endpoints()
    
    def _register_endpoints(self):
        """Register RBAC endpoints with FastAPI"""
        
        @self.app.get("/admin/roles")
        @require_permission(Permission.VIEW_USERS)
        async def list_roles():
            """List all available roles"""
            return {"roles": self.rbac_manager.list_available_roles()}
        
        @self.app.post("/admin/users/{user_id}/roles")
        @require_permission(Permission.ASSIGN_ROLES)
        async def assign_user_role(user_id: str, request_data: Dict[str, Any], request):
            """Assign role to user"""
            role_name = request_data.get("role")
            tenant_id = request_data.get("tenant_id", request.state.user.get("tenant_id"))
            
            try:
                role = UserRole(role_name)
                granted_by = request.state.user.get("user_id")
                
                success = self.rbac_manager.assign_role(user_id, tenant_id, role, granted_by)
                
                if success:
                    self.audit_logger.log_role_assignment(user_id, tenant_id, role, granted_by, "assigned")
                    return {"message": f"Role {role_name} assigned to user {user_id}"}
                else:
                    return {"error": "Failed to assign role", "status_code": 400}
                    
            except ValueError:
                return {"error": f"Invalid role: {role_name}", "status_code": 400}
        
        @self.app.get("/admin/users/{user_id}/permissions")
        @require_permission(Permission.VIEW_USERS)
        async def get_user_permissions(user_id: str, request):
            """Get user's permissions"""
            tenant_id = request.state.user.get("tenant_id")
            permissions = self.rbac_manager.get_user_permissions(user_id, tenant_id)
            
            if permissions:
                return {
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "roles": [role.value for role in permissions.roles],
                    "permissions": [perm.value for perm in permissions.effective_permissions],
                    "granted_at": permissions.granted_at.isoformat(),
                    "expires_at": permissions.expires_at.isoformat() if permissions.expires_at else None
                }
            else:
                return {"error": "User permissions not found", "status_code": 404}
        
        @self.app.get("/admin/audit-log")
        @require_permission(Permission.VIEW_AUDIT_LOGS)
        async def get_audit_log(start_date: Optional[str] = None, end_date: Optional[str] = None):
            """Get RBAC audit log"""
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            
            log_entries = self.audit_logger.get_audit_log(start_date=start_dt, end_date=end_dt)
            return {"audit_log": log_entries, "total_entries": len(log_entries)}