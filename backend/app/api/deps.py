"""FastAPI dependencies: auth, DB session, pagination."""

from collections.abc import AsyncIterator

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield an async DB session for the request lifecycle."""
    from app.db import get_db

    async for session in get_db():
        yield session


async def verify_token(authorization: str | None = Header(None)) -> None:
    """Validate the bearer API token.

    Args:
        authorization: The Authorization header value.

    Raises:
        HTTPException: 401 if the token is missing or invalid.
    """
    settings = get_settings()
    expected = f"Bearer {settings.api_token}"
    if authorization is None or authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class PaginationParams:
    """Common pagination query parameters."""

    def __init__(
        self,
        limit: int = Query(50, ge=1, le=200),
        cursor: str | None = Query(None),
    ) -> None:
        self.limit = limit
        self.cursor = cursor


DbSession = Depends(get_db_session)
AuthToken = Depends(verify_token)
