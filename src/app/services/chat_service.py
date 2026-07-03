from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.chat_repository import chat_repository, message_repository
from app.schemas.chat import ChatCreate, ChatUpdate
from app.models.chat import Chat
from app.models.user import User


class ChatService:

    def create_chat(self, db: Session, data: ChatCreate, current_user: User) -> Chat:
        return chat_repository.create(db, data, user_id=current_user.id)

    def get_user_chats(self, db: Session, current_user: User) -> list[Chat]:
        return chat_repository.get_user_chats(db, user_id=current_user.id)

    def get_chat(self, db: Session, chat_id: int, current_user: User) -> Chat:
        chat = chat_repository.get_by_id(db, chat_id)

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )

        # ownership check — users can only access their own chats
        if chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this chat"
            )

        return chat
    
    def get_chat_history(
        self,
        db: Session,
        chat_id: int,
        current_user: User,
        limit: int = 50
    ) -> dict:
        """
        Returns a chat with its messages.
        limit → max messages to return, default 50.
        For very long chats we don't return everything at once.
        """
        chat = self.get_chat(db, chat_id, current_user)
        total = message_repository.get_message_count(db, chat_id)

        messages = (
            message_repository.get_recent_messages(db, chat_id, limit=limit)
        )

        return {
            "chat_id": chat.id,
            "title": chat.title,
            "messages": messages,
            "total_messages": total,
            "returned_messages": len(messages)
        }

    def update_chat_title(
        self,
        db: Session,
        chat_id: int,
        data: ChatUpdate,
        current_user: User
    ) -> Chat:
        chat = self.get_chat(db, chat_id, current_user)
        return chat_repository.update_title(db, chat, data.title)

    def clear_chat_history(
        self,
        db: Session,
        chat_id: int,
        current_user: User
    ) -> dict:
        """
        Deletes all messages in a chat.
        Keeps the chat itself — just wipes the history.
        """
        self.get_chat(db, chat_id, current_user)
        message_repository.delete_chat_messages(db, chat_id)
        return {"message": "Chat history cleared successfully"}

    def delete_chat(self, db: Session, chat_id: int, current_user: User) -> dict:
        chat = self.get_chat(db, chat_id, current_user)
        chat_repository.delete(db, chat)
        return {"message": "Chat deleted successfully"}


chat_service = ChatService()