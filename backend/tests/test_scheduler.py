"""Tests for scheduler setup."""

from app.jobs.scheduler import create_scheduler


def test_create_scheduler_has_jobs() -> None:
    """create_scheduler should configure all three jobs."""
    scheduler = create_scheduler()
    jobs = scheduler.get_jobs()
    job_ids = {j.id for j in jobs}
    assert job_ids == {"fetch_news", "refresh_prices", "refresh_fx"}


def test_scheduler_job_triggers() -> None:
    """Each job should have a cron trigger."""
    scheduler = create_scheduler()
    jobs = scheduler.get_jobs()
    for job in jobs:
        assert job.trigger is not None
