"""
RitaDrishti-AI — Real-Time Alerts API Endpoints (Database Persisted Signals)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any

from backend.app.core.database import get_db
from backend.app.db.models import AIAnalysisModel, CompanyModel

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def get_active_alerts(db: AsyncSession = Depends(get_db)):
    """Retrieve active system alerts derived from database fake review detection records."""
    stmt = (
        select(AIAnalysisModel, CompanyModel)
        .join(CompanyModel, AIAnalysisModel.company_id == CompanyModel.company_id)
        .where(AIAnalysisModel.is_suspicious == True)
        .order_by(AIAnalysisModel.created_at.desc())
        .limit(50)
    )
    results = await db.execute(stmt)

    alerts = []
    for idx, (analysis, company) in enumerate(results.all(), 1):
        alerts.append({
            "alert_id": f"ALT-{1000 + idx}",
            "type": "Fraud Alert",
            "company_name": company.name,
            "severity": "CRITICAL" if analysis.fake_probability > 0.8 else "WARNING",
            "title": "Suspicious Review Cluster Detected",
            "message": f"Deceptive review probability flagged at {analysis.fake_probability * 100:.1f}%.",
            "timestamp": analysis.created_at.isoformat(),
            "action_required": "Escalate to Fraud Prevention Desk"
        })

    return alerts


@router.get("/summary")
async def get_alerts_summary(db: AsyncSession = Depends(get_db)):
    """Get count summary of active alerts by severity."""
    alerts = await get_active_alerts(db=db)
    critical = sum(1 for a in alerts if a["severity"] == "CRITICAL")
    warning = sum(1 for a in alerts if a["severity"] == "WARNING")
    return {
        "total_active_alerts": len(alerts),
        "critical_count": critical,
        "high_count": 0,
        "warning_count": warning
    }
