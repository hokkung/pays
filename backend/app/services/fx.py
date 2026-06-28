"""FX service: fetch rates, persist, and convert to THB."""

import logging
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fx_rate import FxRate
from app.sources.fx.frankfurter import FrankfurterSource

logger = logging.getLogger(__name__)

THB = "THB"


async def refresh_fx(session: AsyncSession, pairs: list[tuple[str, str]] | None = None) -> int:
    """Fetch FX rates for given pairs and persist them.

    Args:
        session: An async DB session.
        pairs: List of (base, quote) tuples. Defaults to USD/THB and EUR/THB.

    Returns:
        The number of rates successfully fetched and stored.
    """
    if pairs is None:
        pairs = [("USD", THB), ("EUR", THB)]

    source = FrankfurterSource()
    stored = 0

    try:
        for base, quote in pairs:
            if base == quote:
                continue
            rate = await source.fetch_rate(base, quote)
            if rate is None:
                logger.warning("No FX rate for %s/%s", base, quote)
                continue

            fx = FxRate(
                base_ccy=base,
                quote_ccy=quote,
                rate=Decimal(str(rate["rate"])),
                as_of=datetime.now(UTC),
                source="frankfurter",
            )
            session.add(fx)
            stored += 1
    finally:
        await source.close()

    logger.info("Refreshed %d FX rates", stored)
    return stored


async def get_latest_rate(session: AsyncSession, base: str, quote: str) -> Decimal | None:
    """Get the most recent FX rate for a pair.

    Args:
        session: An async DB session.
        base: Base currency ISO code.
        quote: Quote currency ISO code.

    Returns:
        The latest rate, or None if no rate is stored.
    """
    if base == quote:
        return Decimal("1")

    result = await session.execute(
        select(FxRate.rate)
        .where(FxRate.base_ccy == base, FxRate.quote_ccy == quote)
        .order_by(desc(FxRate.as_of))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def convert_to_thb(session: AsyncSession, amount: Decimal, from_ccy: str) -> Decimal | None:
    """Convert an amount from the given currency to THB.

    Args:
        session: An async DB session.
        amount: The amount to convert.
        from_ccy: Source currency ISO code.

    Returns:
        The THB equivalent, or None if no rate is available.
    """
    if from_ccy == THB:
        return amount

    rate = await get_latest_rate(session, from_ccy, THB)
    if rate is None:
        return None

    return amount * rate
