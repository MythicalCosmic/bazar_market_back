"""
Seed the first admin user.

Run inside Docker:
    docker compose exec api python scripts/seed_admin.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import secrets

import bcrypt
from sqlalchemy import select

from src.db.session import async_session
from src.db.models.user import User


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_FIRST_NAME = "Super"
ADMIN_LAST_NAME = "Admin"


async def main():
    async with async_session() as session:
        existing = await session.execute(
            select(User).where(User.username == ADMIN_USERNAME)
        )
        if existing.scalar_one_or_none():
            print(f"Admin '{ADMIN_USERNAME}' already exists, skipping.")
            return

        password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()

        admin = User(
            username=ADMIN_USERNAME,
            first_name=ADMIN_FIRST_NAME,
            last_name=ADMIN_LAST_NAME,
            password_hash=password_hash,
            role="admin",
            referral_code=secrets.token_urlsafe(8),
            is_verified=True,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin created: username={ADMIN_USERNAME}, password={ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
