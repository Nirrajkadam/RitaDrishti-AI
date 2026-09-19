"""
RitaDrishti-AI — Application Settings & Feature Configuration
"""

import sys
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "RitaDrishti-AI"
    APP_ENV: str = "development" # "development", "testing", "production"
    DEBUG: bool = True
    
    # Database Settings (Supports SQLite for testing and PostgreSQL for production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./ritadrishti.db"
    
    # Vector DB & LLM Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    
    # Security & Auth
    JWT_SECRET: str = "ritadrishti_dev_secret_change_in_production_2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "ritadrishti-api"
    JWT_AUDIENCE: str = "ritadrishti-users"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOWED_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501", "http://127.0.0.1:3000"]
    
    # Feature Flags for Optional Subsystems (Disabled by default until Phase 4)
    ENABLE_CREWAI: bool = False
    ENABLE_QDRANT: bool = False
    ENABLE_OLLAMA: bool = False
    ENABLE_NPU: bool = False


settings = Settings()


def validate_production_secrets():
    """Fails fast on startup if default JWT secret is used in production environment."""
    if settings.APP_ENV == "production" and "change_in_production" in settings.JWT_SECRET:
        print("[CRITICAL SECURITY ERROR]: Production environment detected with default JWT_SECRET!", file=sys.stderr)
        sys.exit(1)
