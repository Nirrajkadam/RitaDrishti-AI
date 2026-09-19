"""
RitaDrishti-AI — RAG Copilot Chat API Endpoint
"""

from fastapi import APIRouter
from backend.app.config import settings
from backend.app.core.exceptions import ServiceUnavailableError
from backend.app.db.schemas import ChatQueryRequest, ChatQueryResponse

router = APIRouter()


@router.post("/", response_model=ChatQueryResponse)
async def query_rag_chat(req: ChatQueryRequest):
    """Executes RAG context retrieval and LLM prompt generation for trust copilot chat."""
    if not (settings.ENABLE_OLLAMA and settings.ENABLE_QDRANT):
        raise ServiceUnavailableError(
            code="OLLAMA_OR_QDRANT_DISABLED",
            message="RAG AI Copilot service is disabled. Set ENABLE_OLLAMA=true and ENABLE_QDRANT=true to enable.",
            retryable=False
        )

    from backend.app.rag.rag_engine import RAGEngine
    rag_engine = RAGEngine()
    res = rag_engine.generate_rag_response(query=req.query, company_id=req.company_id)
    return {
        "query": req.query,
        "answer": res["answer"],
        "sources": res["sources"]
    }
