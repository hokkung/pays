"""Tests for RSS source adapter."""

import respx
from httpx import AsyncClient

from app.sources.news.rss import RSSSource

SAMPLE_RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Reuters Finance</title>
  <item>
    <title>Markets Close Higher</title>
    <link>https://reuters.com/article1</link>
    <description>S&P 500 gains 1%.</description>
    <pubDate>Mon, 28 Jun 2026 16:00:00 GMT</pubDate>
  </item>
  <item>
    <title>Oil Prices Drop</title>
    <link>https://reuters.com/article2</link>
    <description>Crude falls on demand concerns.</description>
    <pubDate>Mon, 28 Jun 2026 15:00:00 GMT</pubDate>
  </item>
</channel></rss>"""


@respx.mock
async def test_rss_fetch() -> None:
    """RSSSource should parse entries from a curated feed."""
    respx.get("https://reuters.com/feed").respond(status_code=200, content=SAMPLE_RSS)

    async with AsyncClient() as client:
        source = RSSSource("https://reuters.com/feed", "reuters", client=client)
        articles = await source.fetch()

    assert len(articles) == 2
    assert articles[0]["title"] == "Markets Close Higher"
    assert articles[0]["source"] == "reuters"
    assert articles[1]["url"] == "https://reuters.com/article2"


@respx.mock
async def test_rss_fetch_empty() -> None:
    """Empty feed should return empty list."""
    respx.get("https://reuters.com/feed").respond(
        status_code=200,
        content=(
            b'<?xml version="1.0"?>' b'<rss version="2.0"><channel><title>E</title></channel></rss>'
        ),
    )

    async with AsyncClient() as client:
        source = RSSSource("https://reuters.com/feed", "reuters", client=client)
        articles = await source.fetch()

    assert articles == []


@respx.mock
async def test_rss_skips_no_link() -> None:
    """Entries without link should be skipped."""
    no_link = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>T</title>
  <item><title>No Link</title></item>
  <item><title>OK</title><link>https://x.com/1</link></item>
</channel></rss>"""
    respx.get("https://x.com/feed").respond(status_code=200, content=no_link)

    async with AsyncClient() as client:
        source = RSSSource("https://x.com/feed", "test", client=client)
        articles = await source.fetch()

    assert len(articles) == 1
    assert articles[0]["title"] == "OK"


async def test_rss_close() -> None:
    """close() should clean up the client."""
    source = RSSSource("https://example.com/feed", "test")
    await source.close()
