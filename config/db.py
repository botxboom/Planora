"""SQLite connection helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from config.settings import get_settings


def _db_path() -> Path:
    settings = get_settings()
    path = Path(settings.sqlite_db_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(_db_path())
    connection.row_factory = sqlite3.Row
    return connection
