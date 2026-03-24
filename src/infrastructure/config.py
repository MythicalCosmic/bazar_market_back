import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "bazar")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "bazar")
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "bazar_market")

    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379")
    redis_database: str = os.environ.get("REDIS_DATABASE", "0")

    SESSION_SECRET: str = os.environ.get("SESSION_SECRET", "change-me-in-production")
    SESSION_TTL: int = int(os.environ.get("SESSION_TTL", "86400"))

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
