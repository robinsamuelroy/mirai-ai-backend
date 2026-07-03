from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.rag import RAGRequest, RAGResponse
from app.services.rag_service import rag_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post("/chat/{chat_id}", response_model=RAGResponse)
async def rag_chat(
    chat_id: int,
    request: RAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ask a question in an existing chat.
    Retrieves relevant document chunks and answers using Gemini.
    Saves full conversation to DB.
    """
    return await rag_service.chat(
        db=db,
        chat_id=chat_id,
        question=request.question,
        current_user=current_user,
        document_id=request.document_id,
        top_k=request.top_k
    )


@router.post("/ask", response_model=RAGResponse)
async def quick_ask(
    request: RAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ask a question without an existing chat.
    Creates a new chat automatically, then answers.
    Useful for quick one-off questions.
    """
    return await rag_service.create_chat_and_ask(
        db=db,
        question=request.question,
        current_user=current_user,
        document_id=request.document_id
    )