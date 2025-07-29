"""
OIDC Authentication service for Storied Life.
Supports both Authentik (development) and AWS Cognito (production).
"""

import os
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
import jwt
from jwt import PyJWKClient, PyJWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserResponse


class ProviderAdapter:
    """Base class for provider-specific claim adapters."""
    
    def get_user_info(self, claims: Dict[str, Any]) -> Dict[str, str]:
        """Extract user information from JWT claims."""
        raise NotImplementedError
    
    def get_groups(self, claims: Dict[str, Any]) -> List[str]:
        """Extract user groups from JWT claims."""
        raise NotImplementedError
    
    def is_admin(self, groups: List[str]) -> bool:
        """Determine if user has admin privileges."""
        admin_groups = {"storied-life-admins", "administrators", "admins"}
        return bool(set(groups).intersection(admin_groups))


class AuthentikAdapter(ProviderAdapter):
    """Adapter for Authentik OIDC provider."""
    
    def get_user_info(self, claims: Dict[str, Any]) -> Dict[str, str]:
        """Extract user info from Authentik claims."""
        # Authentik provides name as a single field, try to split it
        full_name = claims.get("name", "")
        name_parts = full_name.split(" ", 1) if full_name else ["", ""]
        
        return {
            "email": claims.get("email", ""),
            "first_name": name_parts[0] if len(name_parts) > 0 else claims.get("given_name", ""),
            "last_name": name_parts[1] if len(name_parts) > 1 else claims.get("family_name", ""),
            "sub": claims.get("sub", ""),
        }
    
    def get_groups(self, claims: Dict[str, Any]) -> List[str]:
        """Extract groups from Authentik claims."""
        groups = claims.get("groups", [])
        if isinstance(groups, str):
            # Handle comma-separated groups
            return [g.strip() for g in groups.split(",") if g.strip()]
        return groups if isinstance(groups, list) else []


class CognitoAdapter(ProviderAdapter):
    """Adapter for AWS Cognito OIDC provider."""
    
    def get_user_info(self, claims: Dict[str, Any]) -> Dict[str, str]:
        """Extract user info from Cognito claims."""
        return {
            "email": claims.get("email", ""),
            "first_name": claims.get("given_name", ""),
            "last_name": claims.get("family_name", ""),
            "sub": claims.get("sub", ""),
        }
    
    def get_groups(self, claims: Dict[str, Any]) -> List[str]:
        """Extract groups from Cognito claims."""
        # Cognito stores groups in cognito:groups claim
        groups = claims.get("cognito:groups", [])
        return groups if isinstance(groups, list) else []


class OIDCAuthenticator:
    """OIDC authentication service with provider abstraction."""
    
    def __init__(self):
        self.provider = settings.AUTH_PROVIDER
        self.issuer_url = settings.OIDC_ISSUER_URL
        self.client_id = settings.OIDC_CLIENT_ID
        self.audience = settings.OIDC_AUDIENCE
        
        # Initialize JWKS client using discovery document
        discovery_url = f"{self.issuer_url.rstrip('/')}/.well-known/openid-configuration"
        
        # For development, we can hardcode the JWKS URI if discovery fails
        # In production, we should always use discovery
        try:
            import requests
            response = requests.get(discovery_url, timeout=10)
            response.raise_for_status()
            discovery_doc = response.json()
            jwks_uri = discovery_doc.get("jwks_uri")
            if not jwks_uri:
                raise ValueError("No jwks_uri in discovery document")
        except Exception as e:
            # Fallback to standard path for development
            print(f"WARNING: OIDC discovery failed ({e}), using fallback JWKS URI")
            jwks_uri = f"{self.issuer_url.rstrip('/')}/jwks/"
        
        self.jwks_client = PyJWKClient(
            uri=jwks_uri,
            cache_keys=True,
            max_cached_keys=50
        )
        
        # Initialize provider adapter
        if self.provider == "cognito":
            self.adapter = CognitoAdapter()
        else:  # default to authentik
            self.adapter = AuthentikAdapter()
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token against provider's JWKS.
        
        Args:
            token: JWT access token
            
        Returns:
            Dict containing verified claims
            
        Raises:
            PyJWTError: If token is invalid
        """
        try:
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # For Authentik, the audience is typically the client ID
            # We'll accept either the configured audience or the client ID
            expected_audiences = [self.audience, self.client_id]
            
            # Verify token - try with different audience values
            claims = None
            verification_error = None
            
            for aud in expected_audiences:
                try:
                    claims = jwt.decode(
                        token,
                        signing_key.key,
                        algorithms=["RS256", "ES256"],
                        audience=aud,
                        issuer=self.issuer_url
                    )
                    break  # Success, stop trying
                except PyJWTError as e:
                    verification_error = e
                    continue  # Try next audience
            
            if claims is None:
                raise verification_error or PyJWTError("No valid audience found")
            
            # Additional validation
            if claims.get("token_use") and claims.get("token_use") != "access":
                raise PyJWTError("Invalid token type")
                
            return claims
            
        except PyJWTError as e:
            raise PyJWTError(f"Token verification failed: {str(e)}")
    
    async def get_user_from_token(self, token: str, db: Session) -> User:
        """
        Extract user from JWT token and sync to database.
        
        Args:
            token: JWT access token
            db: Database session
            
        Returns:
            User: Synchronized user object
        """
        # Verify token and get claims
        claims = await self.verify_token(token)
        
        # Extract user info using provider adapter
        user_info = self.adapter.get_user_info(claims)
        groups = self.adapter.get_groups(claims)
        is_admin = self.adapter.is_admin(groups)
        
        # Get or create user
        user = db.query(User).filter(User.email == user_info["email"]).first()
        
        if not user:
            # Create new user - combine first and last name for full_name
            full_name = f"{user_info['first_name']} {user_info['last_name']}".strip()
            if not full_name:
                full_name = user_info["email"].split("@")[0]  # Fallback to email username
            
            # Generate username from email if not available
            username = user_info["email"].split("@")[0]
            
            user = User(
                email=user_info["email"],
                username=username,
                full_name=full_name,
                role="admin" if is_admin else "user",
                is_active=True,
                external_id=user_info["sub"]  # Store OIDC sub claim
            )
            db.add(user)
        else:
            # Update existing user
            updated = False
            
            # Update full name if first_name or last_name changed
            new_full_name = f"{user_info['first_name']} {user_info['last_name']}".strip()
            if new_full_name and user.full_name != new_full_name:
                user.full_name = new_full_name
                updated = True
                
            # Update role based on admin status
            new_role = "admin" if is_admin else "user"
            if user.role != new_role:
                user.role = new_role
                updated = True
                
            if not user.external_id and user_info["sub"]:
                user.external_id = user_info["sub"]
                updated = True
        
        db.commit()
        db.refresh(user)
        return user
    
    async def get_oidc_config(self) -> Dict[str, Any]:
        """
        Get OIDC configuration for frontend.
        
        Returns:
            Dict containing OIDC configuration
        """
        # Determine redirect URI based on environment
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        return {
            "issuer": self.issuer_url,
            "clientId": self.client_id,
            "redirectUri": f"{base_url}/login/callback",
            "scopes": settings.OIDC_SCOPES.split(),
            "responseType": "code",
            "usePKCE": True,
            "provider": self.provider
        }
    
    async def exchange_code_for_tokens(self, code: str, state: str, code_verifier: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from OIDC callback
            state: State parameter for CSRF protection
            code_verifier: PKCE code verifier
            
        Returns:
            Dict containing tokens and user info
        """
        token_endpoint = f"{self.issuer_url.rstrip('/')}/token"
        redirect_uri = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/login/callback"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier
        }
        
        # Add client secret if configured (for confidential clients)
        if settings.OIDC_CLIENT_SECRET:
            data["client_secret"] = settings.OIDC_CLIENT_SECRET
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            tokens = response.json()
            
            # Verify access token
            access_token = tokens.get("access_token")
            if not access_token:
                raise Exception("No access token received")
            
            # Get user claims from token
            claims = await self.verify_token(access_token)
            
            return {
                "access_token": access_token,
                "refresh_token": tokens.get("refresh_token"),
                "id_token": tokens.get("id_token"),
                "expires_in": tokens.get("expires_in", 3600),
                "claims": claims
            } 