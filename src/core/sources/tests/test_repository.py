from typing import TYPE_CHECKING
from uuid import uuid7

from core.sources.choices import Status
from core.sources.models import Source
from core.sources.repository import SourcesRepository
from core.sources.tests.factories import SourceFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_source_repository_crud(session: AsyncSession) -> None:
    """Create, list, update, and delete a source."""
    repository = SourcesRepository(session=session)

    source = await repository.create(
        data={"filename": "questions.csv", "status": Status.PENDING},
    )

    assert await repository.get(source.id) == source
    assert await repository.list(limit=10, offset=0) == [source]

    updated = await repository.update(
        pk=source.id,
        data={"status": Status.SUCCESS, "total_count": 20},
    )
    assert updated is not None
    assert updated.status is Status.SUCCESS
    assert updated.total_count == 20

    await repository.delete(source.id)
    assert await repository.get(source.id) is None
    await repository.delete(source.id)


async def test_source_repository_returns_none_for_unknown_id(
    session: AsyncSession,
) -> None:
    """Return None when updating a missing source."""
    repository = SourcesRepository(session=session)

    result = await repository.update(
        pk=uuid7(),
        data={"status": Status.FAILURE},
    )

    assert result is None


def test_source_factory_builds_model() -> None:
    """Build a complete source model without persistence."""
    source = SourceFactory.build(status=Status.STARTED)

    assert isinstance(source, Source)
    assert source.status is Status.STARTED
    assert source.filename.endswith(".csv")
