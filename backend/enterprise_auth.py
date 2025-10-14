# Enterprise Authentication Module - SSO Integration
# Provides Single Sign-On capabilities for enterprise deployment

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import jwt

logger = logging.getLogger(__name__)


class SSOProvider(Enum):
    AZURE_AD = "azure_ad"
    GOOGLE_WORKSPACE = "google_workspace"
    OKTA = "okta"
    SAML = "saml"
    LDAP = "ldap"


@dataclass
class SSOConfig:
    """SSO Provider configuration"""

    provider: SSOProvider
    client_id: str
    client_secret: str
    tenant_id: Optional[str] = None
    redirect_uri: str = "http://localhost:8000/auth/callback"
    scopes: List[str] = None

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = ["openid", "email", "profile"]


@dataclass
class UserInfo:
    """Standardized user information from SSO providers"""

    user_id: str
    email: str
    name: str
    groups: List[str]
    tenant_id: Optional[str] = None
    roles: List[str] = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = ["user"]


class _HandlerRegistry:
    """Patch-friendly registry that resolves handlers at call time.

    This allows tests to patch instance methods like ``_handle_azure_ad`` and have
    those patches honored, since resolution happens via ``getattr`` at call time
    rather than storing bound method references at init.
    """

    def __init__(self, manager: "SSOManager"):
        self._manager = manager
        # Map of provider to handler method name
        self._map = {
            SSOProvider.AZURE_AD: "_handle_azure_ad",
            SSOProvider.GOOGLE_WORKSPACE: "_handle_google_workspace",
            SSOProvider.OKTA: "_handle_okta",
            SSOProvider.SAML: "_handle_saml",
            SSOProvider.LDAP: "_handle_ldap",
        }

    def get(self, provider):  # type: ignore[override]
        """Return the current handler callable for the given provider or None."""
        method_name = self._map.get(provider)
        if not method_name:
            return None
        return getattr(self._manager, method_name, None)

    # Mapping-like helpers for tests/compatibility
    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, key) -> bool:  # pragma: no cover - trivial
        return key in self._map

    def keys(self):  # pragma: no cover - convenience
        return self._map.keys()

    def __iter__(self):  # pragma: no cover - convenience
        return iter(self._map)


class SSOManager:
    """Enterprise SSO authentication manager"""

    def __init__(self, config: SSOConfig):
        self.config = config
        # Use a registry to allow patching both the registry.get and the handler methods
        self.provider_handlers = _HandlerRegistry(self)

    @property
    def providers(self):
        """List of supported providers (for health/diagnostics)."""
        # Expose keys to maintain compatibility with integrations that expect this
        return list(self.provider_handlers._map.keys())

    async def authenticate(self, auth_code: str) -> Optional[UserInfo]:
        """Authenticate user via SSO provider"""
        try:
            handler = self.provider_handlers.get(self.config.provider)
            if not handler:
                # Maintain previous behavior (log via exception path -> None)
                raise ValueError(
                    f"Unsupported SSO provider: {self.config.provider}"
                )

            user_info = await handler(auth_code)
            logger.info(f"SSO authentication successful for user: {user_info.email}")
            return user_info

        except Exception as e:
            logger.error(f"SSO authentication failed: {str(e)}")
            return None

    async def _handle_azure_ad(self, auth_code: str) -> UserInfo:
        """Handle Azure AD authentication"""
        # Implementation would use microsoft-identity library
        # For now, return mock data for enterprise setup
        return UserInfo(
            user_id="azure_user_123",
            email="user@enterprise.com",
            name="Enterprise User",
            groups=["Engineers", "AI-Users"],
            tenant_id=self.config.tenant_id,
            roles=["user", "ai_access"],
        )

    async def _handle_google_workspace(self, auth_code: str) -> UserInfo:
        """Handle Google Workspace authentication"""
        # Implementation would use google-auth library
        return UserInfo(
            user_id="google_user_456",
            email="user@company.com",
            name="Google User",
            groups=["Employees"],
            roles=["user"],
        )

    async def _handle_okta(self, auth_code: str) -> UserInfo:
        """Handle Okta authentication"""
        # Implementation would use okta-sdk-python
        return UserInfo(
            user_id="okta_user_789",
            email="user@okta-org.com",
            name="Okta User",
            groups=["Staff", "AI-Power-Users"],
            roles=["user", "advanced"],
        )

    async def _handle_saml(self, auth_code: str) -> UserInfo:
        """Handle SAML authentication"""
        # Implementation would use python3-saml
        return UserInfo(
            user_id="saml_user_101",
            email="user@saml-org.com",
            name="SAML User",
            groups=["Department-A"],
            roles=["user"],
        )

    async def _handle_ldap(self, auth_code: str) -> UserInfo:
        """Handle LDAP authentication"""
        # Implementation would use ldap3
        return UserInfo(
            user_id="ldap_user_202",
            email="user@ldap-org.com",
            name="LDAP User",
            groups=["Domain Users", "AI Users"],
            roles=["user"],
        )

    def generate_jwt_token(
        self, user_info: UserInfo, secret_key: str, expiry_hours: int = 24
    ) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            "user_id": user_info.user_id,
            "email": user_info.email,
            "name": user_info.name,
            "groups": user_info.groups,
            "roles": user_info.roles,
            "tenant_id": user_info.tenant_id,
            "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
            "iat": datetime.utcnow(),
            "iss": "obsidian-ai-assistant",
        }

        return jwt.encode(payload, secret_key, algorithm="HS256")

    def validate_jwt_token(
        self, token: str, secret_key: str
    ) -> Optional[Dict[str, Any]]:
        """Validate and decode JWT token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None


class EnterpriseAuthMiddleware:
    """FastAPI middleware for enterprise authentication"""

    def __init__(self, sso_manager: SSOManager, secret_key: str):
        self.sso_manager = sso_manager
        self.secret_key = secret_key
        self.public_endpoints = {
            "/health",
            "/status",
            "/",
            "/auth/login",
            "/auth/callback",
        }

    async def __call__(self, request, call_next):
        """Process enterprise authentication for requests"""
        path = request.url.path

        # Skip authentication for public endpoints
        if path in self.public_endpoints:
            return await call_next(request)

        # Extract JWT token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"error": "Authentication required", "status_code": 401}

        token = auth_header.split(" ")[1]
        payload = self.sso_manager.validate_jwt_token(token, self.secret_key)

        if not payload:
            return {"error": "Invalid or expired token", "status_code": 401}

        # Add user context to request
        request.state.user = payload
        return await call_next(request)


# FastAPI endpoints for SSO integration
class SSOEndpoints:
    """Enterprise SSO API endpoints"""

    def __init__(self, app, sso_manager: SSOManager, secret_key: str):
        self.app = app
        self.sso_manager = sso_manager
        self.secret_key = secret_key
        self._register_endpoints()

    def _register_endpoints(self):
        """Register SSO endpoints with FastAPI"""

        @self.app.get("/auth/login/{provider}")
        async def initiate_sso_login(provider: str):
            """Initiate SSO login flow"""
            try:
                sso_provider = SSOProvider(provider)
                # Return redirect URL for the SSO provider
                redirect_urls = {
                    SSOProvider.AZURE_AD: f"https://login.microsoftonline.com/{self.sso_manager.config.tenant_id}/oauth2/v2.0/authorize",
                    SSOProvider.GOOGLE_WORKSPACE: "https://accounts.google.com/oauth2/auth",
                    SSOProvider.OKTA: f"https://{self.sso_manager.config.tenant_id}.okta.com/oauth2/default/v1/authorize",
                }

                return {
                    "provider": provider,
                    "redirect_url": redirect_urls.get(sso_provider, ""),
                    "client_id": self.sso_manager.config.client_id,
                    "redirect_uri": self.sso_manager.config.redirect_uri,
                    "scopes": " ".join(self.sso_manager.config.scopes),
                }
            except ValueError:
                return {
                    "error": f"Unsupported SSO provider: {provider}",
                    "status_code": 400,
                }

        @self.app.post("/auth/callback")
        async def handle_sso_callback(request_data: Dict[str, Any]):
            """Handle SSO authentication callback"""
            auth_code = request_data.get("code")
            if not auth_code:
                return {"error": "Authorization code required", "status_code": 400}

            user_info = await self.sso_manager.authenticate(auth_code)
            if not user_info:
                return {"error": "Authentication failed", "status_code": 401}

            # Generate JWT token for the authenticated user
            token = self.sso_manager.generate_jwt_token(user_info, self.secret_key)

            return {
                "token": token,
                "user": {
                    "id": user_info.user_id,
                    "email": user_info.email,
                    "name": user_info.name,
                    "groups": user_info.groups,
                    "roles": user_info.roles,
                    "tenant_id": user_info.tenant_id,
                },
            }

        @self.app.get("/auth/user")
        async def get_current_user(request):
            """Get current authenticated user information"""
            if hasattr(request.state, "user"):
                return {"user": request.state.user}
            return {"error": "Not authenticated", "status_code": 401}

        @self.app.post("/auth/logout")
        async def logout_user():
            """Logout current user (client-side token removal)"""
            return {
                "message": "Logout successful. Please remove the token from client storage."
            }
