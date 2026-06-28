"""FX source interfaces and raw data types."""

from typing import Protocol, TypedDict, runtime_checkable


class RawRate(TypedDict):
    """Raw FX rate data from a source."""

    base_ccy: str
    quote_ccy: str
    rate: float
    as_of: str | None


@runtime_checkable
class FXSource(Protocol):
    """Interface for FX rate sources."""

    async def fetch_rate(self, base: str, quote: str) -> RawRate | None:
        """Fetch the latest rate for a currency pair.

        Args:
            base: Base currency ISO code.
            quote: Quote currency ISO code.

        Returns:
            A raw rate, or None if unavailable.
        """
        ...

    async def fetch_history(self, base: str, quote: str, start: str, end: str) -> list[RawRate]:
        """Fetch historical rates for a currency pair.

        Args:
            base: Base currency ISO code.
            quote: Quote currency ISO code.
            start: Start date (ISO YYYY-MM-DD).
            end: End date (ISO YYYY-MM-DD).

        Returns:
            A list of raw rates.
        """
        ...
