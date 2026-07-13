from typing import final, override

from app_settings import settings
from core.sources.choices import Status
from core.sources.repository import SourcesRepository
from services.api.common.services import BaseService
from services.api.sources.schemas import SourceItem


@final
class IndexingSourcesService(BaseService):
    """Create and enqueue a source indexing process."""

    @override
    async def execute(self) -> SourceItem:
        """Create and enqueue a source indexing process."""
        if self.celery is None:
            raise RuntimeError("Celery is not configured")

        path = settings.source.file_path
        if not path.is_file():
            raise FileNotFoundError(f"Source file not found: {path}")

        sources_repository = SourcesRepository(session=self.session)
        data = {"filename": path.name, "status": Status.PENDING}
        source = await sources_repository.create(data=data)

        sources_indexing_task = self.celery.signature(
            "sources.indexing",
            kwargs={
                "source_id": str(source.id),
                "path": str(path),
            },
        )
        sources_indexing_task.delay()

        return SourceItem.model_validate(source)
