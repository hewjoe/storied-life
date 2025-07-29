"""
User schemas for Storied Life OIDC.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID
from enum import Enum


class UserRoleEnum(str, Enum):
    """User role enumeration for API responses."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    full_name: str
    is_active: bool = True
    email_verified: bool = False


class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    role: str  # Changed from enum to string to match database
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    # Computed properties for backward compatibility
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"
    
    @property
    def is_moderator(self) -> bool:
        """Check if user has moderator role."""
        return self.role == "moderator"
    
    @property
    def first_name(self) -> Optional[str]:
        """Extract first name from full name for backward compatibility."""
        if not self.full_name:
            return None
        parts = self.full_name.split(' ', 1)
        return parts[0] if parts else None
    
    @property
    def last_name(self) -> Optional[str]:
        """Extract last name from full name for backward compatibility."""
        if not self.full_name:
            return None
        parts = self.full_name.split(' ', 1)
        return parts[1] if len(parts) > 1 else None

    class Config:
        from_attributes = True
        use_enum_values = True


class UserProfile(UserResponse):
    """Extended user profile schema."""
    pass


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = None 