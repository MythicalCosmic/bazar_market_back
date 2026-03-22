from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str = getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(getenv("ADMIN_ID", "0"))
    DATABASE_URL: str = getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db")
    DEBUG: bool = getenv("DEBUG", "True").lower() == "true"


settings = Settings()
