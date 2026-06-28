"""Pydantic schemas for Article."""

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel
from app.schemas.topic import TopicResponse


class ArticleResponse(ORMModel):
    """Article response with matched topics."""

    id: int
    source: str
    title: str
    url: str
    summary: str | None
    published_at: datetime
    fetched_at: datetime
    is_read: bool
    topics: list[TopicResponse] = []


class ArticleListResponse(BaseModel):
    """Paginated article list."""

    items: list[ArticleResponse]
    next_cursor: str | None = None
