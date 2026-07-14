from typing import Any, cast
from uuid import UUID

from sqlalchemy import select

from core.answers.models import Answer
from core.common.repository import BaseRepository


class AnswersRepository(BaseRepository[Answer, UUID]):
    """Data access for searchable question-answer pairs."""

    model = Answer

    async def get_hashes(self) -> set[str]:
        """Return hashes of all currently indexed pairs."""
        result = await self.session.scalars(select(Answer.content_hash))
        return set(result.all())

    async def sync(
        self,
        answers: list[Answer],
        current_hashes: set[str],
    ) -> int:
        """Atomically add new pairs and delete pairs absent from the source."""
        try:
            query = select(Answer)
            if current_hashes:
                query = query.where(Answer.content_hash.not_in(current_hashes))

            result = await self.session.scalars(query)
            stale_answers = list(result.all())
            for answer in stale_answers:
                await self.session.delete(answer)

            self.session.add_all(answers)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return len(stale_answers)

    async def search(
        self,
        embedding: list[float],
        limit: int,
    ) -> list[Answer]:
        """Return the nearest pairs by cosine distance."""
        vector = cast("Any", Answer.embedding)
        result = await self.session.scalars(
            select(Answer)
            .order_by(vector.cosine_distance(embedding))
            .limit(limit)
        )
        return list(result.all())
