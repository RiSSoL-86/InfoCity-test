from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid7

from services.celery.sources.tasks import execute_indexing, run_indexing


async def test_execute_indexing_builds_dependencies() -> None:
    """Build task dependencies and dispose the worker database engine."""
    source_id = uuid7()
    session = MagicMock()
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=session)
    context.__aexit__ = AsyncMock(return_value=False)
    embeddings = MagicMock()
    loader = MagicMock()
    service = MagicMock()
    service.execute = AsyncMock(return_value={"total_count": 1})
    engine = MagicMock()
    engine.dispose = AsyncMock()

    with (
        patch(
            "services.celery.sources.tasks.async_session_factory",
            return_value=context,
        ),
        patch(
            "services.celery.sources.tasks.EmbeddingService",
            return_value=embeddings,
        ),
        patch(
            "services.celery.sources.tasks.CsvLoader",
            return_value=loader,
        ) as loader_class,
        patch(
            "services.celery.sources.tasks.IndexingSourcesCeleryService",
            return_value=service,
        ) as service_class,
        patch("services.celery.sources.tasks.engine", new=engine),
    ):
        result = await execute_indexing(source_id, "data/questions.csv")

    assert result == {"total_count": 1}
    loader_class.assert_called_once_with(path=Path("data/questions.csv"))
    service_class.assert_called_once_with(
        session=session,
        embeddings=embeddings,
        loader=loader,
    )
    service.execute.assert_awaited_once_with(source_id=source_id)
    engine.dispose.assert_awaited_once_with()


def test_run_indexing_executes_async_flow() -> None:
    """Convert task arguments and execute the async indexing flow."""
    source_id = uuid7()
    execute_mock = AsyncMock(return_value={"created_count": 1})

    with patch(
        "services.celery.sources.tasks.execute_indexing",
        new=execute_mock,
    ):
        result = run_indexing.run(str(source_id), "data/questions.csv")

    assert result == {"created_count": 1}
    execute_mock.assert_awaited_once_with(
        source_id=source_id,
        path="data/questions.csv",
    )
