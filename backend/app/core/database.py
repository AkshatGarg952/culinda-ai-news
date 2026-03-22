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

# Strip libpq-specific params from URL that asyncpg does not understand
# Render's DATABASE_URL often contains: sslmode=require, channel_binding=prefer, etc.
LIBPQ_ONLY_PARAMS = {"sslmode", "channel_binding"}
parsed = urllib.parse.urlparse(database_url)
query = dict(urllib.parse.parse_qsl(parsed.query))
stripped = {k: v for k, v in query.items() if k in LIBPQ_ONLY_PARAMS}
cleaned_query = {k: v for k, v in query.items() if k not in LIBPQ_ONLY_PARAMS}
parsed = parsed._replace(query=urllib.parse.urlencode(cleaned_query))
database_url = urllib.parse.urlunparse(parsed)

# Handle SSL if sslmode was present
if stripped.get("sslmode") == "require":
    import ssl
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
