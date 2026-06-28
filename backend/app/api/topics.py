"""Topics API router (watchlist CRUD)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthToken, DbSession
from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicResponse

router = APIRouter()


@router.get("", response_model=list[TopicResponse])
async def list_topics(
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> list[TopicResponse]:
    """List all topics."""
    result = await session.execute(select(Topic).order_by(Topic.created_at.desc()))
    return [TopicResponse.model_validate(t) for t in result.scalars()]


@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    payload: TopicCreate,
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> TopicResponse:
    """Create a new topic."""
    topic = Topic(name=payload.name, query=payload.query, enabled=payload.enabled)
    session.add(topic)
    await session.flush()
    return TopicResponse.model_validate(topic)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    session: AsyncSession = DbSession,
    _token: None = AuthToken,
) -> None:
    """Delete a topic by ID."""
    topic = await session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    await session.delete(topic)
