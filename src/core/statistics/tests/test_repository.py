from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.statistics.models import Statistic
from core.statistics.repository import StatisticsRepository
from core.statistics.tests.factories import StatisticFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_statistics_repository_lists_newest_first(
    session: AsyncSession,
) -> None:
    """List statistics in descending creation order."""
    repository = StatisticsRepository(session=session)
    older = StatisticFactory.build(
        query="older",
        created_at=datetime(2099, 1, 1, tzinfo=UTC),
    )
    newer = StatisticFactory.build(
        query="newer",
        created_at=datetime(2100, 1, 1, tzinfo=UTC),
    )
    await repository.save(older)
    await repository.save(newer)

    result = await repository.list(limit=1, offset=0)

    assert result == [newer]


def test_statistic_factory_builds_model() -> None:
    """Build a complete statistic model without persistence."""
    statistic = StatisticFactory.build(execution_time_ms=25.5)

    assert isinstance(statistic, Statistic)
    assert statistic.execution_time_ms == 25.5
