import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(override=False)


class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "bazar")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "bazar")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "bazar_market")

    # Redis
    redis_url: str = os.getenv('REDIS_URL')
    redis_database: str = os.getenv('REDIS_DATABASE')

    # Session
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-me-in-production")
    SESSION_TTL: int = int(os.getenv("SESSION_TTL", "86400"))  # 24 hours

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
