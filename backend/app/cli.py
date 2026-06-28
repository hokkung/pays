"""Typer CLI for running jobs manually and managing the database."""

import asyncio
import logging

import typer

from app.db import session_scope
from app.services import fx as fx_service
from app.services import news as news_service
from app.services import prices as prices_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = typer.Typer(name="pays", help="Pays CLI — run jobs and manage the database.")
jobs_app = typer.Typer(name="jobs", help="Run scheduled jobs manually.")
db_app = typer.Typer(name="db", help="Database management commands.")

app.add_typer(jobs_app, name="jobs")
app.add_typer(db_app, name="db")


@jobs_app.command("fetch-news")
def fetch_news() -> None:
    """Fetch news for all enabled topics."""
    count = asyncio.run(_fetch_news())
    typer.echo(f"Fetched {count} new articles")


async def _fetch_news() -> int:
    async with session_scope() as session:
        return await news_service.fetch_news(session)


@jobs_app.command("refresh-prices")
def refresh_prices() -> None:
    """Refresh prices for all enabled assets."""
    count = asyncio.run(_refresh_prices())
    typer.echo(f"Refreshed {count} prices")


async def _refresh_prices() -> int:
    async with session_scope() as session:
        return await prices_service.refresh_prices(session)


@jobs_app.command("refresh-fx")
def refresh_fx() -> None:
    """Refresh FX rates (USD/THB, EUR/THB)."""
    count = asyncio.run(_refresh_fx())
    typer.echo(f"Refreshed {count} FX rates")


async def _refresh_fx() -> int:
    async with session_scope() as session:
        return await fx_service.refresh_fx(session)


@db_app.command("scheduler")
def run_scheduler() -> None:
    """Run the APScheduler worker process (blocks)."""
    from app.jobs.scheduler import create_scheduler

    scheduler = create_scheduler()
    scheduler.start()
    typer.echo("Scheduler started. Press Ctrl+C to stop.")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    app()
