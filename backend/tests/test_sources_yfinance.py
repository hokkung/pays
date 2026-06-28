"""Tests for yfinance price source adapter with mocked yfinance."""

from unittest.mock import MagicMock, patch

import pytest

from app.sources.prices.base import PriceSource
from app.sources.prices.yfinance_source import YFinanceSource

pytestmark = pytest.mark.asyncio


def _mock_ticker(price: float | None = 150.0, currency: str = "USD") -> MagicMock:
    """Create a mock yf.Ticker instance."""
    ticker = MagicMock()
    fast_info = MagicMock()
    fast_info.last_price = price
    fast_info.currency = currency
    ticker.fast_info = fast_info
    return ticker


class TestYFinanceQuote:
    async def test_fetch_quote_success(self) -> None:
        """Should return a RawQuote for a valid symbol."""
        mock_ticker = _mock_ticker(150.0, "USD")
        with patch("app.sources.prices.yfinance_source.yf.Ticker", return_value=mock_ticker):
            source = YFinanceSource()
            quote = await source.fetch_quote("AAPL")

        assert quote is not None
        assert quote["symbol"] == "AAPL"
        assert quote["price"] == 150.0
        assert quote["currency"] == "USD"

    async def test_fetch_quote_none_price(self) -> None:
        """Should return None when price is None."""
        mock_ticker = _mock_ticker(None, "USD")
        with patch("app.sources.prices.yfinance_source.yf.Ticker", return_value=mock_ticker):
            source = YFinanceSource()
            quote = await source.fetch_quote("BAD")

        assert quote is None

    async def test_fetch_quote_exception(self) -> None:
        """Should return None on exception."""
        with patch(
            "app.sources.prices.yfinance_source.yf.Ticker",
            side_effect=Exception("Network error"),
        ):
            source = YFinanceSource()
            quote = await source.fetch_quote("AAPL")

        assert quote is None


class TestYFinanceHistory:
    async def test_fetch_history_success(self) -> None:
        """Should return history entries."""
        import pandas as pd

        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame(
            {"Close": [148.0, 149.0, 150.0]},
            index=pd.to_datetime(["2026-06-25", "2026-06-26", "2026-06-27"]),
        )
        with patch("app.sources.prices.yfinance_source.yf.Ticker", return_value=mock_ticker):
            source = YFinanceSource()
            history = await source.fetch_history("AAPL", "1mo")

        assert len(history) == 3
        assert history[0]["price"] == 148.0
        assert history[-1]["price"] == 150.0

    async def test_fetch_history_empty(self) -> None:
        """Should return empty list for empty history."""
        import pandas as pd

        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        with patch("app.sources.prices.yfinance_source.yf.Ticker", return_value=mock_ticker):
            source = YFinanceSource()
            history = await source.fetch_history("BAD", "1mo")

        assert history == []

    async def test_fetch_history_exception(self) -> None:
        """Should return empty list on exception."""
        with patch(
            "app.sources.prices.yfinance_source.yf.Ticker",
            side_effect=Exception("API error"),
        ):
            source = YFinanceSource()
            history = await source.fetch_history("AAPL")

        assert history == []


def test_yfinance_is_price_source() -> None:
    """YFinanceSource should satisfy the PriceSource protocol."""
    assert isinstance(YFinanceSource(), PriceSource)
