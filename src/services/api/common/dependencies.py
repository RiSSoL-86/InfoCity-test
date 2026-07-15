from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, cast

from celery import Celery  # noqa: TC002
from fastapi import Request  # noqa: TC002

from database.engine import async_session_factory
from services.rag.embeddings import EmbeddingService  # noqa: TC001

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Provide one database session per FastAPI request."""
    async with async_session_factory() as session:
        yield session


def get_celery(request: Request) -> Celery:
    """Return the Celery application configured at startup."""
    return cast("Celery", request.app.state.celery)


def get_embeddings(request: Request) -> EmbeddingService:
    """Return the embedding client initialized by FastAPI lifespan."""
    return cast("EmbeddingService", request.app.state.embeddings)
