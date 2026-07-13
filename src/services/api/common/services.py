from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from celery import Celery
    from sqlalchemy.ext.asyncio import AsyncSession

    from services.rag.embeddings import EmbeddingService


class BaseService(ABC):
    """Base class for all application services."""

    def __init__(
        self,
        session: AsyncSession,
        celery: Celery | None = None,
        embeddings: EmbeddingService | None = None,
    ) -> None:
        """Initialize shared API service dependencies."""
        self.session = session
        self.celery = celery
        self.embeddings = embeddings

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Run the business operation."""
        raise NotImplementedError
