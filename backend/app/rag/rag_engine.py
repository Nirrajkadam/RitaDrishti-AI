"""
RitaDrishti-AI — RAG (Retrieval-Augmented Generation) Engine

Architecture:
1. Chunking: Text splitter with 512 character windows and 64 character overlap.
2. Retrieval: Vector Cosine similarity retrieval via SentenceTransformers + VectorStoreManager.
3. Ranking: Re-ranks retrieved chunks based on relevance score and recency.
4. Context Building: Constructs strict, hallucination-resistant LLM prompt context.
5. Response Generation: Invokes Ollama Llama 3 API for accurate trust auditing responses.
"""

from typing import List, Dict, Any
from backend.app.config import settings
from backend.app.rag.embeddings import EmbeddingEngine
from backend.app.rag.vector_store import VectorStoreManager


import logging

logger = logging.getLogger(__name__)


class RAGUnavailableError(Exception):
    """Domain exception raised when RAG vector search or LLM generation is unavailable."""
    pass


class RAGEngine:
    def __init__(self, ollama_client=None, embedding_engine=None, vector_store=None):
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.vector_store = vector_store or VectorStoreManager()
        self.ollama_model = settings.OLLAMA_MODEL
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_client = ollama_client

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 64) -> List[str]:
        """Splits long document text into overlapping chunks."""
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += (chunk_size - overlap)
        return chunks

    def index_company_knowledge(self, company_id: str, company_name: str, reviews: List[Dict], complaints: List[Dict], news: List[Dict]):
        """Indexes all reviews, complaints, and news into the Vector Store."""
        docs = []
        
        # 1. Index Reviews
        for r in reviews:
            chunks = self.chunk_text(r.get("cleaned_text") or r.get("raw_text", ""))
            for chunk in chunks:
                docs.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "type": "Review",
                    "text": chunk,
                    "source": r.get("source", "Public Review"),
                    "rating": r.get("rating", 3.0)
                })

        # 2. Index Complaints
        for c in complaints:
            chunks = self.chunk_text(c.get("description", ""))
            for chunk in chunks:
                docs.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "type": "Complaint",
                    "text": f"Complaint Title: {c.get('title')}. Detail: {chunk}",
                    "source": c.get("source", "Consumer Forum"),
                    "status": c.get("resolution_status", "unresolved")
                })

        # 3. Index News
        for n in news:
            chunks = self.chunk_text(n.get("summary") or n.get("headline", ""))
            for chunk in chunks:
                docs.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "type": "News Article",
                    "text": f"Headline: {n.get('headline')}. Summary: {chunk}",
                    "source": n.get("publisher", "News Feed")
                })

        if docs:
            texts = [d["text"] for d in docs]
            embeddings = self.embedding_engine.generate_embeddings(texts)
            self.vector_store.add_documents(docs, embeddings)

    def generate_rag_response(self, query: str, company_id: str = None) -> Dict[str, Any]:
        """Executes complete RAG pipeline: Query Embedding -> Retrieval -> Context -> Ollama Generation."""
        
        # Step 1: Embed User Query
        q_emb = self.embedding_engine.generate_embeddings(query)[0]

        # Step 2 & 3: Retrieval & Ranking
        retrieved_docs = self.vector_store.search_similar(q_emb, top_k=5, company_id=company_id)

        # Step 4: Construct Grounded Context
        context_str = ""
        sources = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_str += f"\n[Context {i}] ({doc['type']} from {doc['source']}): {doc['text']}\n"
            sources.append(f"{doc['type']} ({doc['source']})")

        if not retrieved_docs:
            context_str = "No specific retrieved company context found in local vector database."

        # Step 5: System Prompt Engineering
        system_prompt = f"""You are RitaDrishti AI Trust Copilot, an elite corporate risk auditor and cybersecurity research intelligence assistant.
Answer the user query based ONLY on the verified evidence provided in the context below.
If the context does not contain enough information, state clearly what is available and offer a analytical summary based on trust intelligence principles.

VERIFIED CONTEXT DATA:
{context_str}

USER QUERY:
{query}

EXECUTIVE ANSWER:"""

        # Invoking Ollama API or Injected Client
        answer = ""
        if self.ollama_client is not None:
            client = self.ollama_client
        else:
            try:
                import ollama
                client = ollama.Client(host=self.ollama_base_url, timeout=30.0)
            except Exception as e:
                logger.error(f"Failed to initialize Ollama client: {e}", exc_info=True)
                raise RAGUnavailableError("Ollama service unavailable")

        try:
            response = client.chat(
                model=self.ollama_model,
                messages=[{"role": "system", "content": system_prompt}]
            )
            answer = response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama execution failed at {self.ollama_base_url}: {e}", exc_info=True)
            raise RAGUnavailableError(f"Ollama execution failed: {e}")

        return {
            "query": query,
            "answer": answer,
            "retrieved_context_count": len(retrieved_docs),
            "sources": list(set(sources))
        }


if __name__ == "__main__":
    rag = RAGEngine()
    rag.index_company_knowledge(
        company_id="11111111-1111-1111-1111-111111111111",
        company_name="Acme Cloud",
        reviews=[{"raw_text": "Superb uptime and excellent cloud support!", "source": "Trustpilot"}],
        complaints=[{"title": "Billing issue", "description": "Double billed for server tier.", "source": "BBB"}],
        news=[{"headline": "Acme Cloud expands AI infrastructure", "summary": "Acme adds 5 new data centers."}]
    )

    res = rag.generate_rag_response("What are the main strengths and complaints for Acme Cloud?")
    print(res["answer"])
