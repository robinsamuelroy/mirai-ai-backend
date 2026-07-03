import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_DIR,
    settings=ChromaSettings(anonymized_telemetry=False)
    # disable telemetry — don't send usage data to ChromaDB
)

def get_or_create_collection(collection_name: str):
    return chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

def get_user_collection(user_id: int):
    """Returns the ChromaDB collection for a specific user"""
    collection_name = f"user_{user_id}_documents"
    return get_or_create_collection(collection_name)