from typing import Annotated
from uuid import UUID

from celery import Celery  # noqa: TC002
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.common.dependencies import get_celery, get_db
from services.api.sources.schemas import SourceItem
from services.api.sources.services.get import GetSourcesService
from services.api.sources.services.indexing import IndexingSourcesService

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.post(
    "/indexing",
    response_model=SourceItem,
    status_code=status.HTTP_202_ACCEPTED,
)
async def indexing_view(
    session: Annotated[AsyncSession, Depends(get_db)],
    celery: Annotated[Celery, Depends(get_celery)],
) -> SourceItem:
    """Start background indexing of the prepared source file."""
    service = IndexingSourcesService(session=session, celery=celery)
    return await service.execute()


@router.get("/{source_id}", response_model=SourceItem)
async def get_source_view(
    source_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SourceItem:
    """Return the state of a source indexing process."""
    service = GetSourcesService(session=session)
    source = await service.execute(source_id=source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )
    return source
