from typing import List
from sentence_transformers import SentenceTransformer
import math

# Load the sentence transformer model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Optional cache if you're embedding repeated queries
embedding_cache = {}

def get_embedding(text: str) -> List[float]:
    """Get semantic embedding for a given text using SentenceTransformer."""
    if text in embedding_cache:
        return embedding_cache[text]
    
    embedding = model.encode(text).tolist()
    embedding_cache[text] = embedding
    return embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (norm1 * norm2 + 1e-10)

if __name__ == "__main__":
    emb1 = get_embedding("outdoors nature hiking")
    emb2 = get_embedding("walk in the forest")
    print("Cosine similarity:", cosine_similarity(emb1, emb2))
