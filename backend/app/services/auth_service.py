"""
Authentication service for Storied Life using OIDC.
"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import AuthentikUserInfo


class AuthService:
    """Authentication service using OIDC providers (Authentik/Cognito)."""

    def __init__(self, db: Session):
        self.db = db

    def create_access_token(self, subject: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    async def get_user_by_external_id(self, external_id: str) -> Optional[User]:
        """Get user by external ID (OIDC sub claim)."""
        return self.db.query(User).filter(User.external_id == external_id).first()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    async def get_or_create_user_from_oidc(self, user_info: AuthentikUserInfo) -> User:
        """Get or create user from OIDC token claims."""
        # First try to find by external_id (OIDC sub claim)
        user = None
        if user_info.external_id:
            user = await self.get_user_by_external_id(user_info.external_id)
        
        # Fallback to email lookup for existing users
        if not user:
            user = await self.get_user_by_email(user_info.email)
        
        if not user:
            # Create new user from OIDC info
            # Extract first name from full name if available
            name_parts = user_info.full_name.split(' ', 1) if user_info.full_name else []
            username = user_info.username or user_info.email.split('@')[0]
            
            db_user = User(
                email=user_info.email,
                username=username,
                full_name=user_info.full_name or f"{name_parts[0] if name_parts else 'User'}",
                role=self._get_user_role(user_info),
                is_active=True,
                email_verified=user_info.email_verified if user_info.email_verified is not None else False,
                external_id=user_info.external_id
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        else:
            # Update existing user info if needed
            updated = False
            
            # Update external_id if not set
            if user_info.external_id and not user.external_id:
                user.external_id = user_info.external_id
                updated = True
            
            # Update full name if different
            if user_info.full_name and user.full_name != user_info.full_name:
                user.full_name = user_info.full_name
                updated = True
            
            # Update role based on groups
            new_role = self._get_user_role(user_info)
            if user.role != new_role:
                user.role = new_role
                updated = True
            
            # Update email verification status
            if user_info.email_verified is not None and user.email_verified != user_info.email_verified:
                user.email_verified = user_info.email_verified
                updated = True
            
            # Update last login
            user.last_login = datetime.utcnow()
            updated = True
            
            if updated:
                self.db.commit()
                self.db.refresh(user)
            
            return user

    def _get_user_role(self, user_info: AuthentikUserInfo) -> UserRole:
        """Determine user role based on OIDC groups."""
        if not user_info.groups:
            return UserRole.USER
        
        # Check for admin groups
        admin_groups = {"storied-life-admins", "administrators", "admins", "authentik Admins"}
        if set(user_info.groups).intersection(admin_groups):
            return UserRole.ADMIN
            
        # Check for moderator groups  
        moderator_groups = {"storied-life-moderators", "moderators"}
        if set(user_info.groups).intersection(moderator_groups):
            return UserRole.MODERATOR
            
        return UserRole.USER 