from pydantic_settings import BaseSettings, SettingsConfigDict

from app_settings.constants import ENV_FILE


class EmbeddingSettings(BaseSettings):
    """Embedding model settings."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="EMBEDDING_",
        extra="ignore",
    )

    model_name: str = "intfloat/multilingual-e5-small"
