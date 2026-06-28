"""News service: fetch, deduplicate, match, and persist articles."""

import hashlib
import logging
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article
from app.models.topic import Topic
from app.sources.news.base import RawArticle
from app.sources.news.google_news import GoogleNewsSource

logger = logging.getLogger(__name__)


def compute_content_hash(title: str) -> str:
    """Compute a SHA256 hash of a normalized article title for dedup.

    Args:
        title: The article title.

    Returns:
        A hex digest string.
    """
    normalized = title.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def matches_keywords(text: str, keywords: str) -> bool:
    """Check if any of the comma-separated keywords appear in the text.

    Matching is case-insensitive and substring-based.

    Args:
        text: The text to search (title + summary).
        keywords: Comma-separated keywords (e.g. "AI, semiconductors, TSMC").

    Returns:
        True if any keyword is found.
    """
    text_lower = text.lower()
    return any(kw.strip().lower() in text_lower for kw in keywords.split(",") if kw.strip())


def parse_published_date(date_str: str | None) -> datetime:
    """Parse an RSS/Atom date string into a timezone-aware datetime.

    Falls back to the current UTC time if parsing fails.

    Args:
        date_str: A date string (typically RFC 2822 from RSS feeds).

    Returns:
        A timezone-aware datetime.
    """
    if not date_str:
        return datetime.now(UTC)
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (TypeError, ValueError):
        return datetime.now(UTC)


async def fetch_news(session: AsyncSession) -> int:
    """Fetch news for all enabled topics and persist new articles.

    For each enabled topic, queries the Google News RSS source, deduplicates
    by URL, computes a content hash, and associates articles with their
    matching topics.

    Args:
        session: An async DB session.

    Returns:
        The number of newly inserted articles.
    """
    result = await session.execute(select(Topic).where(Topic.enabled.is_(True)))
    topics = list(result.scalars())
    if not topics:
        logger.info("No enabled topics; skipping news fetch")
        return 0

    source = GoogleNewsSource()
    new_count = 0

    try:
        for topic in topics:
            try:
                raw_articles = await source.fetch(topic.query)
            except Exception:
                logger.exception("Failed to fetch news for topic '%s'", topic.name)
                continue

            for raw in raw_articles:
                new_count += await _upsert_article(session, raw, topic)
    finally:
        await source.close()

    logger.info("Fetched %d new articles", new_count)
    return new_count


async def _upsert_article(session: AsyncSession, raw: RawArticle, topic: Topic) -> int:
    """Insert an article if new (by URL) and associate it with a topic.

    Args:
        session: An async DB session.
        raw: The raw article data from the source.
        topic: The topic that matched this article.

    Returns:
        1 if a new article was inserted, 0 if it already existed.
    """
    existing = await session.execute(
        select(Article).options(selectinload(Article.topics)).where(Article.url == raw["url"])
    )
    article = existing.scalar_one_or_none()

    if article is None:
        article = Article(
            source=raw["source"],
            title=raw["title"],
            url=raw["url"],
            summary=raw["summary"],
            published_at=parse_published_date(raw["published_at"]),
            content_hash=compute_content_hash(raw["title"]),
            is_read=False,
        )
        session.add(article)
        await session.flush()
        await session.refresh(article, ["topics"])
        article.topics.append(topic)
        return 1

    if topic not in article.topics:
        article.topics.append(topic)
    return 0
