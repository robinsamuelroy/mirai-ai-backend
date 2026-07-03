# src/app/schemas/search.py

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: int = None  # optional filter


class ChunkResult(BaseModel):
    content: str
    metadata: dict
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[ChunkResult]
    total_results: int