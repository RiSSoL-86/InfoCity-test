from uuid import UUID, uuid7

from sqlalchemy import CheckConstraint, Float, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from core.common.models import Base


class Statistic(Base):
    """Timing statistics for one user search request."""

    __tablename__ = "statistics"
    __table_args__ = (
        CheckConstraint(
            "char_length(trim(query)) > 0",
            name="ck_statistics_query_not_blank",
        ),
        CheckConstraint(
            "execution_time_ms >= 0",
            name="ck_statistics_execution_time_not_negative",
        ),
        Index("ix_statistics_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
