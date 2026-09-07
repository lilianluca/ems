from enum import StrEnum

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Deployment environment the application is running in."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env")

    # --- Application ---
    environment: Environment = Environment.PRODUCTION

    # --- Postgres ---
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    # --- InfluxDB ---
    influxdb_host: str = "http://influxdb:8181"
    influxdb_token: str
    influxdb_database: str

    # --- JWT ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- OTE ---
    ote_api_base_url: str = "https://spotovaelektrina.cz/api/v1/price"

    # --- Tariff ---
    # The spot price is only part of what a kWh costs. Importing adds the
    # supplier's margin, the regulated fees set by ERÚ and VAT; exporting is paid
    # as the bare commodity. That asymmetry is what makes storing own generation
    # worth more than arbitrage, so the optimiser needs both sides separately.
    #
    # These are placeholder magnitudes — replace them from an actual bill, and
    # note that they differ by distribution area and tariff rate.
    supplier_margin_czk_kwh: float = 0.30
    distribution_fees_czk_kwh: float = 1.80
    vat_rate: float = 0.21
    # Share of the spot price paid for electricity fed back into the grid.
    export_factor: float = 1.0

    # --- Celery ---
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    @computed_field
    @property
    def is_development(self) -> bool:
        """True when running locally with relaxed security settings."""
        return self.environment is Environment.DEVELOPMENT

    @computed_field
    @property
    def database_url(self) -> str:
        """Construct the database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()  # type: ignore
