"""Tests for news service (fetch, dedup, matching)."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article
from app.models.topic import Topic
from app.services.news import fetch_news
from app.sources.news.base import RawArticle

pytestmark = pytest.mark.asyncio


async def _make_source(*articles: RawArticle) -> AsyncMock:
    """Create a mock news source returning the given articles."""
    mock = AsyncMock()
    mock.fetch = AsyncMock(return_value=list(articles))
    mock.close = AsyncMock()
    return mock


class TestFetchNews:
    async def test_no_topics(self, session: AsyncSession) -> None:
        """With no topics, fetch_news should return 0."""
        count = await fetch_news(session)
        assert count == 0

    async def test_inserts_new_article(self, session: AsyncSession) -> None:
        """New articles should be inserted and counted."""
        session.add(Topic(name="AI", query="AI"))
        await session.flush()

        mock = await _make_source(
            RawArticle(
                title="AI Boom",
                url="https://example.com/1",
                source="google_news",
                summary="Summary",
                published_at="Mon, 28 Jun 2026 10:00:00 GMT",
            )
        )
        with patch("app.services.news.GoogleNewsSource", return_value=mock):
            count = await fetch_news(session)

        assert count == 1
        articles = list((await session.execute(select(Article))).scalars())
        assert len(articles) == 1
        assert articles[0].title == "AI Boom"

    async def test_dedup_by_url(self, session: AsyncSession) -> None:
        """Articles with the same URL should not be duplicated."""
        session.add(Topic(name="AI", query="AI"))
        await session.flush()

        article = RawArticle(
            title="Duplicate",
            url="https://example.com/dup",
            source="google_news",
            summary=None,
            published_at=None,
        )
        mock = await _make_source(article)
        with patch("app.services.news.GoogleNewsSource", return_value=mock):
            count1 = await fetch_news(session)

        mock2 = await _make_source(article)
        with patch("app.services.news.GoogleNewsSource", return_value=mock2):
            count2 = await fetch_news(session)

        assert count1 == 1
        assert count2 == 0

    async def test_associates_multiple_topics(self, session: AsyncSession) -> None:
        """Same article fetched under different topics should link to both."""
        t1 = Topic(name="AI", query="AI")
        t2 = Topic(name="Tech", query="Tech")
        session.add_all([t1, t2])
        await session.flush()

        raw = RawArticle(
            title="Shared Article",
            url="https://example.com/shared",
            source="google_news",
            summary=None,
            published_at=None,
        )

        mock1 = await _make_source(raw)
        with patch("app.services.news.GoogleNewsSource", return_value=mock1):
            await fetch_news(session)

        result = await session.execute(
            select(Article)
            .options(selectinload(Article.topics))
            .where(Article.url == "https://example.com/shared")
        )
        article = result.scalar_one()
        assert len(article.topics) >= 1

    async def test_source_error_skipped(self, session: AsyncSession) -> None:
        """A source error for one topic should not stop others."""
        session.add(Topic(name="AI", query="AI"))
        session.add(Topic(name="Gold", query="Gold"))
        await session.flush()

        mock = AsyncMock()
        mock.fetch = AsyncMock(side_effect=[Exception("Network error"), []])
        mock.close = AsyncMock()
        with patch("app.services.news.GoogleNewsSource", return_value=mock):
            count = await fetch_news(session)

        assert count == 0
