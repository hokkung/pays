"""Tests for Topics API endpoints."""

import pytest

pytestmark = pytest.mark.asyncio


class TestTopicsCRUD:
    """End-to-end CRUD tests for the topics API."""

    async def test_create_topic(self, client: object) -> None:
        """POST /api/topics should create and return a topic."""
        resp = await client.post(  # type: ignore[union-attr]
            "/api/topics",
            json={"name": "AI", "query": "AI infrastructure", "enabled": True},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "AI"
        assert data["query"] == "AI infrastructure"
        assert data["enabled"] is True
        assert "id" in data

    async def test_list_topics(self, client: object) -> None:
        """GET /api/topics should list all topics."""
        await client.post(  # type: ignore[union-attr]
            "/api/topics", json={"name": "Semiconductors", "query": "TSMC, NVDA"}
        )
        await client.post(  # type: ignore[union-attr]
            "/api/topics", json={"name": "Gold", "query": "gold price"}
        )

        resp = await client.get("/api/topics")  # type: ignore[union-attr]
        assert resp.status_code == 200
        topics = resp.json()
        assert len(topics) == 2

    async def test_delete_topic(self, client: object) -> None:
        """DELETE /api/topics/{id} should remove the topic."""
        resp = await client.post(  # type: ignore[union-attr]
            "/api/topics", json={"name": "Bonds", "query": "treasury yields"}
        )
        topic_id = resp.json()["id"]

        resp = await client.delete(f"/api/topics/{topic_id}")  # type: ignore[union-attr]
        assert resp.status_code == 204

        resp = await client.get("/api/topics")  # type: ignore[union-attr]
        assert len(resp.json()) == 0

    async def test_delete_nonexistent_topic(self, client: object) -> None:
        """DELETE on a missing topic should return 404."""
        resp = await client.delete("/api/topics/99999")  # type: ignore[union-attr]
        assert resp.status_code == 404
