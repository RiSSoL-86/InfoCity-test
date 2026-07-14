from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.answers.schemas import AnswerItem, SearchInput
from services.api.answers.services.search import SearchAnswersService
from services.api.common.dependencies import get_db, get_embeddings
from services.rag.embeddings import EmbeddingService  # noqa: TC001

router = APIRouter(prefix="/answers", tags=["Answers"])


@router.post("/search", response_model=list[AnswerItem])
async def search_answers_view(
    data: SearchInput,
    session: Annotated[AsyncSession, Depends(get_db)],
    embeddings: Annotated[EmbeddingService, Depends(get_embeddings)],
) -> list[AnswerItem]:
    """Return the five answers nearest to the query."""
    service = SearchAnswersService(
        session=session,
        embeddings=embeddings,
    )
    return await service.execute(query=data.query)
