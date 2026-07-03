# src/app/routers/search_router.py

from fastapi import APIRouter, Depends
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import search_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.post("/", response_model=SearchResponse)
def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Searches user's documents by semantic similarity.
    No DB session needed — ChromaDB handles everything.
    """
    results = search_service.search(
        user_id=current_user.id,
        query=request.query,
        top_k=request.top_k,
        document_id=request.document_id
    )

    return SearchResponse(
        query=request.query,
        results=results,
        total_results=len(results)
    )