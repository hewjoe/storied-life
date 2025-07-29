"""
Tests for OIDC Authentication service.
Validates configuration, token verification, user synchronization, and provider adapters.
"""

import pytest
import jwt
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import httpx
from sqlalchemy.orm import Session

from app.services.oidc_auth import (
    OIDCAuthenticator, 
    AuthentikAdapter, 
    CognitoAdapter,
    ProviderAdapter
)
from app.models.user import User
from app.core.config import settings


@pytest.mark.unit
@pytest.mark.auth
class TestProviderAdapters:
    """Test provider-specific claim adapters."""
    
    def test_authentik_adapter_user_info(self):
        """Test Authentik user info extraction."""
        adapter = AuthentikAdapter()
        
        # Test with full name
        claims = {
            "email": "test@example.com",
            "name": "John Doe",
            "sub": "auth_user_123"
        }
        
        user_info = adapter.get_user_info(claims)
        assert user_info["email"] == "test@example.com"
        assert user_info["first_name"] == "John"
        assert user_info["last_name"] == "Doe"
        assert user_info["sub"] == "auth_user_123"
    
    def test_authentik_adapter_given_family_names(self):
        """Test Authentik adapter with given_name and family_name."""
        adapter = AuthentikAdapter()
        
        claims = {
            "email": "jane@example.com",
            "given_name": "Jane",
            "family_name": "Smith",
            "sub": "auth_user_456"
        }
        
        user_info = adapter.get_user_info(claims)
        assert user_info["first_name"] == "Jane"
        assert user_info["last_name"] == "Smith"
    
    def test_authentik_adapter_groups_list(self):
        """Test Authentik groups extraction from list."""
        adapter = AuthentikAdapter()
        
        claims = {
            "groups": ["storied-life-admins", "users", "family-members"]
        }
        
        groups = adapter.get_groups(claims)
        assert groups == ["storied-life-admins", "users", "family-members"]
    
    def test_authentik_adapter_groups_string(self):
        """Test Authentik groups extraction from comma-separated string."""
        adapter = AuthentikAdapter()
        
        claims = {
            "groups": "storied-life-admins, users, family-members"
        }
        
        groups = adapter.get_groups(claims)
        assert groups == ["storied-life-admins", "users", "family-members"]
    
    def test_cognito_adapter_user_info(self):
        """Test Cognito user info extraction."""
        adapter = CognitoAdapter()
        
        claims = {
            "email": "cognito@example.com",
            "given_name": "Alice",
            "family_name": "Johnson",
            "sub": "cognito-uuid-789"
        }
        
        user_info = adapter.get_user_info(claims)
        assert user_info["email"] == "cognito@example.com"
        assert user_info["first_name"] == "Alice"
        assert user_info["last_name"] == "Johnson"
        assert user_info["sub"] == "cognito-uuid-789"
    
    def test_cognito_adapter_groups(self):
        """Test Cognito groups extraction."""
        adapter = CognitoAdapter()
        
        claims = {
            "cognito:groups": ["administrators", "premium-users"]
        }
        
        groups = adapter.get_groups(claims)
        assert groups == ["administrators", "premium-users"]
    
    def test_is_admin_detection(self):
        """Test admin role detection across providers."""
        adapter = AuthentikAdapter()
        
        # Test admin groups
        assert adapter.is_admin(["storied-life-admins"]) is True
        assert adapter.is_admin(["administrators"]) is True
        assert adapter.is_admin(["admins"]) is True
        assert adapter.is_admin(["users", "storied-life-admins"]) is True
        
        # Test non-admin groups
        assert adapter.is_admin(["users"]) is False
        assert adapter.is_admin(["guests", "family-members"]) is False
        assert adapter.is_admin([]) is False


@pytest.mark.unit
@pytest.mark.oidc
class TestOIDCAuthenticator:
    """Test OIDC authenticator functionality."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('app.services.oidc_auth.settings') as mock:
            mock.AUTH_PROVIDER = "authentik"
            mock.OIDC_ISSUER_URL = "https://auth.storied-life.me/application/o/storied-life/"
            mock.OIDC_CLIENT_ID = "storied-life-web"
            mock.OIDC_AUDIENCE = "storied-life-api"
            mock.OIDC_SCOPES = "openid profile email"
            mock.OIDC_JWKS_CACHE_TTL = 3600
            yield mock
    
    @pytest.fixture
    def authenticator(self, mock_settings):
        """Create OIDC authenticator for testing."""
        with patch('app.services.oidc_auth.PyJWKClient'):
            return OIDCAuthenticator()
    
    def test_authenticator_initialization_authentik(self, mock_settings):
        """Test authenticator initialization with Authentik provider."""
        with patch('app.services.oidc_auth.PyJWKClient') as mock_jwks:
            authenticator = OIDCAuthenticator()
            
            assert authenticator.provider == "authentik"
            assert isinstance(authenticator.adapter, AuthentikAdapter)
            assert authenticator.issuer_url == "https://auth.storied-life.me/application/o/storied-life/"
            
            # Verify JWKS client initialization
            mock_jwks.assert_called_once()
            args, kwargs = mock_jwks.call_args
            assert kwargs['uri'] == "https://auth.storied-life.me/application/o/storied-life/.well-known/jwks.json"
            assert kwargs['cache_keys'] is True
            assert kwargs['cache_jwks_ttl'] == 3600
    
    def test_authenticator_initialization_cognito(self, mock_settings):
        """Test authenticator initialization with Cognito provider."""
        mock_settings.AUTH_PROVIDER = "cognito"
        
        with patch('app.services.oidc_auth.PyJWKClient'):
            authenticator = OIDCAuthenticator()
            
            assert authenticator.provider == "cognito"
            assert isinstance(authenticator.adapter, CognitoAdapter)
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, authenticator):
        """Test successful token verification."""
        # Mock token and claims
        test_token = "valid.jwt.token"
        expected_claims = {
            "sub": "user123",
            "email": "test@example.com",
            "aud": "storied-life-api",
            "iss": "https://auth.storied-life.me/application/o/storied-life/",
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        }
        
        # Mock JWKS client and JWT decode
        mock_signing_key = Mock()
        mock_signing_key.key = "mock_key"
        authenticator.jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
        
        with patch('app.services.oidc_auth.jwt.decode', return_value=expected_claims):
            claims = await authenticator.verify_token(test_token)
            
            assert claims == expected_claims
            authenticator.jwks_client.get_signing_key_from_jwt.assert_called_once_with(test_token)
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid_audience(self, authenticator):
        """Test token verification with invalid audience."""
        test_token = "invalid.audience.token"
        
        mock_signing_key = Mock()
        mock_signing_key.key = "mock_key"
        authenticator.jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
        
        with patch('app.services.oidc_auth.jwt.decode', side_effect=jwt.InvalidAudienceError("Invalid audience")):
            with pytest.raises(jwt.PyJWTError, match="Token verification failed"):
                await authenticator.verify_token(test_token)
    
    @pytest.mark.asyncio
    async def test_verify_token_wrong_type(self, authenticator):
        """Test token verification with wrong token type."""
        test_token = "id.token.not.access"
        invalid_claims = {
            "sub": "user123",
            "token_use": "id",  # Should be "access"
            "aud": "storied-life-api",
            "iss": "https://auth.storied-life.me/application/o/storied-life/"
        }
        
        mock_signing_key = Mock()
        mock_signing_key.key = "mock_key"
        authenticator.jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
        
        with patch('app.services.oidc_auth.jwt.decode', return_value=invalid_claims):
            with pytest.raises(jwt.PyJWTError, match="Invalid token type"):
                await authenticator.verify_token(test_token)
    
    @pytest.mark.asyncio
    async def test_get_user_from_token_new_user(self, authenticator):
        """Test user creation from token."""
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        
        # Mock token verification
        test_claims = {
            "sub": "new_user_123",
            "email": "newuser@example.com",
            "name": "New User",
            "groups": ["users"]
        }
        
        with patch.object(authenticator, 'verify_token', return_value=test_claims):
            user = await authenticator.get_user_from_token("test_token", mock_db)
            
            # Verify user creation
            assert mock_db.add.called
            assert mock_db.commit.called
            assert mock_db.refresh.called
            
            # Verify user was added with correct data
            added_user = mock_db.add.call_args[0][0]
            assert added_user.email == "newuser@example.com"
            assert added_user.first_name == "New"
            assert added_user.last_name == "User"
            assert added_user.external_id == "new_user_123"
            assert added_user.is_admin is False
            assert added_user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_user_from_token_admin_user(self, authenticator):
        """Test admin user creation from token."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        test_claims = {
            "sub": "admin_user_456",
            "email": "admin@example.com",
            "name": "Admin User",
            "groups": ["storied-life-admins", "users"]
        }
        
        with patch.object(authenticator, 'verify_token', return_value=test_claims):
            await authenticator.get_user_from_token("test_token", mock_db)
            
            added_user = mock_db.add.call_args[0][0]
            assert added_user.is_admin is True
    
    @pytest.mark.asyncio
    async def test_get_user_from_token_existing_user(self, authenticator):
        """Test updating existing user from token."""
        # Create mock existing user
        existing_user = User(
            email="existing@example.com",
            first_name="Old",
            last_name="Name",
            is_admin=False,
            external_id="existing_123"
        )
        
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        test_claims = {
            "sub": "existing_123",
            "email": "existing@example.com",
            "name": "Updated Name",
            "groups": ["storied-life-admins"]  # Now admin
        }
        
        with patch.object(authenticator, 'verify_token', return_value=test_claims):
            user = await authenticator.get_user_from_token("test_token", mock_db)
            
            # Verify user updates
            assert user.first_name == "Updated"
            assert user.last_name == "Name"
            assert user.is_admin is True
            assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_get_oidc_config(self, authenticator):
        """Test OIDC configuration generation."""
        with patch.dict('os.environ', {'FRONTEND_URL': 'https://storied-life.me'}):
            config = await authenticator.get_oidc_config()
            
            expected_config = {
                "issuer": "https://auth.storied-life.me/application/o/storied-life/",
                "clientId": "storied-life-web",
                "redirectUri": "https://storied-life.me/login/callback",
                "scopes": ["openid", "profile", "email"],
                "responseType": "code",
                "usePKCE": True,
                "provider": "authentik"
            }
            
            assert config == expected_config
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_success(self, authenticator):
        """Test successful authorization code exchange."""
        # Mock successful token response
        mock_token_response = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_456",
            "id_token": "id_token_789",
            "expires_in": 3600
        }
        
        test_claims = {
            "sub": "user123",
            "email": "test@example.com"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_token_response
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            with patch.object(authenticator, 'verify_token', return_value=test_claims):
                result = await authenticator.exchange_code_for_tokens(
                    code="auth_code_123",
                    state="state_456",
                    code_verifier="verifier_789"
                )
                
                assert result["access_token"] == "access_token_123"
                assert result["refresh_token"] == "refresh_token_456"
                assert result["expires_in"] == 3600
                assert result["claims"] == test_claims
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_failure(self, authenticator):
        """Test failed authorization code exchange."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Invalid authorization code"
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            with pytest.raises(Exception, match="Token exchange failed"):
                await authenticator.exchange_code_for_tokens(
                    code="invalid_code",
                    state="state",
                    code_verifier="verifier"
                )


@pytest.mark.integration
@pytest.mark.config
@pytest.mark.slow
class TestConfigurationValidation:
    """Test OIDC configuration validation."""
    
    @pytest.mark.asyncio
    async def test_issuer_accessibility(self):
        """Test that OIDC issuer is accessible."""
        issuer_url = settings.OIDC_ISSUER_URL
        
        async with httpx.AsyncClient() as client:
            try:
                # Test well-known endpoint
                response = await client.get(f"{issuer_url.rstrip('/')}/.well-known/openid-configuration")
                assert response.status_code == 200
                
                config = response.json()
                assert "issuer" in config
                assert "authorization_endpoint" in config
                assert "token_endpoint" in config
                assert "jwks_uri" in config
                
            except httpx.RequestError:
                pytest.skip("OIDC issuer not accessible - check configuration")
    
    @pytest.mark.asyncio
    async def test_jwks_endpoint_accessibility(self):
        """Test that JWKS endpoint is accessible."""
        issuer_url = settings.OIDC_ISSUER_URL
        jwks_url = f"{issuer_url.rstrip('/')}/.well-known/jwks.json"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(jwks_url)
                assert response.status_code == 200
                
                jwks = response.json()
                assert "keys" in jwks
                assert len(jwks["keys"]) > 0
                
                # Validate key structure
                key = jwks["keys"][0]
                assert "kty" in key  # Key type
                assert "use" in key or "key_ops" in key  # Key usage
                assert "kid" in key  # Key ID
                
            except httpx.RequestError:
                pytest.skip("JWKS endpoint not accessible - check configuration")
    
    def test_required_environment_variables(self):
        """Test that all required environment variables are set."""
        required_vars = [
            'AUTH_PROVIDER',
            'OIDC_ISSUER_URL',
            'OIDC_CLIENT_ID',
            'OIDC_AUDIENCE'
        ]
        
        for var in required_vars:
            value = getattr(settings, var, None)
            assert value is not None, f"Required environment variable {var} is not set"
            assert value.strip() != "", f"Required environment variable {var} is empty"
    
    def test_provider_specific_configuration(self):
        """Test provider-specific configuration."""
        if settings.AUTH_PROVIDER == "cognito":
            assert settings.COGNITO_USER_POOL_ID is not None
            assert settings.COGNITO_REGION is not None
        elif settings.AUTH_PROVIDER == "authentik":
            assert settings.AUTHENTIK_HOST is not None
    
    def test_urls_are_valid(self):
        """Test that configured URLs are valid."""
        import urllib.parse
        
        # Test issuer URL
        parsed = urllib.parse.urlparse(settings.OIDC_ISSUER_URL)
        assert parsed.scheme in ['http', 'https']
        assert parsed.netloc != ""
        
        # For production, should be HTTPS
        if settings.AUTH_PROVIDER == "cognito":
            assert parsed.scheme == "https", "Cognito requires HTTPS"


# Pytest fixtures for integration tests
@pytest.fixture
def db_session():
    """Mock database session for testing."""
    return Mock(spec=Session)


@pytest.fixture
def sample_authentik_token():
    """Sample Authentik JWT token for testing."""
    # This would be a real token in integration tests
    # For unit tests, we mock the verification
    return "mock.jwt.token"


@pytest.fixture
def sample_cognito_token():
    """Sample Cognito JWT token for testing."""
    return "mock.cognito.token"


# Test data for provider-specific testing
AUTHENTIK_TEST_CLAIMS = {
    "sub": "ak_user_123",
    "email": "authentik@example.com",
    "name": "Authentik User",
    "groups": ["storied-life-admins", "users"],
    "aud": "storied-life-api",
    "iss": "https://auth.storied-life.me/application/o/storied-life/",
    "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
}

COGNITO_TEST_CLAIMS = {
    "sub": "cognito-uuid-456",
    "email": "cognito@example.com",
    "given_name": "Cognito",
    "family_name": "User",
    "cognito:groups": ["administrators"],
    "aud": "storied-life-api",
    "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_ABCDEF123",
    "token_use": "access",
    "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
} 