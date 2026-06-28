"""Pydantic schemas for JobRun."""

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class JobRunResponse(ORMModel):
    """Job run response."""

    id: int
    job_name: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    items_processed: int
    error: str | None


class JobRunListResponse(BaseModel):
    """List of recent job runs."""

    items: list[JobRunResponse]


class JobTriggerResponse(BaseModel):
    """Response after manually triggering a job."""

    job_name: str
    status: str
    items_processed: int
    error: str | None = None
