"""Pydantic schemas for Asset."""

from pydantic import BaseModel, Field

from app.models.asset import AssetType
from app.schemas.common import ORMModel


class AssetBase(BaseModel):
    """Shared asset fields."""

    symbol: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    asset_type: AssetType
    currency: str = Field("USD", max_length=3)
    notes: str | None = None
    enabled: bool = True


class AssetCreate(AssetBase):
    """Payload for creating an asset."""


class AssetUpdate(BaseModel):
    """Payload for partially updating an asset."""

    symbol: str | None = Field(None, max_length=50)
    name: str | None = Field(None, max_length=200)
    asset_type: AssetType | None = None
    currency: str | None = Field(None, max_length=3)
    notes: str | None = None
    enabled: bool | None = None


class AssetResponse(ORMModel, AssetBase):
    """Asset response with read-only fields."""

    id: int


class AssetWithLatestResponse(ORMModel, AssetBase):
    """Asset joined with its latest price and optional THB conversion."""

    id: int
    latest_price: float | None = None
    latest_price_currency: str | None = None
    latest_price_as_of: str | None = None
    price_in_thb: float | None = None
