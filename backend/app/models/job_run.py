"""Job run model for lightweight observability of scheduled fetches."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class JobRun(Base):
    """A record of a single job execution (fetch_news, refresh_prices, etc.).

    Attributes:
        job_name: Name of the job.
        started_at: When the job started.
        finished_at: When the job finished (null if still running).
        status: "running", "success", or "failed".
        items_processed: Number of items fetched/persisted.
        error: Error message if the job failed.
    """

    __tablename__ = "job_runs"

    job_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    items_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
