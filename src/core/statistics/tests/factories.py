from datetime import UTC, datetime
from uuid import uuid7

import factory

from core.statistics.models import Statistic


class StatisticFactory(factory.Factory):
    """Build statistic models for tests."""

    class Meta:
        """Configure the generated model."""

        model = Statistic

    id = factory.LazyFunction(uuid7)
    query = factory.Sequence(lambda number: f"Search query {number}")
    execution_time_ms = 10.0
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))
