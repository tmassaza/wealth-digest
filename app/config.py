from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione applicativa letta da variabili ambiente e file .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "wealth-digest"
    database_url: str = Field(default="postgresql+psycopg://wealth_digest:wealth_digest@localhost:5432/wealth_digest")
    newsdata_api_key: str = "pub_7b378a6a29934e278f42b8b9916974af"
    newsdata_base_url: str = "https://newsdata.io/api/1/news"
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache

def get_settings() -> Settings:
    """Restituisce una sola istanza condivisa delle impostazioni."""

    return Settings()
