from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.common.dependencies import get_db
from services.api.statistics.schemas import StatisticItem
from services.api.statistics.services.list import ListStatisticsService

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("", response_model=list[StatisticItem])
async def get_statistics_view(
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[StatisticItem]:
    """Return paginated search statistics."""
    service = ListStatisticsService(session=session)
    return await service.execute(limit=limit, offset=offset)
