# tests/agent/test_enterprise_tenant.py
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add the backend to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.enterprise_tenant import (
    TenantConfig,
    TenantEndpoints,
    TenantLimits,
    TenantManager,
    TenantTier,
    TenantUsage,
)


class TestTenantTierEnum:
    """Test suite for TenantTier enum."""

    def test_tenant_tier_values(self):
        """Test that all expected tenant tiers are defined."""
        expected_tiers = {"basic", "pro", "enterprise", "custom"}
        actual_tiers = {tier.value for tier in TenantTier}

        assert actual_tiers == expected_tiers

    def test_tenant_tier_hierarchy(self):
        """Test tenant tier hierarchy makes sense."""
        # Test that tiers are properly defined
        assert TenantTier.BASIC.value == "basic"
        assert TenantTier.PROFESSIONAL.value == "pro"
        assert TenantTier.ENTERPRISE.value == "enterprise"
        assert TenantTier.CUSTOM.value == "custom"


class TestTenantLimitsDataClass:
    """Test suite for TenantLimits data class."""

    def test_tenant_limits_creation(self):
        """Test basic tenant limits creation."""
        limits = TenantLimits(
            max_users=50,
            max_documents=10000,
            max_storage_gb=100,
            max_api_calls_per_hour=1000,
            max_concurrent_requests=10,
        )

        assert limits.max_users == 50
        assert limits.max_documents == 10000
        assert limits.max_storage_gb == 100
        assert limits.max_api_calls_per_hour == 1000
        assert limits.max_concurrent_requests == 10
        assert limits.features_enabled == []  # Default empty list

    def test_tenant_limits_with_features(self):
        """Test tenant limits with enabled features."""
        features = ["sso", "advanced_analytics", "custom_models"]

        limits = TenantLimits(
            max_users=100,
            max_documents=50000,
            max_storage_gb=500,
            max_api_calls_per_hour=5000,
            max_concurrent_requests=25,
            features_enabled=features,
        )

        assert limits.features_enabled == features
        assert "sso" in limits.features_enabled
        assert "advanced_analytics" in limits.features_enabled

    def test_tenant_limits_immutable_after_creation(self):
        """Test that limits can be accessed after creation."""
        limits = TenantLimits(
            max_users=10,
            max_documents=1000,
            max_storage_gb=10,
            max_api_calls_per_hour=100,
            max_concurrent_requests=5,
        )

        # Should be able to access all fields
        assert isinstance(limits.max_users, int)
        assert isinstance(limits.max_documents, int)
        assert isinstance(limits.max_storage_gb, int)
        assert isinstance(limits.max_api_calls_per_hour, int)
        assert isinstance(limits.max_concurrent_requests, int)
        assert isinstance(limits.features_enabled, list)


class TestTenantConfigDataClass:
    """Test suite for TenantConfig data class."""

    def test_tenant_config_creation_basic(self):
        """Test basic tenant config creation."""
        limits = TenantLimits(10, 1000, 10, 100, 5)
        created_time = datetime.utcnow()

        config = TenantConfig(
            tenant_id="tenant_123",
            name="Test Company",
            tier=TenantTier.BASIC,
            limits=limits,
            created_at=created_time,
            admin_email="admin@testcompany.com",
        )

        assert config.tenant_id == "tenant_123"
        assert config.name == "Test Company"
        assert config.tier == TenantTier.BASIC
        assert config.limits == limits
        assert config.created_at == created_time
        assert config.admin_email == "admin@testcompany.com"
        assert config.status == "active"  # Default value
        assert config.custom_domain is None
        assert config.sso_config is None
        assert config.billing_config is None

    def test_tenant_config_with_optional_fields(self):
        """Test tenant config with optional fields."""
        limits = TenantLimits(100, 50000, 500, 5000, 25)
        sso_config = {"provider": "azure_ad", "client_id": "test_client"}
        billing_config = {"plan": "enterprise", "billing_cycle": "monthly"}

        config = TenantConfig(
            tenant_id="enterprise_tenant",
            name="Enterprise Corp",
            tier=TenantTier.ENTERPRISE,
            limits=limits,
            created_at=datetime.utcnow(),
            admin_email="admin@enterprise.com",
            status="active",
            custom_domain="ai.enterprise.com",
            sso_config=sso_config,
            billing_config=billing_config,
        )

        assert config.custom_domain == "ai.enterprise.com"
        assert config.sso_config == sso_config
        assert config.billing_config == billing_config

    def test_tenant_config_status_values(self):
        """Test different status values for tenant config."""
        limits = TenantLimits(10, 1000, 10, 100, 5)
        statuses = ["active", "suspended", "terminated"]

        for status in statuses:
            config = TenantConfig(
                tenant_id=f"tenant_{status}",
                name=f"Test {status}",
                tier=TenantTier.BASIC,
                limits=limits,
                created_at=datetime.utcnow(),
                admin_email=f"admin@{status}.com",
                status=status,
            )

            assert config.status == status


class TestTenantUsageDataClass:
    """Test suite for TenantUsage data class."""

    def test_tenant_usage_creation(self):
        """Test tenant usage creation."""
        last_updated = datetime.utcnow()

        usage = TenantUsage(
            tenant_id="usage_tenant",
            current_users=25,
            current_documents=5000,
            storage_used_gb=75.5,
            api_calls_this_hour=250,
            concurrent_requests=3,
            last_updated=last_updated,
        )

        assert usage.tenant_id == "usage_tenant"
        assert usage.current_users == 25
        assert usage.current_documents == 5000
        assert usage.storage_used_gb == 75.5
        assert usage.api_calls_this_hour == 250
        assert usage.concurrent_requests == 3
        assert usage.last_updated == last_updated

    def test_tenant_usage_zero_values(self):
        """Test tenant usage with zero values."""
        usage = TenantUsage(
            tenant_id="empty_tenant",
            current_users=0,
            current_documents=0,
            storage_used_gb=0.0,
            api_calls_this_hour=0,
            concurrent_requests=0,
            last_updated=datetime.utcnow(),
        )

        assert usage.current_users == 0
        assert usage.current_documents == 0
        assert usage.storage_used_gb == 0.0
        assert usage.api_calls_this_hour == 0
        assert usage.concurrent_requests == 0

    def test_tenant_usage_high_values(self):
        """Test tenant usage with high values."""
        usage = TenantUsage(
            tenant_id="large_tenant",
            current_users=10000,
            current_documents=1000000,
            storage_used_gb=9999.99,
            api_calls_this_hour=50000,
            concurrent_requests=500,
            last_updated=datetime.utcnow(),
        )

        assert usage.current_users == 10000
        assert usage.current_documents == 1000000
        assert usage.storage_used_gb == 9999.99
        assert usage.api_calls_this_hour == 50000
        assert usage.concurrent_requests == 500


class TestTenantManager:
    """Test suite for TenantManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tenant_manager = TenantManager()

    def test_tenant_manager_initialization(self):
        """Test tenant manager initialization."""
        assert isinstance(self.tenant_manager.tenants, dict)
        assert isinstance(self.tenant_manager.usage_metrics, dict)
        assert isinstance(self.tenant_manager.tier_limits, dict)

        # Should have limits for all tiers
        assert len(self.tenant_manager.tier_limits) == len(TenantTier)
        for tier in TenantTier:
            assert tier in self.tenant_manager.tier_limits

    def test_default_tier_limits(self):
        """Test that default tier limits are properly set."""
        basic_limits = self.tenant_manager.tier_limits[TenantTier.BASIC]
        pro_limits = self.tenant_manager.tier_limits[TenantTier.PROFESSIONAL]
        enterprise_limits = self.tenant_manager.tier_limits[TenantTier.ENTERPRISE]

        # Basic limits should be smallest
        assert basic_limits.max_users <= pro_limits.max_users
        assert pro_limits.max_users <= enterprise_limits.max_users

        # Check that limits are TenantLimits objects
        assert isinstance(basic_limits, TenantLimits)
        assert isinstance(pro_limits, TenantLimits)
        assert isinstance(enterprise_limits, TenantLimits)

    def test_create_tenant_basic(self):
        """Test creating a basic tenant."""
        tenant_config = self.tenant_manager.create_tenant(
            name="Basic Company", admin_email="admin@basic.com", tier=TenantTier.BASIC
        )

        assert tenant_config is not None
        assert tenant_config.name == "Basic Company"
        assert tenant_config.admin_email == "admin@basic.com"
        assert tenant_config.tier == TenantTier.BASIC
        assert tenant_config.status == "active"

        # Should be in tenants dict
        assert tenant_config.tenant_id in self.tenant_manager.tenants

    def test_create_tenant_with_custom_config(self):
        """Test creating a tenant with custom configuration."""
        custom_domain = "ai.custom.com"
        sso_config = {"provider": "okta", "domain": "custom.okta.com"}

        tenant_config = self.tenant_manager.create_tenant(
            name="Custom Company",
            admin_email="admin@custom.com",
            tier=TenantTier.ENTERPRISE,
            custom_domain=custom_domain,
            sso_config=sso_config,
        )

        assert tenant_config.custom_domain == custom_domain
        assert tenant_config.sso_config == sso_config

    def test_create_tenant_generates_unique_ids(self):
        """Test that creating tenants generates unique IDs."""
        tenant1 = self.tenant_manager.create_tenant(
            "Company 1", "admin1@test.com", TenantTier.BASIC
        )
        tenant2 = self.tenant_manager.create_tenant(
            "Company 2", "admin2@test.com", TenantTier.BASIC
        )

        assert tenant1.tenant_id != tenant2.tenant_id
        assert len(tenant1.tenant_id) > 0
        assert len(tenant2.tenant_id) > 0

    def test_get_tenant_existing(self):
        """Test getting an existing tenant."""
        # Create a tenant first
        created_tenant = self.tenant_manager.create_tenant(
            "Get Test Company", "admin@gettest.com", TenantTier.PROFESSIONAL
        )

        # Get the tenant
        retrieved_tenant = self.tenant_manager.get_tenant(created_tenant.tenant_id)

        assert retrieved_tenant is not None
        assert retrieved_tenant.tenant_id == created_tenant.tenant_id
        assert retrieved_tenant.name == created_tenant.name

    def test_get_tenant_nonexistent(self):
        """Test getting a nonexistent tenant."""
        retrieved_tenant = self.tenant_manager.get_tenant("nonexistent_tenant_id")

        assert retrieved_tenant is None

    def test_update_tenant_status(self):
        """Test updating tenant status."""
        # Create a tenant
        tenant = self.tenant_manager.create_tenant(
            "Status Test", "admin@status.com", TenantTier.BASIC
        )

        # Update status to suspended
        success = self.tenant_manager.update_tenant_status(tenant.tenant_id, "suspended")

        assert success is True

        # Verify status was updated
        updated_tenant = self.tenant_manager.get_tenant(tenant.tenant_id)
        assert updated_tenant.status == "suspended"

    def test_update_tenant_status_invalid_tenant(self):
        """Test updating status for invalid tenant."""
        success = self.tenant_manager.update_tenant_status("invalid_tenant_id", "suspended")

        assert success is False

    def test_get_tenant_usage_existing(self):
        """Test getting usage for existing tenant."""
        # Create a tenant
        tenant = self.tenant_manager.create_tenant(
            "Usage Test", "admin@usage.com", TenantTier.PROFESSIONAL
        )

        # Get usage (should be initialized)
        usage = self.tenant_manager.get_tenant_usage(tenant.tenant_id)

        assert usage is not None
        assert usage.tenant_id == tenant.tenant_id
        assert usage.current_users == 0  # Should start at 0
        assert usage.current_documents == 0
        assert usage.storage_used_gb == 0.0

    def test_get_tenant_usage_nonexistent(self):
        """Test getting usage for nonexistent tenant."""
        usage = self.tenant_manager.get_tenant_usage("nonexistent_tenant")

        assert usage is None

    def test_update_tenant_usage(self):
        """Test updating tenant usage metrics."""
        # Create a tenant
        tenant = self.tenant_manager.create_tenant(
            "Update Usage Test", "admin@updateusage.com", TenantTier.ENTERPRISE
        )

        # Update usage
        success = self.tenant_manager.update_tenant_usage(
            tenant.tenant_id,
            current_users=50,
            current_documents=25000,
            storage_used_gb=250.5,
            api_calls_this_hour=1500,
            concurrent_requests=8,
        )

        assert success is True

        # Verify usage was updated
        usage = self.tenant_manager.get_tenant_usage(tenant.tenant_id)
        assert usage.current_users == 50
        assert usage.current_documents == 25000
        assert usage.storage_used_gb == 250.5
        assert usage.api_calls_this_hour == 1500
        assert usage.concurrent_requests == 8

    def test_update_tenant_usage_invalid_tenant(self):
        """Test updating usage for invalid tenant."""
        success = self.tenant_manager.update_tenant_usage("invalid_tenant", current_users=10)

        assert success is False

    def test_check_tenant_limits_within_limits(self):
        """Test checking tenant limits when within limits."""
        # Create a basic tenant
        tenant = self.tenant_manager.create_tenant(
            "Limits Test", "admin@limits.com", TenantTier.BASIC
        )

        # Update usage to be within limits
        basic_limits = self.tenant_manager.tier_limits[TenantTier.BASIC]
        self.tenant_manager.update_tenant_usage(
            tenant.tenant_id,
            current_users=basic_limits.max_users - 1,  # Just under limit
            current_documents=basic_limits.max_documents - 1,
            storage_used_gb=basic_limits.max_storage_gb - 1,
            api_calls_this_hour=basic_limits.max_api_calls_per_hour - 1,
            concurrent_requests=basic_limits.max_concurrent_requests - 1,
        )

        # Check limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(tenant.tenant_id)

        assert within_limits is True
        assert len(violations) == 0

    def test_check_tenant_limits_exceeds_limits(self):
        """Test checking tenant limits when exceeding limits."""
        # Create a basic tenant
        tenant = self.tenant_manager.create_tenant(
            "Exceed Limits Test", "admin@exceed.com", TenantTier.BASIC
        )

        # Update usage to exceed limits
        basic_limits = self.tenant_manager.tier_limits[TenantTier.BASIC]
        self.tenant_manager.update_tenant_usage(
            tenant.tenant_id,
            current_users=basic_limits.max_users + 1,  # Exceed limit
            current_documents=basic_limits.max_documents + 1000,
        )

        # Check limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(tenant.tenant_id)

        assert within_limits is False
        assert len(violations) > 0
        assert any("users" in violation.lower() for violation in violations)

    def test_check_tenant_limits_invalid_tenant(self):
        """Test checking limits for invalid tenant."""
        within_limits, violations = self.tenant_manager.check_tenant_limits("invalid_tenant")

        assert within_limits is False
        assert len(violations) > 0
        assert "not found" in violations[0].lower()

    def test_list_tenants_empty(self):
        """Test listing tenants when none exist."""
        tenants = self.tenant_manager.list_tenants()

        assert isinstance(tenants, list)
        assert len(tenants) == 0

    def test_list_tenants_with_tenants(self):
        """Test listing tenants when some exist."""
        # Create multiple tenants
        tenant1 = self.tenant_manager.create_tenant(
            "List Test 1", "admin1@list.com", TenantTier.BASIC
        )
        tenant2 = self.tenant_manager.create_tenant(
            "List Test 2", "admin2@list.com", TenantTier.PROFESSIONAL
        )

        tenants = self.tenant_manager.list_tenants()

        assert len(tenants) == 2
        tenant_ids = [t.tenant_id for t in tenants]
        assert tenant1.tenant_id in tenant_ids
        assert tenant2.tenant_id in tenant_ids

    def test_list_tenants_by_tier(self):
        """Test listing tenants filtered by tier."""
        # Create tenants with different tiers
        basic_tenant = self.tenant_manager.create_tenant(
            "Basic Tenant", "basic@test.com", TenantTier.BASIC
        )
        pro_tenant = self.tenant_manager.create_tenant(
            "Pro Tenant", "pro@test.com", TenantTier.PROFESSIONAL
        )
        enterprise_tenant = self.tenant_manager.create_tenant(
            "Enterprise Tenant", "enterprise@test.com", TenantTier.ENTERPRISE
        )
        # List only basic tenants
        basic_tenants = self.tenant_manager.list_tenants(tier_filter=TenantTier.BASIC)
        assert len(basic_tenants) == 1
        assert basic_tenants[0].tenant_id == basic_tenant.tenant_id
        assert basic_tenants[0].tier == TenantTier.BASIC

        # Test professional tier filtering
        pro_tenants = self.tenant_manager.list_tenants(tier_filter=TenantTier.PROFESSIONAL)
        assert len(pro_tenants) == 1
        assert pro_tenants[0].tenant_id == pro_tenant.tenant_id
        assert pro_tenants[0].tier == TenantTier.PROFESSIONAL

        # Test enterprise tier filtering
        enterprise_tenants = self.tenant_manager.list_tenants(tier_filter=TenantTier.ENTERPRISE)
        assert len(enterprise_tenants) == 1
        assert enterprise_tenants[0].tenant_id == enterprise_tenant.tenant_id
        assert enterprise_tenants[0].tier == TenantTier.ENTERPRISE

    def test_list_tenants_by_status(self):
        """Test listing tenants filtered by status."""
        # Create tenants and change status of one
        active_tenant = self.tenant_manager.create_tenant(
            "Active Tenant", "active@test.com", TenantTier.BASIC
        )
        suspended_tenant = self.tenant_manager.create_tenant(
            "Suspended Tenant", "suspended@test.com", TenantTier.BASIC
        )
        self.tenant_manager.update_tenant_status(suspended_tenant.tenant_id, "suspended")

        # List only active tenants
        active_tenants = self.tenant_manager.list_tenants(status_filter="active")

        assert len(active_tenants) == 1
        assert active_tenants[0].tenant_id == active_tenant.tenant_id
        assert active_tenants[0].status == "active"

    def test_delete_tenant_existing(self):
        """Test deleting an existing tenant."""
        # Create a tenant
        tenant = self.tenant_manager.create_tenant(
            "Delete Test", "admin@delete.com", TenantTier.BASIC
        )

        # Delete the tenant
        success = self.tenant_manager.delete_tenant(tenant.tenant_id)

        assert success is True

        # Verify tenant was removed
        deleted_tenant = self.tenant_manager.get_tenant(tenant.tenant_id)
        assert deleted_tenant is None

    def test_delete_tenant_nonexistent(self):
        """Test deleting a nonexistent tenant."""
        success = self.tenant_manager.delete_tenant("nonexistent_tenant")

        assert success is False

    def test_tenant_feature_check(self):
        """Test checking if tenant has specific features enabled."""
        # Create enterprise tenant (should have advanced features)
        tenant = self.tenant_manager.create_tenant(
            "Feature Test", "admin@feature.com", TenantTier.ENTERPRISE
        )
        # Verify tenant was created with correct tier
        assert tenant.tier == TenantTier.ENTERPRISE
        assert tenant.name == "Feature Test"
        assert tenant.admin_email == "admin@feature.com"

        # Check if tenant has advanced features (depends on implementation)
        enterprise_limits = self.tenant_manager.tier_limits[TenantTier.ENTERPRISE]
        # Features should be defined for enterprise tier
        assert isinstance(enterprise_limits.features_enabled, list)


class TestTenantEndpoints:
    """Test suite for TenantEndpoints."""

    def test_tenant_endpoints_initialization(self):
        """Test that TenantEndpoints can be initialized."""
        endpoints = TenantEndpoints()

        assert endpoints is not None
        # This is a minimal stub, so just test it exists


class TestTenantIntegration:
    """Integration tests for tenant management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tenant_manager = TenantManager()

    def test_full_tenant_lifecycle(self):
        """Test complete tenant lifecycle."""
        # Create tenant
        tenant = self.tenant_manager.create_tenant(
            "Lifecycle Test Corp", "admin@lifecycle.com", TenantTier.PROFESSIONAL
        )

        assert tenant is not None
        assert tenant.status == "active"

        # Update usage
        success = self.tenant_manager.update_tenant_usage(
            tenant.tenant_id,
            current_users=25,
            current_documents=5000,
            storage_used_gb=100.0,
        )
        assert success is True

        # Check limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(tenant.tenant_id)
        # Should be within professional limits
        assert within_limits is True

        # Suspend tenant
        success = self.tenant_manager.update_tenant_status(tenant.tenant_id, "suspended")
        assert success is True

        # Verify suspension
        updated_tenant = self.tenant_manager.get_tenant(tenant.tenant_id)
        assert updated_tenant.status == "suspended"

        # Reactivate tenant
        success = self.tenant_manager.update_tenant_status(tenant.tenant_id, "active")
        assert success is True

        # Delete tenant
        success = self.tenant_manager.delete_tenant(tenant.tenant_id)
        assert success is True

        # Verify deletion
        deleted_tenant = self.tenant_manager.get_tenant(tenant.tenant_id)
        assert deleted_tenant is None

    def test_multi_tenant_isolation(self):
        """Test that tenants are properly isolated."""
        # Create multiple tenants
        tenant1 = self.tenant_manager.create_tenant(
            "Isolation Test 1", "admin1@isolation.com", TenantTier.BASIC
        )
        tenant2 = self.tenant_manager.create_tenant(
            "Isolation Test 2", "admin2@isolation.com", TenantTier.PROFESSIONAL
        )

        # Update usage for tenant1
        self.tenant_manager.update_tenant_usage(
            tenant1.tenant_id, current_users=5, current_documents=1000
        )

        # Update usage for tenant2
        self.tenant_manager.update_tenant_usage(
            tenant2.tenant_id, current_users=50, current_documents=25000
        )

        # Verify isolation - tenant1 usage shouldn't affect tenant2
        usage1 = self.tenant_manager.get_tenant_usage(tenant1.tenant_id)
        usage2 = self.tenant_manager.get_tenant_usage(tenant2.tenant_id)

        assert usage1.current_users == 5
        assert usage1.current_documents == 1000

        assert usage2.current_users == 50
        assert usage2.current_documents == 25000

        # Check that each tenant has different limits based on tier
        limits1 = tenant1.limits
        limits2 = tenant2.limits

        # Different tiers should have different limits
        assert limits1.max_users != limits2.max_users

    def test_tenant_tier_upgrade_scenario(self):
        """Test scenario where tenant needs tier upgrade."""
        # Create basic tenant
        basic_tenant = self.tenant_manager.create_tenant(
            "Upgrade Test", "admin@upgrade.com", TenantTier.BASIC
        )

        # Get basic limits
        basic_limits = self.tenant_manager.tier_limits[TenantTier.BASIC]

        # Exceed basic limits
        self.tenant_manager.update_tenant_usage(
            basic_tenant.tenant_id,
            current_users=basic_limits.max_users + 5,  # Exceed user limit
        )

        # Check limits - should be exceeded
        within_limits, violations = self.tenant_manager.check_tenant_limits(basic_tenant.tenant_id)
        assert within_limits is False
        assert len(violations) > 0

        # Simulate tier upgrade by creating new config with professional tier
        # (In real implementation, there would be an upgrade_tenant_tier method)
        professional_tenant = self.tenant_manager.create_tenant(
            "Upgrade Test (Upgraded)", "admin@upgrade.com", TenantTier.PROFESSIONAL
        )

        # Update usage to same levels
        self.tenant_manager.update_tenant_usage(
            professional_tenant.tenant_id, current_users=basic_limits.max_users + 5
        )

        # Should now be within professional limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(
            professional_tenant.tenant_id
        )
        assert within_limits is True  # Should be within professional tier limits


class TestResourceLimits:
    """Test resource limit checking and management."""

    def setup_method(self):
        """Set up test tenant manager and tenant."""
        from agent.enterprise_tenant import TenantManager, TenantTier

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Resource Test", "admin@resource.com", TenantTier.BASIC
        )
        self.tenant_id = self.tenant.tenant_id

    def test_check_resource_limit_users_within_limit(self):
        """Test checking user limit when within bounds."""
        result = self.tenant_manager.check_resource_limit(
            self.tenant_id, "users", requested_amount=5
        )
        assert result is True

    def test_check_resource_limit_users_exceeds_limit(self):
        """Test checking user limit when exceeded."""
        # Set usage to near limit
        self.tenant_manager.update_tenant_usage(
            self.tenant_id, current_users=self.tenant.limits.max_users - 1
        )
        result = self.tenant_manager.check_resource_limit(
            self.tenant_id, "users", requested_amount=5
        )
        assert result is False

    def test_check_resource_limit_documents(self):
        """Test document limit checking."""
        result = self.tenant_manager.check_resource_limit(
            self.tenant_id, "documents", requested_amount=100
        )
        assert result is True

    def test_check_resource_limit_api_calls(self):
        """Test API calls limit checking."""
        result = self.tenant_manager.check_resource_limit(
            self.tenant_id, "api_calls", requested_amount=50
        )
        assert result is True

    def test_check_resource_limit_concurrent_requests(self):
        """Test concurrent requests limit checking."""
        result = self.tenant_manager.check_resource_limit(
            self.tenant_id, "concurrent_requests", requested_amount=2
        )
        assert result is True

    def test_check_resource_limit_invalid_tenant(self):
        """Test resource limit check with invalid tenant."""
        result = self.tenant_manager.check_resource_limit("invalid-id", "users", requested_amount=1)
        assert result is False

    def test_check_resource_limit_suspended_tenant(self):
        """Test resource limit check for suspended tenant."""
        self.tenant_manager.update_tenant_status(self.tenant_id, "suspended")
        result = self.tenant_manager.check_resource_limit(
            self.tenant_id, "users", requested_amount=1
        )
        assert result is False

    def test_check_resource_limit_unknown_resource_type(self):
        """Test resource limit check with unknown resource type."""
        result = self.tenant_manager.check_resource_limit(
            self.tenant_id, "unknown_resource", requested_amount=1
        )
        assert result is True  # Returns True for unknown types


class TestUsageIncrement:
    """Test usage increment functionality."""

    def setup_method(self):
        """Set up test tenant manager and tenant."""
        from agent.enterprise_tenant import TenantManager, TenantTier

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Increment Test", "admin@increment.com", TenantTier.BASIC
        )
        self.tenant_id = self.tenant.tenant_id

    def test_increment_usage_users(self):
        """Test incrementing user usage."""
        initial_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        initial_users = initial_usage.current_users

        self.tenant_manager.increment_usage(self.tenant_id, "users", amount=3)

        updated_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert updated_usage.current_users == initial_users + 3

    def test_increment_usage_documents(self):
        """Test incrementing document usage."""
        initial_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        initial_docs = initial_usage.current_documents

        self.tenant_manager.increment_usage(self.tenant_id, "documents", amount=10)

        updated_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert updated_usage.current_documents == initial_docs + 10

    def test_increment_usage_api_calls(self):
        """Test incrementing API call usage."""
        self.tenant_manager.increment_usage(self.tenant_id, "api_calls", amount=5)

        updated_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert updated_usage.api_calls_this_hour == 5

    def test_increment_usage_concurrent_requests(self):
        """Test incrementing concurrent requests."""
        self.tenant_manager.increment_usage(self.tenant_id, "concurrent_requests", amount=2)

        updated_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert updated_usage.concurrent_requests == 2

    def test_increment_usage_storage(self):
        """Test incrementing storage usage."""
        self.tenant_manager.increment_usage(self.tenant_id, "storage", amount=5)

        updated_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert updated_usage.storage_used_gb == 5.0

    def test_increment_usage_invalid_tenant(self):
        """Test increment usage with invalid tenant ID."""
        # Should not raise error, just ignore
        self.tenant_manager.increment_usage("invalid-id", "users", amount=1)

    def test_increment_usage_updates_timestamp(self):
        """Test that increment_usage updates last_updated timestamp."""
        initial_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        initial_timestamp = initial_usage.last_updated

        import time

        time.sleep(0.01)  # Small delay to ensure timestamp difference

        self.tenant_manager.increment_usage(self.tenant_id, "users", amount=1)

        updated_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert updated_usage.last_updated > initial_timestamp


class TestHourlyMetricsReset:
    """Test hourly metrics reset functionality."""

    def setup_method(self):
        """Set up test tenant manager and tenant."""
        from agent.enterprise_tenant import TenantManager, TenantTier

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Reset Test", "admin@reset.com", TenantTier.BASIC
        )
        self.tenant_id = self.tenant.tenant_id

    def test_reset_hourly_metrics(self):
        """Test resetting hourly metrics."""
        # Increment API calls
        self.tenant_manager.increment_usage(self.tenant_id, "api_calls", amount=100)

        usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert usage.api_calls_this_hour == 100

        # Reset hourly metrics
        self.tenant_manager.reset_hourly_metrics(self.tenant_id)

        usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert usage.api_calls_this_hour == 0

    def test_reset_hourly_metrics_invalid_tenant(self):
        """Test reset with invalid tenant ID."""
        # Should not raise error
        self.tenant_manager.reset_hourly_metrics("invalid-id")

    def test_reset_hourly_metrics_updates_timestamp(self):
        """Test that reset updates timestamp."""
        initial_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        initial_timestamp = initial_usage.last_updated

        import time

        time.sleep(0.01)

        self.tenant_manager.reset_hourly_metrics(self.tenant_id)

        updated_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert updated_usage.last_updated > initial_timestamp


class TestTenantSuspension:
    """Test tenant suspension functionality."""

    def setup_method(self):
        """Set up test tenant manager and tenant."""
        from agent.enterprise_tenant import TenantManager, TenantTier

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Suspend Test", "admin@suspend.com", TenantTier.BASIC
        )
        self.tenant_id = self.tenant.tenant_id

    def test_suspend_tenant(self):
        """Test suspending a tenant."""
        self.tenant_manager.suspend_tenant(self.tenant_id, reason="Payment overdue")

        tenant = self.tenant_manager.get_tenant(self.tenant_id)
        assert tenant.status == "suspended"

    def test_suspend_tenant_without_reason(self):
        """Test suspending tenant without reason."""
        self.tenant_manager.suspend_tenant(self.tenant_id)

        tenant = self.tenant_manager.get_tenant(self.tenant_id)
        assert tenant.status == "suspended"

    def test_suspend_tenant_invalid_id(self):
        """Test suspending non-existent tenant."""
        # Should not raise error
        self.tenant_manager.suspend_tenant("invalid-id", reason="Test")


class TestTenantIsolation:
    """Test tenant isolation functionality."""

    def setup_method(self):
        """Set up test tenant manager and isolation."""
        from agent.enterprise_tenant import (
            TenantIsolation,
            TenantManager,
            TenantTier,
        )

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Isolation Test", "admin@isolation.com", TenantTier.BASIC
        )
        self.tenant_id = self.tenant.tenant_id
        self.isolation = TenantIsolation(self.tenant_manager)

    def test_get_tenant_vault_path(self):
        """Test getting isolated vault path."""
        path = self.isolation.get_tenant_vault_path(self.tenant_id)
        assert path == f"./vaults/tenant_{self.tenant_id}"
        assert self.tenant_id in path

    def test_get_tenant_vault_path_invalid_tenant(self):
        """Test vault path with invalid tenant."""
        with pytest.raises(ValueError, match="Invalid or missing tenant_id"):
            self.isolation.get_tenant_vault_path("invalid-id")

    def test_get_tenant_vault_path_empty_tenant_id(self):
        """Test vault path with empty tenant ID."""
        with pytest.raises(ValueError, match="Invalid or missing tenant_id"):
            self.isolation.get_tenant_vault_path("")

    def test_get_tenant_cache_path(self):
        """Test getting isolated cache path."""
        path = self.isolation.get_tenant_cache_path(self.tenant_id)
        assert path == f"./agent/cache/tenant_{self.tenant_id}"
        assert self.tenant_id in path

    def test_get_tenant_cache_path_invalid_tenant(self):
        """Test cache path with invalid tenant."""
        with pytest.raises(ValueError, match="Invalid or missing tenant_id"):
            self.isolation.get_tenant_cache_path("invalid-id")

    def test_get_tenant_models_path(self):
        """Test getting isolated models path."""
        path = self.isolation.get_tenant_models_path(self.tenant_id)
        assert path == f"./models/tenant_{self.tenant_id}"
        assert self.tenant_id in path

    def test_get_tenant_models_path_invalid_tenant(self):
        """Test models path with invalid tenant."""
        with pytest.raises(ValueError, match="Invalid or missing tenant_id"):
            self.isolation.get_tenant_models_path("invalid-id")

    def test_get_tenant_logs_path(self):
        """Test getting isolated logs path."""
        path = self.isolation.get_tenant_logs_path(self.tenant_id)
        assert path == f"./logs/tenant_{self.tenant_id}"
        assert self.tenant_id in path

    def test_get_tenant_logs_path_invalid_tenant(self):
        """Test logs path with invalid tenant."""
        with pytest.raises(ValueError, match="Invalid or missing tenant_id"):
            self.isolation.get_tenant_logs_path("invalid-id")

    def test_filter_user_access_valid(self):
        """Test user access filtering with valid resource."""
        resource = f"/vaults/tenant_{self.tenant_id}/document.md"
        result = self.isolation.filter_user_access(self.tenant_id, "user123", resource)
        assert result is True

    def test_filter_user_access_invalid_resource(self):
        """Test user access filtering with resource from different tenant."""
        resource = "/vaults/tenant_other_id/document.md"
        result = self.isolation.filter_user_access(self.tenant_id, "user123", resource)
        assert result is False

    def test_filter_user_access_invalid_tenant(self):
        """Test user access filtering with invalid tenant."""
        resource = f"/vaults/tenant_{self.tenant_id}/document.md"
        result = self.isolation.filter_user_access("invalid-id", "user123", resource)
        assert result is False

    def test_filter_user_access_suspended_tenant(self):
        """Test user access filtering for suspended tenant."""
        self.tenant_manager.suspend_tenant(self.tenant_id)
        resource = f"/vaults/tenant_{self.tenant_id}/document.md"
        result = self.isolation.filter_user_access(self.tenant_id, "user123", resource)
        assert result is False


class TestBillingManager:
    """Test billing manager functionality."""

    def setup_method(self):
        """Set up test tenant manager and billing manager."""
        from agent.enterprise_tenant import BillingManager, TenantManager, TenantTier

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Billing Test", "admin@billing.com", TenantTier.PROFESSIONAL
        )
        self.tenant_id = self.tenant.tenant_id
        self.billing_manager = BillingManager(self.tenant_manager)

    def test_record_usage_event(self):
        """Test recording a usage event."""
        self.billing_manager.record_usage_event(
            self.tenant_id, "api_call", quantity=10, metadata={"endpoint": "/ask"}
        )

        assert self.tenant_id in self.billing_manager.usage_history
        events = self.billing_manager.usage_history[self.tenant_id]
        assert len(events) == 1
        assert events[0]["event_type"] == "api_call"
        assert events[0]["quantity"] == 10

    def test_record_multiple_usage_events(self):
        """Test recording multiple usage events."""
        self.billing_manager.record_usage_event(self.tenant_id, "api_call", quantity=5)
        self.billing_manager.record_usage_event(self.tenant_id, "document_index", quantity=2)

        events = self.billing_manager.usage_history[self.tenant_id]
        assert len(events) == 2

    def test_generate_usage_report(self):
        """Test generating usage report."""
        from datetime import datetime, timedelta

        # Record some events
        self.billing_manager.record_usage_event(self.tenant_id, "api_call", quantity=10)
        self.billing_manager.record_usage_event(self.tenant_id, "api_call", quantity=5)
        self.billing_manager.record_usage_event(self.tenant_id, "document_index", quantity=3)

        # Generate report
        start_date = datetime.utcnow() - timedelta(hours=1)
        end_date = datetime.utcnow() + timedelta(hours=1)

        report = self.billing_manager.generate_usage_report(self.tenant_id, start_date, end_date)

        assert report["tenant_id"] == self.tenant_id
        assert report["tenant_name"] == "Billing Test"
        assert report["total_events"] == 3
        assert report["usage_summary"]["api_call"] == 15
        assert report["usage_summary"]["document_index"] == 3
        assert report["tier"] == "pro"

    def test_generate_usage_report_empty(self):
        """Test generating report with no events."""
        from datetime import datetime, timedelta

        start_date = datetime.utcnow() - timedelta(hours=1)
        end_date = datetime.utcnow() + timedelta(hours=1)

        report = self.billing_manager.generate_usage_report(self.tenant_id, start_date, end_date)

        assert report["total_events"] == 0
        assert report["usage_summary"] == {}

    def test_generate_usage_report_date_filtering(self):
        """Test that usage report filters by date range."""
        from datetime import datetime, timedelta

        # Record event
        self.billing_manager.record_usage_event(self.tenant_id, "api_call", quantity=10)

        # Generate report with past date range (should be empty)
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow() - timedelta(days=6)

        report = self.billing_manager.generate_usage_report(self.tenant_id, start_date, end_date)

        assert report["total_events"] == 0


class TestFeatureAccess:
    """Test feature access checking."""

    def setup_method(self):
        """Set up test tenant manager and tenants."""
        from agent.enterprise_tenant import TenantManager, TenantTier

        self.tenant_manager = TenantManager()
        self.basic_tenant = self.tenant_manager.create_tenant(
            "Basic Feature Test", "basic@feature.com", TenantTier.BASIC
        )
        self.pro_tenant = self.tenant_manager.create_tenant(
            "Pro Feature Test", "pro@feature.com", TenantTier.PROFESSIONAL
        )

    def test_has_feature_access_enabled(self):
        """Test feature access when feature is enabled."""
        # Professional tier has 'analytics' feature
        result = self.tenant_manager.has_feature_access(self.pro_tenant.tenant_id, "analytics")
        assert result is True

    def test_has_feature_access_disabled(self):
        """Test feature access when feature is disabled."""
        # Basic tier doesn't have 'analytics' feature
        result = self.tenant_manager.has_feature_access(self.basic_tenant.tenant_id, "analytics")
        assert result is False

    def test_has_feature_access_invalid_tenant(self):
        """Test feature access with invalid tenant."""
        result = self.tenant_manager.has_feature_access("invalid-id", "sso")
        assert result is False

    def test_has_feature_access_all_features(self):
        """Test when tenant has 'all' features enabled."""
        from agent.enterprise_tenant import TenantTier

        enterprise_tenant = self.tenant_manager.create_tenant(
            "Enterprise Feature Test", "enterprise@feature.com", TenantTier.ENTERPRISE
        )

        # Enterprise tier has more features
        result = self.tenant_manager.has_feature_access(enterprise_tenant.tenant_id, "any_feature")
        # Will return True if 'all' is in features or if feature is explicitly listed
        assert isinstance(result, bool)


class TestTenantUpgrade:
    """Test tenant tier upgrade functionality."""

    def setup_method(self):
        """Set up test tenant manager and tenant."""
        from agent.enterprise_tenant import TenantManager, TenantTier

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Upgrade Test", "admin@upgrade.com", TenantTier.BASIC
        )
        self.tenant_id = self.tenant.tenant_id

    def test_upgrade_tenant_basic_to_pro(self):
        """Test upgrading tenant from basic to professional."""
        from agent.enterprise_tenant import TenantTier

        result = self.tenant_manager.upgrade_tenant(self.tenant_id, TenantTier.PROFESSIONAL)
        assert result is True

        tenant = self.tenant_manager.get_tenant(self.tenant_id)
        assert tenant.tier == TenantTier.PROFESSIONAL
        assert tenant.limits.max_users == 100  # Professional tier limit

    def test_upgrade_tenant_to_enterprise(self):
        """Test upgrading tenant to enterprise tier."""
        from agent.enterprise_tenant import TenantTier

        result = self.tenant_manager.upgrade_tenant(self.tenant_id, TenantTier.ENTERPRISE)
        assert result is True

        tenant = self.tenant_manager.get_tenant(self.tenant_id)
        assert tenant.tier == TenantTier.ENTERPRISE

    def test_upgrade_tenant_invalid_id(self):
        """Test upgrade with invalid tenant ID."""
        from agent.enterprise_tenant import TenantTier

        result = self.tenant_manager.upgrade_tenant("invalid-id", TenantTier.ENTERPRISE)
        assert result is False

    def test_upgrade_tenant_updates_limits(self):
        """Test that upgrade updates tenant limits."""
        from agent.enterprise_tenant import TenantTier

        # Get initial limits
        initial_tenant = self.tenant_manager.get_tenant(self.tenant_id)
        initial_max_users = initial_tenant.limits.max_users

        # Upgrade
        self.tenant_manager.upgrade_tenant(self.tenant_id, TenantTier.PROFESSIONAL)

        # Check updated limits
        updated_tenant = self.tenant_manager.get_tenant(self.tenant_id)
        assert updated_tenant.limits.max_users > initial_max_users


class TestMultiTenantMiddleware:
    """Test multi-tenant middleware functionality."""

    def setup_method(self):
        """Set up test tenant manager, middleware, and mock request."""
        from unittest.mock import AsyncMock, MagicMock

        from agent.enterprise_tenant import (
            MultiTenantMiddleware,
            TenantManager,
            TenantTier,
        )

        self.tenant_manager = TenantManager()
        self.tenant = self.tenant_manager.create_tenant(
            "Middleware Test", "admin@middleware.com", TenantTier.BASIC
        )
        self.tenant_id = self.tenant.tenant_id
        self.middleware = MultiTenantMiddleware(self.tenant_manager)

        # Create mock request
        self.mock_request = MagicMock()
        self.mock_request.state = MagicMock()
        self.mock_request.headers = {"X-Tenant-ID": self.tenant_id}

        # Create mock call_next
        self.mock_call_next = AsyncMock()
        self.mock_call_next.return_value = MagicMock(status_code=200)

    def test_extract_tenant_id_from_header(self):
        """Test extracting tenant ID from header."""
        tenant_id = self.middleware._extract_tenant_id(self.mock_request)
        assert tenant_id == self.tenant_id

    def test_extract_tenant_id_from_user_state(self):
        """Test extracting tenant ID from user state."""
        self.mock_request.state.user = {"tenant_id": self.tenant_id}
        tenant_id = self.middleware._extract_tenant_id(self.mock_request)
        assert tenant_id == self.tenant_id

    def test_extract_tenant_id_missing(self):
        """Test extracting tenant ID when missing."""
        self.mock_request.headers = {}
        tenant_id = self.middleware._extract_tenant_id(self.mock_request)
        assert tenant_id is None

    @pytest.mark.asyncio
    async def test_middleware_call_success(self):
        """Test successful middleware call."""
        response = await self.middleware(self.mock_request, self.mock_call_next)

        assert response.status_code == 200
        assert hasattr(self.mock_request.state, "tenant_id")
        assert self.mock_request.state.tenant_id == self.tenant_id
        self.mock_call_next.assert_called_once_with(self.mock_request)

    @pytest.mark.asyncio
    async def test_middleware_call_missing_tenant_id(self):
        """Test middleware call with missing tenant ID."""
        self.mock_request.headers = {}
        response = await self.middleware(self.mock_request, self.mock_call_next)

        assert response.status_code == 400
        # Extract JSON content
        import json

        content = json.loads(response.body.decode())
        assert "error" in content
        assert "tenant" in content["error"].lower()

    @pytest.mark.asyncio
    async def test_middleware_call_invalid_tenant_id(self):
        """Test middleware call with invalid tenant ID."""
        self.mock_request.headers = {"X-Tenant-ID": "invalid-tenant-id"}
        response = await self.middleware(self.mock_request, self.mock_call_next)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_middleware_concurrent_request_tracking(self):
        """Test that middleware tracks concurrent requests."""
        initial_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        initial_concurrent = initial_usage.concurrent_requests

        # Call middleware
        await self.middleware(self.mock_request, self.mock_call_next)

        # After completion, concurrent requests should be back to initial
        final_usage = self.tenant_manager.get_tenant_usage(self.tenant_id)
        assert final_usage.concurrent_requests == initial_concurrent

    @pytest.mark.asyncio
    async def test_middleware_concurrent_limit_exceeded(self):
        """Test middleware behavior when concurrent limit is exceeded."""
        # Set concurrent requests to limit
        self.tenant_manager.update_tenant_usage(
            self.tenant_id,
            concurrent_requests=self.tenant.limits.max_concurrent_requests,
        )

        response = await self.middleware(self.mock_request, self.mock_call_next)

        assert response.status_code == 429
        import json

        content = json.loads(response.body.decode())
        assert "limit" in content["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__])
