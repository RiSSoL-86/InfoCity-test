from pydantic_settings import BaseSettings, SettingsConfigDict

from app_settings.constants import ENV_FILE


class CelerySettings(BaseSettings):
    """Read Celery broker/backend from CELERY_* env vars."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="CELERY_",
        extra="ignore",
    )

    broker_url: str = "redis://redis:6379/0"
    result_backend: str = "redis://redis:6379/1"
    task_track_started: bool = True
