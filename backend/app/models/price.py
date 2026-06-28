"""Price model (time-series for assets)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Price(Base):
    """A historical price point for an asset.

    Attributes:
        asset_id: FK to assets.id.
        price: The quoted price.
        currency: ISO currency code of the price.
        as_of: Timestamp the price is valid for.
        source: Where the price came from (e.g. "yfinance").
    """

    __tablename__ = "prices"

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (Index("ix_prices_asset_as_of", "asset_id", "as_of"),)
