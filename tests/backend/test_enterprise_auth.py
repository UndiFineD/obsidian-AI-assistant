# tests/backend/test_enterprise_auth.py
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import jwt
import pytest

# Add the backend to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.enterprise_auth import (
    EnterpriseAuthMiddleware,
    SSOConfig,
    SSOManager,
    SSOProvider,
    UserInfo,
)


class TestSSOConfig:
    """Test suite for SSO configuration."""

    def test_sso_config_creation(self):
        """Test basic SSO config creation."""
        config = SSOConfig(
            provider=SSOProvider.AZURE_AD,
            client_id="test_client_id",
            client_secret="test_client_secret",
            tenant_id="test_tenant_id"
        )

        assert config.provider == SSOProvider.AZURE_AD
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.tenant_id == "test_tenant_id"
        assert config.redirect_uri == "http://localhost:8000/auth/callback"
        assert config.scopes == ["openid", "email", "profile"]

    def test_sso_config_custom_redirect_uri(self):
        """Test SSO config with custom redirect URI."""
        custom_uri = "https://enterprise.com/auth/callback"
        config = SSOConfig(
            provider=SSOProvider.GOOGLE_WORKSPACE,
            client_id="google_client",
            client_secret="google_secret",
            redirect_uri=custom_uri
        )

        assert config.redirect_uri == custom_uri

    def test_sso_config_custom_scopes(self):
        """Test SSO config with custom scopes."""
        custom_scopes = ["openid", "email", "profile", "groups"]
        config = SSOConfig(
            provider=SSOProvider.OKTA,
            client_id="okta_client",
            client_secret="okta_secret",
            scopes=custom_scopes
        )

        assert config.scopes == custom_scopes

    def test_sso_config_default_scopes_post_init(self):
        """Test that default scopes are set in post_init."""
        config = SSOConfig(
            provider=SSOProvider.SAML,
            client_id="saml_client",
            client_secret="saml_secret",
            scopes=None  # Explicitly set to None
        )

        assert config.scopes == ["openid", "email", "profile"]


class TestUserInfo:
    """Test suite for UserInfo data class."""

    def test_user_info_creation(self):
        """Test basic UserInfo creation."""
        user = UserInfo(
            user_id="test_user_123",
            email="test@example.com",
            name="Test User",
            groups=["Engineering", "AI-Users"]
        )

        assert user.user_id == "test_user_123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.groups == ["Engineering", "AI-Users"]
        assert user.tenant_id is None
        assert user.roles == ["user"]  # Default role

    def test_user_info_with_custom_roles(self):
        """Test UserInfo with custom roles."""
        custom_roles = ["admin", "power_user"]
        user = UserInfo(
            user_id="admin_user_456",
            email="admin@example.com",
            name="Admin User",
            groups=["Admins"],
            roles=custom_roles
        )

        assert user.roles == custom_roles

    def test_user_info_with_tenant(self):
        """Test UserInfo with tenant ID."""
        user = UserInfo(
            user_id="tenant_user_789",
            email="user@tenant.com",
            name="Tenant User",
            groups=["Tenant-A"],
            tenant_id="tenant_123"
        )

        assert user.tenant_id == "tenant_123"

    def test_user_info_default_roles_post_init(self):
        """Test that default roles are set in post_init."""
        user = UserInfo(
            user_id="default_user",
            email="default@example.com",
            name="Default User",
            groups=["Users"],
            roles=None  # Explicitly set to None
        )

        assert user.roles == ["user"]


class TestSSOManager:
    """Test suite for SSO Manager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SSOConfig(
            provider=SSOProvider.AZURE_AD,
            client_id="test_client",
            client_secret="test_secret",
            tenant_id="test_tenant"
        )
        self.sso_manager = SSOManager(self.config)

    @pytest.mark.asyncio
    async def test_sso_manager_initialization(self):
        """Test SSO Manager initialization."""
        assert self.sso_manager.config == self.config
        assert len(self.sso_manager.provider_handlers) == 5
        assert SSOProvider.AZURE_AD in self.sso_manager.provider_handlers

    @pytest.mark.asyncio
    async def test_authenticate_azure_ad_success(self):
        """Test successful Azure AD authentication."""
        auth_code = "test_auth_code_123"

        with patch.object(self.sso_manager, '_handle_azure_ad') as mock_handler:
            mock_user = UserInfo(
                user_id="azure_123",
                email="user@azure.com",
                name="Azure User",
                groups=["Engineers"]
            )
            mock_handler.return_value = mock_user

            result = await self.sso_manager.authenticate(auth_code)

            assert result == mock_user
            mock_handler.assert_called_once_with(auth_code)

    @pytest.mark.asyncio
    async def test_authenticate_google_workspace_success(self):
        """Test successful Google Workspace authentication."""
        config = SSOConfig(
            provider=SSOProvider.GOOGLE_WORKSPACE,
            client_id="google_client",
            client_secret="google_secret"
        )
        sso_manager = SSOManager(config)
        auth_code = "google_auth_code"

        result = await sso_manager.authenticate(auth_code)

        assert result is not None
        assert result.user_id == "google_user_456"
        assert result.email == "user@company.com"
        assert result.name == "Google User"

    @pytest.mark.asyncio
    async def test_authenticate_okta_success(self):
        """Test successful Okta authentication."""
        config = SSOConfig(
            provider=SSOProvider.OKTA,
            client_id="okta_client",
            client_secret="okta_secret"
        )
        sso_manager = SSOManager(config)
        auth_code = "okta_auth_code"

        result = await sso_manager.authenticate(auth_code)

        assert result is not None
        assert result.user_id == "okta_user_789"
        assert result.email == "user@okta-org.com"
        assert "advanced" in result.roles

    @pytest.mark.asyncio
    async def test_authenticate_saml_success(self):
        """Test successful SAML authentication."""
        config = SSOConfig(
            provider=SSOProvider.SAML,
            client_id="saml_client",
            client_secret="saml_secret"
        )
        sso_manager = SSOManager(config)
        auth_code = "saml_auth_code"

        result = await sso_manager.authenticate(auth_code)

        assert result is not None
        assert result.user_id == "saml_user_101"
        assert result.email == "user@saml-org.com"

    @pytest.mark.asyncio
    async def test_authenticate_ldap_success(self):
        """Test successful LDAP authentication."""
        config = SSOConfig(
            provider=SSOProvider.LDAP,
            client_id="ldap_client",
            client_secret="ldap_secret"
        )
        sso_manager = SSOManager(config)
        auth_code = "ldap_auth_code"

        result = await sso_manager.authenticate(auth_code)

        assert result is not None
        assert result.user_id == "ldap_user_202"
        assert result.email == "user@ldap-org.com"

    @pytest.mark.asyncio
    async def test_authenticate_unsupported_provider(self):
        """Test authentication with unsupported provider."""
        # Create a config with an invalid provider (mock it)
        with patch.object(self.sso_manager.config, 'provider', 'invalid_provider'):
            with patch.object(
                self.sso_manager.provider_handlers, 'get', return_value=None
            ):
                result = await self.sso_manager.authenticate("auth_code")
                assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_handler_exception(self):
        """Test authentication when handler raises exception."""
        auth_code = "test_code"

        with patch.object(self.sso_manager, '_handle_azure_ad') as mock_handler:
            mock_handler.side_effect = Exception("Handler error")

            result = await self.sso_manager.authenticate(auth_code)

            assert result is None

    def test_generate_jwt_token(self):
        """Test JWT token generation."""
        user_info = UserInfo(
            user_id="jwt_user_123",
            email="jwt@example.com",
            name="JWT User",
            groups=["JWT-Group"],
            roles=["jwt_role"],
            tenant_id="jwt_tenant"
        )
        secret_key = "test_secret_key_123"

        token = self.sso_manager.generate_jwt_token(user_info, secret_key)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode token to verify contents
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        assert decoded["user_id"] == user_info.user_id
        assert decoded["email"] == user_info.email
        assert decoded["name"] == user_info.name
        assert decoded["groups"] == user_info.groups
        assert decoded["roles"] == user_info.roles
        assert decoded["tenant_id"] == user_info.tenant_id
        assert decoded["iss"] == "obsidian-ai-assistant"

    def test_generate_jwt_token_custom_expiry(self):
        """Test JWT token generation with custom expiry."""
        user_info = UserInfo(
            user_id="exp_user",
            email="exp@example.com",
            name="Expiry User",
            groups=["Expiry"]
        )
        secret_key = "expiry_secret"
        custom_expiry = 48  # 48 hours

        token = self.sso_manager.generate_jwt_token(
            user_info, secret_key, expiry_hours=custom_expiry
        )

        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        exp_time = datetime.fromtimestamp(decoded["exp"])
        iat_time = datetime.fromtimestamp(decoded["iat"])

        # Check that expiry is approximately 48 hours from issue time
        time_diff = exp_time - iat_time
        # Within 1 minute tolerance
        assert abs(time_diff.total_seconds() - (custom_expiry * 3600)) < 60

    def test_validate_jwt_token_valid(self):
        """Test JWT token validation with valid token."""
        user_info = UserInfo(
            user_id="valid_user",
            email="valid@example.com",
            name="Valid User",
            groups=["Valid"]
        )
        secret_key = "validation_secret"

        token = self.sso_manager.generate_jwt_token(user_info, secret_key)
        result = self.sso_manager.validate_jwt_token(token, secret_key)

        assert result is not None
        assert result["user_id"] == user_info.user_id
        assert result["email"] == user_info.email

    def test_validate_jwt_token_invalid_secret(self):
        """Test JWT token validation with invalid secret."""
        user_info = UserInfo(
            user_id="invalid_secret_user",
            email="invalid@example.com",
            name="Invalid Secret User",
            groups=["Invalid"]
        )
        correct_secret = "correct_secret"
        wrong_secret = "wrong_secret"

        token = self.sso_manager.generate_jwt_token(user_info, correct_secret)
        result = self.sso_manager.validate_jwt_token(token, wrong_secret)

        assert result is None

    def test_validate_jwt_token_expired(self):
        """Test JWT token validation with expired token."""
        user_info = UserInfo(
            user_id="expired_user",
            email="expired@example.com",
            name="Expired User",
            groups=["Expired"]
        )
        secret_key = "expired_secret"

        # Create token that expires immediately
        token = self.sso_manager.generate_jwt_token(
            user_info, secret_key, expiry_hours=-1
        )
        result = self.sso_manager.validate_jwt_token(token, secret_key)

        assert result is None

    def test_validate_jwt_token_malformed(self):
        """Test JWT token validation with malformed token."""
        secret_key = "malformed_secret"
        malformed_token = "this.is.not.a.valid.jwt.token"

        result = self.sso_manager.validate_jwt_token(malformed_token, secret_key)

        assert result is None


class TestEnterpriseAuthMiddleware:
    """Test suite for Enterprise Auth Middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        config = SSOConfig(
            provider=SSOProvider.AZURE_AD,
            client_id="middleware_client",
            client_secret="middleware_secret"
        )
        sso_manager = SSOManager(config)
        self.secret_key = "middleware_secret_key"
        self.middleware = EnterpriseAuthMiddleware(sso_manager, self.secret_key)

    def test_middleware_initialization(self):
        """Test middleware initialization."""
        assert self.middleware.sso_manager is not None
        assert self.middleware.secret_key == self.secret_key
        assert len(self.middleware.public_endpoints) > 0
        assert "/health" in self.middleware.public_endpoints
        assert "/auth/login" in self.middleware.public_endpoints

    @pytest.mark.asyncio
    async def test_middleware_public_endpoint_bypass(self):
        """Test that public endpoints bypass authentication."""
        mock_request = Mock()
        mock_request.url.path = "/health"

        mock_call_next = AsyncMock(return_value="success")

        result = await self.middleware(mock_request, mock_call_next)

        assert result == "success"
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_middleware_missing_auth_header(self):
        """Test middleware with missing Authorization header."""
        mock_request = Mock()
        mock_request.url.path = "/api/protected"
        mock_request.headers.get.return_value = None

        mock_call_next = AsyncMock()

        result = await self.middleware(mock_request, mock_call_next)

        assert result["error"] == "Authentication required"
        assert result["status_code"] == 401
        mock_call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_middleware_invalid_auth_header_format(self):
        """Test middleware with invalid Authorization header format."""
        mock_request = Mock()
        mock_request.url.path = "/api/protected"
        mock_request.headers.get.return_value = "InvalidFormat token"

        mock_call_next = AsyncMock()

        result = await self.middleware(mock_request, mock_call_next)

        assert result["error"] == "Authentication required"
        assert result["status_code"] == 401

    def test_all_sso_providers_available(self):
        """Test that all SSO providers are available."""
        expected_providers = {
            SSOProvider.AZURE_AD,
            SSOProvider.GOOGLE_WORKSPACE,
            SSOProvider.OKTA,
            SSOProvider.SAML,
            SSOProvider.LDAP
        }

        available_providers = set(SSOProvider)

        assert available_providers == expected_providers


class TestSSOProviderHandlers:
    """Test suite for individual SSO provider handlers."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SSOConfig(
            provider=SSOProvider.AZURE_AD,
            client_id="handler_client",
            client_secret="handler_secret",
            tenant_id="handler_tenant"
        )
        self.sso_manager = SSOManager(self.config)

    @pytest.mark.asyncio
    async def test_azure_ad_handler_returns_correct_user_info(self):
        """Test Azure AD handler returns correctly formatted UserInfo."""
        auth_code = "azure_test_code"

        result = await self.sso_manager._handle_azure_ad(auth_code)

        assert isinstance(result, UserInfo)
        assert result.user_id == "azure_user_123"
        assert result.email == "user@enterprise.com"
        assert result.tenant_id == self.config.tenant_id
        assert "Engineers" in result.groups
        assert "ai_access" in result.roles

    @pytest.mark.asyncio
    async def test_google_workspace_handler_returns_correct_user_info(self):
        """Test Google Workspace handler returns correctly formatted UserInfo."""
        auth_code = "google_test_code"

        result = await self.sso_manager._handle_google_workspace(auth_code)

        assert isinstance(result, UserInfo)
        assert result.user_id == "google_user_456"
        assert result.email.endswith("@company.com")
        assert "Employees" in result.groups

    @pytest.mark.asyncio
    async def test_all_handlers_return_user_info_objects(self):
        """Test that all SSO handlers return UserInfo objects."""
        handlers = [
            self.sso_manager._handle_azure_ad,
            self.sso_manager._handle_google_workspace,
            self.sso_manager._handle_okta,
            self.sso_manager._handle_saml,
            self.sso_manager._handle_ldap,
        ]

        for handler in handlers:
            result = await handler("test_code")
            assert isinstance(result, UserInfo)
            assert result.user_id is not None
            assert result.email is not None
            assert result.name is not None
            assert isinstance(result.groups, list)
            assert isinstance(result.roles, list)


if __name__ == "__main__":
    pytest.main([__file__])
