"""Tests for News API endpoints."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.topic import Topic

pytestmark = pytest.mark.asyncio


async def _seed_article(
    session: AsyncSession,
    title: str = "Test Article",
    url: str = "https://example.com/test",
    is_read: bool = False,
) -> Article:
    """Insert a test article and return it."""
    article = Article(
        source="google_news",
        title=title,
        url=url,
        summary="A summary",
        published_at=datetime.now(UTC),
        content_hash="abc123",
        is_read=is_read,
    )
    session.add(article)
    await session.flush()
    return article


class TestNewsAPI:
    """Tests for the news API endpoints."""

    async def test_list_news_empty(self, client: object) -> None:
        """GET /api/news with no articles should return empty list."""
        resp = await client.get("/api/news")  # type: ignore[union-attr]
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["next_cursor"] is None

    async def test_list_news_returns_articles(self, client: object, session: AsyncSession) -> None:
        """GET /api/news should return inserted articles."""
        await _seed_article(session, title="Article A", url="https://example.com/a")
        await _seed_article(session, title="Article B", url="https://example.com/b")
        await session.commit()

        resp = await client.get("/api/news")  # type: ignore[union-attr]
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2

    async def test_list_news_filter_is_read(self, client: object, session: AsyncSession) -> None:
        """GET /api/news?is_read=true should filter by read state."""
        await _seed_article(session, title="Read One", url="https://example.com/r1", is_read=True)
        await _seed_article(
            session, title="Unread One", url="https://example.com/u1", is_read=False
        )
        await session.commit()

        resp = await client.get("/api/news?is_read=true")  # type: ignore[union-attr]
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["title"] == "Read One"

    async def test_list_news_filter_by_topic(self, client: object, session: AsyncSession) -> None:
        """GET /api/news?topic=AI should filter by topic name."""
        topic = Topic(name="AI", query="AI")
        session.add(topic)
        await session.flush()

        article = await _seed_article(session, title="AI News", url="https://example.com/ai")
        await session.refresh(article, ["topics"])
        article.topics.append(topic)

        await _seed_article(session, title="Other News", url="https://example.com/other")
        await session.commit()

        resp = await client.get("/api/news?topic=AI")  # type: ignore[union-attr]
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["title"] == "AI News"

    async def test_mark_article_read(self, client: object, session: AsyncSession) -> None:
        """POST /api/news/{id}/read should set is_read to True."""
        article = await _seed_article(session, title="To Read", url="https://example.com/tr")
        await session.commit()

        resp = await client.post(f"/api/news/{article.id}/read")  # type: ignore[union-attr]
        assert resp.status_code == 200
        assert resp.json()["is_read"] is True

    async def test_mark_nonexistent_article_read(self, client: object) -> None:
        """POST on a missing article should return 404."""
        resp = await client.post("/api/news/99999/read")  # type: ignore[union-attr]
        assert resp.status_code == 404

    async def test_news_pagination(self, client: object, session: AsyncSession) -> None:
        """Pagination should limit results and provide next_cursor."""
        for i in range(5):
            await _seed_article(session, title=f"Article {i}", url=f"https://example.com/p{i}")
        await session.commit()

        resp = await client.get("/api/news?limit=2")  # type: ignore[union-attr]
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["next_cursor"] is not None

        resp2 = await client.get(f"/api/news?limit=2&cursor={data['next_cursor']}")  # type: ignore[union-attr]
        data2 = resp2.json()
        assert len(data2["items"]) == 2
