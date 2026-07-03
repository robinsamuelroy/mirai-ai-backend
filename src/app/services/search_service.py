# src/app/services/search_service.py

from fastapi import HTTPException, status
from app.core.chromadb_client import get_user_collection
from app.utils.embeddings import generate_embedding


class SearchService:

    def search(self, user_id: int, query: str, top_k: int = 5, document_id: int = None) -> list[dict]:
        if not query.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty")
        query_embedding = generate_embedding(query)
        where_filter = None
        if document_id is not None:
            where_filter = {"document_id": document_id}
        # step 3 — search ChromaDB
        collection = get_user_collection(user_id)
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
                # documents  → original chunk text
                # metadatas  → chunk_index, document_id, filename etc.
                # distances  → cosine distance (lower = more similar)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Search failed: {str(e)}"
            )

        # step 4 — format results cleanly
        chunks = []

        if not results["documents"] or not results["documents"][0]:
            return []

        for i in range(len(results["documents"][0])):
            distance = results["distances"][0][i]
            similarity_score = round(1 - distance, 4)
            # cosine distance → similarity score
            # distance 0.0 = identical  → score 1.0
            # distance 1.0 = opposite   → score 0.0
            # we want HIGH score = MORE similar

            chunks.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity_score": similarity_score,
            })

        # sort by similarity — most relevant first
        chunks.sort(key=lambda x: x["similarity_score"], reverse=True)

        return chunks


search_service = SearchService()



# results = {

# "documents":[
#     [
#         "FastAPI is a modern web framework.",
#         "Python is a programming language."
#     ]
# ],

# "metadatas":[
#     [
#         {
#             "document_id":1,
#             "chunk_index":1
#         },
#         {
#             "document_id":1,
#             "chunk_index":0
#         }
#     ]
# ],

# "distances":[
#     [
#         0.05,
#         0.61
#     ]
# ]

# }