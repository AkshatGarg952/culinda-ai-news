from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "news_db"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/news_db"
    sync_database_url: str = "postgresql://postgres:postgres@localhost:5432/news_db"
    gemini_api_key: str = ""
    smtp_email: str = ""
    smtp_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
