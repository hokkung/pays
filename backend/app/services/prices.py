"""Prices service: fetch and persist asset price quotes."""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.price import Price
from app.sources.prices.yfinance_source import YFinanceSource

logger = logging.getLogger(__name__)


async def refresh_prices(session: AsyncSession) -> int:
    """Fetch latest prices for all enabled assets and persist them.

    Args:
        session: An async DB session.

    Returns:
        The number of prices successfully fetched and stored.
    """
    result = await session.execute(select(Asset).where(Asset.enabled.is_(True)))
    assets = list(result.scalars())
    if not assets:
        logger.info("No enabled assets; skipping price refresh")
        return 0

    source = YFinanceSource()
    stored = 0

    for asset in assets:
        quote = await source.fetch_quote(asset.symbol)
        if quote is None:
            logger.warning("No quote returned for %s", asset.symbol)
            continue

        price = Price(
            asset_id=asset.id,
            price=quote["price"],
            currency=quote["currency"] or asset.currency,
            as_of=datetime.now(UTC),
            source="yfinance",
        )
        session.add(price)
        stored += 1

    logger.info("Refreshed %d prices", stored)
    return stored
