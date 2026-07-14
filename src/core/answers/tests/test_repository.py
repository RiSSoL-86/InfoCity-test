from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from core.answers.models import EMBEDDING_DIMENSION, Answer
from core.answers.repository import AnswersRepository
from core.answers.tests.factories import AnswerFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_answer_repository_hashes_and_vector_search(
    session: AsyncSession,
) -> None:
    """Return stored hashes and the nearest vector."""
    repository = AnswersRepository(session=session)
    nearest_vector = [1.0] + [0.0] * (EMBEDDING_DIMENSION - 1)
    other_vector = [0.0, 1.0] + [0.0] * (EMBEDDING_DIMENSION - 2)
    nearest = AnswerFactory.build(embedding=nearest_vector)
    other = AnswerFactory.build(embedding=other_vector)
    await repository.save(nearest)
    await repository.save(other)

    hashes = await repository.get_hashes()
    result = await repository.search(embedding=nearest_vector, limit=1)

    assert hashes == {nearest.content_hash, other.content_hash}
    assert result == [nearest]


async def test_answer_repository_synchronizes_snapshot(
    session: AsyncSession,
) -> None:
    """Insert current answers and remove stale answers."""
    repository = AnswersRepository(session=session)
    stale = AnswerFactory.build()
    current = AnswerFactory.build()
    await repository.save(stale)

    deleted_count = await repository.sync(
        answers=[current],
        current_hashes={current.content_hash},
    )

    assert deleted_count == 1
    assert await repository.get(stale.id) is None
    assert await repository.get(current.id) == current


async def test_answer_repository_rolls_back_failed_sync(
    session: AsyncSession,
) -> None:
    """Roll back synchronization when commit fails."""
    repository = AnswersRepository(session=session)
    with patch.object(
        session,
        "commit",
        new=AsyncMock(side_effect=RuntimeError("commit failed")),
    ):
        with pytest.raises(RuntimeError, match="commit failed"):
            await repository.sync(answers=[], current_hashes=set())


def test_answer_factory_builds_model() -> None:
    """Build a complete answer model without persistence."""
    answer = AnswerFactory.build()

    assert isinstance(answer, Answer)
    assert len(answer.embedding) == EMBEDDING_DIMENSION
    assert len(answer.content_hash) == 64
