"""
RitaDrishti-AI — Database Repositories Pattern
Provides transactional data access methods for Companies, Reviews, AI Analyses, Users, and Trust Scores.
"""

import uuid
from typing import Optional, List, Dict, Any, Tuple, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.db.models import UserModel, CompanyModel, ReviewModel, AIAnalysisModel, TrustScoreModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "analyst"
    ) -> UserModel:
        from backend.app.core.security import hash_password
        hashed_pwd = hash_password(password)
        user = UserModel(
            email=email.lower().strip(),
            username=username.lower().strip(),
            password_hash=hashed_pwd,
            full_name=full_name,
            role=role
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        stmt = select(UserModel).where(UserModel.username == username.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: Union[uuid.UUID, str]) -> Optional[UserModel]:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = select(UserModel).where(UserModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company(
        self,
        name: str,
        domain: str,
        industry: str,
        description: Optional[str] = None,
        country_code: str = "US"
    ) -> CompanyModel:
        company = CompanyModel(
            name=name.strip(),
            domain=domain.lower().strip(),
            industry=industry.strip(),
            description=description,
            country_code=country_code.upper()
        )
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def get_by_id(self, company_id: Union[uuid.UUID, str]) -> Optional[CompanyModel]:
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)
        stmt = select(CompanyModel).where(CompanyModel.company_id == company_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_domain(self, domain: str) -> Optional[CompanyModel]:
        stmt = select(CompanyModel).where(CompanyModel.domain == domain.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_companies(self, limit: int = 20, offset: int = 0) -> List[CompanyModel]:
        stmt = select(CompanyModel).order_by(CompanyModel.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_review_with_analysis(
        self,
        company_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        source: str,
        rating: float,
        raw_text: str,
        cleaned_text: str,
        reviewer_name: str,
        fake_probability: float,
        is_suspicious: bool,
        sentiment_score: float,
        sentiment_label: str,
        feature_metrics: dict,
        model_version: str = "v1.0.0"
    ) -> Tuple[ReviewModel, AIAnalysisModel]:
        """
        ATOMIC TRANSACTION: Creates both Review and AIAnalysis records in a single database transaction.
        If either fails, the transaction rolls back cleanly.
        """
        review = ReviewModel(
            company_id=company_id,
            user_id=user_id,
            source=source,
            rating=rating,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            reviewer_name=reviewer_name
        )
        self.session.add(review)
        await self.session.flush() # Generate review_id

        analysis = AIAnalysisModel(
            company_id=company_id,
            review_id=review.review_id,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score,
            fake_probability=fake_probability,
            is_suspicious=is_suspicious,
            feature_metrics=feature_metrics,
            model_version=model_version
        )
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(review)
        await self.session.refresh(analysis)

        return review, analysis

    async def get_review_with_analysis(self, review_id: uuid.UUID) -> Optional[Tuple[ReviewModel, Optional[AIAnalysisModel]]]:
        stmt = select(ReviewModel).options(selectinload(ReviewModel.ai_analysis)).where(ReviewModel.review_id == review_id)
        result = await self.session.execute(stmt)
        review = result.scalar_one_or_none()
        if not review:
            return None
        return review, review.ai_analysis
