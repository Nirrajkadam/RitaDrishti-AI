"""
RitaDrishti-AI — Companies REST API Endpoints (Persistent SQLAlchemy AsyncSession)
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.core.exceptions import EntityNotFoundError, AuthenticationError
from backend.app.db.models import UserModel
from backend.app.db.repositories import CompanyRepository
from backend.app.db.schemas import CompanyCreate, CompanyResponse

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve companies audited by RitaDrishti-AI."""
    repo = CompanyRepository(db)
    companies = await repo.list_companies(limit=limit, offset=offset)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get company profile details by UUID."""
    repo = CompanyRepository(db)
    company = await repo.get_by_id(company_id)
    if not company:
        raise EntityNotFoundError(f"Company with ID '{company_id}' not found.")
    return company


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_in: CompanyCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new company for trust intelligence auditing.
    Requires Authentication (Bearer JWT).
    """
    repo = CompanyRepository(db)
    
    # Domain uniqueness check
    existing = await repo.get_by_domain(company_in.domain)
    if existing:
        raise AuthenticationError(f"Company with domain '{company_in.domain}' is already registered.")

    company = await repo.create_company(
        name=company_in.name,
        domain=company_in.domain,
        industry=company_in.industry,
        description=company_in.description,
        country_code=company_in.country_code or "US"
    )
    return company
