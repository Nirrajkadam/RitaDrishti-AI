# RitaDrishti-AI
### Enterprise Trust Intelligence & Autonomous Risk Auditing Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

---

## Executive Overview

**RitaDrishti-AI** is an AI-powered Trust Intelligence and Risk Auditing Platform designed for enterprise risk assessment, fake review detection, and reputational auditing.

The system ingests customer review text, executes regex PII sanitization (masking emails, phone numbers, credit cards, and SSNs), processes features through a trained **Scikit-Learn Machine Learning Pipeline** (`ColumnTransformer`: TF-IDF N-grams + 6 style features -> `LogisticRegression`), and persists records atomically in a relational database (`SQLite` for unit testing, `PostgreSQL` for production via SQLAlchemy 2.0 and Alembic).

---

## Key Working Capabilities (Core Vertical Workflow)

| Layer | Technology | Functional Responsibility | Status |
| :--- | :--- | :--- | :--- |
| **Security & Authentication** | `pwdlib[argon2]`, `pyjwt` | Public rate-limited registration/login endpoints (`POST /auth/register`, `POST /auth/login`); Bearer JWT validation. | **Verified Prototype Layer** |
| **Data Sanitization** | Python Regex Engine | Automated PII redaction (emails, phone numbers, payment details, SSNs) before persistence and ML processing. | **Verified Prototype Layer** |
| **Fake Review ML Classifier** | `scikit-learn` Pipeline, `joblib` | Real probability scoring $[0.0, 1.0]$ combining TF-IDF vectorization with character case ratios, exclamation density, and lexical entropy. | **Verified Prototype Layer** |
| **Relational Storage & Migration** | `SQLAlchemy` 2.0, `Alembic`, `asyncpg`, `aiosqlite` | Portable AsyncSession repositories with atomic multi-table transactions and versioned Alembic schema migrations. | **Verified Prototype Layer** |
| **Frontend Applications** | `Next.js` 14 (App Router) & `Streamlit` | Modern web interface (Next.js) and interactive analytical dashboard (Streamlit). | **Verified Prototype Layer** |
| **RAG & Multi-Agent Subsystems** | `Ollama` / `Qdrant` / `CrewAI` | Vector search, Llama 3 LLM copilot, and autonomous agent audit briefs (disabled by default via feature flags). | **Experimental (Flagged)** |
| **NPU Hardware Acceleration** | ONNX Runtime DirectML / QNN | Edge hardware acceleration on Qualcomm Snapdragon NPU processors. | **Experimental (Flagged)** |

---

## Verified End-to-End Vertical Workflow

```text
Authenticated User
  ├──> POST /api/v1/auth/register & /login (Argon2 + PyJWT)
  ├──> POST /api/v1/companies (Authenticated DB company record creation)
  └──> POST /api/v1/reviews/analyze (Authenticated)
        ├──> PII Redaction (`sanitize_text`: emails, phones, SSNs, credit cards)
        ├──> ML Inference (`FakeReviewEngine`: ColumnTransformer + LogisticRegression)
        ├──> Atomic DB Persistence (`ReviewRepository.create_review_with_analysis`)
        └──> Returns { review: ReviewResponse, analysis: AIAnalysisResponse }
```

---

## Subsystem Feature Flags

To prevent ungrounded mock responses, optional subsystems are strictly controlled via environment feature flags in `backend/app/config.py`:

```ini
ENABLE_CREWAI=false   # Toggles CrewAI Multi-Agent audit reports
ENABLE_QDRANT=false   # Toggles Qdrant vector database search
ENABLE_OLLAMA=false   # Toggles Ollama Llama 3 RAG AI Copilot
ENABLE_NPU=false      # Toggles Snapdragon NPU hardware acceleration
```
*When disabled, endpoints return structured HTTP `503 Service Unavailable` errors with explicit service codes rather than synthetic fallbacks.*

---

## Quickstart Guide

### 1. Local Setup
```bash
# Clone repository
git clone https://github.com/Nirrajkadam/RitaDrishti-AI.git
cd RitaDrishti-AI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run machine learning model training script
python backend/app/ml/train_fake_review_model.py
```

### 2. Run Database Migrations
```bash
alembic -c backend/alembic.ini upgrade head
```

### 3. Run Pytest Test Suite & Coverage
```bash
pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing
```

### 4. Start API Gateway
```bash
python backend/app/main.py
```
- API Base URL: `http://localhost:8000`
- Swagger Documentation: `http://localhost:8000/docs`

### 5. Start Next.js Frontend
```bash
cd frontend
npm ci
npm run build
npm start
```
- Frontend URL: `http://localhost:3000`

### 6. Single-Command Docker Deployment
```bash
docker-compose up --build -d
```

---

## Author & License

Developed by **Niraj Kadam** (Computer Science Graduate & CDAC PG-DBDA Scholar).

- **GitHub Profile**: [github.com/Nirrajkadam](https://github.com/Nirrajkadam)
- **Repository**: [RitaDrishti-AI](https://github.com/Nirrajkadam/RitaDrishti-AI)

Released under the **MIT License**.
