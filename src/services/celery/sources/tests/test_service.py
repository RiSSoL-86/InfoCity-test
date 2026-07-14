from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid7

import pytest

from core.answers.models import EMBEDDING_DIMENSION, Answer
from core.answers.repository import AnswersRepository
from core.sources.choices import Status
from core.sources.repository import SourcesRepository
from core.sources.tests.factories import SourceFactory
from services.celery.sources.services.indexing import (
    IndexingSourcesCeleryService,
)
from services.rag.schemas import Pair

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_indexing_service_synchronizes_source(
    session: AsyncSession,
) -> None:
    """Create embeddings and mark a completed indexing process successful."""
    source = await SourcesRepository(session=session).save(
        SourceFactory.build(),
    )
    pair = Pair(
        question="How do I reset my password?",
        answer="Use the recovery form.",
        content_hash="a" * 64,
    )
    loader = MagicMock()
    loader.load = AsyncMock(return_value=[pair])
    embeddings = MagicMock()
    embeddings.embed_passages = AsyncMock(
        return_value=[[0.1] * EMBEDDING_DIMENSION],
    )
    service = IndexingSourcesCeleryService(
        session=session,
        embeddings=embeddings,
        loader=loader,
    )

    result = await service.execute(source_id=source.id)
    stored_source = await SourcesRepository(session=session).get(source.id)

    assert result == {
        "total_count": 1,
        "created_count": 1,
        "deleted_count": 0,
    }
    assert stored_source is not None
    assert stored_source.status is Status.SUCCESS
    assert stored_source.total_count == 1
    assert await AnswersRepository(session=session).get_hashes() == {
        pair.content_hash
    }
    embeddings.embed_passages.assert_awaited_once_with(
        texts=[pair.question],
    )


async def test_indexing_service_skips_existing_pair(
    session: AsyncSession,
) -> None:
    """Avoid rebuilding embeddings for an unchanged source pair."""
    pair = Pair(
        question="Question",
        answer="Answer",
        content_hash="b" * 64,
    )
    await AnswersRepository(session=session).save(
        Answer(
            question=pair.question,
            answer=pair.answer,
            content_hash=pair.content_hash,
            embedding=[0.2] * EMBEDDING_DIMENSION,
        ),
    )
    source = await SourcesRepository(session=session).save(
        SourceFactory.build(),
    )
    loader = MagicMock()
    loader.load = AsyncMock(return_value=[pair])
    embeddings = MagicMock()
    embeddings.embed_passages = AsyncMock()
    service = IndexingSourcesCeleryService(
        session=session,
        embeddings=embeddings,
        loader=loader,
    )

    result = await service.execute(source_id=source.id)

    assert result == {
        "total_count": 1,
        "created_count": 0,
        "deleted_count": 0,
    }
    embeddings.embed_passages.assert_not_awaited()


async def test_indexing_service_marks_failed_source(
    session: AsyncSession,
) -> None:
    """Persist failure details when source loading fails."""
    source = await SourcesRepository(session=session).save(
        SourceFactory.build(),
    )
    loader = MagicMock()
    loader.load = AsyncMock(side_effect=ValueError("invalid csv"))
    service = IndexingSourcesCeleryService(
        session=session,
        embeddings=MagicMock(),
        loader=loader,
    )

    with pytest.raises(ValueError, match="invalid csv"):
        await service.execute(source_id=source.id)

    stored_source = await SourcesRepository(session=session).get(source.id)
    assert stored_source is not None
    assert stored_source.status is Status.FAILURE
    assert stored_source.error == "ValueError: invalid csv"


async def test_indexing_service_requires_source(
    session: AsyncSession,
) -> None:
    """Reject an indexing process for an unknown source."""
    loader = MagicMock()
    loader.load = AsyncMock(return_value=[])
    service = IndexingSourcesCeleryService(
        session=session,
        embeddings=MagicMock(),
        loader=loader,
    )

    with pytest.raises(ValueError, match="Source not found"):
        await service.execute(source_id=uuid7())


async def test_indexing_service_requires_dependencies(
    session: AsyncSession,
) -> None:
    """Reject missing embeddings or source loader dependencies."""
    with pytest.raises(RuntimeError, match="Embeddings are not configured"):
        await IndexingSourcesCeleryService(session=session).execute(
            source_id=uuid7(),
        )

    with pytest.raises(RuntimeError, match="Loader is not configured"):
        await IndexingSourcesCeleryService(
            session=session,
            embeddings=MagicMock(),
        ).execute(source_id=uuid7())
