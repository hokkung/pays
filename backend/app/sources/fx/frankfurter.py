"""Frankfurter FX source (ECB data, free, no key required)."""

import logging
from datetime import date

import httpx

from app.config import get_settings
from app.sources.fx.base import RawRate

logger = logging.getLogger(__name__)


class FrankfurterSource:
    """Fetches FX rates from the Frankfurter API (ECB reference rates).

    API docs: https://www.frankfurter.app/docs/
    Includes THB. Free, no API key needed.
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        """Initialize with an optional httpx client.

        Args:
            client: Optional pre-configured httpx async client.
        """
        self._client = client
        self._base_url = get_settings().frankfurter_base_url

    async def _get_client(self) -> httpx.AsyncClient:
        """Return the httpx client, creating one if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=get_settings().http_timeout_seconds,
                follow_redirects=True,
            )
        return self._client

    async def fetch_rate(self, base: str, quote: str) -> RawRate | None:
        """Fetch the latest FX rate for a currency pair.

        Args:
            base: Base currency ISO code (e.g. "USD").
            quote: Quote currency ISO code (e.g. "THB").

        Returns:
            A raw rate, or None if the pair is unavailable.
        """
        client = await self._get_client()
        response = await client.get(
            f"{self._base_url}/latest",
            params={"from": base, "to": quote},
        )
        if response.status_code != 200:
            logger.warning("Frankfurter returned %d for %s/%s", response.status_code, base, quote)
            return None

        data = response.json()
        rates = data.get("rates", {})
        rate = rates.get(quote)
        if rate is None:
            return None

        return RawRate(
            base_ccy=base,
            quote_ccy=quote,
            rate=float(rate),
            as_of=data.get("date"),
        )

    async def fetch_history(self, base: str, quote: str, start: str, end: str) -> list[RawRate]:
        """Fetch historical FX rates for a currency pair.

        Args:
            base: Base currency ISO code.
            quote: Quote currency ISO code.
            start: Start date (ISO YYYY-MM-DD).
            end: End date (ISO YYYY-MM-DD).

        Returns:
            A list of raw rates (one per business day).
        """
        client = await self._get_client()
        response = await client.get(
            f"{self._base_url}/{start}..",
            params={"from": base, "to": quote},
        )
        if response.status_code != 200:
            logger.warning(
                "Frankfurter history returned %d for %s/%s",
                response.status_code,
                base,
                quote,
            )
            return []

        data = response.json()
        rates_by_date: dict[str, dict[str, float]] = data.get("rates", {})
        results: list[RawRate] = []
        for date_str, rates in sorted(rates_by_date.items()):
            rate = rates.get(quote)
            if rate is not None:
                results.append(
                    RawRate(
                        base_ccy=base,
                        quote_ccy=quote,
                        rate=float(rate),
                        as_of=date_str,
                    )
                )

        _ = end  # Frankfurter uses start.. for range; end not needed for URL
        return results

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


def default_date_range(months: int = 1) -> tuple[str, str]:
    """Return a (start, end) ISO date pair spanning the last N months.

    Args:
        months: Number of months to look back.

    Returns:
        A tuple of (start_date, end_date) as ISO strings.
    """
    today = date.today()
    start_year = today.year
    start_month = today.month - months
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    start = date(start_year, start_month, today.day)
    return start.isoformat(), today.isoformat()
