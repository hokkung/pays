"""Jobs API router (manual triggers + run history)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthToken, DbSession
from app.jobs.definitions import JOB_REGISTRY
from app.schemas.job_run import JobRunListResponse, JobRunResponse, JobTriggerResponse
from app.services import jobs as jobs_service

router = APIRouter()


@router.post("/{job_name}/run", response_model=JobTriggerResponse)
async def run_job(
    job_name: str,
    _token: None = AuthToken,
) -> JobTriggerResponse:
    """Manually trigger a job by name.

    Available jobs: fetch_news, refresh_prices, refresh_fx.
    """
    job_fn = JOB_REGISTRY.get(job_name)
    if job_fn is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown job: {job_name}",
        )

    try:
        count = await job_fn()
        return JobTriggerResponse(job_name=job_name, status="success", items_processed=count)
    except Exception as exc:
        return JobTriggerResponse(
            job_name=job_name, status="failed", items_processed=0, error=str(exc)[:500]
        )


@router.get("/runs", response_model=JobRunListResponse)
async def list_runs(
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
    limit: int = 20,
) -> JobRunListResponse:
    """Get recent job run history."""
    runs = await jobs_service.get_recent_runs(session, limit=limit)
    return JobRunListResponse(items=[JobRunResponse.model_validate(r) for r in runs])
