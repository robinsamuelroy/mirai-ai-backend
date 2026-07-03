from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.services.search_service import search_service
from app.services.chat_service import chat_service
from app.repositories.chat_repository import message_repository
from app.core.gemini_client import get_gemini_response
from app.models.user import User
from app.models.message import RoleEnum, Message
from app.schemas.chat import ChatCreate


class RAGService:

    def build_conversation_history(
        self,
        messages: list[Message]
    ) -> str:
        """
        Formats recent messages as conversation history string.
        Gemini needs to know what was already said to answer follow-ups.

        Example output:
            User: What is FastAPI?
            Assistant: FastAPI is a modern Python web framework...
            User: How does it compare to Django?
        """
        if not messages:
            return ""

        history_lines = []
        for msg in messages:
            role_label = "User" if msg.role == RoleEnum.user else "Assistant"
            history_lines.append(f"{role_label}: {msg.content}")

        return "\n".join(history_lines)

    def build_prompt(
        self,
        question: str,
        chunks: list[dict],
        conversation_history: str = ""
    ) -> str:
        """
        Builds RAG prompt with optional conversation history.
        History gives Gemini memory of previous turns.
        """
        context_blocks = []
        for i, chunk in enumerate(chunks):
            source = chunk["metadata"].get("original_filename", "Unknown")
            score = chunk["similarity_score"]
            context_blocks.append(
                f"[Source {i+1}: {source} | Relevance: {score}]\n"
                f"{chunk['content']}"
            )

        context_text = "\n\n---\n\n".join(context_blocks)

        # include conversation history only if it exists
        history_section = ""
        if conversation_history:
            history_section = f"""
CONVERSATION HISTORY (for context):
{conversation_history}

"""

        prompt = f"""You are an intelligent knowledge assistant.
Answer questions accurately based on the provided document context.
{history_section}
CONTEXT FROM USER'S DOCUMENTS:
{context_text}

RULES:
- Answer using ONLY information from the context above
- If context is insufficient, say so clearly
- Reference which source your answer comes from
- Consider the conversation history when answering follow-up questions
- Be concise and precise
- Never fabricate information

CURRENT QUESTION: {question}

ANSWER:"""

        return prompt

    async def chat(
        self,
        db: Session,
        chat_id: int,
        question: str,
        current_user: User,
        document_id: int = None,
        top_k: int = 5
    ) -> dict:
        """
        Full RAG pipeline with conversation memory:
        1. Verify ownership
        2. Load recent conversation history
        3. Save user message
        4. Search relevant chunks
        5. Build prompt with history + context
        6. Get Gemini response
        7. Save assistant reply
        8. Return answer with sources
        """
        # step 1 — verify ownership
        chat = chat_service.get_chat(db, chat_id, current_user)

        # step 2 — load last 10 messages for memory
        # we fetch BEFORE saving current message
        recent_messages = message_repository.get_recent_messages(
            db, chat_id, limit=10
        )
        conversation_history = self.build_conversation_history(recent_messages)

        # step 3 — save current user message
        message_repository.create(
            db=db,
            chat_id=chat_id,
            role=RoleEnum.user,
            content=question
        )

        # step 4 — search relevant chunks
        chunks = search_service.search(
            user_id=current_user.id,
            query=question,
            top_k=top_k,
            document_id=document_id
        )

        if not chunks:
            answer = (
                "I could not find relevant information in your documents "
                "to answer this question. Please upload and process "
                "relevant documents first."
            )
            sources = []
        else:
            # step 5 — build prompt with history
            prompt = self.build_prompt(
                question=question,
                chunks=chunks,
                conversation_history=conversation_history
            )

            # step 6 — get Gemini response
            try:
                answer = get_gemini_response(prompt)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"AI service unavailable: {str(e)}"
                )

            sources = [
                {
                    "filename": c["metadata"].get("original_filename"),
                    "chunk_index": c["metadata"].get("chunk_index"),
                    "similarity_score": c["similarity_score"],
                }
                for c in chunks
            ]

        # step 7 — save assistant reply
        message_repository.create(
            db=db,
            chat_id=chat_id,
            role=RoleEnum.assistant,
            content=answer
        )

        return {
            "chat_id": chat_id,
            "question": question,
            "answer": answer,
            "sources": sources,
            "chunks_used": len(chunks)
        }

    async def create_chat_and_ask(
        self,
        db: Session,
        question: str,
        current_user: User,
        document_id: int = None
    ) -> dict:
        title = question[:50] + "..." if len(question) > 50 else question

        chat = chat_service.create_chat(
            db=db,
            data=ChatCreate(title=title),
            current_user=current_user
        )

        return await self.chat(
            db=db,
            chat_id=chat.id,
            question=question,
            current_user=current_user,
            document_id=document_id
        )


rag_service = RAGService()