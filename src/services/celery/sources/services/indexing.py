from typing import final, override
from uuid import UUID

from core.answers.models import Answer
from core.answers.repository import AnswersRepository
from core.sources.choices import Status
from core.sources.repository import SourcesRepository
from services.celery.common.services import BaseCeleryService


@final
class IndexingSourcesCeleryService(BaseCeleryService):
    """Index the current CSV snapshot in the vector database."""

    @override
    async def execute(self, source_id: UUID) -> dict[str, int]:
        """Synchronize source pairs with the vector database."""
        if self.embeddings is None:
            raise RuntimeError("Embeddings are not configured")
        if self.loader is None:
            raise RuntimeError("Loader is not configured")

        sources_repository = SourcesRepository(session=self.session)
        answers_repository = AnswersRepository(session=self.session)

        data = {"status": Status.STARTED, "error": None}
        source = await sources_repository.update(pk=source_id, data=data)
        if source is None:
            raise ValueError(f"Source not found: {source_id}")

        try:
            pairs = await self.loader.load()
            existing_hashes = await answers_repository.get_hashes()
            new_pairs = [
                pair
                for pair in pairs
                if pair.content_hash not in existing_hashes
            ]
            vectors = (
                await self.embeddings.embed_passages(
                    texts=[pair.question for pair in new_pairs],
                )
                if new_pairs
                else []
            )
            new_answers = [
                Answer(
                    question=pair.question,
                    answer=pair.answer,
                    content_hash=pair.content_hash,
                    embedding=vector,
                )
                for pair, vector in zip(new_pairs, vectors, strict=True)
            ]
            current_hashes = {pair.content_hash for pair in pairs}
            deleted_count = await answers_repository.sync(
                answers=new_answers,
                current_hashes=current_hashes,
            )
            result = {
                "total_count": len(pairs),
                "created_count": len(new_answers),
                "deleted_count": deleted_count,
            }
            await sources_repository.update(
                source_id,
                {"status": Status.SUCCESS, "error": None, **result},
            )
            return result
        except Exception as error:
            await sources_repository.update(
                source_id,
                {
                    "status": Status.FAILURE,
                    "error": f"{type(error).__name__}: {error}",
                },
            )
            raise
