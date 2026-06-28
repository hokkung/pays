"""Application configuration via pydantic-settings (12-factor)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven application settings.

    All values can be overridden via environment variables or a .env file.
    The app runs with zero paid keys using the defaults.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://pays:pays@localhost:5432/pays"

    # Auth (single-user API token)
    api_token: str = "changeme"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # HTTP client
    http_timeout_seconds: float = 30.0

    # Scheduler (cron expressions)
    fetch_news_cron: str = "0 * * * *"
    refresh_prices_cron: str = "0 * * * *"
    refresh_fx_cron: str = "0 * * * *"

    # Data source URLs
    frankfurter_base_url: str = "https://api.frankfurter.app"
    google_news_base_url: str = "https://news.google.com/rss/search"

    # Optional API keys (not required for basic operation)
    fred_api_key: str | None = None


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
