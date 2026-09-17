"""
RitaDrishti-AI — Pydantic Validation Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID


# Company Schemas
class CompanyBase(BaseModel):
    name: str
    domain: str
    industry: str
    description: Optional[str] = None
    country_code: Optional[str] = "US"

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    company_id: UUID
    verified_status: bool
    created_at: datetime
    class Config:
        from_attributes = True


# Review Schemas
class ReviewCreate(BaseModel):
    company_id: UUID
    source: str
    rating: float = Field(..., ge=1.0, le=5.0)
    raw_text: str
    reviewer_name: Optional[str] = "Anonymous"

class ReviewResponse(ReviewCreate):
    review_id: UUID
    cleaned_text: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


# Trust & Risk Schemas
class TrustScoreResponse(BaseModel):
    company_id: UUID
    trust_index: float
    transparency_score: float
    sentiment_factor: float
    fake_review_penalty: float
    complaint_penalty: float
    trust_tier: str

class RiskScoreResponse(BaseModel):
    company_id: UUID
    overall_risk_score: float
    fraud_risk: float
    regulatory_risk: float
    reputational_risk: float
    risk_level: str
    anomaly_signals: List[str]


# Chat & Report Schemas
class ChatQueryRequest(BaseModel):
    query: str
    company_id: Optional[str] = None

class ChatQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]

class AuditReportRequest(BaseModel):
    company_name: str
    company_id: Optional[str] = None

class AuditReportResponse(BaseModel):
    company_name: str
    report_markdown: str
