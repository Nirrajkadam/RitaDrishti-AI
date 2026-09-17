"""
RitaDrishti-AI — FastAPI Main Server Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.endpoints import companies, reviews, trust, risk, chat, reports, alerts, search

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI-Powered Trust Intelligence & Multi-Agent Auditing Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit Frontend & External Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews & Sentiment"])
app.include_router(trust.router, prefix="/api/v1/trust", tags=["Trust Scores"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Intelligence"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["RAG AI Copilot"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Multi-Agent Reports"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Real-Time Alerts"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Global & Natural Language Search"])


@app.get("/")
async def root():
    return {
        "status": "online",
        "platform": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
