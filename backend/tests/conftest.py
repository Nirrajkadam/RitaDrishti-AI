"""
RitaDrishti-AI — Pytest Fixtures Configuration
Provides in-memory SQLite AsyncSession and httpx.AsyncClient fixtures for fast isolated testing.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.db.models import Base

# In-memory SQLite engine for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Creates isolated in-memory database tables for each test function."""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Provides httpx AsyncClient connected to the FastAPI app with test db session dependency override."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient):
    """Registers and authenticates a test user, returning Bearer authorization headers."""
    user_payload = {
        "email": "testuser@ritadrishti.ai",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=user_payload)
    assert reg_resp.status_code == 201

    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "TestPassword123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
