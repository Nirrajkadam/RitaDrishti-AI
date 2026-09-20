"""
RitaDrishti-AI — Authentication API & Security Unit Tests
"""

import pytest
from httpx import AsyncClient
from backend.app.core.security import (
    hash_password, verify_password, create_access_token, decode_access_token
)


@pytest.mark.asyncio
async def test_password_hashing_argon2():
    password = "MySecurePassword2026!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


@pytest.mark.asyncio
async def test_jwt_token_generation_and_decoding():
    subject = "11111111-1111-1111-1111-111111111111"
    token = create_access_token(subject=subject)
    decoded = decode_access_token(token)
    assert decoded["sub"] == subject
    assert decoded["iss"] == "ritadrishti-api"
    assert decoded["token_type"] == "access"


@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient):
    payload = {
        "email": "user1@ritadrishti.ai",
        "username": "user1",
        "password": "Password123!",
        "full_name": "User One"
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "user1"
    assert data["email"] == "user1@ritadrishti.ai"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_user_registration_duplicate_username(client: AsyncClient):
    payload = {
        "email": "user1@ritadrishti.ai",
        "username": "user1",
        "password": "Password123!"
    }
    await client.post("/api/v1/auth/register", json=payload)

    # Attempt duplicate username
    dup_payload = {
        "email": "user2@ritadrishti.ai",
        "username": "user1",
        "password": "Password123!"
    }
    resp = await client.post("/api/v1/auth/register", json=dup_payload)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient):
    reg_payload = {
        "email": "user_login@ritadrishti.ai",
        "username": "user_login",
        "password": "SecretPassword123!"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "user_login",
        "password": "SecretPassword123!"
    })
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_login_invalid_password(client: AsyncClient):
    reg_payload = {
        "email": "user_invalid@ritadrishti.ai",
        "username": "user_invalid",
        "password": "SecretPassword123!"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "user_invalid",
        "password": "WrongPassword!"
    })
    assert login_resp.status_code == 401
    assert login_resp.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    company_payload = {
        "name": "Unauthorized Company",
        "domain": "unauth.com",
        "industry": "Fintech"
    }
    resp = await client.post("/api/v1/companies/", json=company_payload)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] in ("UNAUTHORIZED", "AUTHENTICATION_FAILED")


@pytest.mark.asyncio
async def test_get_current_authenticated_user_endpoint(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user_id" in data
    assert "username" in data
