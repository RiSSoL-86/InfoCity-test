from datetime import UTC, datetime
from hashlib import sha256
from uuid import uuid7

import factory

from core.answers.models import EMBEDDING_DIMENSION, Answer


class AnswerFactory(factory.Factory):
    """Build answer models for tests."""

    class Meta:
        """Configure the generated model."""

        model = Answer

    id = factory.LazyFunction(uuid7)
    question = factory.Sequence(lambda number: f"Question {number}?")
    answer = factory.Sequence(lambda number: f"Answer {number}.")
    content_hash = factory.LazyAttribute(
        lambda obj: sha256(
            f"{obj.question}\x1f{obj.answer}".encode(),
        ).hexdigest(),
    )
    embedding = factory.LazyFunction(
        lambda: [0.0] * EMBEDDING_DIMENSION,
    )
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))
