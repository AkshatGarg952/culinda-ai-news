from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.db_config import build_async_database_config, build_sync_database_url

database_url, connect_args = build_async_database_config(settings.database_url)

engine = create_async_engine(database_url, echo=False, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

sync_database_url = build_sync_database_url(settings.sync_database_url, settings.database_url)
sync_engine = create_engine(sync_database_url)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
