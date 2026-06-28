"""Topic model for news watchlist keywords."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Topic(Base, TimestampMixin):
    """A news topic / keyword watchlist entry.

    Attributes:
        name: Human-readable label.
        query: Keywords passed to the news source (e.g. Google News RSS).
        enabled: Whether this topic is actively fetched and matched.
    """

    __tablename__ = "topics"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
