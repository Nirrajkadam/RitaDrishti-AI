# RitaDrishti-AI — Resume, Portfolio & Technical Interview Guide

Designed for CDAC PG-DBDA Placement, Tech Lead / CTO Roles, and Engineering Applications (*Data Engineer, Backend Engineer, AI/ML Engineer*).

---

## 1. Resume Project Descriptions

### For Software & AI/ML Engineer Roles
> **RitaDrishti-AI — Lead Software & ML Engineer** | *Python, FastAPI, Scikit-Learn, PyJWT, Argon2, SQLAlchemy 2.0, Next.js, PostgreSQL*
> - Built an authenticated Trust & Risk Intelligence platform processing customer reviews with automatic PII sanitization (emails, phone numbers, credit cards, SSNs).
> - Developed a Scikit-Learn Machine Learning Pipeline (`ColumnTransformer` combining TF-IDF N-gram vectorizer + `StandardScaler` on 6 style features -> `LogisticRegression`) detecting deceptive reviews with real probability scoring.
> - Formulated a multi-factor mathematical Trust Index algorithm incorporating transparency, authenticity, complaint severity penalties, and anomaly signals.
> - Implemented portable SQLAlchemy 2.0 AsyncSession repositories with atomic multi-table transactions, Argon2 password hashing, JWT bearer tokens, and versioned Alembic schema migrations.

---

## 2. STAR Format Interview Preparation

### Question: "Describe a complex data pipeline you designed and how you handled PII security and transactional database persistence."
* **Situation**: In RitaDrishti-AI, public review inputs contained sensitive PII (emails, phone numbers, credit cards, SSNs) and required reliable multi-table atomic storage.
* **Task**: Design a compliant, high-speed ingestion ETL pipeline that sanitizes data before database insertion and atomic analysis.
* **Action**: Implemented regex masking for PII, created atomic AsyncSession database repositories (`ReviewRepository.create_review_with_analysis`), and used Argon2 + PyJWT for secure API authentication.
* **Result**: Guaranteed automated regex redaction of target PII categories (emails, phone numbers, credit cards, SSNs) prior to DB storage and achieved zero partial-state writes through single-transaction database rollbacks.
