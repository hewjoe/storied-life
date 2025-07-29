"""
API Dependencies for database connections, authentication, etc.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jwt import PyJWTError

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.oidc_auth import OIDCAuthenticator
from app.schemas.auth import AuthentikUserInfo

# Security scheme for JWT tokens (fallback)
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_oidc_authenticator() -> OIDCAuthenticator:
    """Get OIDC authenticator instance."""
    return OIDCAuthenticator()


def get_user_from_authentik_headers(request: Request) -> Optional[AuthentikUserInfo]:
    """
    LEGACY: Extract user information from Authentik forward-auth headers.
    
    This is kept for backwards compatibility during migration.
    Will be removed once OIDC migration is complete.
    """
    headers = request.headers
    
    # Check if we have the required Authentik headers
    email = headers.get("X-authentik-email")
    if not email:
        return None
    
    # Parse groups from header (comma-separated string)
    groups_header = headers.get("X-authentik-groups", "")
    groups = [g.strip() for g in groups_header.split(",") if g.strip()] if groups_header else []
    
    return AuthentikUserInfo(
        email=email,
        full_name=headers.get("X-authentik-name"),  # Authentik sends full name
        username=headers.get("X-authentik-username"),
        groups=groups,
        # For backward compatibility, split full name into first/last
        first_name=headers.get("X-authentik-name", "").split(' ', 1)[0] if headers.get("X-authentik-name") else None,
        last_name=headers.get("X-authentik-name", "").split(' ', 1)[1] if headers.get("X-authentik-name") and ' ' in headers.get("X-authentik-name") else None
    )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Optional[User]:
    """
    Get the current authenticated user.
    
    Authentication priority:
    1. OIDC access token from cookie (web clients)
    2. OIDC access token from Authorization header (API clients)
    3. Legacy JWT token (backwards compatibility)
    4. Legacy Authentik headers (backwards compatibility)
    
    Args:
        request: FastAPI request object
        credentials: Optional JWT token from Authorization header
        access_token: Optional OIDC token from secure cookie
        db: Database session
        oidc_auth: OIDC authenticator service
    
    Returns:
        User: Current authenticated user or None for anonymous access
    """
    
    # Try OIDC access token from cookie first (web clients)
    if access_token:
        try:
            user = await oidc_auth.get_user_from_token(access_token, db)
            return user
        except PyJWTError:
            # Invalid token, continue to other methods
            pass
    
    # Try OIDC access token from Authorization header (API clients)
    if credentials and credentials.scheme.lower() == "bearer":
        try:
            user = await oidc_auth.get_user_from_token(credentials.credentials, db)
            return user
        except PyJWTError:
            # Not an OIDC token, try legacy JWT
            pass
    
    # Legacy: Try JWT token authentication (backwards compatibility)
    if credentials:
        try:
            from jose import jwt
            payload = jwt.decode(
                credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id:
                auth_service = AuthService(db)
                user = await auth_service.get_user_by_id(user_id)
                return user
        except Exception:
            pass
    
    # Legacy: Try Authentik forward-auth headers (backwards compatibility)
    authentik_user_info = get_user_from_authentik_headers(request)
    if authentik_user_info:
        auth_service = AuthService(db)
        user = await auth_service.get_or_create_user_from_oidc(authentik_user_info)
        return user
    
    # Return None for anonymous access (some endpoints allow this)
    return None


async def require_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Require an authenticated user, raising an exception if none is found.
    
    Args:
        current_user: Current user from get_current_user dependency
    
    Returns:
        User: Authenticated user
    
    Raises:
        HTTPException: If no authenticated user is found
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def require_admin_user(
    current_user: User = Depends(require_authenticated_user)
) -> User:
    """
    Require an admin user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User: Admin user
    
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Optional[User]:
    """
    Get the current user but don't require authentication.
    
    This is useful for endpoints that show different content for
    authenticated vs anonymous users.
    """
    return await get_current_user(request, credentials, access_token, db, oidc_auth) 