"""
RitaDrishti-AI — Companies REST API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import uuid4, UUID
from app.db.schemas import CompanyCreate, CompanyResponse

router = APIRouter()

# Mock in-memory database store for demonstration & low-latency execution
MOCK_COMPANIES = [
    {
        "company_id": UUID("11111111-1111-1111-1111-111111111111"),
        "name": "Acme Cloud Solutions",
        "domain": "acmecloud.io",
        "industry": "Cloud SaaS",
        "description": "Enterprise SaaS provider offering cloud infrastructure & AI middleware.",
        "verified_status": True,
        "country_code": "US",
        "created_at": "2026-01-15T10:00:00Z"
    },
    {
        "company_id": UUID("22222222-2222-2222-2222-222222222222"),
        "name": "FinPay Tech",
        "domain": "finpay.com",
        "industry": "Fintech",
        "description": "Digital payment gateway and mobile wallet service.",
        "verified_status": True,
        "country_code": "US",
        "created_at": "2026-02-20T12:30:00Z"
    }
]

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(limit: int = Query(10, ge=1, le=100)):
    """Retrieve all verified companies audited by RitaDrishti-AI."""
    return MOCK_COMPANIES[:limit]

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: UUID):
    """Get company profile details by UUID."""
    for comp in MOCK_COMPANIES:
        if comp["company_id"] == company_id:
            return comp
    raise HTTPException(status_code=404, detail="Company not found")

@router.post("/", response_model=CompanyResponse, status_code=201)
async def create_company(company: CompanyCreate):
    """Register a new company for trust intelligence auditing."""
    new_comp = {
        "company_id": uuid4(),
        "name": company.name,
        "domain": company.domain,
        "industry": company.industry,
        "description": company.description,
        "verified_status": False,
        "country_code": company.country_code or "US",
        "created_at": "2026-09-17T21:00:00Z"
    }
    MOCK_COMPANIES.append(new_comp)
    return new_comp
