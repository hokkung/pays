"""Tests for jobs service (with_job_run wrapper)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.job_run import JobRun
from app.services.jobs import get_recent_runs, with_job_run

pytestmark = pytest.mark.asyncio


def _make_scope(factory: async_sessionmaker[AsyncSession]):
    """Create a patched session_scope that uses the given factory."""

    @asynccontextmanager
    async def mock_scope() -> AsyncIterator[AsyncSession]:
        sess = factory()
        try:
            yield sess
            await sess.commit()
        except Exception:
            await sess.rollback()
            raise
        finally:
            await sess.close()

    return mock_scope


class TestWithJobRun:
    async def test_success(self, engine) -> None:
        """Successful job should record success status."""
        factory = async_sessionmaker(engine, expire_on_commit=False)

        async def job_fn() -> int:
            return 42

        with patch("app.services.jobs.session_scope", _make_scope(factory)):
            result = await with_job_run("test_job", job_fn)

        assert result == 42

        sess = factory()
        try:
            runs = await get_recent_runs(sess, limit=5)
            assert len(runs) == 1
            assert runs[0].job_name == "test_job"
            assert runs[0].status == "success"
            assert runs[0].items_processed == 42
        finally:
            await sess.close()

    async def test_failure(self, engine) -> None:
        """Failed job should record failure status and re-raise."""
        factory = async_sessionmaker(engine, expire_on_commit=False)

        async def job_fn() -> int:
            raise RuntimeError("Something went wrong")

        with patch("app.services.jobs.session_scope", _make_scope(factory)):
            with pytest.raises(RuntimeError, match="Something went wrong"):
                await with_job_run("failing_job", job_fn)

        sess = factory()
        try:
            runs = await get_recent_runs(sess, limit=5)
            assert len(runs) == 1
            assert runs[0].status == "failed"
            assert runs[0].error is not None
            assert "Something went wrong" in runs[0].error
        finally:
            await sess.close()


class TestGetRecentRuns:
    async def test_empty(self, session: AsyncSession) -> None:
        """Empty database should return empty list."""
        runs = await get_recent_runs(session)
        assert runs == []

    async def test_returns_runs(self, session: AsyncSession) -> None:
        """Should return inserted runs."""
        session.add(JobRun(job_name="test", status="success", items_processed=5))
        await session.flush()
        runs = await get_recent_runs(session)
        assert len(runs) == 1
        assert runs[0].job_name == "test"
