"""Job definitions: thin wrappers around service functions with job_run recording."""

from collections.abc import Awaitable, Callable

from app.db import session_scope
from app.services import fx as fx_service
from app.services import jobs as jobs_service
from app.services import news as news_service
from app.services import prices as prices_service


async def run_fetch_news() -> int:
    """Execute the fetch_news job with job_run recording.

    Returns:
        The number of new articles fetched.
    """

    async def _run() -> int:
        async with session_scope() as session:
            return await news_service.fetch_news(session)

    return await jobs_service.with_job_run("fetch_news", _run)


async def run_refresh_prices() -> int:
    """Execute the refresh_prices job with job_run recording.

    Returns:
        The number of prices refreshed.
    """

    async def _run() -> int:
        async with session_scope() as session:
            return await prices_service.refresh_prices(session)

    return await jobs_service.with_job_run("refresh_prices", _run)


async def run_refresh_fx() -> int:
    """Execute the refresh_fx job with job_run recording.

    Returns:
        The number of FX rates refreshed.
    """

    async def _run() -> int:
        async with session_scope() as session:
            return await fx_service.refresh_fx(session)

    return await jobs_service.with_job_run("refresh_fx", _run)


JOB_REGISTRY: dict[str, Callable[[], Awaitable[int]]] = {
    "fetch_news": run_fetch_news,
    "refresh_prices": run_refresh_prices,
    "refresh_fx": run_refresh_fx,
}
