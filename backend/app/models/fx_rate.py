"""FX rate model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FxRate(Base):
    """An FX rate snapshot for a currency pair.

    Attributes:
        base_ccy: Base currency ISO code.
        quote_ccy: Quote currency ISO code.
        rate: Exchange rate (1 base_ccy = rate quote_ccy).
        as_of: Timestamp the rate is valid for.
        source: Where the rate came from (e.g. "frankfurter").
    """

    __tablename__ = "fx_rates"

    base_ccy: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_ccy: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint("base_ccy", "quote_ccy", "as_of", name="uq_fx_pair_asof"),
        Index("ix_fx_rates_pair", "base_ccy", "quote_ccy"),
    )
