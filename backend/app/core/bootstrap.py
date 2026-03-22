import asyncio
import logging
import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.schema import User, UserRole
from app.seed import seed_sources

logger = logging.getLogger(__name__)
MVP_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def run_migrations() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    alembic_config = Config(str(base_dir / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(base_dir / "alembic"))
    command.upgrade(alembic_config, "head")


async def ensure_mvp_user() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == MVP_USER_ID))
        if result.scalars().first():
            return

        session.add(
            User(
                id=MVP_USER_ID,
                name="MVP User",
                email="mvp@culinda.ai",
                role=UserRole.admin,
            )
        )
        await session.commit()
        logger.info("seeded_mvp_user")


async def initialize_database() -> None:
    await asyncio.to_thread(run_migrations)
    await ensure_mvp_user()
    await seed_sources()
