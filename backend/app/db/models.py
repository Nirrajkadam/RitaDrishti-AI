"""
RitaDrishti-AI — Portable SQLAlchemy 2.0 ORM Database Models
Uses portable SQLAlchemy types (Uuid, JSON, DateTime) compatible with both SQLite and PostgreSQL.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, Uuid, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="analyst")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    @property
    def hashed_password(self) -> str:
        return self.password_hash


class CompanyModel(Base):
    __tablename__ = "companies"

    company_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    verified_status: Mapped[bool] = mapped_column(Boolean, default=False)
    country_code: Mapped[str] = mapped_column(String(10), default="US")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    reviews = relationship("ReviewModel", back_populates="company", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysisModel", back_populates="company", cascade="all, delete-orphan")
    trust_scores = relationship("TrustScoreModel", back_populates="company", cascade="all, delete-orphan")


class ReviewModel(Base):
    __tablename__ = "reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_text: Mapped[str] = mapped_column(Text, nullable=True)
    reviewer_name: Mapped[str] = mapped_column(String(150), default="Anonymous")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = relationship("CompanyModel", back_populates="reviews")
    ai_analysis = relationship("AIAnalysisModel", back_populates="review", uselist=False, cascade="all, delete-orphan")


class AIAnalysisModel(Base):
    __tablename__ = "ai_analysis"

    analysis_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    review_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("reviews.review_id", ondelete="CASCADE"), nullable=True, index=True)
    sentiment_label: Mapped[str] = mapped_column(String(20), nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    fake_probability: Mapped[float] = mapped_column(Float, nullable=False)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    feature_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    model_version: Mapped[str] = mapped_column(String(100), default="v1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = relationship("CompanyModel", back_populates="ai_analyses")
    review = relationship("ReviewModel", back_populates="ai_analysis")


class TrustScoreModel(Base):
    __tablename__ = "trust_scores"

    score_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    trust_index: Mapped[float] = mapped_column(Float, nullable=False)
    transparency_score: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment_factor: Mapped[float] = mapped_column(Float, nullable=False)
    fake_review_penalty: Mapped[float] = mapped_column(Float, nullable=False)
    complaint_penalty: Mapped[float] = mapped_column(Float, nullable=False)
    trust_tier: Mapped[str] = mapped_column(String(20), default="Moderate Trust")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    company = relationship("CompanyModel", back_populates="trust_scores")
