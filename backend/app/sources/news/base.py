"""News source interfaces and raw data types."""

from typing import Protocol, TypedDict, runtime_checkable


class RawArticle(TypedDict):
    """Raw article data from a news source before persistence."""

    title: str
    url: str
    source: str
    summary: str | None
    published_at: str | None


@runtime_checkable
class NewsSource(Protocol):
    """Interface for news sources (RSS feeds, APIs, etc.)."""

    async def fetch(self, query: str) -> list[RawArticle]:
        """Fetch articles matching the given query/keyword.

        Args:
            query: Search keywords or topic query string.

        Returns:
            A list of raw articles.
        """
        ...
