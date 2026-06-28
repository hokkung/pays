"""Article model and article-topic association table."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

# Many-to-many association table
article_topics = Table(
    "article_topics",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("topic_id", ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
)


class Article(Base, TimestampMixin):
    """A fetched news article.

    Attributes:
        source: Where the article came from (e.g. "google_news").
        title: Article headline.
        url: Canonical URL (unique, used for dedup).
        summary: Short snippet / description.
        published_at: When the article was originally published.
        content_hash: SHA256 of normalized title for dedup.
        is_read: Whether the user has marked it read.
    """

    __tablename__ = "articles"

    source: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), unique=True, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    topics: Mapped[list["Topic"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        secondary=article_topics,
        lazy="selectin",
    )
