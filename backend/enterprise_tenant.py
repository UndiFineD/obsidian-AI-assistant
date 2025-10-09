# Enterprise Multi-Tenant Architecture
# Provides tenant isolation, resource management, and billing capabilities

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
import uuid
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class TenantTier(Enum):
    BASIC = "basic"          # Small teams (1-10 users)
    PROFESSIONAL = "pro"     # Medium teams (11-100 users)  
    ENTERPRISE = "enterprise" # Large orgs (100+ users)
    CUSTOM = "custom"        # Custom enterprise deployments

@dataclass
class TenantLimits:
    """Resource limits per tenant"""
    max_users: int
    max_documents: int
    max_storage_gb: int
    max_api_calls_per_hour: int
    max_concurrent_requests: int
    features_enabled: List[str] = field(default_factory=list)

@dataclass
class TenantConfig:
    """Tenant configuration and metadata"""
    tenant_id: str
    name: str
    tier: TenantTier
    limits: TenantLimits
    created_at: datetime
    admin_email: str
    status: str = "active"  # active, suspended, terminated
    custom_domain: Optional[str] = None
    sso_config: Optional[Dict[str, Any]] = None
    billing_config: Optional[Dict[str, Any]] = None

@dataclass
class TenantUsage:
    """Current usage metrics for a tenant"""
    tenant_id: str
    current_users: int
    current_documents: int
    storage_used_gb: float
    api_calls_this_hour: int
    concurrent_requests: int
    last_updated: datetime

class TenantManager:
    """Multi-tenant architecture manager"""
    
    def __init__(self):
        self.tenants: Dict[str, TenantConfig] = {}
        self.usage_metrics: Dict[str, TenantUsage] = {}
        self.tier_limits = self._initialize_tier_limits()
    
    def _initialize_tier_limits(self) -> Dict[TenantTier, TenantLimits]:
        """Initialize default limits for each tier"""
        return {
            TenantTier.BASIC: TenantLimits(
                max_users=10,
                max_documents=1000,
                max_storage_gb=5,
                max_api_calls_per_hour=1000,
                max_concurrent_requests=5,
                features_enabled=["basic_ai", "document_search"]
            ),
            TenantTier.PROFESSIONAL: TenantLimits(
                max_users=100,
                max_documents=10000,
                max_storage_gb=50,
                max_api_calls_per_hour=5000,
                max_concurrent_requests=20,
                features_enabled=["basic_ai", "document_search", "voice_processing", "analytics"]
            ),
            TenantTier.ENTERPRISE: TenantLimits(
                max_users=1000,
                max_documents=100000,
                max_storage_gb=500,
                max_api_calls_per_hour=25000,
                max_concurrent_requests=100,
                features_enabled=["basic_ai", "document_search", "voice_processing", "analytics", "sso", "audit_logging", "custom_models"]
            ),
            TenantTier.CUSTOM: TenantLimits(
                max_users=999999,
                max_documents=999999,
                max_storage_gb=99999,
                max_api_calls_per_hour=999999,
                max_concurrent_requests=500,
                features_enabled=["all"]
            )
        }
    
    def create_tenant(self, name: str, tier: TenantTier, admin_email: str, 
                     custom_limits: Optional[TenantLimits] = None) -> TenantConfig:
        """Create a new tenant"""
        if not name or not isinstance(name, str):
            raise ValueError("Tenant name must be a non-empty string.")
        if not admin_email or "@" not in admin_email:
            raise ValueError("A valid admin email is required.")
        if not isinstance(tier, TenantTier):
            raise ValueError(f"Invalid tenant tier provided. Must be one of {list(TenantTier)}.")

        tenant_id = str(uuid.uuid4())
        
        # Use custom limits or default tier limits
        limits = custom_limits or self.tier_limits[tier]
        
        tenant = TenantConfig(
            tenant_id=tenant_id,
            name=name,
            tier=tier,
            limits=limits,
            created_at=datetime.utcnow(),
            admin_email=admin_email
        )
        
        self.tenants[tenant_id] = tenant
        
        # Initialize usage metrics
        self.usage_metrics[tenant_id] = TenantUsage(
            tenant_id=tenant_id,
            current_users=0,
            current_documents=0,
            storage_used_gb=0.0,
            api_calls_this_hour=0,
            concurrent_requests=0,
            last_updated=datetime.utcnow()
        )
        
        logger.info(f"Created tenant: {name} (ID: {tenant_id}, Tier: {tier.value})")
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant configuration"""
        return self.tenants.get(tenant_id)
    
    def get_tenant_usage(self, tenant_id: str) -> Optional[TenantUsage]:
        """Get tenant usage metrics"""
        return self.usage_metrics.get(tenant_id)
    
    def check_resource_limit(self, tenant_id: str, resource_type: str, 
                           requested_amount: int = 1) -> bool:
        """Check if tenant can use additional resources"""
        tenant = self.get_tenant(tenant_id)
        usage = self.get_tenant_usage(tenant_id)
        
        if not tenant or not usage or tenant.status != "active":
            return False
        
        limits = tenant.limits
        
        # Check specific resource limits
        if resource_type == "users":
            return usage.current_users + requested_amount <= limits.max_users
        elif resource_type == "documents":
            return usage.current_documents + requested_amount <= limits.max_documents
        elif resource_type == "api_calls":
            return usage.api_calls_this_hour + requested_amount <= limits.max_api_calls_per_hour
        elif resource_type == "concurrent_requests":
            return usage.concurrent_requests + requested_amount <= limits.max_concurrent_requests
        
        return True
    
    def increment_usage(self, tenant_id: str, resource_type: str, amount: int = 1):
        """Increment usage counter for a tenant"""
        usage = self.usage_metrics.get(tenant_id)
        if not usage:
            return
        
        if resource_type == "users":
            usage.current_users += amount
        elif resource_type == "documents":
            usage.current_documents += amount
        elif resource_type == "api_calls":
            usage.api_calls_this_hour += amount
        elif resource_type == "concurrent_requests":
            usage.concurrent_requests += amount
        elif resource_type == "storage":
            usage.storage_used_gb += amount
        
        usage.last_updated = datetime.utcnow()
    
    def reset_hourly_metrics(self, tenant_id: str):
        """Reset hourly usage metrics (called by scheduler)"""
        usage = self.usage_metrics.get(tenant_id)
        if usage:
            usage.api_calls_this_hour = 0
            usage.last_updated = datetime.utcnow()
    
    def has_feature_access(self, tenant_id: str, feature: str) -> bool:
        """Check if tenant has access to a specific feature"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        return (feature in tenant.limits.features_enabled or 
                "all" in tenant.limits.features_enabled)
    
    def upgrade_tenant(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Upgrade tenant to a new tier"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        old_tier = tenant.tier
        tenant.tier = new_tier
        tenant.limits = self.tier_limits[new_tier]
        
        logger.info(f"Upgraded tenant {tenant_id} from {old_tier.value} to {new_tier.value}")
        return True
    
    def suspend_tenant(self, tenant_id: str, reason: str = ""):
        """Suspend tenant access"""
        tenant = self.get_tenant(tenant_id)
        if tenant:
            tenant.status = "suspended"
            logger.warning(f"Suspended tenant {tenant_id}: {reason}")
    
    def list_tenants(self, status: Optional[str] = None) -> List[TenantConfig]:
        """List all tenants, optionally filtered by status"""
        if status:
            return [t for t in self.tenants.values() if t.status == status]
        return list(self.tenants.values())

class TenantIsolation:
    """Provides data and resource isolation between tenants"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
    
    def get_tenant_vault_path(self, tenant_id: str) -> str:
        """Get isolated vault path for tenant"""
        return f"./vaults/tenant_{tenant_id}"
    
    def get_tenant_cache_path(self, tenant_id: str) -> str:
        """Get isolated cache path for tenant"""
        return f"./cache/tenant_{tenant_id}"
    
    def get_tenant_models_path(self, tenant_id: str) -> str:
        """Get isolated models path for tenant"""
        return f"./models/tenant_{tenant_id}"
    
    def get_tenant_logs_path(self, tenant_id: str) -> str:
        """Get isolated logs path for tenant"""
        return f"./logs/tenant_{tenant_id}"
    
    def filter_user_access(self, tenant_id: str, user_id: str, resource: str) -> bool:
        """Check if user has access to resource within tenant"""
        # Implement tenant-specific access control
        tenant = self.tenant_manager.get_tenant(tenant_id)
        return tenant is not None and tenant.status == "active"

class BillingManager:
    """Enterprise billing and usage tracking"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.usage_history: Dict[str, List[Dict]] = {}
    
    def record_usage_event(self, tenant_id: str, event_type: str, 
                          quantity: int, metadata: Optional[Dict] = None):
        """Record a billable usage event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "quantity": quantity,
            "metadata": metadata or {}
        }
        
        if tenant_id not in self.usage_history:
            self.usage_history[tenant_id] = []
        
        self.usage_history[tenant_id].append(event)
    
    def generate_usage_report(self, tenant_id: str, start_date: datetime, 
                            end_date: datetime) -> Dict[str, Any]:
        """Generate usage report for billing"""
        events = self.usage_history.get(tenant_id, [])
        
        # Filter events by date range
        filtered_events = []
        for event in events:
            event_date = datetime.fromisoformat(event["timestamp"])
            if start_date <= event_date <= end_date:
                filtered_events.append(event)
        
        # Aggregate usage by type
        usage_summary = {}
        for event in filtered_events:
            event_type = event["event_type"]
            if event_type not in usage_summary:
                usage_summary[event_type] = 0
            usage_summary[event_type] += event["quantity"]
        
        tenant = self.tenant_manager.get_tenant(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant.name if tenant else "Unknown",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "usage_summary": usage_summary,
            "total_events": len(filtered_events),
            "tier": tenant.tier.value if tenant else "unknown"
        }

# FastAPI middleware for multi-tenant isolation
class MultiTenantMiddleware:
    """Middleware to enforce tenant isolation"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
    
    async def __call__(self, request, call_next):
        """Enforce tenant isolation and limits"""
        # Extract tenant ID from JWT token or header
        tenant_id = self._extract_tenant_id(request)
        
        if not tenant_id:
            return JSONResponse(
                status_code=400,
                content={"error": "Tenant ID required", "type": "tenant_error"}
            )
        
        # Check tenant status and limits
        if not self.tenant_manager.check_resource_limit(tenant_id, "concurrent_requests"):
            return JSONResponse(
                status_code=429,
                content={"error": "Concurrent request limit exceeded", "type": "rate_limit_error"}
            )
        
        # Add tenant context to request
        request.state.tenant_id = tenant_id
        
        # Increment concurrent request counter
        self.tenant_manager.increment_usage(tenant_id, "concurrent_requests")
        
        try:
            response = await call_next(request)
            return response
        finally:
            # Decrement concurrent request counter
            self.tenant_manager.increment_usage(tenant_id, "concurrent_requests", -1)
    
    def _extract_tenant_id(self, request) -> Optional[str]:
        """Extract tenant ID from request"""
        # Try to get from JWT token first
        if hasattr(request.state, 'user') and 'tenant_id' in request.state.user:
            return request.state.user['tenant_id']
        
        # Fallback to header
        return request.headers.get("X-Tenant-ID")