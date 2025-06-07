"""
Memorials API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.memorial import MemorialCreate, MemorialUpdate, MemorialResponse, MemorialList
from app.services.memorial_service import MemorialService

router = APIRouter()


@router.get("/", response_model=MemorialList)
async def get_memorials(
    skip: int = Query(0, ge=0, description="Number of memorials to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of memorials to return"),
    search: Optional[str] = Query(None, description="Search in memorial names"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemorialList:
    """
    Retrieve memorials accessible to the current user.
    """
    memorial_service = MemorialService(db)
    
    memorials, total = await memorial_service.get_user_memorials(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
    )
    
    return MemorialList(
        memorials=memorials,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{memorial_id}", response_model=MemorialResponse)
async def get_memorial(
    memorial_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemorialResponse:
    """
    Get a specific memorial by ID.
    """
    memorial_service = MemorialService(db)
    
    memorial = await memorial_service.get_memorial(memorial_id, current_user.id)
    
    if not memorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memorial not found"
        )
    
    return memorial


@router.post("/", response_model=MemorialResponse, status_code=status.HTTP_201_CREATED)
async def create_memorial(
    memorial_data: MemorialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemorialResponse:
    """
    Create a new memorial.
    """
    memorial_service = MemorialService(db)
    
    memorial = await memorial_service.create_memorial(memorial_data, current_user.id)
    
    return memorial


@router.put("/{memorial_id}", response_model=MemorialResponse)
async def update_memorial(
    memorial_id: UUID,
    memorial_data: MemorialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MemorialResponse:
    """
    Update an existing memorial.
    """
    memorial_service = MemorialService(db)
    
    # Verify user has permission to edit this memorial
    if not await memorial_service.can_user_edit_memorial(current_user.id, memorial_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this memorial"
        )
    
    memorial = await memorial_service.update_memorial(memorial_id, memorial_data)
    
    if not memorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memorial not found"
        )
    
    return memorial


@router.delete("/{memorial_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memorial(
    memorial_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a memorial.
    """
    memorial_service = MemorialService(db)
    
    # Verify user has permission to delete this memorial
    if not await memorial_service.can_user_delete_memorial(current_user.id, memorial_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this memorial"
        )
    
    success = await memorial_service.delete_memorial(memorial_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memorial not found"
        ) 