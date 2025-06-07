"""
AI Chat API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.chat import ChatMessage, ChatResponse, ChatConversation
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/{memorial_id}", response_model=ChatResponse)
async def chat_with_memorial(
    memorial_id: UUID,
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    Chat with the AI persona of a memorial.
    """
    chat_service = ChatService(db)
    
    # Verify user has access to this memorial
    if not await chat_service.can_user_chat_with_memorial(current_user.id, memorial_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to chat with this memorial"
        )
    
    response = await chat_service.send_message(
        memorial_id=memorial_id,
        user_id=current_user.id,
        message=message.content
    )
    
    return response


@router.get("/{memorial_id}/history", response_model=ChatConversation)
async def get_chat_history(
    memorial_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatConversation:
    """
    Get chat history for a memorial.
    """
    chat_service = ChatService(db)
    
    # Verify user has access to this memorial
    if not await chat_service.can_user_chat_with_memorial(current_user.id, memorial_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view chat history for this memorial"
        )
    
    conversation = await chat_service.get_conversation_history(
        memorial_id=memorial_id,
        user_id=current_user.id,
        limit=limit
    )
    
    return conversation


@router.delete("/{memorial_id}/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    memorial_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Clear chat history for a memorial.
    """
    chat_service = ChatService(db)
    
    # Verify user has permission to clear chat history
    if not await chat_service.can_user_manage_memorial_chat(current_user.id, memorial_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to clear chat history for this memorial"
        )
    
    await chat_service.clear_conversation_history(
        memorial_id=memorial_id,
        user_id=current_user.id
    ) 