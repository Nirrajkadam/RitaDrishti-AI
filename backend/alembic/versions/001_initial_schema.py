"""Initial RitaDrishti-AI Database Schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='analyst'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 2. companies table
    op.create_table(
        'companies',
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('verified_status', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('country_code', sa.String(length=10), nullable=False, server_default='US'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('company_id')
    )
    op.create_index(op.f('ix_companies_domain'), 'companies', ['domain'], unique=True)
    op.create_index(op.f('ix_companies_industry'), 'companies', ['industry'], unique=False)

    # 3. reviews table
    op.create_table(
        'reviews',
        sa.Column('review_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('cleaned_text', sa.Text(), nullable=True),
        sa.Column('reviewer_name', sa.String(length=150), nullable=False, server_default='Anonymous'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('review_id')
    )
    op.create_index(op.f('ix_reviews_company_id'), 'reviews', ['company_id'], unique=False)
    op.create_index(op.f('ix_reviews_user_id'), 'reviews', ['user_id'], unique=False)

    # 4. ai_analysis table
    op.create_table(
        'ai_analysis',
        sa.Column('analysis_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('review_id', sa.Uuid(), nullable=True),
        sa.Column('sentiment_label', sa.String(length=20), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('fake_probability', sa.Float(), nullable=False),
        sa.Column('is_suspicious', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('feature_metrics', sa.JSON(), nullable=False),
        sa.Column('model_version', sa.String(length=100), nullable=False, server_default='v1.0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.review_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('analysis_id')
    )
    op.create_index(op.f('ix_ai_analysis_company_id'), 'ai_analysis', ['company_id'], unique=False)
    op.create_index(op.f('ix_ai_analysis_review_id'), 'ai_analysis', ['review_id'], unique=False)

    # 5. trust_scores table
    op.create_table(
        'trust_scores',
        sa.Column('score_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('trust_index', sa.Float(), nullable=False),
        sa.Column('transparency_score', sa.Float(), nullable=False),
        sa.Column('sentiment_factor', sa.Float(), nullable=False),
        sa.Column('fake_review_penalty', sa.Float(), nullable=False),
        sa.Column('complaint_penalty', sa.Float(), nullable=False),
        sa.Column('trust_tier', sa.String(length=20), nullable=False, server_default='Moderate Trust'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('score_id')
    )
    op.create_index(op.f('ix_trust_scores_company_id'), 'trust_scores', ['company_id'], unique=False)


def downgrade() -> None:
    op.drop_table('trust_scores')
    op.drop_table('ai_analysis')
    op.drop_table('reviews')
    op.drop_table('companies')
    op.drop_table('users')
