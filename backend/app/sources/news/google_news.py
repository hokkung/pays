"""Google News RSS news source."""

import asyncio
import logging

import feedparser
import httpx

from app.config import get_settings
from app.sources.news.base import RawArticle

logger = logging.getLogger(__name__)


class GoogleNewsSource:
    """Fetches news via Google News RSS keyword search.

    Uses httpx for the async HTTP request and feedparser (in a thread) to
    parse the RSS XML response.
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        """Initialize with an optional httpx client.

        Args:
            client: Optional pre-configured httpx async client.
        """
        self._client = client
        self._base_url = get_settings().google_news_base_url

    async def _get_client(self) -> httpx.AsyncClient:
        """Return the httpx client, creating one if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=get_settings().http_timeout_seconds,
                follow_redirects=True,
            )
        return self._client

    async def fetch(self, query: str) -> list[RawArticle]:
        """Fetch articles from Google News RSS for the given query.

        Args:
            query: Search keywords.

        Returns:
            A list of raw articles.
        """
        client = await self._get_client()
        response = await client.get(self._base_url, params={"q": query})
        response.raise_for_status()

        return await asyncio.to_thread(_parse_feed, response.content)

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


def _parse_feed(content: bytes) -> list[RawArticle]:
    """Parse RSS feed bytes into a list of RawArticle dicts.

    Args:
        content: Raw RSS XML bytes.

    Returns:
        A list of RawArticle dicts.
    """
    feed = feedparser.parse(content)
    results: list[RawArticle] = []
    for entry in feed.entries:
        link: str = str(entry.get("link", ""))
        if not link:
            continue
        results.append(
            RawArticle(
                title=str(entry.get("title", "")),
                url=link,
                source="google_news",
                summary=entry.get("summary"),
                published_at=entry.get("published"),
            )
        )
    return results
