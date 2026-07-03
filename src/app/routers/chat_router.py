from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import (ChatCreate, ChatUpdate, ChatResponse, ChatHistoryResponse)
from app.services.chat_service import chat_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)

@router.post("/", response_model=ChatResponse, status_code=201)
def create_chat(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return chat_service.create_chat(db, data, current_user)


@router.get("/", response_model=list[ChatResponse])
def get_my_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return chat_service.get_user_chats(db, current_user)


@router.get("/{chat_id}/history", response_model=ChatHistoryResponse)
def get_chat_history(
    chat_id: int,
    limit: int = Query(default=50, le=200),
    # Query() lets us add validation to query params
    # le=200 means limit cannot exceed 200
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns chat with its message history.
    Use ?limit=N to control how many messages to return.
    Example: GET /chats/1/history?limit=20
    """
    return chat_service.get_chat_history(db, chat_id, current_user, limit)


@router.patch("/{chat_id}", response_model=ChatResponse)
def update_chat_title(
    chat_id: int,
    data: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rename a chat"""
    return chat_service.update_chat_title(db, chat_id, data, current_user)


@router.delete("/{chat_id}/history")
def clear_history(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Wipes messages but keeps the chat"""
    return chat_service.clear_chat_history(db, chat_id, current_user)


@router.delete("/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return chat_service.delete_chat(db, chat_id, current_user)