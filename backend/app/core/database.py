from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

sync_engine = create_engine(settings.sync_database_url)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
