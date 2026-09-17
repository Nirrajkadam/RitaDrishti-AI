-- SentinelX Trust AI — Enterprise PostgreSQL Database Schema
-- Version: 1.0.0
-- Database: PostgreSQL 18+

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- -----------------------------------------------------------------------------
-- 1. COMPANIES TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS companies (
    company_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    industry VARCHAR(100) NOT NULL,
    description TEXT,
    verified_status BOOLEAN DEFAULT FALSE,
    country_code VARCHAR(10) DEFAULT 'US',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_name_trgm ON companies USING gin(name gin_trgm_ops);

-- -----------------------------------------------------------------------------
-- 2. USERS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    role VARCHAR(50) DEFAULT 'analyst', -- admin, analyst, enterprise_user
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- -----------------------------------------------------------------------------
-- 3. REVIEWS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL, -- e.g., 'Trustpilot', 'Google', 'G2'
    rating NUMERIC(3, 2) CHECK (rating >= 1.00 AND rating <= 5.00),
    raw_text TEXT NOT NULL,
    cleaned_text TEXT,
    reviewer_name VARCHAR(150),
    reviewer_metadata JSONB DEFAULT '{}'::jsonb,
    review_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_company_id ON reviews(company_id);
CREATE INDEX idx_reviews_source ON reviews(source);
CREATE INDEX idx_reviews_date ON reviews(review_date DESC);
CREATE INDEX idx_reviews_raw_text_trgm ON reviews USING gin(raw_text gin_trgm_ops);

-- -----------------------------------------------------------------------------
-- 4. COMPLAINTS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL, -- e.g., 'BBB', 'ConsumerAffairs', 'CustomForm'
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    resolution_status VARCHAR(50) DEFAULT 'unresolved', -- 'resolved', 'pending', 'unresolved'
    severity_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    complaint_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_complaints_company_id ON complaints(company_id);
CREATE INDEX idx_complaints_status ON complaints(resolution_status);
CREATE INDEX idx_complaints_severity ON complaints(severity_level);

-- -----------------------------------------------------------------------------
-- 5. NEWS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS news (
    news_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    headline VARCHAR(500) NOT NULL,
    source_url TEXT NOT NULL,
    publisher VARCHAR(150),
    summary TEXT,
    publish_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_company_id ON news(company_id);
CREATE INDEX idx_news_publish_date ON news(publish_date DESC);

-- -----------------------------------------------------------------------------
-- 6. AI_ANALYSIS TABLE (Sentiment & Fake Review Scores)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    review_id UUID REFERENCES reviews(review_id) ON DELETE SET NULL,
    sentiment_label VARCHAR(20) NOT NULL, -- 'positive', 'negative', 'neutral'
    sentiment_score NUMERIC(5, 4) CHECK (sentiment_score >= -1.0000 AND sentiment_score <= 1.0000),
    fake_probability NUMERIC(5, 4) CHECK (fake_probability >= 0.0000 AND fake_probability <= 1.0000),
    is_suspicious BOOLEAN DEFAULT FALSE,
    feature_breakdown JSONB DEFAULT '{}'::jsonb, -- Store extracted N-grams, readability, entropy
    model_version VARCHAR(50) DEFAULT 'v1.0.0-distilbert-xgboost',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_analysis_company_id ON ai_analysis(company_id);
CREATE INDEX idx_ai_analysis_review_id ON ai_analysis(review_id);
CREATE INDEX idx_ai_analysis_sentiment ON ai_analysis(sentiment_label);
CREATE INDEX idx_ai_analysis_suspicious ON ai_analysis(is_suspicious);

-- -----------------------------------------------------------------------------
-- 7. TRUST_SCORES TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trust_scores (
    score_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    trust_index NUMERIC(5, 2) CHECK (trust_index >= 0.00 AND trust_index <= 100.00),
    transparency_score NUMERIC(5, 2) CHECK (transparency_score >= 0.00 AND transparency_score <= 100.00),
    sentiment_factor NUMERIC(5, 2),
    fake_review_penalty NUMERIC(5, 2),
    complaint_penalty NUMERIC(5, 2),
    trust_tier VARCHAR(20) DEFAULT 'Moderate Trust', -- 'High Trust', 'Moderate Trust', 'Low Trust', 'Critical Alert'
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trust_scores_company_id ON trust_scores(company_id);
CREATE INDEX idx_trust_scores_trust_index ON trust_scores(trust_index DESC);

-- -----------------------------------------------------------------------------
-- 8. RISK_SCORES TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS risk_scores (
    risk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    overall_risk_score NUMERIC(5, 2) CHECK (overall_risk_score >= 0.00 AND overall_risk_score <= 100.00),
    fraud_risk NUMERIC(5, 2),
    regulatory_risk NUMERIC(5, 2),
    reputational_risk NUMERIC(5, 2),
    risk_level VARCHAR(20) DEFAULT 'Medium', -- 'Low', 'Medium', 'High', 'Severe'
    anomaly_signals JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_scores_company_id ON risk_scores(company_id);
CREATE INDEX idx_risk_scores_overall_risk ON risk_scores(overall_risk_score DESC);

-- -----------------------------------------------------------------------------
-- 9. REPORTS TABLE (Multi-Agent & Executive Audits)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    report_title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) DEFAULT 'executive_audit', -- 'executive_audit', 'risk_assessment', 'compliance_brief'
    markdown_content TEXT NOT NULL,
    executive_summary TEXT,
    generated_by VARCHAR(100) DEFAULT 'CrewAI Multi-Agent System',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_company_id ON reports(company_id);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);

-- -----------------------------------------------------------------------------
-- OPTIMIZATION & PERFORMANCE SUGGESTIONS
-- -----------------------------------------------------------------------------
-- 1. Table Partitioning: For high-scale production deployment, partition the `reviews` and `ai_analysis`
--    tables by `review_date` / `created_at` using PostgreSQL RANGE partitioning.
-- 2. Trigram GIN Indexes: `pg_trgm` indexes on `raw_text` and company `name` enable sub-10ms full-text search.
-- 3. JSONB GIN Indexes: Create specific JSONB path indexes for fast metadata lookup:
--    CREATE INDEX idx_reviews_metadata_gin ON reviews USING gin (reviewer_metadata);
-- 4. Connection Pooling: Use PgBouncer or SQLAlchemy Async Engine connection pools with max_overflow=20.
