"""Pydantic schemas for Price."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class PriceResponse(ORMModel):
    """Price point response."""

    id: int
    asset_id: int
    price: Decimal
    currency: str
    as_of: datetime
    source: str


class PriceListResponse(BaseModel):
    """List of price points (history)."""

    items: list[PriceResponse]
