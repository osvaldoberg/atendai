from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI
    openai_api_key: str = ""
    openai_llm_model: str = "gpt-4o"
    openai_llm_fallback_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://atendai:atendai@localhost:5432/atendai"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # Evolution API
    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance_name: str = "atendai"

    # Admin
    admin_username: str = "admin"
    admin_password: str = "changeme"

    # App
    app_env: str = "development"
    app_secret_key: str = "changeme"
    log_level: str = "INFO"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
