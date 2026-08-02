from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "D&D AI Game Master"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/dnd_ai"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    ollama_num_ctx: int = 16384       # context window tokens (Ollama default is only 2048)
    ollama_temperature: float = 0.8   # 0.8 balances creativity with coherence for narrative GM
    vector_store_path: Path = Path(__file__).resolve().parents[1] / "data" / "vectors"
    rag_collection_name: str = "dnd_srd_rules"
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 120
    rag_top_k: int = 4

    cors_origins: list[str] = ["http://localhost:5173"]
    secret_key: str
    attachments_dir: Path = Path(__file__).resolve().parents[1] / "uploads" / "campaigns"

    # Rate limiting
    rate_limit_chat: str = "10/minute"
    rate_limit_auth: str = "5/minute"

    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).resolve().parents[1] / ".env",  # backend/.env
            ".env",                                         # CWD/.env (fallback)
        ],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if not v or v == "change-me":
            raise ValueError(
                "SECRET_KEY must be set to a strong random value. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
