from typing import final, override

from core.statistics.repository import StatisticsRepository
from services.api.common.services import BaseService
from services.api.statistics.schemas import StatisticItem


@final
class ListStatisticsService(BaseService):
    """Return a page of search statistics."""

    @override
    async def execute(self, limit: int, offset: int) -> list[StatisticItem]:
        """Return a page of search statistics."""
        statistics_repository = StatisticsRepository(session=self.session)
        statistics = await statistics_repository.list(
            limit=limit, offset=offset
        )
        return [
            StatisticItem.model_validate(statistic) for statistic in statistics
        ]
