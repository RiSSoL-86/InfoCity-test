from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.sources.choices import Status  # noqa: TC001


class SourceItem(BaseModel):
    """Represent a source indexing process."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: Status
    error: str | None
    total_count: int
    created_count: int
    deleted_count: int
    created_at: datetime
    updated_at: datetime
