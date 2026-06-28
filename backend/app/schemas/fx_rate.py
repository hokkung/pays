"""Pydantic schemas for FxRate."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class FxRateResponse(ORMModel):
    """FX rate response."""

    id: int
    base_ccy: str
    quote_ccy: str
    rate: Decimal
    as_of: datetime
    source: str


class FxRateListResponse(BaseModel):
    """List of latest FX rates."""

    items: list[FxRateResponse]
