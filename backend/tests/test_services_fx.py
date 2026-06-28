"""Tests for FX service (refresh_fx)."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fx_rate import FxRate
from app.services.fx import refresh_fx
from app.sources.fx.base import RawRate

pytestmark = pytest.mark.asyncio


def _mock_rate(base: str, quote: str, rate: float) -> RawRate:
    return RawRate(base_ccy=base, quote_ccy=quote, rate=rate, as_of="2026-06-28")


class TestRefreshFx:
    async def test_default_pairs(self, session: AsyncSession) -> None:
        """Should fetch USD/THB and EUR/THB by default."""
        mock = AsyncMock()
        mock.fetch_rate = AsyncMock(
            side_effect=[
                _mock_rate("USD", "THB", 33.5),
                _mock_rate("EUR", "THB", 36.0),
            ]
        )
        mock.close = AsyncMock()
        with patch("app.services.fx.FrankfurterSource", return_value=mock):
            count = await refresh_fx(session)

        assert count == 2
        rates = list((await session.execute(select(FxRate))).scalars())
        assert len(rates) == 2

    async def test_custom_pairs(self, session: AsyncSession) -> None:
        """Should fetch custom pairs."""
        mock = AsyncMock()
        mock.fetch_rate = AsyncMock(return_value=_mock_rate("JPY", "THB", 0.21))
        mock.close = AsyncMock()
        with patch("app.services.fx.FrankfurterSource", return_value=mock):
            count = await refresh_fx(session, [("JPY", "THB")])

        assert count == 1

    async def test_skips_failed_rate(self, session: AsyncSession) -> None:
        """Should skip pairs that return None."""
        mock = AsyncMock()
        mock.fetch_rate = AsyncMock(return_value=None)
        mock.close = AsyncMock()
        with patch("app.services.fx.FrankfurterSource", return_value=mock):
            count = await refresh_fx(session)

        assert count == 0

    async def test_skips_same_currency(self, session: AsyncSession) -> None:
        """Should skip pairs where base == quote."""
        mock = AsyncMock()
        mock.fetch_rate = AsyncMock()
        mock.close = AsyncMock()
        with patch("app.services.fx.FrankfurterSource", return_value=mock):
            count = await refresh_fx(session, [("THB", "THB")])

        assert count == 0
