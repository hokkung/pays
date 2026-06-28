"""yfinance price source implementation."""

import asyncio
import logging

import yfinance as yf

from app.sources.prices.base import RawHistoryEntry, RawQuote

logger = logging.getLogger(__name__)


class YFinanceSource:
    """Fetches asset quotes and history via yfinance (Yahoo Finance).

    yfinance is synchronous, so all calls are wrapped with asyncio.to_thread
    to stay async-compatible.
    """

    async def fetch_quote(self, symbol: str) -> RawQuote | None:
        """Fetch the latest quote for a symbol.

        Args:
            symbol: Ticker symbol (e.g. "AAPL", "GLD", "GC=F").

        Returns:
            A raw quote, or None if the symbol is invalid.
        """
        try:
            return await asyncio.to_thread(_get_quote, symbol)
        except Exception:
            logger.exception("Failed to fetch quote for %s", symbol)
            return None

    async def fetch_history(self, symbol: str, period: str = "1mo") -> list[RawHistoryEntry]:
        """Fetch historical daily prices for a symbol.

        Args:
            symbol: Ticker symbol.
            period: yfinance period string (e.g. "1mo", "3mo", "1y").

        Returns:
            A list of history entries (one per trading day).
        """
        try:
            return await asyncio.to_thread(_get_history, symbol, period)
        except Exception:
            logger.exception("Failed to fetch history for %s", symbol)
            return []


def _get_quote(symbol: str) -> RawQuote | None:
    """Get latest price info via yfinance fast_info.

    Args:
        symbol: Ticker symbol.

    Returns:
        A RawQuote, or None if the symbol is invalid.
    """
    ticker = yf.Ticker(symbol)
    fast_info = ticker.fast_info
    price = fast_info.last_price
    if price is None:
        return None
    currency = str(fast_info.currency or "USD")
    return RawQuote(
        symbol=symbol,
        price=float(price),
        currency=currency,
        as_of=None,
    )


def _get_history(symbol: str, period: str) -> list[RawHistoryEntry]:
    """Get historical prices via yfinance.

    Args:
        symbol: Ticker symbol.
        period: Period string.

    Returns:
        A list of RawHistoryEntry (one per trading day).
    """
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)
    if hist.empty:
        return []

    results: list[RawHistoryEntry] = []
    for index, row in hist.iterrows():
        as_of = index.isoformat() if hasattr(index, "isoformat") else str(index)
        results.append(
            RawHistoryEntry(
                symbol=symbol,
                price=float(row["Close"]),
                as_of=str(as_of),
            )
        )
    return results
