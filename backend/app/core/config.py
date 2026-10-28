from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/research_agent.db"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_OUTPUT_TOKENS: int = 4096

    # Scholarly Discovery APIs
    CROSSREF_MAILTO: str = "research-agent@example.com"
    OPENALEX_EMAIL: str = "research-agent@example.com"

    # Execution limits & budgets
    MAX_RESEARCH_ROUNDS: int = 3
    MAX_SEARCH_QUERIES: int = 15
    MAX_UNIQUE_SOURCES: int = 40
    MAX_PAGE_FETCHES: int = 20
    TASK_TIMEOUT_SECONDS: int = 600
    CONCURRENCY_LIMIT: int = 4

    @property
    def is_llm_configured(self) -> bool:
        return bool(self.LLM_API_KEY and self.LLM_API_KEY.strip())


@lru_cache()
def get_settings() -> Settings:
    return Settings()
