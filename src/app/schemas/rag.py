# src/app/schemas/rag.py
from typing import Optional
from pydantic import BaseModel


class RAGRequest(BaseModel):
    question: str
    document_id: Optional[int] = None
    top_k: int = 5


class SourceReference(BaseModel):
    filename: str
    chunk_index: int
    similarity_score: float


class RAGResponse(BaseModel):
    chat_id: int
    question: str
    answer: str
    sources: list[SourceReference]
    chunks_used: int