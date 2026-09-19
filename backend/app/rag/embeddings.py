"""
RitaDrishti-AI — Local Vector Embeddings Generator
Uses SentenceTransformers (all-MiniLM-L6-v2) to generate 384-dimensional dense vector embeddings.
"""

from typing import List, Union
import numpy as np


class EmbeddingEngine:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"[EmbeddingEngine Warning]: Could not load {model_name}, falling back to dummy vectors: {e}")

    def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generates 384-dim dense embedding vectors for input text(s)."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        if not self.model:
            raise RuntimeError("SentenceTransformer model is unavailable. Install sentence-transformers to generate embeddings.")

        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()
