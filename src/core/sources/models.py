from uuid import UUID, uuid7

from sqlalchemy import (
    CheckConstraint,
    Enum,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.common.models import Base
from core.sources.choices import Status


class Source(Base):
    """A dataset synchronization started from the bundled CSV file."""

    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint(
            "char_length(trim(filename)) > 0",
            name="ck_sources_filename_not_blank",
        ),
        CheckConstraint(
            "total_count >= 0",
            name="ck_sources_total_count_not_negative",
        ),
        CheckConstraint(
            "created_count >= 0",
            name="ck_sources_created_count_not_negative",
        ),
        CheckConstraint(
            "deleted_count >= 0",
            name="ck_sources_deleted_count_not_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="source_status"),
        default=Status.PENDING,
        server_default=Status.PENDING.value,
        nullable=False,
    )
    error: Mapped[str | None] = mapped_column(Text)
    total_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    created_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    deleted_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
