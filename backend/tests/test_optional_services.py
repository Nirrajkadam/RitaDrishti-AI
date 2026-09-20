"""
Behavioral Unit Tests: Subsystem Feature Flags & Optional Subsystem Error Handling
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
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
    resp = await client.post("/api/v1/reports/generate", json={"company_id": str(uuid4())}, headers=auth_headers)
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "CREWAI_DISABLED"


def test_crew_manager_raises_evidence_unavailable_error():
    crew = CrewManager()
    empty_evidence = AuditEvidence(company_name="Empty Enterprise")
    with pytest.raises(EvidenceUnavailableError):
        crew.run_full_audit(empty_evidence)


def test_report_with_review_evidence_only():
    from backend.app.agents.crew_manager import ReviewAnalysisEvidence
    crew = CrewManager()
    evidence = AuditEvidence(
        company_name="Review Only Corp",
        trust_score=82.4,
        analyses=[ReviewAnalysisEvidence(raw_text="Great service", cleaned_text="Great service", sentiment_score=0.9, fake_probability=0.02, is_suspicious=False)]
    )
    res = crew.run_full_audit(evidence)
    report = res["report_markdown"]
    assert "Review Analysis Assessment" in report
    assert "No complaint, regulatory, news, or external OSINT evidence was included" in report
    assert "consumer dispute resolution audit" not in report
    assert "360-degree" not in report


def test_report_with_all_supported_evidence_categories():
    from backend.app.agents.crew_manager import ReviewAnalysisEvidence, ComplaintEvidence, ArticleEvidence
    crew = CrewManager()
    evidence = AuditEvidence(
        company_name="Full Data Corp",
        trust_score=91.0,
        articles=[ArticleEvidence(headline="Expansion", summary="Opened new data center", publisher="TechNews")],
        complaints=[ComplaintEvidence(title="Billing issue", description="Double billed", severity_level="medium", resolution_status="resolved")],
        analyses=[ReviewAnalysisEvidence(raw_text="Awesome product", cleaned_text="Awesome product", sentiment_score=0.95, fake_probability=0.01, is_suspicious=False)]
    )
    res = crew.run_full_audit(evidence)
    report = res["report_markdown"]
    assert "Multi-Source Trust Assessment" in report


def test_report_with_reviews_and_complaints():
    from backend.app.agents.crew_manager import ReviewAnalysisEvidence, ComplaintEvidence
    crew = CrewManager()
    evidence = AuditEvidence(
        company_name="RevComp Corp",
        trust_score=75.0,
        complaints=[ComplaintEvidence(title="Issue", description="Resolved", resolution_status="resolved")],
        analyses=[ReviewAnalysisEvidence(raw_text="Good", cleaned_text="Good", sentiment_score=0.8, fake_probability=0.01, is_suspicious=False)]
    )
    res = crew.run_full_audit(evidence)
    assert "Review and Complaint Assessment" in res["report_markdown"]


def test_report_with_reviews_and_news():
    from backend.app.agents.crew_manager import ReviewAnalysisEvidence, ArticleEvidence
    crew = CrewManager()
    evidence = AuditEvidence(
        company_name="RevNews Corp",
        trust_score=78.0,
        articles=[ArticleEvidence(headline="News", summary="Sum", publisher="Pub")],
        analyses=[ReviewAnalysisEvidence(raw_text="Good", cleaned_text="Good", sentiment_score=0.8, fake_probability=0.01, is_suspicious=False)]
    )
    res = crew.run_full_audit(evidence)
    assert "Review and Media Assessment" in res["report_markdown"]


def test_bounded_evidence_validation():
    from pydantic import ValidationError
    from backend.app.agents.crew_manager import ReviewAnalysisEvidence

    # Valid bounds pass
    valid_ev = ReviewAnalysisEvidence(raw_text="Good", cleaned_text="Good", sentiment_score=0.5, fake_probability=0.1, is_suspicious=False)
    assert valid_ev.fake_probability == 0.1

    # Fake probability out of bounds [0.0, 1.0] raises ValidationError
    with pytest.raises(ValidationError):
        ReviewAnalysisEvidence(raw_text="Bad", cleaned_text="Bad", sentiment_score=0.0, fake_probability=1.5, is_suspicious=True)
