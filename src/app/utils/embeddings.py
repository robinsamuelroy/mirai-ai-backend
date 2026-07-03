from sentence_transformers import SentenceTransformer
from typing import List

model = SentenceTransformer("all-MiniLM-L6-v2")
#   - small and fast
#   - 384 dimensional vectors
#   - good quality for semantic search
#   - downloads automatically on first run (~80MB)

def generate_embedding(text: str) -> List[float]:
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    embeddings = model.encode(texts, convert_to_numpy=True, batch_size=32)
    return embeddings.tolist()


