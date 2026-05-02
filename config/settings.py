"""Environment-driven application settings."""

from __future__ import annotations

from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str = Field(default="planora")
    app_env: str = Field(default="dev")
    judge_threshold: int = Field(default=7, ge=1, le=10)
    max_refinement_loops: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Max judge→feedback→retry cycles before giving up (lower = faster).",
    )
    skip_web_search: bool = Field(
        default=False,
        description="If true, web_search_travel returns immediately without calling Tavily.",
    )
    web_search_cache_ttl_seconds: int = Field(
        default=3600,
        ge=0,
        description="TTL for identical Tavily queries (0 disables cache).",
    )
    sqlite_db_path: str = Field(default="data/planora.db")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    db_path = os.getenv("PLANORA_DB_PATH", "data/planora.db")
    return Settings(
        app_name=os.getenv("PLANORA_APP_NAME", "planora"),
        app_env=os.getenv("PLANORA_APP_ENV", "dev"),
        judge_threshold=int(os.getenv("PLANORA_JUDGE_THRESHOLD", "7")),
        max_refinement_loops=int(os.getenv("PLANORA_MAX_REFINEMENT_LOOPS", "1")),
        skip_web_search=_env_truthy("PLANORA_SKIP_WEB_SEARCH", "false"),
        web_search_cache_ttl_seconds=int(os.getenv("PLANORA_WEB_SEARCH_CACHE_TTL", "3600")),
        sqlite_db_path=db_path,
    )
