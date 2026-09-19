"""
RitaDrishti-AI — FastAPI Main Server Entrypoint
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.core.database import init_db
from backend.app.core.exceptions import RitaDrishtiException
from backend.app.api.v1.endpoints import (
    auth, companies, reviews, trust, risk, chat, reports, alerts, search
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan setup & teardown."""
    # Ensure database tables exist (SQLite fallback / dev setup)
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI-Powered Trust Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(RitaDrishtiException)
async def ritadrishti_exception_handler(request: Request, exc: RitaDrishtiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable
            }
        }
    )


# Register Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews & ML Analysis"])
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
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
