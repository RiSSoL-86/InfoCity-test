import asyncio
from pathlib import Path
from uuid import UUID

from app_settings import settings
from database.engine import async_session_factory, engine
from services.celery import celery_app
from services.celery.sources.services.indexing import (
    IndexingSourcesCeleryService,
)
from services.rag.embeddings import EmbeddingService
from services.rag.loaders import CsvLoader


async def execute_indexing(source_id: UUID, path: str) -> dict[str, int]:
    """Run one indexing process with an async database session."""
    embeddings = EmbeddingService(
        model_name=settings.embedding.model_name,
    )
    loader = CsvLoader(path=Path(path))
    try:
        async with async_session_factory() as session:
            service = IndexingSourcesCeleryService(
                session=session,
                embeddings=embeddings,
                loader=loader,
            )
            return await service.execute(source_id=source_id)
    finally:
        await engine.dispose()


@celery_app.task(name="sources.indexing")
def run_indexing(source_id: str, path: str) -> dict[str, int]:
    """Celery entry point for source indexing."""
    return asyncio.run(
        execute_indexing(source_id=UUID(source_id), path=path),
    )
