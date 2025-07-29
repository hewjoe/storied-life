"""
User model for authentication and user management.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.db.session import Base


class UserRole(enum.Enum):
    """User role enumeration matching database enum."""
    USER = "user"
    ADMIN = "admin"  
    MODERATOR = "moderator"


class User(Base):
    """User model for storing user account information.
    
    Designed for OIDC authentication - no password storage required.
    User identity is managed by external OIDC provider (Authentik/Cognito).
    """
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum('user', 'admin', 'moderator', name='user_role'), default='user', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    profile_image_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    external_id = Column(String(255), nullable=True, index=True)  # OIDC sub claim
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"
    
    @property 
    def is_moderator(self) -> bool:
        """Check if user has moderator role."""
        return self.role == "moderator"
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>" 