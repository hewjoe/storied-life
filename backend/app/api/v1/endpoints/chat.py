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


@router.post("/{legacy_id}", response_model=ChatResponse)
async def chat_with_legacy(
    legacy_id: UUID,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    Chat with the AI persona of a legacy.
    
    This endpoint allows users to have conversations with an AI representation
    of the person whose legacy is preserved on the platform.
    """
    # Verify user has access to this legacy
    if not await chat_service.can_user_chat_with_legacy(current_user.id, legacy_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to chat with this legacy"
        )
    
    response = await chat_service.send_message(
        legacy_id=legacy_id,
        user_id=current_user.id,
        message=chat_request.message,
        conversation_id=chat_request.conversation_id,
    )
    
    return response


@router.get("/{legacy_id}/history", response_model=ChatConversation)
async def get_chat_history(
    legacy_id: UUID,
    conversation_id: Optional[UUID] = Query(None, description="Specific conversation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatConversation:
    """
    Get chat history for a legacy.
    
    Retrieves the conversation history between the user and the AI persona
    for the specified legacy.
    """
    # Verify user has access to this legacy
    if not await chat_service.can_user_chat_with_legacy(current_user.id, legacy_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view chat history for this legacy"
        )
    
    conversation = await chat_service.get_conversation_history(
        legacy_id=legacy_id,
        user_id=current_user.id,
        conversation_id=conversation_id,
    )
    
    return conversation


@router.delete("/{legacy_id}/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    legacy_id: UUID,
    conversation_id: Optional[UUID] = Query(None, description="Specific conversation ID to clear"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Clear chat history for a legacy.
    
    Clears the conversation history between the user and the AI persona.
    If conversation_id is provided, only that conversation is cleared.
    """
    if not await chat_service.can_user_manage_legacy_chat(current_user.id, legacy_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to clear chat history for this legacy"
        )
    
    await chat_service.clear_conversation_history(
        legacy_id=legacy_id,
        user_id=current_user.id,
        conversation_id=conversation_id,
    ) 