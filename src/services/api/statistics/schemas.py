from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StatisticItem(BaseModel):
    """Represent statistics for one search request."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    query: str
    execution_time_ms: float
    created_at: datetime
