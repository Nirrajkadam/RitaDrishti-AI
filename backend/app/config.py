"""
SentinelX Trust AI — Application Settings & Configuration
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SentinelX Trust AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://sentinelx:sentinelx_secret@localhost:5432/sentinelx_trust_db"
    
    # Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # Ollama LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    
    # Security
    JWT_SECRET: str = "super_secret_jwt_key_sentinelx_2026"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
