from pydantic import BaseModel
from datetime import datetime

class ChatCreate(BaseModel):
    title: str = "New Chat"

class ChatUpdate(BaseModel):
    title: str

class ChatResponse(BaseModel):
    id: int
    title: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    # role is NOT accepted from the user
    # user always sends "user" role — AI always responds as "assistant"
    # the API decides the role, not the client

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatWithMessages(BaseModel):
    """Used when fetching a full chat with all its messages"""
    id: int
    title: str
    user_id: int
    created_at: datetime
    messages: list[MessageResponse] = []

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    """
    Returns paginated chat history.
    Useful when a chat has hundreds of messages.
    """
    chat_id: int
    title: str
    messages: list[MessageResponse]
    total_messages: int
    returned_messages: int