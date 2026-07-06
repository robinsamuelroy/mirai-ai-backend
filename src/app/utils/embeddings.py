from typing import List
from sentence_transformers import SentenceTransformer
from src.app.core.config import settings

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    token=settings.HF_TOKEN,
)

def generate_embedding(text: str) -> List[float]:
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    embeddings = model.encode(texts, convert_to_numpy=True, batch_size=32)
    return embeddings.tolist()


