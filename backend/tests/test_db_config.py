from app.core.db_config import build_async_database_config, build_sync_database_url


def test_build_async_database_config_normalizes_render_style_url():
    database_url, connect_args = build_async_database_config(
        "postgresql://user:pass@db.example.com:5432/news_db?sslmode=require&channel_binding=prefer"
    )

    assert database_url == "postgresql+asyncpg://user:pass@db.example.com:5432/news_db"
    assert "ssl" in connect_args


def test_build_sync_database_url_falls_back_to_database_url():
    sync_database_url = build_sync_database_url(
        None,
        "postgresql+asyncpg://user:pass@db.example.com:5432/news_db",
    )

    assert sync_database_url == "postgresql://user:pass@db.example.com:5432/news_db"
