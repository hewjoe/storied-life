"""
User service for managing user operations.
"""

from typing import Optional, Tuple, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserResponse


class UserService:
    """Service for user-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user_uuid = UUID(user_id)
            return self.db.query(User).filter(User.id == user_uuid).first()
        except ValueError:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    async def update_user(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        for field, value in user_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def get_users(self, skip: int = 0, limit: int = 20) -> Tuple[List[User], int]:
        """Get users with pagination."""
        query = self.db.query(User)
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    async def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activate a user account."""
        return await self.update_user(user_id, {"is_active": True})
    
    async def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate a user account."""
        return await self.update_user(user_id, {"is_active": False}) 