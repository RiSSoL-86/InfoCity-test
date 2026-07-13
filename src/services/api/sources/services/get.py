from typing import final, override
from uuid import UUID

from core.sources.repository import SourcesRepository
from services.api.common.services import BaseService
from services.api.sources.schemas import SourceItem


@final
class GetSourcesService(BaseService):
    """Return the current state of one synchronization attempt."""

    @override
    async def execute(self, source_id: UUID) -> SourceItem | None:
        """Return one source indexing process."""
        sources_repository = SourcesRepository(session=self.session)
        source = await sources_repository.get(source_id)
        if source is None:
            return None
        return SourceItem.model_validate(source)
