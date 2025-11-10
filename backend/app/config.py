from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "D&D AI Game Master"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/dnd_ai"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    vector_store_path: Path = Path(__file__).resolve().parents[1] / "data" / "vectors"
    rag_collection_name: str = "dnd_srd_rules"
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 120
    rag_top_k: int = 4

    cors_origins: list[str] = ["http://localhost:5173"]
    secret_key: str = "change-me"
    attachments_dir: Path = Path(__file__).resolve().parents[1] / "uploads" / "campaigns"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
