from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.statistics.repository import StatisticsRepository
from core.statistics.tests.factories import StatisticFactory

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_statistics_endpoint_returns_page(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Return a paginated list of search statistics."""
    statistic = StatisticFactory.build(
        query="How do I change my email?",
        created_at=datetime(2100, 1, 1, tzinfo=UTC),
    )
    await StatisticsRepository(session=session).save(statistic)

    response = await client.get("/api/statistics", params={"limit": 1})

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(statistic.id)
    assert response.json()[0]["query"] == statistic.query


async def test_statistics_endpoint_validates_pagination(
    client: AsyncClient,
) -> None:
    """Reject pagination values outside the allowed range."""
    response = await client.get("/api/statistics", params={"limit": 0})

    assert response.status_code == 422
