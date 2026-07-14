from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from services.rag.embeddings import EmbeddingService
    from services.rag.loaders import CsvLoader


class BaseCeleryService(ABC):
    """Base class for business operations executed by Celery."""

    def __init__(
        self,
        session: AsyncSession,
        embeddings: EmbeddingService | None = None,
        loader: CsvLoader | None = None,
    ) -> None:
        """Initialize shared Celery service dependencies."""
        self.session = session
        self.embeddings = embeddings
        self.loader = loader

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Run the background business operation."""
        raise NotImplementedError
