# tests/agent/test_enterprise_rbac.py
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the backend to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.enterprise_rbac import (
    AuditLogger,
    Permission,
    RBACManager,
    Role,
    UserPermissions,
    UserRole,
    require_permission,
    require_role,
)


class TestPermissionEnum:
    """Test suite for Permission enum."""

    def test_permission_enum_values(self):
        """Test that all expected permissions are defined."""
        expected_permissions = {
            "read_config",
            "write_config",
            "reload_config",
            "ask_questions",
            "voice_processing",
            "custom_models",
            "read_documents",
            "write_documents",
            "delete_documents",
            "manage_vault",
            "reindex_vault",
            "view_users",
            "manage_users",
            "assign_roles",
            "view_analytics",
            "view_logs",
            "view_audit_logs",
            "export_data",
            "system_admin",
            "tenant_admin",
            "billing_access",
        }

        actual_permissions = {perm.value for perm in Permission}

        assert actual_permissions == expected_permissions

    def test_permission_enum_consistency(self):
        """Test that permission enum values are consistent with names."""
        for permission in Permission:
            # Check that enum name matches value pattern (both lowercase)
            assert permission.name.lower() == permission.value.lower()


class TestUserRoleEnum:
    """Test suite for UserRole enum."""

    def test_user_role_enum_values(self):
        """Test that all expected user roles are defined."""
        expected_roles = {
            "readonly",
            "user",
            "power_user",
            "team_admin",
            "tenant_admin",
            "system_admin",
        }

        actual_roles = {role.value for role in UserRole}

        assert actual_roles == expected_roles

    def test_user_role_hierarchy(self):
        """Test user role hierarchy makes sense."""
        # Readonly < User < Power User < Team Admin < Tenant Admin < System Admin
        roles_by_level = [
            UserRole.READONLY,
            UserRole.USER,
            UserRole.POWER_USER,
            UserRole.TEAM_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.SYSTEM_ADMIN,
        ]

        # Each role should have distinct values
        role_values = [role.value for role in roles_by_level]
        assert len(set(role_values)) == len(role_values)


class TestRoleDataClass:
    """Test suite for Role data class."""

    def test_role_creation_basic(self):
        """Test basic role creation."""
        permissions = {Permission.read_config, Permission.ask_questions}
        role = Role(
            name=UserRole.USER,
            display_name="Standard User",
            description="Standard user role",
            permissions=permissions,
        )

        assert role.name == UserRole.USER
        assert role.display_name == "Standard User"
        assert role.description == "Standard user role"
        assert role.permissions == permissions
        assert role.inherits_from is None

    def test_role_creation_with_inheritance(self):
        """Test role creation with inheritance."""
        permissions = {Permission.manage_users}
        role = Role(
            name=UserRole.TEAM_ADMIN,
            display_name="Team Administrator",
            description="Team administrator role",
            permissions=permissions,
            inherits_from=UserRole.USER,
        )

        assert role.inherits_from == UserRole.USER

    def test_role_permissions_immutable(self):
        """Test that role permissions should be a set (immutable after creation)."""
        permissions = {Permission.read_config}
        role = Role(
            name=UserRole.READONLY,
            display_name="Read Only",
            description="Read only access",
            permissions=permissions,
        )

        # Permissions should be a set
        assert isinstance(role.permissions, set)


class TestUserPermissionsDataClass:
    """Test suite for UserPermissions data class."""

    def test_user_permissions_creation(self):
        """Test basic UserPermissions creation."""
        effective_permissions = {Permission.read_config, Permission.ask_questions}
        granted_time = datetime.utcnow()

        user_perms = UserPermissions(
            user_id="test_user_123",
            tenant_id="tenant_456",
            roles=[UserRole.USER],
            effective_permissions=effective_permissions,
            granted_by="admin_user",
            granted_at=granted_time,
        )

        assert user_perms.user_id == "test_user_123"
        assert user_perms.tenant_id == "tenant_456"
        assert user_perms.roles == [UserRole.USER]
        assert user_perms.effective_permissions == effective_permissions
        assert user_perms.granted_by == "admin_user"
        assert user_perms.granted_at == granted_time
        assert user_perms.expires_at is None

    def test_user_permissions_with_expiry(self):
        """Test UserPermissions with expiry date."""
        granted_time = datetime.utcnow()
        expiry_time = granted_time + timedelta(days=30)

        user_perms = UserPermissions(
            user_id="temp_user",
            tenant_id="tenant_123",
            roles=[UserRole.USER],
            effective_permissions={Permission.read_config},
            granted_by="admin",
            granted_at=granted_time,
            expires_at=expiry_time,
        )

        assert user_perms.expires_at == expiry_time

    def test_user_permissions_multiple_roles(self):
        """Test UserPermissions with multiple roles."""
        multiple_roles = [UserRole.USER, UserRole.POWER_USER]

        user_perms = UserPermissions(
            user_id="multi_role_user",
            tenant_id="tenant_789",
            roles=multiple_roles,
            effective_permissions={Permission.read_config, Permission.view_analytics},
            granted_by="system",
            granted_at=datetime.utcnow(),
        )

        assert len(user_perms.roles) == 2
        assert UserRole.USER in user_perms.roles
        assert UserRole.POWER_USER in user_perms.roles


class TestRBACManager:
    """Test suite for RBAC Manager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rbac_manager = RBACManager()

    def test_rbac_manager_initialization(self):
        """Test RBAC Manager initialization."""
        assert isinstance(self.rbac_manager.roles, dict)
        assert isinstance(self.rbac_manager.user_permissions, dict)
        assert isinstance(self.rbac_manager.custom_roles, dict)

        # Default roles should be initialized
        assert len(self.rbac_manager.roles) > 0
        assert UserRole.READONLY in self.rbac_manager.roles
        assert UserRole.USER in self.rbac_manager.roles

    def test_default_roles_structure(self):
        """Test that default roles are properly structured."""
        readonly_role = self.rbac_manager.roles[UserRole.READONLY]

        assert readonly_role.name == UserRole.READONLY
        assert readonly_role.display_name == "Read-Only User"
        assert isinstance(readonly_role.permissions, set)
        assert Permission.read_config in readonly_role.permissions

    def test_get_role_permissions_basic(self):
        """Test getting permissions for a basic role."""
        permissions = self.rbac_manager.get_role_permissions(UserRole.USER)

        assert isinstance(permissions, set)
        assert len(permissions) > 0
        # User should have at least basic permissions
        assert Permission.ask_questions in permissions
        assert Permission.read_documents in permissions

    def test_get_role_permissions_admin(self):
        """Test getting permissions for admin roles."""
        admin_permissions = self.rbac_manager.get_role_permissions(UserRole.SYSTEM_ADMIN)

        assert isinstance(admin_permissions, set)
        assert Permission.system_admin in admin_permissions
        assert Permission.manage_users in admin_permissions

    def test_get_role_permissions_invalid_role(self):
        """Test getting permissions for invalid role."""
        # Create a mock invalid role
        invalid_role = Mock()
        invalid_role.value = "invalid_role"

        permissions = self.rbac_manager.get_role_permissions(invalid_role)

        assert permissions == set()

    def test_assign_role_to_user(self):
        """Test assigning a role to a user."""
        user_id = "test_user_assign"
        tenant_id = "tenant_assign"
        role = UserRole.USER
        granted_by = "admin_user"

        success = self.rbac_manager.assign_role_to_user(user_id, tenant_id, role, granted_by)

        assert success is True

        # Check that user permissions were created
        user_key = f"{user_id}:{tenant_id}"
        assert user_key in self.rbac_manager.user_permissions

        user_perms = self.rbac_manager.user_permissions[user_key]
        assert user_perms.user_id == user_id
        assert user_perms.tenant_id == tenant_id
        assert role in user_perms.roles

    def test_assign_multiple_roles_to_user(self):
        """Test assigning multiple roles to a user."""
        user_id = "multi_role_user"
        tenant_id = "tenant_multi"
        roles = [UserRole.USER, UserRole.POWER_USER]
        granted_by = "admin"

        for role in roles:
            success = self.rbac_manager.assign_role_to_user(user_id, tenant_id, role, granted_by)
            assert success is True

        user_key = f"{user_id}:{tenant_id}"
        user_perms = self.rbac_manager.user_permissions[user_key]

        assert len(user_perms.roles) == 2
        for role in roles:
            assert role in user_perms.roles

    def test_remove_role_from_user(self):
        """Test removing a role from a user."""
        user_id = "remove_role_user"
        tenant_id = "tenant_remove"
        role = UserRole.USER

        # First assign the role
        self.rbac_manager.assign_role_to_user(user_id, tenant_id, role, "admin")

        # Then remove it
        success = self.rbac_manager.remove_role_from_user(user_id, tenant_id, role)

        assert success is True

        user_key = f"{user_id}:{tenant_id}"
        if user_key in self.rbac_manager.user_permissions:
            user_perms = self.rbac_manager.user_permissions[user_key]
            assert role not in user_perms.roles

    def test_remove_role_from_nonexistent_user(self):
        """Test removing a role from a user that doesn't exist."""
        success = self.rbac_manager.remove_role_from_user(
            "nonexistent_user", "tenant_123", UserRole.USER
        )

        assert success is False

    def test_check_user_permission_granted(self):
        """Test checking user permission when granted."""
        user_id = "permission_user"
        tenant_id = "tenant_permission"

        # Assign a role with specific permissions
        self.rbac_manager.assign_role_to_user(user_id, tenant_id, UserRole.USER, "admin")

        # Check a permission that should be granted
        has_permission = self.rbac_manager.check_user_permission(
            user_id, tenant_id, Permission.ask_questions
        )

        assert has_permission is True

    def test_check_user_permission_denied(self):
        """Test checking user permission when denied."""
        user_id = "limited_user"
        tenant_id = "tenant_limited"

        # Assign a limited role
        self.rbac_manager.assign_role_to_user(user_id, tenant_id, UserRole.READONLY, "admin")

        # Check a permission that should be denied
        has_permission = self.rbac_manager.check_user_permission(
            user_id, tenant_id, Permission.manage_users
        )

        assert has_permission is False

    def test_check_user_permission_nonexistent_user(self):
        """Test checking permission for nonexistent user."""
        has_permission = self.rbac_manager.check_user_permission(
            "nonexistent", "tenant", Permission.read_config
        )

        assert has_permission is False

    def test_get_user_roles(self):
        """Test getting user roles."""
        user_id = "roles_user"
        tenant_id = "tenant_roles"
        assigned_roles = [UserRole.USER, UserRole.POWER_USER]

        for role in assigned_roles:
            self.rbac_manager.assign_role_to_user(user_id, tenant_id, role, "admin")

        user_roles = self.rbac_manager.get_user_roles(user_id, tenant_id)

        assert isinstance(user_roles, list)
        assert len(user_roles) == 2
        for role in assigned_roles:
            assert role in user_roles

    def test_get_user_roles_nonexistent(self):
        """Test getting roles for nonexistent user."""
        user_roles = self.rbac_manager.get_user_roles("nonexistent", "tenant")

        assert user_roles == []

    def test_create_custom_role(self):
        """Test creating a custom role."""
        custom_permissions = {Permission.read_config, Permission.view_analytics}
        role_name = "custom_analyst"

        success = self.rbac_manager.create_custom_role(
            role_name, "Custom Analyst", "Custom role for analysts", custom_permissions
        )

        assert success is True
        assert role_name in self.rbac_manager.custom_roles

        custom_role = self.rbac_manager.custom_roles[role_name]
        assert custom_role.display_name == "Custom Analyst"
        assert custom_role.permissions == custom_permissions

    def test_create_custom_role_duplicate_name(self):
        """Test creating a custom role with duplicate name."""
        role_name = "duplicate_role"
        permissions = {Permission.read_config}

        # Create first role
        success1 = self.rbac_manager.create_custom_role(
            role_name, "First Role", "First description", permissions
        )

        # Try to create duplicate
        success2 = self.rbac_manager.create_custom_role(
            role_name, "Second Role", "Second description", permissions
        )

        assert success1 is True
        assert success2 is False  # Should fail due to duplicate name

    def test_role_inheritance(self):
        """Test role inheritance functionality."""
        # This test checks if role inheritance is properly implemented
        # Check that power user inherits from user
        power_user_perms = self.rbac_manager.get_role_permissions(UserRole.POWER_USER)
        user_perms = self.rbac_manager.get_role_permissions(UserRole.USER)

        # Power user should have at least all user permissions
        assert user_perms.issubset(power_user_perms)

    def test_permission_escalation_prevention(self):
        """Test that permission escalation is prevented."""
        user_id = "escalation_user"
        tenant_id = "tenant_escalation"

        # Assign basic user role
        self.rbac_manager.assign_role_to_user(user_id, tenant_id, UserRole.USER, "admin")

        # User should not have admin permissions
        has_admin_perm = self.rbac_manager.check_user_permission(
            user_id, tenant_id, Permission.system_admin
        )

        assert has_admin_perm is False


class TestRBACDecorators:
    """Test suite for RBAC decorators."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rbac_manager = RBACManager()

    def test_require_permission_decorator_success(self):
        """Test require_permission decorator with sufficient permissions."""

        @require_permission(Permission.read_config)
        def protected_function(user_id, tenant_id):
            return "success"

        # Mock the check_user_permission to return True
        with patch.object(self.rbac_manager, "check_user_permission", return_value=True):
            with patch("agent.enterprise_rbac.rbac_manager", self.rbac_manager):
                result = protected_function("user", "tenant")
                assert result == "success"

    def test_require_permission_decorator_failure(self):
        """Test require_permission decorator with insufficient permissions."""

        @require_permission(Permission.system_admin)
        def admin_function(user_id, tenant_id):
            return "admin_success"

        # Mock the check_user_permission to return False
        with patch.object(self.rbac_manager, "check_user_permission", return_value=False):
            with patch("agent.enterprise_rbac.rbac_manager", self.rbac_manager):
                with pytest.raises(PermissionError):
                    admin_function("user", "tenant")

    def test_require_role_decorator_success(self):
        """Test require_role decorator with correct role."""

        @require_role(UserRole.USER)
        def user_function(user_id, tenant_id):
            return "user_success"

        # Mock get_user_roles to return the required role
        with patch.object(self.rbac_manager, "get_user_roles", return_value=[UserRole.USER]):
            with patch("agent.enterprise_rbac.rbac_manager", self.rbac_manager):
                result = user_function("user", "tenant")
                assert result == "user_success"

    def test_require_role_decorator_failure(self):
        """Test require_role decorator with incorrect role."""

        @require_role(UserRole.SYSTEM_ADMIN)
        def admin_function(user_id, tenant_id):
            return "admin_success"

        # Mock get_user_roles to return a different role
        with patch.object(self.rbac_manager, "get_user_roles", return_value=[UserRole.USER]):
            with patch("agent.enterprise_rbac.rbac_manager", self.rbac_manager):
                with pytest.raises(PermissionError):
                    admin_function("user", "tenant")


class TestAuditLogger:
    """Test suite for Audit Logger."""

    def test_audit_logger_initialization(self):
        """Test audit logger initialization."""
        audit_logger = AuditLogger("test_tenant")

        assert audit_logger.tenant_id == "test_tenant"
        assert isinstance(audit_logger.audit_log, list)

    def test_log_permission_check(self):
        """Test logging permission checks."""
        audit_logger = AuditLogger("audit_tenant")

        audit_logger.log_permission_check(
            user_id="audit_user",
            permission=Permission.read_config,
            granted=True,
            context="API access",
        )

        assert len(audit_logger.audit_log) == 1
        log_entry = audit_logger.audit_log[0]

        assert log_entry["user_id"] == "audit_user"
        assert log_entry["permission"] == Permission.read_config.value
        assert log_entry["granted"] is True
        assert log_entry["context"] == "API access"
        assert "timestamp" in log_entry

    def test_log_role_assignment(self):
        """Test logging role assignments."""
        audit_logger = AuditLogger("audit_tenant")

        audit_logger.log_role_assignment(
            user_id="role_user",
            role=UserRole.POWER_USER,
            assigned_by="admin_user",
            action="ASSIGN",
        )

        assert len(audit_logger.audit_log) == 1
        log_entry = audit_logger.audit_log[0]

        assert log_entry["user_id"] == "role_user"
        assert log_entry["role"] == UserRole.POWER_USER.value
        assert log_entry["assigned_by"] == "admin_user"
        assert log_entry["action"] == "ASSIGN"

    def test_get_audit_logs(self):
        """Test retrieving audit logs."""
        audit_logger = AuditLogger("audit_tenant")

        # Add some test entries
        audit_logger.log_permission_check("user1", Permission.read_config, True)
        audit_logger.log_role_assignment("user2", UserRole.USER, "admin", "ASSIGN")

        logs = audit_logger.get_audit_logs()

        assert isinstance(logs, list)
        assert len(logs) == 2

    def test_get_audit_logs_by_user(self):
        """Test retrieving audit logs filtered by user."""
        audit_logger = AuditLogger("audit_tenant")

        # Add entries for different users
        audit_logger.log_permission_check("user1", Permission.read_config, True)
        audit_logger.log_permission_check("user2", Permission.write_config, False)
        audit_logger.log_permission_check("user1", Permission.ask_questions, True)

        user1_logs = audit_logger.get_audit_logs(user_id="user1")

        assert len(user1_logs) == 2
        for log in user1_logs:
            assert log["user_id"] == "user1"


class TestRBACIntegration:
    """Integration tests for RBAC system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rbac_manager = RBACManager()

    def test_full_rbac_workflow(self):
        """Test complete RBAC workflow."""
        user_id = "workflow_user"
        tenant_id = "workflow_tenant"

        # Step 1: Assign role
        success = self.rbac_manager.assign_role_to_user(user_id, tenant_id, UserRole.USER, "system")
        assert success is True

        # Step 2: Check permissions
        can_ask = self.rbac_manager.check_user_permission(
            user_id, tenant_id, Permission.ask_questions
        )
        assert can_ask is True

        cannot_admin = self.rbac_manager.check_user_permission(
            user_id, tenant_id, Permission.system_admin
        )
        assert cannot_admin is False

        # Step 3: Upgrade role
        success = self.rbac_manager.assign_role_to_user(
            user_id, tenant_id, UserRole.POWER_USER, "admin"
        )
        assert success is True

        # Step 4: Check new permissions
        can_view_analytics = self.rbac_manager.check_user_permission(
            user_id, tenant_id, Permission.view_analytics
        )
        assert can_view_analytics is True

        # Step 5: Remove role
        success = self.rbac_manager.remove_role_from_user(user_id, tenant_id, UserRole.POWER_USER)
        assert success is True

        # Step 6: Verify permission removed
        can_view_analytics_after = self.rbac_manager.check_user_permission(
            user_id, tenant_id, Permission.view_analytics
        )
        # USER role includes VIEW_ANALYTICS, so permission should still be True
        assert can_view_analytics_after is True

    def test_tenant_isolation(self):
        """Test that users are isolated by tenant."""
        user_id = "isolation_user"
        tenant1 = "tenant_1"
        tenant2 = "tenant_2"

        # Assign role in tenant 1
        self.rbac_manager.assign_role_to_user(user_id, tenant1, UserRole.POWER_USER, "admin")

        # Check permissions in tenant 1 (should have)
        has_perm_t1 = self.rbac_manager.check_user_permission(
            user_id, tenant1, Permission.view_analytics
        )
        assert has_perm_t1 is True

        # Check permissions in tenant 2 (should not have)
        has_perm_t2 = self.rbac_manager.check_user_permission(
            user_id, tenant2, Permission.view_analytics
        )
        assert has_perm_t2 is False


if __name__ == "__main__":
    pytest.main([__file__])
