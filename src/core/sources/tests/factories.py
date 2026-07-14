from datetime import UTC, datetime
from uuid import uuid7

import factory

from core.sources.choices import Status
from core.sources.models import Source


class SourceFactory(factory.Factory):
    """Build source models for tests."""

    class Meta:
        """Configure the generated model."""

        model = Source

    id = factory.LazyFunction(uuid7)
    filename = factory.Sequence(lambda number: f"questions-{number}.csv")
    status = Status.PENDING
    error = None
    total_count = 0
    created_count = 0
    deleted_count = 0
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))
