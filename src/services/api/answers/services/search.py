from datetime import UTC, datetime
from time import perf_counter
from typing import final, override

from core.answers.repository import AnswersRepository
from core.statistics.repository import StatisticsRepository
from services.api.answers.schemas import AnswerItem
from services.api.common.services import BaseService

SEARCH_LIMIT = 5


@final
class SearchAnswersService(BaseService):
    """Find the nearest answers and store query timing statistics."""

    @override
    async def execute(self, query: str) -> list[AnswerItem]:
        """Search for answers and store request statistics."""
        if self.embeddings is None:
            raise RuntimeError("Embeddings are not configured")

        received_at = datetime.now(UTC)
        started_at = perf_counter()

        embedding = await self.embeddings.embed_query(text=query)
        answers_repository = AnswersRepository(session=self.session)
        answers = await answers_repository.search(
            embedding=embedding,
            limit=SEARCH_LIMIT,
        )

        execution_time_ms = (perf_counter() - started_at) * 1000
        statistics_repository = StatisticsRepository(session=self.session)
        data = {
            "query": query,
            "execution_time_ms": execution_time_ms,
            "created_at": received_at,
        }
        await statistics_repository.create(data=data)
        return [AnswerItem.model_validate(answer) for answer in answers]
