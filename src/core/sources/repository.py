from uuid import UUID

from core.common.repository import BaseRepository
from core.sources.models import Source


class SourcesRepository(BaseRepository[Source, UUID]):
    """Data access for source synchronization attempts."""

    model = Source
