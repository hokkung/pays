"""Pydantic schemas for Topic."""

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TopicBase(BaseModel):
    """Shared topic fields."""

    name: str = Field(..., max_length=200)
    query: str = Field(..., max_length=500)
    enabled: bool = True


class TopicCreate(TopicBase):
    """Payload for creating a topic."""


class TopicUpdate(BaseModel):
    """Payload for partially updating a topic."""

    name: str | None = Field(None, max_length=200)
    query: str | None = Field(None, max_length=500)
    enabled: bool | None = None


class TopicResponse(ORMModel, TopicBase):
    """Topic response with read-only fields."""

    id: int
