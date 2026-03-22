import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif database_url.startswith("postgresql://") and "asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

connect_args = {}
if "sslmode" in database_url:
    parsed = urllib.parse.urlparse(database_url)
    query = dict(urllib.parse.parse_qsl(parsed.query))
    if "sslmode" in query:
        ssl_mode = query.pop("sslmode")
        new_query = urllib.parse.urlencode(query)
        parsed = parsed._replace(query=new_query)
        database_url = urllib.parse.urlunparse(parsed)
        if ssl_mode == "require":
            import ssl
            # Simple permissive SSL context for Render
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx

engine = create_async_engine(database_url, echo=False, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

sync_database_url = settings.sync_database_url
if sync_database_url.startswith("postgres://"):
    sync_database_url = sync_database_url.replace("postgres://", "postgresql://", 1)

sync_engine = create_engine(sync_database_url)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
