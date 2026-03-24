import os


class Settings:
    database_url: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://bazar:bazar@localhost:5432/bazar_market",
    )
    database_url_sync: str = os.environ.get(
        "DATABASE_URL_SYNC",
        "postgresql+psycopg2://bazar:bazar@localhost:5432/bazar_market",
    )
    redis_url: str = os.environ.get(
        "REDIS_URL",
        "redis://localhost:6379",
    )
    redis_database: str = os.environ.get("REDIS_DATABASE", "0")
    SESSION_SECRET: str = os.environ.get("SESSION_SECRET", "change-me-in-production")
    SESSION_TTL: int = int(os.environ.get("SESSION_TTL", "86400"))


settings = Settings()
