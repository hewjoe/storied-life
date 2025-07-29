"""
Stories API endpoints for managing memories and stories.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.story import Story
from app.schemas.story import StoryCreate, StoryUpdate, StoryResponse, StoryList
from app.services.story_service import StoryService

router = APIRouter()


@router.get("/", response_model=StoryList)
async def get_stories(
    legacy_id: Optional[UUID] = Query(None, description="Filter by legacy ID"),
    skip: int = Query(0, ge=0, description="Number of stories to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of stories to return"),
    search: Optional[str] = Query(None, description="Search in story content"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoryList:
    """
    Retrieve stories with optional filtering and pagination.
    
    - **legacy_id**: Filter stories for a specific legacy
    - **skip**: Number of stories to skip (for pagination)
    - **limit**: Maximum number of stories to return
    - **search**: Search term to filter stories by content
    - **tags**: Filter stories by tags
    """
    story_service = StoryService(db)
    
    stories, total = await story_service.get_stories(
        user_id=current_user.id,
        legacy_id=legacy_id,
        skip=skip,
        limit=limit,
        search=search,
        tags=tags,
    )
    
    return StoryList(
        stories=stories,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoryResponse:
    """
    Get a specific story by ID.
    
    - **story_id**: UUID of the story to retrieve
    """
    story_service = StoryService(db)
    
    story = await story_service.get_story(story_id, current_user.id)
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return story


@router.post("/", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(
    story_data: StoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoryResponse:
    """
    Create a new story.
    
    - **title**: Story title
    - **content**: Story content/text
    - **legacy_id**: ID of the legacy this story belongs to
    - **tags**: Optional list of tags
    - **visibility_level**: Story visibility (public, private, group)
    """
    story_service = StoryService(db)
    
    # Verify user has permission to add stories to this legacy
    if not await story_service.can_user_add_story(current_user.id, story_data.legacy_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add stories to this legacy"
        )
    
    story = await story_service.create_story(story_data, current_user.id)
    
    return story


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: UUID,
    story_data: StoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoryResponse:
    """
    Update an existing story.
    
    - **story_id**: UUID of the story to update
    - **title**: Updated story title
    - **content**: Updated story content
    - **tags**: Updated list of tags
    - **visibility_level**: Updated visibility level
    """
    story_service = StoryService(db)
    
    # Verify user has permission to edit this story
    if not await story_service.can_user_edit_story(current_user.id, story_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this story"
        )
    
    story = await story_service.update_story(story_id, story_data)
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return story


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a story.
    
    - **story_id**: UUID of the story to delete
    """
    story_service = StoryService(db)
    
    # Verify user has permission to delete this story
    if not await story_service.can_user_delete_story(current_user.id, story_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this story"
        )
    
    success = await story_service.delete_story(story_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )


@router.post("/{story_id}/approve", response_model=StoryResponse)
async def approve_story(
    story_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoryResponse:
    """
    Approve a pending story (admin only).
    
    - **story_id**: UUID of the story to approve
    """
    story_service = StoryService(db)
    
    # Verify user is admin for the legacy
    if not await story_service.is_user_legacy_admin(current_user.id, story_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to approve stories"
        )
    
    story = await story_service.approve_story(story_id, current_user.id)
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return story 