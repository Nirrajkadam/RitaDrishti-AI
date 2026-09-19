"""
RitaDrishti-AI — Security & JWT Authentication Module
Uses Argon2 (via pwdlib / passlib) for password hashing and PyJWT for bearer token validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.core.database import get_db
from backend.app.core.exceptions import AuthenticationError
from backend.app.db.models import UserModel
from backend.app.db.repositories import UserRepository

# Initialize Password Hash Engine using Argon2
password_hash_engine = PasswordHash((Argon2Hasher(),))
security_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hashes plain text password using Argon2."""
    return password_hash_engine.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against Argon2 hash."""
    return password_hash_engine.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generates signed JWT access token containing exp, iss, aud, and token_type claims."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "token_type": "access"
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """Validates JWT expiration, issuer, audience, and token type."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={"verify_exp": True, "verify_iss": True, "verify_aud": True}
        )
        if payload.get("token_type") != "access":
            raise AuthenticationError("Invalid token type claim", code="INVALID_TOKEN_TYPE")
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("JWT token has expired", code="TOKEN_EXPIRED")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"JWT validation failed: {str(e)}", code="INVALID_TOKEN")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """FastAPI dependency protecting write endpoints with HTTP Bearer token validation and DB user fetch."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authentication credentials were not provided", code="UNAUTHORIZED")

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Subject claim missing in token", code="INVALID_TOKEN_SUBJECT")

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID UUID format in token", code="INVALID_TOKEN_SUBJECT")

    repo = UserRepository(db)
    user = await repo.get_by_id(user_uuid)
    if not user:
        raise AuthenticationError("User account no longer exists", code="USER_NOT_FOUND")

    return user
