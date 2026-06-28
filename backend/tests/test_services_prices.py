"""Tests for prices service."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetType
from app.models.price import Price
from app.services.prices import refresh_prices
from app.sources.prices.base import RawQuote

pytestmark = pytest.mark.asyncio


def _mock_quote(price: float = 150.0, currency: str = "USD") -> RawQuote:
    return RawQuote(symbol="AAPL", price=price, currency=currency, as_of=None)


class TestRefreshPrices:
    async def test_no_assets(self, session: AsyncSession) -> None:
        """With no assets, should return 0."""
        count = await refresh_prices(session)
        assert count == 0

    async def test_stores_prices(self, session: AsyncSession) -> None:
        """Should fetch and store prices for enabled assets."""
        session.add(Asset(symbol="AAPL", name="Apple", asset_type=AssetType.STOCK, currency="USD"))
        session.add(Asset(symbol="GLD", name="Gold ETF", asset_type=AssetType.GOLD, currency="USD"))
        await session.flush()

        mock = AsyncMock()
        mock.fetch_quote = AsyncMock(
            side_effect=[
                _mock_quote(150.0),
                _mock_quote(200.0),
            ]
        )
        with patch("app.services.prices.YFinanceSource", return_value=mock):
            count = await refresh_prices(session)

        assert count == 2
        prices = list((await session.execute(select(Price))).scalars())
        assert len(prices) == 2

    async def test_skips_failed_quote(self, session: AsyncSession) -> None:
        """Should skip assets that return None."""
        session.add(
            Asset(symbol="BAD", name="Bad Asset", asset_type=AssetType.STOCK, currency="USD")
        )
        session.add(
            Asset(symbol="OK", name="Good Asset", asset_type=AssetType.STOCK, currency="USD")
        )
        await session.flush()

        mock = AsyncMock()
        mock.fetch_quote = AsyncMock(side_effect=[None, _mock_quote(100.0)])
        with patch("app.services.prices.YFinanceSource", return_value=mock):
            count = await refresh_prices(session)

        assert count == 1

    async def test_skips_disabled_assets(self, session: AsyncSession) -> None:
        """Disabled assets should be skipped."""
        session.add(
            Asset(
                symbol="OFF",
                name="Disabled",
                asset_type=AssetType.STOCK,
                currency="USD",
                enabled=False,
            )
        )
        await session.flush()

        mock = AsyncMock()
        mock.fetch_quote = AsyncMock(return_value=_mock_quote())
        with patch("app.services.prices.YFinanceSource", return_value=mock):
            count = await refresh_prices(session)

        assert count == 0
