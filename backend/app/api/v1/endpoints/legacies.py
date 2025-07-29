"""
Legacies API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.legacy import LegacyCreate, LegacyUpdate, LegacyResponse, LegacyList
from app.services.legacy_service import LegacyService

router = APIRouter()


@router.get("/", response_model=LegacyList)
async def get_legacies(
    skip: int = Query(0, ge=0, description="Number of legacies to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of legacies to return"),
    search: Optional[str] = Query(None, description="Search in legacy names"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LegacyList:
    """
    Retrieve legacies accessible to the current user.
    """
    legacy_service = LegacyService(db)
    
    legacies, total = await legacy_service.get_user_legacies(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
    )
    
    return LegacyList(
        legacies=legacies,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{legacy_id}", response_model=LegacyResponse)
async def get_legacy(
    legacy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LegacyResponse:
    """
    Get a specific legacy by ID.
    """
    legacy_service = LegacyService(db)
    
    legacy = await legacy_service.get_legacy(legacy_id, current_user.id)
    
    if not legacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Legacy not found"
        )
    
    return legacy


@router.post("/", response_model=LegacyResponse, status_code=status.HTTP_201_CREATED)
async def create_legacy(
    legacy_data: LegacyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LegacyResponse:
    """
    Create a new legacy.
    """
    legacy_service = LegacyService(db)
    
    legacy = await legacy_service.create_legacy(legacy_data, current_user.id)
    
    return legacy


@router.put("/{legacy_id}", response_model=LegacyResponse)
async def update_legacy(
    legacy_id: UUID,
    legacy_data: LegacyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LegacyResponse:
    """
    Update an existing legacy.
    """
    legacy_service = LegacyService(db)
    
    # Verify user has permission to edit this legacy
    if not await legacy_service.can_user_edit_legacy(current_user.id, legacy_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this legacy"
        )
    
    legacy = await legacy_service.update_legacy(legacy_id, legacy_data)
    
    if not legacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Legacy not found"
        )
    
    return legacy


@router.delete("/{legacy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_legacy(
    legacy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a legacy.
    """
    legacy_service = LegacyService(db)
    
    # Verify user has permission to delete this legacy
    if not await legacy_service.can_user_delete_legacy(current_user.id, legacy_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this legacy"
        )
    
    success = await legacy_service.delete_legacy(legacy_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Legacy not found"
        ) 