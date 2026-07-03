# src/app/repositories/chat_repository.py

from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.models.message import Message, RoleEnum
from app.schemas.chat import ChatCreate


class ChatRepository:

    def create(self, db: Session, data: ChatCreate, user_id: int) -> Chat:
        chat = Chat(title=data.title, user_id=user_id)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    def get_by_id(self, db: Session, chat_id: int) -> Chat | None:
        return db.query(Chat).filter(Chat.id == chat_id).first()

    def get_user_chats(self, db: Session, user_id: int) -> list[Chat]:
        """Get all chats belonging to a user"""
        return db.query(Chat).filter(Chat.user_id == user_id).all()

    def delete(self, db: Session, chat: Chat) -> None:
        db.delete(chat)
        db.commit()


class MessageRepository:

    def create(self, db: Session, chat_id: int, role: RoleEnum, content: str) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_chat_messages(self, db: Session, chat_id: int) -> list[Message]:
        """Get all messages in a chat ordered by time"""
        return (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .all()
        )
    
    def get_recent_messages(self, db: Session, chat_id: int, limit: int = 10) -> list[Message]:
        """
        Fetches last N messages for conversation memory.
        We don't send entire history to Gemini — too many tokens.
        Last 10 messages gives enough context without overloading.
        """
        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        # reverse so oldest is first — natural conversation order
        return list(reversed(messages))
    
    def delete_chat_messages(self, db: Session, chat_id: int) -> None:
        """Clears all messages in a chat without deleting the chat itself"""
        db.query(Message).filter(Message.chat_id == chat_id).delete()
        db.commit()

    def get_message_count(self, db: Session, chat_id: int) -> int:
        return (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .count()
        )

chat_repository = ChatRepository()
message_repository = MessageRepository()