"""Shared test fixtures for async DB sessions, app, and HTTP client."""

import os

# Set test environment BEFORE importing app modules.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("API_TOKEN", "test-token")

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.api.deps import get_db_session, verify_token  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import *  # noqa: E402, F403 — register all models
from app.models.base import Base  # noqa: E402


@pytest_asyncio.fixture
async def engine():
    """Create an in-memory SQLite async engine with all tables.

    Uses StaticPool so all sessions share a single connection (required for
    in-memory SQLite to be visible across sessions).
    """
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:  # type: ignore[misc]
    """Provide an async DB session backed by in-memory SQLite."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    sess = factory()
    try:
        yield sess
    finally:
        await sess.close()


@pytest_asyncio.fixture
async def app(engine):
    """Create a FastAPI app with test dependency overrides."""
    application = create_app()
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db() -> AsyncSession:
        sess = factory()
        try:
            yield sess
            await sess.commit()
        except Exception:
            await sess.rollback()
            raise
        finally:
            await sess.close()

    async def override_auth() -> None:
        return None

    application.dependency_overrides[get_db_session] = override_db
    application.dependency_overrides[verify_token] = override_auth
    yield application
    application.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    """Provide an async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
