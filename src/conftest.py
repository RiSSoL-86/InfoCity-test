from collections.abc import AsyncIterator
from unittest.mock import MagicMock
from uuid import uuid7

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app import app
from app_settings import settings
from core import Base
from services.api.common.dependencies import get_celery, get_db, get_embeddings

test_engine = create_async_engine(
    settings.db.url,
    poolclass=NullPool,
)


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Provide isolated temporary tables for one test."""
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        schema = f"test_{uuid7().hex}"
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        await connection.execute(
            text(f'SET LOCAL search_path TO "{schema}", public'),
        )
        await connection.run_sync(
            lambda sync_connection: Base.metadata.create_all(
                sync_connection,
                checkfirst=False,
            ),
        )
        async_session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield async_session
        finally:
            await async_session.close()
            await transaction.rollback()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Provide an API client with the test database session."""

    async def override_db() -> AsyncIterator[AsyncSession]:
        """Return the current test database session."""
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_celery] = MagicMock
    app.dependency_overrides[get_embeddings] = MagicMock
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client
    app.dependency_overrides.clear()
