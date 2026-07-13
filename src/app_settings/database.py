from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from app_settings.constants import ENV_FILE


class DatabaseSettings(BaseSettings):
    """Read database connection values from POSTGRES_* env vars."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="POSTGRES_",
        extra="ignore",
    )

    db: str
    user: str
    password: str
    host: str
    port: int = 5432

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """Async DSN for SQLAlchemy + asyncpg."""
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db,
        ).render_as_string(
            hide_password=False,
        )
