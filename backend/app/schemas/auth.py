"""
Authentication schemas for Storied Life OIDC.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema for JWT payload."""
    email: Optional[str] = None
    user_id: Optional[str] = None
    external_id: Optional[str] = None  # OIDC sub claim


class OIDCConfig(BaseModel):
    """OIDC configuration response."""
    issuer: str
    client_id: str
    redirect_uri: str
    scopes: list[str]
    response_type: str = "code"
    code_challenge_method: str = "S256"


class AuthCallbackRequest(BaseModel):
    """OIDC callback request schema."""
    code: str
    state: str
    code_verifier: str


class AuthentikUserInfo(BaseModel):
    """Schema for user information from OIDC token claims."""
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    external_id: Optional[str] = None  # OIDC sub claim
    email_verified: Optional[bool] = None
    groups: Optional[list[str]] = None
    
    # Legacy fields for backward compatibility during transition
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-generate full_name from first_name + last_name if needed
        if not self.full_name and (self.first_name or self.last_name):
            parts = []
            if self.first_name:
                parts.append(self.first_name)
            if self.last_name:
                parts.append(self.last_name)
            self.full_name = " ".join(parts)


class AuthStatus(BaseModel):
    """Authentication status response."""
    authenticated: bool
    user: Optional[dict] = None
    auth_method: Optional[str] = None
    provider: str
    oidc_enabled: bool = True
    legacy_authentik_headers: bool = False 