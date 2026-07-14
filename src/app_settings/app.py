from pydantic_settings import BaseSettings, SettingsConfigDict

from app_settings.constants import ENV_FILE


class AppSettings(BaseSettings):
    """General service settings."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = "InfoCity Semantic Search"
    debug: bool = False
