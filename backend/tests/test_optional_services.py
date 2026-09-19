"""
Behavioral Unit Tests: Subsystem Feature Flags & Optional Subsystem Error Handling
"""

import pytest
from httpx import AsyncClient
from backend.app.config import settings
from backend.app.rag.rag_engine import RAGEngine, RAGUnavailableError
from backend.app.agents.crew_manager import CrewManager, AuditEvidence, EvidenceUnavailableError


@pytest.mark.asyncio
async def test_chat_disabled_flag_returns_503(client: AsyncClient):
    resp = await client.post("/api/v1/chat/", json={"query": "Test query"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "OLLAMA_OR_QDRANT_DISABLED"


@pytest.mark.asyncio
async def test_reports_disabled_flag_returns_503(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/reports/generate", json={"company_name": "Acme Cloud"}, headers=auth_headers)
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "CREWAI_DISABLED"


def test_crew_manager_raises_evidence_unavailable_error():
    crew = CrewManager()
    empty_evidence = AuditEvidence(company_name="Empty Enterprise")
    with pytest.raises(EvidenceUnavailableError):
        crew.run_full_audit(empty_evidence)


def test_crew_manager_evidence_driven_audit():
    crew = CrewManager()
    evidence = AuditEvidence(
        company_name="Acme Tech",
        trust_score=88.5,
        articles=[{"headline": "Growth", "summary": "Expanded data centers.", "publisher": "Tech Daily"}],
        complaints=[{"title": "Billing", "description": "Resolved refund.", "resolution_status": "resolved"}],
        analyses=[{"raw_text": "Good", "cleaned_text": "Good", "sentiment_score": 0.8, "fake_probability": 0.01, "is_suspicious": False}]
    )
    res = crew.run_full_audit(evidence)
    assert res["status"] == "Completed"
    assert "Acme Tech" in res["report_markdown"]
    assert "88.5" in res["agent_findings"][3]["findings"]
