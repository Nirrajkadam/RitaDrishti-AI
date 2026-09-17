"""
SentinelX Trust AI — FAISS & Qdrant Vector Store Manager
Indexes text chunks and performs Cosine Similarity Vector Searches.
"""

from typing import List, Dict, Any
import numpy as np


class VectorStoreManager:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.documents = []
        self.vectors = []
        self.faiss_index = None

        try:
            import faiss
            self.faiss_index = faiss.IndexFlatIP(dimension) # Inner Product (Cosine Similarity on normalized vectors)
        except Exception as e:
            print(f"[VectorStoreManager Warning]: FAISS not available, using in-memory cosine fallback: {e}")

    def add_documents(self, docs: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Indexes document chunks along with their vector embeddings."""
        for doc, emb in zip(docs, embeddings):
            self.documents.append(doc)
            self.vectors.append(emb)

        if self.faiss_index is not None and embeddings:
            np_vectors = np.array(embeddings, dtype=np.float32)
            self.faiss_index.add(np_vectors)

    def search_similar(self, query_vector: List[float], top_k: int = 4, company_id: str = None) -> List[Dict[str, Any]]:
        """Performs Vector Cosine Similarity Search with optional company metadata filtering."""
        if not self.documents or not query_vector:
            return []

        q_vec = np.array(query_vector, dtype=np.float32).reshape(1, -1)

        if self.faiss_index is not None and self.faiss_index.ntotal > 0:
            scores, indices = self.faiss_index.search(q_vec, min(top_k * 3, self.faiss_index.ntotal))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc["similarity_score"] = float(score)
                    if company_id and str(doc.get("company_id")) != str(company_id):
                        continue
                    results.append(doc)
                    if len(results) >= top_k:
                        break
            return results

        # Fallback In-Memory Dot-Product Cosine Search
        results = []
        for doc, emb in zip(self.documents, self.vectors):
            if company_id and str(doc.get("company_id")) != str(company_id):
                continue
            sim = float(np.dot(q_vec, np.array(emb, dtype=np.float32)))
            d = doc.copy()
            d["similarity_score"] = sim
            results.append(d)

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]
