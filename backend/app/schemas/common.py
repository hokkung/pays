"""Common schema helpers (pagination, etc.)."""

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for all Pydantic models that read from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class CursorPage(BaseModel):
    """Generic cursor-based pagination envelope."""

    items: list  # type: ignore[type-arg]
    next_cursor: str | None = None
