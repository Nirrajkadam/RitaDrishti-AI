"""
RitaDrishti-AI — RAG Copilot Chat API Endpoint
"""

from fastapi import APIRouter
from app.db.schemas import ChatQueryRequest, ChatQueryResponse
from app.rag.rag_engine import RAGEngine

router = APIRouter()
rag_engine = RAGEngine()

@router.post("/", response_model=ChatQueryResponse)
async def query_rag_chat(req: ChatQueryRequest):
    """Executes RAG context retrieval and LLM prompt generation for trust copilot chat."""
    res = rag_engine.generate_rag_response(query=req.query, company_id=req.company_id)
    return {
        "query": req.query,
        "answer": res["answer"],
        "sources": res["sources"]
    }
