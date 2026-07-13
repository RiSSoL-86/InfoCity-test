from uuid import UUID, uuid7

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.common.models import Base

EMBEDDING_DIMENSION = 384


class Answer(Base):
    """An active question-answer pair used for semantic search."""

    __tablename__ = "answers"
    __table_args__ = (
        CheckConstraint(
            "char_length(trim(question)) > 0",
            name="ck_answers_question_not_blank",
        ),
        CheckConstraint(
            "char_length(trim(answer)) > 0",
            name="ck_answers_answer_not_blank",
        ),
        UniqueConstraint(
            "content_hash",
            name="uq_answers_content_hash",
        ),
        Index(
            "ix_answers_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIMENSION),
        nullable=False,
    )
