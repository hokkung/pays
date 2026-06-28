"""Tests for FX API endpoints."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fx_rate import FxRate

pytestmark = pytest.mark.asyncio


async def _seed_fx(
    session: AsyncSession,
    base: str = "USD",
    quote: str = "THB",
    rate: str = "33.50",
) -> None:
    from datetime import UTC, datetime
    from decimal import Decimal

    session.add(
        FxRate(
            base_ccy=base,
            quote_ccy=quote,
            rate=Decimal(rate),
            as_of=datetime.now(UTC),
            source="frankfurter",
        )
    )
    await session.flush()


class TestFxAPI:
    async def test_latest_rates(self, client: object, session: AsyncSession) -> None:
        await _seed_fx(session, "USD", "THB", "33.50")
        await _seed_fx(session, "EUR", "THB", "36.00")
        await session.commit()

        resp = await client.get("/api/fx")  # type: ignore[union-attr]
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 2

    async def test_latest_rates_filter_base(self, client: object, session: AsyncSession) -> None:
        await _seed_fx(session, "USD", "THB", "33.50")
        await _seed_fx(session, "EUR", "THB", "36.00")
        await session.commit()

        resp = await client.get("/api/fx?base=USD")  # type: ignore[union-attr]
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["base_ccy"] == "USD"

    async def test_rate_history(self, client: object, session: AsyncSession) -> None:
        from datetime import UTC, datetime, timedelta
        from decimal import Decimal

        for i in range(3):
            session.add(
                FxRate(
                    base_ccy="USD",
                    quote_ccy="THB",
                    rate=Decimal(f"3{i}.00"),
                    as_of=datetime.now(UTC) - timedelta(days=i),
                    source="frankfurter",
                )
            )
        await session.commit()

        resp = await client.get("/api/fx/history?base=USD&quote=THB")  # type: ignore[union-attr]
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 3

    async def test_latest_empty(self, client: object) -> None:
        resp = await client.get("/api/fx")  # type: ignore[union-attr]
        assert resp.status_code == 200
        assert resp.json()["items"] == []
