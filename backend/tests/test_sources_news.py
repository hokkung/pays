"""Tests for news source adapters (Google News RSS) with mocked HTTP."""

import respx
from httpx import AsyncClient

from app.sources.news.base import NewsSource
from app.sources.news.google_news import GoogleNewsSource

SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>"semiconductors" - Google News</title>
    <item>
      <title>TSMC Reports Record Quarterly Earnings</title>
      <link>https://example.com/article1</link>
      <description>TSMC beats expectations on AI chip demand.</description>
      <pubDate>Mon, 28 Jun 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>NVIDIA Announces New GPU Architecture</title>
      <link>https://example.com/article2</link>
      <description>Next-gen Blackwell chips shipping Q3.</description>
      <pubDate>Mon, 28 Jun 2026 09:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


@respx.mock
async def test_google_news_fetch_returns_articles() -> None:
    """GoogleNewsSource should parse RSS entries into RawArticle dicts."""
    respx.get("https://news.google.com/rss/search").respond(status_code=200, content=SAMPLE_RSS)

    async with AsyncClient() as client:
        source = GoogleNewsSource(client=client)
        articles = await source.fetch("semiconductors")

    assert len(articles) == 2
    assert articles[0]["title"] == "TSMC Reports Record Quarterly Earnings"
    assert articles[0]["url"] == "https://example.com/article1"
    assert articles[0]["source"] == "google_news"
    assert articles[0]["summary"] is not None
    assert "TSMC" in articles[0]["summary"]


@respx.mock
async def test_google_news_fetch_empty_feed() -> None:
    """An empty RSS feed should return an empty list."""
    empty_rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Empty</title></channel></rss>"""
    respx.get("https://news.google.com/rss/search").respond(status_code=200, content=empty_rss)

    async with AsyncClient() as client:
        source = GoogleNewsSource(client=client)
        articles = await source.fetch("nonexistent")

    assert articles == []


@respx.mock
async def test_google_news_skips_entries_without_link() -> None:
    """Entries without a link should be skipped."""
    no_link_rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Test</title>
  <item><title>No Link Article</title></item>
  <item><title>Has Link</title><link>https://example.com/ok</link></item>
</channel></rss>"""
    respx.get("https://news.google.com/rss/search").respond(status_code=200, content=no_link_rss)

    async with AsyncClient() as client:
        source = GoogleNewsSource(client=client)
        articles = await source.fetch("test")

    assert len(articles) == 1
    assert articles[0]["title"] == "Has Link"


def test_google_news_is_news_source() -> None:
    """GoogleNewsSource should satisfy the NewsSource protocol."""
    source = GoogleNewsSource()
    assert isinstance(source, NewsSource)
