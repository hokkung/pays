"""Tests for Jobs API endpoints."""

from unittest.mock import AsyncMock

import pytest

from app.jobs.definitions import JOB_REGISTRY

pytestmark = pytest.mark.asyncio


class TestJobsAPI:
    async def test_trigger_unknown_job(self, client: object) -> None:
        """Unknown job name should return 404."""
        resp = await client.post("/api/jobs/nonexistent/run")  # type: ignore[union-attr]
        assert resp.status_code == 404

    async def test_trigger_success(self, client: object) -> None:
        """Known job should run and return success."""
        mock_fn = AsyncMock(return_value=10)
        original = JOB_REGISTRY.copy()
        JOB_REGISTRY.clear()
        JOB_REGISTRY["test_job"] = mock_fn
        try:
            resp = await client.post("/api/jobs/test_job/run")  # type: ignore[union-attr]
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["items_processed"] == 10
        finally:
            JOB_REGISTRY.clear()
            JOB_REGISTRY.update(original)

    async def test_trigger_failure(self, client: object) -> None:
        """Job that raises should return failed status."""
        mock_fn = AsyncMock(side_effect=RuntimeError("fail"))
        original = JOB_REGISTRY.copy()
        JOB_REGISTRY.clear()
        JOB_REGISTRY["bad_job"] = mock_fn
        try:
            resp = await client.post("/api/jobs/bad_job/run")  # type: ignore[union-attr]
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "failed"
            assert data["error"] is not None
        finally:
            JOB_REGISTRY.clear()
            JOB_REGISTRY.update(original)

    async def test_list_runs(self, client: object) -> None:
        """GET /api/jobs/runs should return run list."""
        resp = await client.get("/api/jobs/runs")  # type: ignore[union-attr]
        assert resp.status_code == 200
        assert "items" in resp.json()
