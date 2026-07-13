from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from core.common.models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[ModelT: Base, IdT]:
    """Generic data-access layer."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session."""
        self.session = session

    async def get(self, pk: IdT) -> ModelT | None:
        """Return a single entity by primary key, or None if absent."""
        return await self.session.get(self.model, pk)

    async def list(self, limit: int, offset: int) -> list[ModelT]:
        """Return a page of entities, newest first."""
        result = await self.session.execute(
            select(self.model)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def save(self, entity: ModelT) -> ModelT:
        """Persist a new or modified entity, commit and return it."""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def create(self, data: Mapping[str, Any]) -> ModelT:
        """Build an entity from `data`, persist it and return it."""
        return await self.save(self.model(**dict(data)))

    async def update(self, pk: IdT, data: dict[str, Any]) -> ModelT | None:
        """Apply `data` to the entity with `pk`; return None if absent."""
        entity = await self.get(pk)
        if entity is None:
            return None
        for field, value in data.items():
            setattr(entity, field, value)
        return await self.save(entity)

    async def delete(self, pk: IdT) -> None:
        """Delete the entity with `pk` if it exists, and commit."""
        entity = await self.get(pk)
        if entity is not None:
            await self.session.delete(entity)
            await self.session.commit()
