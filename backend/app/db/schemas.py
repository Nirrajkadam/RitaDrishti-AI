"""
RitaDrishti-AI — Pydantic Validation Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID


# User Auth Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    username: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime


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
    model_config = ConfigDict(from_attributes=True)

    company_id: UUID
    verified_status: bool
    created_at: datetime


# Review Schemas
class ReviewCreate(BaseModel):
    company_id: UUID
    source: str
    rating: float = Field(..., ge=1.0, le=5.0)
    raw_text: str
    reviewer_name: Optional[str] = "Anonymous"

class ReviewResponse(ReviewCreate):
    model_config = ConfigDict(from_attributes=True)

    review_id: UUID
    cleaned_text: Optional[str] = None
    created_at: datetime

class AIAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: UUID
    review_id: UUID
    fake_probability: float
    is_suspicious: bool
    sentiment_score: float
    sentiment_label: str
    feature_metrics: Dict[str, Any]
    model_version: str
    created_at: datetime

class ReviewWithAnalysisResponse(BaseModel):
    review: ReviewResponse
    analysis: AIAnalysisResponse


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
