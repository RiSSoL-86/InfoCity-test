from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app import app
from core.answers.repository import AnswersRepository
from core.answers.tests.factories import AnswerFactory
from core.statistics.repository import StatisticsRepository
from services.api.answers.services.search import SearchAnswersService
from services.api.common.dependencies import get_embeddings

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_search_endpoint_returns_answers(client: AsyncClient) -> None:
    """Return semantic search results and store statistics."""
    answer = AnswerFactory.build(
        question="How can I reset my password?",
        answer="Use the password recovery form.",
    )
    embeddings = MagicMock()
    embeddings.embed_query = AsyncMock(return_value=[0.1, 0.2])
    app.dependency_overrides[get_embeddings] = lambda: embeddings
    search_mock = AsyncMock(return_value=[answer])
    create_mock = AsyncMock()

    with (
        patch.object(AnswersRepository, "search", new=search_mock),
        patch.object(StatisticsRepository, "create", new=create_mock),
    ):
        response = await client.post(
            "/api/answers/search",
            json={"query": "I forgot my password"},
        )

    assert response.status_code == 200
    assert response.json() == [
        {
            "question": "How can I reset my password?",
            "answer": "Use the password recovery form.",
        }
    ]
    embeddings.embed_query.assert_awaited_once_with(
        text="I forgot my password",
    )
    search_mock.assert_awaited_once_with(embedding=[0.1, 0.2], limit=5)
    assert create_mock.await_args.kwargs["data"]["query"] == (
        "I forgot my password"
    )


@pytest.mark.parametrize("query", ["", "   "])
async def test_search_endpoint_rejects_blank_query(
    client: AsyncClient,
    query: str,
) -> None:
    """Reject an empty semantic search query."""
    response = await client.post(
        "/api/answers/search",
        json={"query": query},
    )

    assert response.status_code == 422


async def test_search_service_requires_embeddings(
    session: AsyncSession,
) -> None:
    """Fail explicitly when embeddings are not configured."""
    service = SearchAnswersService(session=session)

    with pytest.raises(RuntimeError, match="Embeddings are not configured"):
        await service.execute(query="question")
