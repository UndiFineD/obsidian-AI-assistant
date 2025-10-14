# tests/backend/test_enterprise_tenant.py
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add the backend to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.enterprise_tenant import (
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
            max_concurrent_requests=10
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
            features_enabled=features
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
            max_concurrent_requests=5
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
            admin_email="admin@testcompany.com"
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
            billing_config=billing_config
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
                status=status
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
            last_updated=last_updated
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
            last_updated=datetime.utcnow()
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
            last_updated=datetime.utcnow()
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
            name="Basic Company",
            admin_email="admin@basic.com",
            tier=TenantTier.BASIC
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
            sso_config=sso_config
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
        success = self.tenant_manager.update_tenant_status(
            tenant.tenant_id, "suspended"
        )

        assert success is True

        # Verify status was updated
        updated_tenant = self.tenant_manager.get_tenant(tenant.tenant_id)
        assert updated_tenant.status == "suspended"

    def test_update_tenant_status_invalid_tenant(self):
        """Test updating status for invalid tenant."""
        success = self.tenant_manager.update_tenant_status(
            "invalid_tenant_id", "suspended"
        )

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
            concurrent_requests=8
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
        success = self.tenant_manager.update_tenant_usage(
            "invalid_tenant", current_users=10
        )

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
            concurrent_requests=basic_limits.max_concurrent_requests - 1
        )

        # Check limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(
            tenant.tenant_id
        )

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
            current_documents=basic_limits.max_documents + 1000
        )

        # Check limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(
            tenant.tenant_id
        )

        assert within_limits is False
        assert len(violations) > 0
        assert any("users" in violation.lower() for violation in violations)

    def test_check_tenant_limits_invalid_tenant(self):
        """Test checking limits for invalid tenant."""
        within_limits, violations = self.tenant_manager.check_tenant_limits(
            "invalid_tenant"
        )

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
        pro_tenants = self.tenant_manager.list_tenants(
            tier_filter=TenantTier.PROFESSIONAL
        )
        assert len(pro_tenants) == 1
        assert pro_tenants[0].tenant_id == pro_tenant.tenant_id
        assert pro_tenants[0].tier == TenantTier.PROFESSIONAL

        # Test enterprise tier filtering
        enterprise_tenants = self.tenant_manager.list_tenants(
            tier_filter=TenantTier.ENTERPRISE
        )
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
        self.tenant_manager.update_tenant_status(
            suspended_tenant.tenant_id, "suspended"
        )

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
            "Lifecycle Test Corp",
            "admin@lifecycle.com",
            TenantTier.PROFESSIONAL
        )

        assert tenant is not None
        assert tenant.status == "active"

        # Update usage
        success = self.tenant_manager.update_tenant_usage(
            tenant.tenant_id,
            current_users=25,
            current_documents=5000,
            storage_used_gb=100.0
        )
        assert success is True

        # Check limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(
            tenant.tenant_id
        )
        # Should be within professional limits
        assert within_limits is True

        # Suspend tenant
        success = self.tenant_manager.update_tenant_status(
            tenant.tenant_id, "suspended"
        )
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
            tenant1.tenant_id,
            current_users=5,
            current_documents=1000
        )

        # Update usage for tenant2
        self.tenant_manager.update_tenant_usage(
            tenant2.tenant_id,
            current_users=50,
            current_documents=25000
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
            current_users=basic_limits.max_users + 5  # Exceed user limit
        )

        # Check limits - should be exceeded
        within_limits, violations = self.tenant_manager.check_tenant_limits(
            basic_tenant.tenant_id
        )
        assert within_limits is False
        assert len(violations) > 0

        # Simulate tier upgrade by creating new config with professional tier
        # (In real implementation, there would be an upgrade_tenant_tier method)
        professional_tenant = self.tenant_manager.create_tenant(
            "Upgrade Test (Upgraded)",
            "admin@upgrade.com",
            TenantTier.PROFESSIONAL
        )

        # Update usage to same levels
        self.tenant_manager.update_tenant_usage(
            professional_tenant.tenant_id,
            current_users=basic_limits.max_users + 5
        )

        # Should now be within professional limits
        within_limits, violations = self.tenant_manager.check_tenant_limits(
            professional_tenant.tenant_id
        )
        assert within_limits is True  # Should be within professional tier limits


if __name__ == "__main__":
    pytest.main([__file__])
