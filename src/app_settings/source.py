from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app_settings.constants import ENV_FILE, PROJECT_DIR


class SourceSettings(BaseSettings):
    """Settings for the bundled question-answer CSV file."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="SOURCE_",
        extra="ignore",
    )

    file_path: Path = PROJECT_DIR / "data" / "questions.csv"

    @field_validator("file_path", mode="after")
    @classmethod
    def resolve_file_path(cls, value: Path) -> Path:
        """Resolve relative source paths from the project directory."""
        if value.is_absolute():
            return value
        return PROJECT_DIR / value
