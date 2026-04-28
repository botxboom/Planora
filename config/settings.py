"""Environment-driven application settings."""

from __future__ import annotations

from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = Field(default="planora")
    app_env: str = Field(default="dev")
    judge_threshold: int = Field(default=7, ge=1, le=10)
    max_refinement_loops: int = Field(default=2, ge=0, le=5)
    sqlite_db_path: str = Field(default="data/planora.db")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    db_path = os.getenv("PLANORA_DB_PATH", "data/planora.db")
    return Settings(
        app_name=os.getenv("PLANORA_APP_NAME", "planora"),
        app_env=os.getenv("PLANORA_APP_ENV", "dev"),
        judge_threshold=int(os.getenv("PLANORA_JUDGE_THRESHOLD", "7")),
        max_refinement_loops=int(os.getenv("PLANORA_MAX_REFINEMENT_LOOPS", "2")),
        sqlite_db_path=db_path,
    )
