from uuid import UUID

from core.common.repository import BaseRepository
from core.statistics.models import Statistic


class StatisticsRepository(BaseRepository[Statistic, UUID]):
    """Data access for search statistics."""

    model = Statistic
