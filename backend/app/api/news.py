"""News API router."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthToken, DbSession
from app.models.article import Article
from app.models.topic import Topic
from app.schemas.article import ArticleListResponse, ArticleResponse

router = APIRouter()


@router.get("/news", response_model=ArticleListResponse)
async def list_news(
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
    topic: str | None = Query(None, description="Filter by topic name"),
    is_read: bool | None = Query(None, description="Filter by read state"),
    limit: int = Query(50, ge=1, le=200),
    cursor: int | None = Query(None, description="Article ID cursor for pagination"),
) -> ArticleListResponse:
    """List articles, optionally filtered by topic and read state.

    Results are sorted newest-first with cursor-based pagination.
    """
    query = select(Article)
    if topic:
        query = query.join(Article.topics).where(Topic.name == topic)
    if is_read is not None:
        query = query.where(Article.is_read == is_read)
    if cursor is not None:
        query = query.where(Article.id < cursor)

    query = query.order_by(desc(Article.published_at), desc(Article.id)).limit(limit + 1)
    result = await session.execute(query)
    articles = list(result.scalars())

    next_cursor: str | None = None
    if len(articles) > limit:
        next_cursor = str(articles[limit - 1].id)
        articles = articles[:limit]

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in articles],
        next_cursor=next_cursor,
    )


@router.post("/news/{article_id}/read", response_model=ArticleResponse)
async def mark_read(
    article_id: int,
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> ArticleResponse:
    """Mark an article as read."""
    article = await session.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.is_read = True
    await session.flush()
    return ArticleResponse.model_validate(article)
