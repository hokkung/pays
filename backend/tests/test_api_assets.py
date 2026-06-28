"""Tests for Assets API endpoints."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetType
from app.models.fx_rate import FxRate
from app.models.price import Price
from app.services.fx import THB

pytestmark = pytest.mark.asyncio


async def _seed_asset(
    session: AsyncSession,
    symbol: str = "AAPL",
    name: str = "Apple Inc",
    asset_type: AssetType = AssetType.STOCK,
    currency: str = "USD",
) -> Asset:
    asset = Asset(symbol=symbol, name=name, asset_type=asset_type, currency=currency)
    session.add(asset)
    await session.flush()
    return asset


class TestAssetsCRUD:
    async def test_create_asset(self, client: object) -> None:
        resp = await client.post(  # type: ignore[union-attr]
            "/api/assets",
            json={
                "symbol": "GLD",
                "name": "SPDR Gold",
                "asset_type": "gold",
                "currency": "USD",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["symbol"] == "GLD"
        assert data["asset_type"] == "gold"

    async def test_list_assets(self, client: object, session: AsyncSession) -> None:
        await _seed_asset(session, "AAPL", "Apple")
        await _seed_asset(session, "TLT", "Long Treasury", AssetType.BOND)
        await session.commit()

        resp = await client.get("/api/assets")  # type: ignore[union-attr]
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_delete_asset(self, client: object, session: AsyncSession) -> None:
        asset = await _seed_asset(session, "NVDA", "NVIDIA")
        await session.commit()

        resp = await client.delete(f"/api/assets/{asset.id}")  # type: ignore[union-attr]
        assert resp.status_code == 204

        resp = await client.get("/api/assets")  # type: ignore[union-attr]
        assert len(resp.json()) == 0

    async def test_delete_nonexistent(self, client: object) -> None:
        resp = await client.delete("/api/assets/99999")  # type: ignore[union-attr]
        assert resp.status_code == 404


class TestAssetPrices:
    async def test_get_prices(self, client: object, session: AsyncSession) -> None:
        from datetime import UTC, datetime
        from decimal import Decimal

        asset = await _seed_asset(session)
        for i in range(3):
            session.add(
                Price(
                    asset_id=asset.id,
                    price=Decimal(f"{150 + i}.00"),
                    currency="USD",
                    as_of=datetime.now(UTC),
                    source="yfinance",
                )
            )
        await session.commit()

        resp = await client.get(f"/api/assets/{asset.id}/prices")  # type: ignore[union-attr]
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 3


class TestAssetsWithLatest:
    async def test_with_latest_no_prices(self, client: object, session: AsyncSession) -> None:
        await _seed_asset(session)
        await session.commit()

        resp = await client.get("/api/assets/with-latest")  # type: ignore[union-attr]
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["latest_price"] is None
        assert data[0]["price_in_thb"] is None

    async def test_with_latest_and_thb(self, client: object, session: AsyncSession) -> None:
        from datetime import UTC, datetime
        from decimal import Decimal

        asset = await _seed_asset(session, "AAPL", "Apple", AssetType.STOCK, "USD")
        session.add(
            Price(
                asset_id=asset.id,
                price=Decimal("150.00"),
                currency="USD",
                as_of=datetime.now(UTC),
                source="yfinance",
            )
        )
        session.add(
            FxRate(
                base_ccy="USD",
                quote_ccy=THB,
                rate=Decimal("33.50"),
                as_of=datetime.now(UTC),
                source="frankfurter",
            )
        )
        await session.commit()

        resp = await client.get("/api/assets/with-latest")  # type: ignore[union-attr]
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["latest_price"] == 150.0
        assert data[0]["price_in_thb"] is not None
        assert abs(data[0]["price_in_thb"] - 5025.0) < 0.01
