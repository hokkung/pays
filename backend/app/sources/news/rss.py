"""RSS news source for curated feeds."""

import asyncio
import logging

import feedparser
import httpx

from app.config import get_settings
from app.sources.news.base import RawArticle

logger = logging.getLogger(__name__)


class RSSSource:
    """Fetches news from a curated RSS/Atom feed URL."""

    def __init__(
        self, feed_url: str, source_name: str, client: httpx.AsyncClient | None = None
    ) -> None:
        """Initialize with a feed URL and name.

        Args:
            feed_url: The RSS/Atom feed URL.
            source_name: A label for this source.
            client: Optional pre-configured httpx async client.
        """
        self._feed_url = feed_url
        self._source_name = source_name
        self._client = client

    async def _get_client(self) -> httpx.AsyncClient:
        """Return the httpx client, creating one if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=get_settings().http_timeout_seconds,
                follow_redirects=True,
            )
        return self._client

    async def fetch(self, query: str | None = None) -> list[RawArticle]:
        """Fetch all articles from the feed (query is ignored for raw feeds).

        Args:
            query: Ignored — curated feeds return all entries.

        Returns:
            A list of raw articles.
        """
        client = await self._get_client()
        response = await client.get(self._feed_url)
        response.raise_for_status()

        return await asyncio.to_thread(_parse_feed, response.content, self._source_name)

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


def _parse_feed(content: bytes, source_name: str) -> list[RawArticle]:
    """Parse RSS feed bytes into a list of RawArticle dicts.

    Args:
        content: Raw RSS XML bytes.
        source_name: Label to assign as the source.

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
                source=source_name,
                summary=entry.get("summary"),
                published_at=entry.get("published"),
            )
        )
    return results
