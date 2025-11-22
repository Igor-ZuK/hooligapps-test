import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=BASE_DIR / ".env",
        extra="allow",
    )

    service_name: str = "hooligapps_test_backend"
    version: str = "0.0.1"
    api_version: str = "1.0"
    api_version_prefix: str = "v1"

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
    log_level: str = "info"
    reload: bool = False
    debug: bool = False
    generate_docs: bool = True

    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_host: str = Field(default="localhost")
    postgres_port: str = Field(default="5432")
    postgres_dbname: str = Field(default="hooligapps_test_backend_db")
    postgres_pool_size: int = 30
    postgres_max_overflow: int = 10
    postgres_recycle_pool_ttl: int = 300
    log_db_session: bool = False

    front_domains: list[str] = ["http://localhost:8080"]

    @property
    def database_url(self) -> str:
        # Check for DATABASE_URL environment variable first
        database_url_env = os.getenv("DATABASE_URL")
        if database_url_env:
            return database_url_env

        # Otherwise, construct from individual fields
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_dbname}"
        )


settings = Settings()

engine = create_async_engine(
    settings.database_url,
    future=True,
    echo=settings.log_db_session,
    pool_size=settings.postgres_pool_size,
    max_overflow=settings.postgres_max_overflow,
    pool_recycle=settings.postgres_recycle_pool_ttl,
)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
