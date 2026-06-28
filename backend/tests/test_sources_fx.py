"""Tests for FX source adapters (Frankfurter) with mocked HTTP."""

import respx
from httpx import AsyncClient

from app.sources.fx.base import FXSource
from app.sources.fx.frankfurter import FrankfurterSource


@respx.mock
async def test_frankfurter_fetch_rate() -> None:
    """FrankfurterSource should parse the latest rate response."""
    respx.get("https://api.frankfurter.app/latest").respond(
        status_code=200,
        json={
            "amount": 1.0,
            "base": "USD",
            "date": "2026-06-28",
            "rates": {"THB": 33.375},
        },
    )

    async with AsyncClient() as client:
        source = FrankfurterSource(client=client)
        rate = await source.fetch_rate("USD", "THB")

    assert rate is not None
    assert rate["base_ccy"] == "USD"
    assert rate["quote_ccy"] == "THB"
    assert rate["rate"] == 33.375
    assert rate["as_of"] == "2026-06-28"


@respx.mock
async def test_frankfurter_fetch_rate_not_found() -> None:
    """A 404 response should return None."""
    respx.get("https://api.frankfurter.app/latest").respond(status_code=404)

    async with AsyncClient() as client:
        source = FrankfurterSource(client=client)
        rate = await source.fetch_rate("XXX", "THB")

    assert rate is None


@respx.mock
async def test_frankfurter_fetch_history() -> None:
    """FrankfurterSource should parse historical rate responses."""
    respx.get(url__regex=r"https://api\.frankfurter\.app/\d{4}-\d{2}-\d{2}\.\.").respond(
        status_code=200,
        json={
            "amount": 1.0,
            "base": "USD",
            "start_date": "2026-06-20",
            "end_date": "2026-06-28",
            "rates": {
                "2026-06-23": {"THB": 33.20},
                "2026-06-24": {"THB": 33.43},
                "2026-06-25": {"THB": 33.40},
            },
        },
    )

    async with AsyncClient() as client:
        source = FrankfurterSource(client=client)
        rates = await source.fetch_history("USD", "THB", "2026-06-20", "2026-06-28")

    assert len(rates) == 3
    assert rates[0]["as_of"] == "2026-06-23"
    assert rates[0]["rate"] == 33.20
    assert rates[-1]["as_of"] == "2026-06-25"
    assert rates[-1]["rate"] == 33.40


@respx.mock
async def test_frankfurter_fetch_rate_missing_quote() -> None:
    """If the quote currency is missing from rates, return None."""
    respx.get("https://api.frankfurter.app/latest").respond(
        status_code=200,
        json={"amount": 1.0, "base": "USD", "date": "2026-06-28", "rates": {}},
    )

    async with AsyncClient() as client:
        source = FrankfurterSource(client=client)
        rate = await source.fetch_rate("USD", "THB")

    assert rate is None


def test_frankfurter_is_fx_source() -> None:
    """FrankfurterSource should satisfy the FXSource protocol."""
    source = FrankfurterSource()
    assert isinstance(source, FXSource)


async def test_frankfurter_close_owned_client() -> None:
    """close() should clean up the owned client."""
    source = FrankfurterSource()
    await source._get_client()
    assert source._client is not None
    await source.close()
    assert source._client is None


async def test_frankfurter_close_no_client() -> None:
    """close() should be safe when no client exists."""
    source = FrankfurterSource()
    await source.close()


def test_default_date_range() -> None:
    """default_date_range should return ISO date strings."""
    from app.sources.fx.frankfurter import default_date_range

    start, end = default_date_range(1)
    assert "-" in start
    assert "-" in end
    assert len(start) == 10
    assert len(end) == 10
