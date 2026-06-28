"""Job run recording service for lightweight observability."""

import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import session_scope
from app.models.job_run import JobRun

logger = logging.getLogger(__name__)


async def with_job_run(
    job_name: str,
    job_fn: Callable[[], Awaitable[int]],
) -> int:
    """Execute a job function and record the result in job_runs.

    Creates a JobRun record with status "running" before execution,
    then updates it to "success" or "failed" after completion.

    Args:
        job_name: Name of the job (e.g. "fetch_news").
        job_fn: An async callable that returns the number of items processed.

    Returns:
        The number of items processed by the job.
    """
    run_id = await _create_run(job_name)

    try:
        result = await job_fn()
        await _finish_run(run_id, "success", items=result)
        return result
    except Exception as exc:
        await _finish_run(run_id, "failed", error=str(exc)[:1000])
        raise


async def _create_run(job_name: str) -> int:
    """Create a job_run record and return its ID."""
    async with session_scope() as session:
        run = JobRun(job_name=job_name, status="running")
        session.add(run)
        await session.flush()
        return run.id


async def _finish_run(
    run_id: int,
    status: str,
    items: int = 0,
    error: str | None = None,
) -> None:
    """Update a job_run record with the final status."""
    async with session_scope() as session:
        run = await session.get(JobRun, run_id)
        if run is not None:
            run.status = status
            run.items_processed = items
            run.error = error
            run.finished_at = datetime.now(UTC)


async def get_recent_runs(session: AsyncSession, limit: int = 20) -> list[JobRun]:
    """Get recent job runs for observability.

    Args:
        session: An async DB session.
        limit: Maximum number of runs to return.

    Returns:
        A list of recent JobRun records, newest first.
    """
    result = await session.execute(select(JobRun).order_by(JobRun.started_at.desc()).limit(limit))
    return list(result.scalars())
