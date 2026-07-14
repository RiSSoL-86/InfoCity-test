from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from uuid import uuid7

import pytest

from app import app
from app_settings import settings
from services.api.common.dependencies import get_celery
from services.api.sources.services.indexing import IndexingSourcesService

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_indexing_and_get_source_endpoints(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Create an indexing process and return its current state."""
    celery = MagicMock()
    task = MagicMock()
    celery.signature.return_value = task
    app.dependency_overrides[get_celery] = lambda: celery

    create_response = await client.post("/api/sources/indexing")
    source_id = create_response.json()["id"]
    get_response = await client.get(f"/api/sources/{source_id}")

    assert create_response.status_code == 202
    assert create_response.json()["status"] == "PENDING"
    assert get_response.status_code == 200
    assert get_response.json()["id"] == source_id
    celery.signature.assert_called_once_with(
        "sources.indexing",
        kwargs={
            "source_id": source_id,
            "path": str(settings.source.file_path),
        },
    )
    task.delay.assert_called_once_with()


async def test_get_source_endpoint_returns_not_found(
    client: AsyncClient,
) -> None:
    """Return 404 for an unknown source."""
    response = await client.get(f"/api/sources/{uuid7()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Source not found"}


async def test_indexing_service_requires_celery(
    session: AsyncSession,
) -> None:
    """Fail explicitly when Celery is not configured."""
    service = IndexingSourcesService(session=session)

    with pytest.raises(RuntimeError, match="Celery is not configured"):
        await service.execute()


async def test_indexing_service_requires_source_file(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Fail explicitly when the configured CSV file is missing."""
    missing_path = tmp_path / "missing.csv"
    monkeypatch.setattr(settings.source, "file_path", missing_path)
    service = IndexingSourcesService(
        session=session,
        celery=MagicMock(),
    )

    with pytest.raises(FileNotFoundError, match="Source file not found"):
        await service.execute()
