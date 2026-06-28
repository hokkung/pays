"""APScheduler setup with a SQLAlchemy job store backed by Postgres."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.jobs.definitions import run_fetch_news, run_refresh_fx, run_refresh_prices

logger = logging.getLogger(__name__)


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler AsyncIO scheduler.

    Jobs are stored in Postgres (SQLAlchemyJobStore) so they survive restarts.
    Each job calls a thin wrapper around a service function.

    Returns:
        A configured (but not started) AsyncIOScheduler.
    """
    settings = get_settings()
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        run_fetch_news,
        CronTrigger.from_crontab(settings.fetch_news_cron),
        id="fetch_news",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_refresh_prices,
        CronTrigger.from_crontab(settings.refresh_prices_cron),
        id="refresh_prices",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_refresh_fx,
        CronTrigger.from_crontab(settings.refresh_fx_cron),
        id="refresh_fx",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    return scheduler
