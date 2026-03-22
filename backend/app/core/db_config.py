import ssl
import urllib.parse
from typing import Any

LIBPQ_ONLY_PARAMS = {"sslmode", "channel_binding"}


def build_async_database_config(raw_database_url: str) -> tuple[str, dict[str, Any]]:
    database_url = raw_database_url
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://") and "asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    connect_args: dict[str, Any] = {}
    parsed = urllib.parse.urlparse(database_url)
    query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    stripped = {key: value for key, value in query.items() if key in LIBPQ_ONLY_PARAMS}
    cleaned_query = {key: value for key, value in query.items() if key not in LIBPQ_ONLY_PARAMS}

    if cleaned_query != query:
        parsed = parsed._replace(query=urllib.parse.urlencode(cleaned_query))
        database_url = urllib.parse.urlunparse(parsed)

    if stripped.get("sslmode") == "require":
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = context

    return database_url, connect_args


def build_sync_database_url(
    raw_sync_database_url: str | None,
    fallback_database_url: str,
) -> str:
    database_url = raw_sync_database_url or fallback_database_url
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return database_url
