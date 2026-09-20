"""
Unit tests for RAG engine, vector store, and embeddings engine
"""

import pytest
from backend.app.rag.vector_store import VectorStoreManager
from backend.app.rag.rag_engine import RAGEngine
from backend.app.rag.embeddings import EmbeddingEngine


def test_vector_store_add_and_search():
    store = VectorStoreManager(dimension=4)
    docs = [
        {"company_id": "1", "type": "Review", "text": "Cloud service is great", "source": "Trustpilot"},
        {"company_id": "2", "type": "Complaint", "text": "Billing issue", "source": "BBB"}
    ]
    embeddings = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0]
    ]
    store.add_documents(docs, embeddings)

    results = store.search_similar([1.0, 0.0, 0.0, 0.0], top_k=2)
    assert len(results) > 0
    assert results[0]["company_id"] == "1"


def test_vector_store_filter_by_company_id():
    store = VectorStoreManager(dimension=4)
    docs = [
        {"company_id": "100", "type": "Review", "text": "Good", "source": "A"},
        {"company_id": "200", "type": "Review", "text": "Bad", "source": "B"}
    ]
    embeddings = [
        [0.5, 0.5, 0.0, 0.0],
        [0.5, 0.5, 0.0, 0.0]
    ]
    store.add_documents(docs, embeddings)

    results = store.search_similar([0.5, 0.5, 0.0, 0.0], top_k=5, company_id="200")
    assert len(results) == 1
    assert results[0]["company_id"] == "200"


def test_rag_engine_chunking():
    rag = RAGEngine()
    text = "A" * 1200
    chunks = rag.chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_embeddings_unsupported_model_raises():
    engine = EmbeddingEngine(model_name="invalid/non-existent-model-xyz")
    if not engine.model:
        with pytest.raises(RuntimeError):
            engine.generate_embeddings("test text")


def test_rag_engine_index_company_knowledge():
    class FakeEmbeddingEngine:
        def generate_embeddings(self, texts):
            if isinstance(texts, str):
                return [[0.1] * 384]
            return [[0.1] * 384 for _ in texts]

    rag = RAGEngine(embedding_engine=FakeEmbeddingEngine())
    rag.index_company_knowledge(
        company_id="11111111-1111-1111-1111-111111111111",
        company_name="Acme Cloud",
        reviews=[{"raw_text": "Great service!", "source": "Trustpilot"}],
        complaints=[{"title": "Billing", "description": "Double billed.", "source": "BBB"}],
        news=[{"headline": "Expansion", "summary": "New infrastructure.", "publisher": "TechNews"}]
    )
    assert len(rag.vector_store.documents) == 3



def test_successful_injected_rag_client():
    from backend.app.rag.rag_engine import RAGEngine

    class FakeEmbeddingEngine:
        def generate_embeddings(self, texts):
            if isinstance(texts, str):
                return [[0.1] * 384]
            return [[0.1] * 384 for _ in texts]

    class FakeOllamaClient:
        def chat(self, model, messages):
            return {"message": {"content": "Grounded answer: Acme Cloud has excellent uptime."}}

    rag = RAGEngine(ollama_client=FakeOllamaClient(), embedding_engine=FakeEmbeddingEngine())
    res = rag.generate_rag_response("What are Acme Cloud strengths?")
    assert res["answer"] == "Grounded answer: Acme Cloud has excellent uptime."


def test_rag_timeout_error_handling():
    from backend.app.rag.rag_engine import RAGEngine, RAGUnavailableError

    class FakeEmbeddingEngine:
        def generate_embeddings(self, texts):
            if isinstance(texts, str):
                return [[0.1] * 384]
            return [[0.1] * 384 for _ in texts]

    class TimeoutOllamaClient:
        def chat(self, model, messages):
            raise TimeoutError("Ollama request timed out after 30 seconds")

    rag = RAGEngine(ollama_client=TimeoutOllamaClient(), embedding_engine=FakeEmbeddingEngine())
    with pytest.raises(RAGUnavailableError):
        rag.generate_rag_response("What are Acme Cloud strengths?")
