"""FastAPI application factory."""

import logging

from fastapi import FastAPI

from app.api.assets import router as assets_router
from app.api.fx import router as fx_router
from app.api.jobs import router as jobs_router
from app.api.news import router as news_router
from app.api.topics import router as topics_router

logging.getLogger(__name__).addHandler(logging.NullHandler())


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A configured FastAPI instance with all routers registered.
    """
    app = FastAPI(
        title="Pays",
        description="Personal finance & asset management API",
        version="0.1.0",
    )

    app.include_router(news_router, prefix="/api", tags=["news"])
    app.include_router(topics_router, prefix="/api/topics", tags=["topics"])
    app.include_router(assets_router, prefix="/api/assets", tags=["assets"])
    app.include_router(fx_router, prefix="/api/fx", tags=["fx"])
    app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])

    @app.get("/healthz", tags=["health"])
    async def healthz() -> dict[str, str]:
        """Liveness probe."""
        return {"status": "ok"}

    return app


app = create_app()
