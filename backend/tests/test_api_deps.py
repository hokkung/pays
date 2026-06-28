"""Tests for API auth dependency."""

import pytest
from fastapi import HTTPException

from app.api.deps import verify_token

pytestmark = pytest.mark.asyncio


async def test_verify_token_missing() -> None:
    """Missing Authorization header should raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_token(None)
    assert exc_info.value.status_code == 401


async def test_verify_token_wrong() -> None:
    """Wrong token should raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_token("Bearer wrong-token")
    assert exc_info.value.status_code == 401


async def test_verify_token_correct() -> None:
    """Correct token should not raise."""
    await verify_token("Bearer test-token")


async def test_verify_token_no_bearer_prefix() -> None:
    """Token without Bearer prefix should raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_token("test-token")
    assert exc_info.value.status_code == 401


async def test_verify_token_empty() -> None:
    """Empty string should raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await verify_token("")
    assert exc_info.value.status_code == 401
