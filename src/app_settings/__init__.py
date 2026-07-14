from pydantic import BaseModel, Field

from app_settings.app import AppSettings
from app_settings.celery import CelerySettings
from app_settings.database import DatabaseSettings
from app_settings.embedding import EmbeddingSettings
from app_settings.source import SourceSettings

__all__ = ["settings"]


class Settings(BaseModel):
    """Application settings grouped by domain."""

    app: AppSettings = Field(default_factory=AppSettings)
    db: DatabaseSettings = Field(default_factory=lambda: DatabaseSettings())
    celery: CelerySettings = Field(default_factory=CelerySettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    source: SourceSettings = Field(default_factory=SourceSettings)


def get_settings() -> Settings:
    """Return the settings singleton."""
    return Settings()


settings = get_settings()
