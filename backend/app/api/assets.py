"""Assets API router (watchlist CRUD + prices + latest with THB conversion)."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthToken, DbSession
from app.models.asset import Asset
from app.models.price import Price
from app.schemas.asset import AssetCreate, AssetResponse, AssetWithLatestResponse
from app.schemas.price import PriceListResponse, PriceResponse
from app.services import fx as fx_service

router = APIRouter()


@router.get("", response_model=list[AssetResponse])
async def list_assets(
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> list[AssetResponse]:
    """List all assets."""
    result = await session.execute(select(Asset).order_by(Asset.created_at.desc()))
    return [AssetResponse.model_validate(a) for a in result.scalars()]


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> AssetResponse:
    """Create a new asset."""
    asset = Asset(
        symbol=payload.symbol,
        name=payload.name,
        asset_type=payload.asset_type,
        currency=payload.currency,
        notes=payload.notes,
        enabled=payload.enabled,
    )
    session.add(asset)
    await session.flush()
    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> None:
    """Delete an asset by ID."""
    asset = await session.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    await session.delete(asset)


@router.get("/{asset_id}/prices", response_model=PriceListResponse)
async def get_prices(
    asset_id: int,
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
    limit: int = Query(100, ge=1, le=500),
) -> PriceListResponse:
    """Get price history for an asset."""
    result = await session.execute(
        select(Price).where(Price.asset_id == asset_id).order_by(desc(Price.as_of)).limit(limit)
    )
    return PriceListResponse(items=[PriceResponse.model_validate(p) for p in result.scalars()])


@router.get("/with-latest", response_model=list[AssetWithLatestResponse])
async def list_with_latest(
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> list[AssetWithLatestResponse]:
    """List assets joined with latest price and optional THB conversion."""
    result = await session.execute(select(Asset).order_by(Asset.created_at.desc()))
    assets = list(result.scalars())

    responses: list[AssetWithLatestResponse] = []
    for asset in assets:
        price_result = await session.execute(
            select(Price).where(Price.asset_id == asset.id).order_by(desc(Price.as_of)).limit(1)
        )
        latest = price_result.scalar_one_or_none()

        price_in_thb: float | None = None
        if latest is not None:
            thb = await fx_service.convert_to_thb(session, latest.price, latest.currency)
            price_in_thb = float(thb) if thb is not None else None

        responses.append(
            AssetWithLatestResponse(
                id=asset.id,
                symbol=asset.symbol,
                name=asset.name,
                asset_type=asset.asset_type,
                currency=asset.currency,
                notes=asset.notes,
                enabled=asset.enabled,
                latest_price=float(latest.price) if latest else None,
                latest_price_currency=latest.currency if latest else None,
                latest_price_as_of=latest.as_of.isoformat() if latest else None,
                price_in_thb=price_in_thb,
            )
        )

    return responses
