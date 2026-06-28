"""Asset model for the watchlist."""

import enum

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AssetType(enum.StrEnum):
    """Supported asset types (extensible via new enum members)."""

    STOCK = "stock"
    ETF = "etf"
    GOLD = "gold"
    BOND = "bond"


class Asset(Base, TimestampMixin):
    """A tracked asset on the watchlist.

    Attributes:
        symbol: Ticker / identifier (e.g. "AAPL", "GLD", "GC=F").
        name: Human-readable name.
        asset_type: One of stock, etf, gold, bond.
        currency: ISO currency code (e.g. "USD").
        notes: Optional free-text notes.
        enabled: Whether prices are actively refreshed.
    """

    __tablename__ = "assets"

    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type_enum", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
