"""FX API router."""

from fastapi import APIRouter, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthToken, DbSession
from app.models.fx_rate import FxRate
from app.schemas.fx_rate import FxRateListResponse, FxRateResponse

router = APIRouter()


@router.get("", response_model=FxRateListResponse)
async def latest_rates(
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
    base: str | None = Query(None, description="Filter by base currency"),
) -> FxRateListResponse:
    """Get the latest FX rates, optionally filtered by base currency.

    Returns the most recent rate per (base, quote) pair.
    """
    query = select(FxRate).order_by(FxRate.base_ccy, FxRate.quote_ccy, desc(FxRate.as_of))
    if base:
        query = query.where(FxRate.base_ccy == base.upper())

    result = await session.execute(query)
    all_rates = list(result.scalars())

    seen: set[tuple[str, str]] = set()
    latest: list[FxRate] = []
    for rate in all_rates:
        pair = (rate.base_ccy, rate.quote_ccy)
        if pair not in seen:
            seen.add(pair)
            latest.append(rate)

    return FxRateListResponse(items=[FxRateResponse.model_validate(r) for r in latest])


@router.get("/history", response_model=FxRateListResponse)
async def rate_history(
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
    base: str = Query(..., description="Base currency"),
    quote: str = Query(..., description="Quote currency"),
    limit: int = Query(100, ge=1, le=500),
) -> FxRateListResponse:
    """Get FX rate history for a specific pair."""
    result = await session.execute(
        select(FxRate)
        .where(FxRate.base_ccy == base.upper(), FxRate.quote_ccy == quote.upper())
        .order_by(desc(FxRate.as_of))
        .limit(limit)
    )
    return FxRateListResponse(items=[FxRateResponse.model_validate(r) for r in result.scalars()])
