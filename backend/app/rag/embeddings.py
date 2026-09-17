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

        if self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.tolist()

        # Fallback dummy normalized random embeddings for offline/testing mode
        dim = 384
        dummy_list = []
        for text in texts:
            # Seed based on text hash for deterministic fallback
            seed = sum(ord(c) for c in text) % 10000
            np.random.seed(seed)
            vec = np.random.randn(dim)
            vec = vec / np.linalg.norm(vec)
            dummy_list.append(vec.tolist())
        return dummy_list
