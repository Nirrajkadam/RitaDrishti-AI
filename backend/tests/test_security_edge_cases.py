"""
Behavioral Unit Tests: Security, Authentication, Rate Limiting & Token Expiration
"""

import pytest
from datetime import timedelta
from fastapi import Request
from backend.app.config import settings
from backend.app.core.security import (
    create_access_token, decode_access_token, hash_password, verify_password
)
from backend.app.core.rate_limiter import RateLimiter
from backend.app.core.exceptions import AuthenticationError, RitaDrishtiException


def test_jwt_token_creation_and_expiration():
    token = create_access_token("user_123", expires_delta=timedelta(minutes=15))
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user_123"

    # Expired token test
    expired_token = create_access_token("user_123", expires_delta=timedelta(seconds=-10))
    with pytest.raises(AuthenticationError):
        decode_access_token(expired_token)

    # Invalid string token test
    with pytest.raises(AuthenticationError):
        decode_access_token("malformed.jwt.payload")


def test_argon2_password_hashing():
    pwd = "ComplexPassword987!"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed)
    assert not verify_password("IncorrectPassword", hashed)


def test_sliding_window_rate_limiter():
    # Force APP_ENV to production for testing rate limiter execution
    old_env = settings.APP_ENV
    settings.APP_ENV = "production"
    try:
        limiter = RateLimiter(requests_limit=2, window_seconds=60)

        class DummyClient:
            host = "192.168.1.100"

        class DummyRequest:
            client = DummyClient()

        req = DummyRequest()
        limiter(req)
        limiter(req)

        with pytest.raises(RitaDrishtiException) as exc_info:
            limiter(req)
        assert exc_info.value.status_code == 429
    finally:
        settings.APP_ENV = old_env
