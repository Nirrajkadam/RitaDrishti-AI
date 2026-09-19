"""
Unit tests for CrewAI Multi-Agent Fleet
"""

import pytest
from backend.app.agents.crew_manager import (
    ResearchAgent, RiskAgent, ComplianceAgent, TrustAgent, ReportAgent, CrewManager,
    AuditEvidence, ArticleEvidence, ComplaintEvidence, ReviewAnalysisEvidence, EvidenceUnavailableError
)


def test_research_agent():
    agent = ResearchAgent()
    res = agent.run("Acme Cloud", news_articles=[{"headline": "Growth", "summary": "Expanded", "publisher": "Press"}])
    assert res["agent"] == "ResearchAgent"
    assert "Acme Cloud" in res["findings"]


def test_risk_agent():
    agent = RiskAgent()
    res = agent.run("Acme Cloud", complaints_count=10, fake_prob=0.35)
    assert res["agent"] == "RiskAgent"
    assert "High Risk" in res["findings"]


def test_compliance_agent():
    agent = ComplianceAgent()
    res = agent.run("Acme Cloud", resolved_disputes=8, total_disputes=10)
    assert res["agent"] == "ComplianceAgent"
    assert "80.0%" in res["findings"]


def test_trust_agent():
    agent = TrustAgent()
    res = agent.run("Acme Cloud", trust_score=85.0)
    assert res["agent"] == "TrustAgent"
    assert "High Trust" in res["findings"]


def test_crew_manager_raises_evidence_unavailable():
    crew = CrewManager()
    empty = AuditEvidence(company_name="Unreviewed Entity")
    with pytest.raises(EvidenceUnavailableError):
        crew.run_full_audit(empty)


def test_crew_manager_full_audit_with_evidence():
    crew = CrewManager()
    evidence = AuditEvidence(
        company_name="Acme Cloud",
        trust_score=85.0,
        articles=[ArticleEvidence(headline="Expansion", summary="Data center", publisher="TechNews")],
        complaints=[ComplaintEvidence(title="Billing", description="Resolved refund", resolution_status="resolved")],
        analyses=[ReviewAnalysisEvidence(raw_text="Good", cleaned_text="Good", sentiment_score=0.8, fake_probability=0.02, is_suspicious=False)]
    )
    res = crew.run_full_audit(evidence)
    assert res["company_name"] == "Acme Cloud"
    assert res["status"] == "Completed"
    assert len(res["agent_findings"]) == 4
    assert "# 🛡️ Executive Trust Audit Report: Acme Cloud" in res["report_markdown"]
