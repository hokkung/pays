"""Price source interfaces and raw data types."""

from typing import Protocol, TypedDict, runtime_checkable


class RawQuote(TypedDict):
    """Raw quote data from a price source."""

    symbol: str
    price: float
    currency: str
    as_of: str | None


class RawHistoryEntry(TypedDict):
    """A single price history point."""

    symbol: str
    price: float
    as_of: str


@runtime_checkable
class PriceSource(Protocol):
    """Interface for asset price sources."""

    async def fetch_quote(self, symbol: str) -> RawQuote | None:
        """Fetch the latest quote for a symbol.

        Args:
            symbol: Ticker symbol (e.g. "AAPL", "GLD").

        Returns:
            A raw quote, or None if unavailable.
        """
        ...

    async def fetch_history(self, symbol: str, period: str = "1mo") -> list[RawHistoryEntry]:
        """Fetch historical price data for a symbol.

        Args:
            symbol: Ticker symbol.
            period: Period string (e.g. "1mo", "3mo", "1y").

        Returns:
            A list of history entries.
        """
        ...
