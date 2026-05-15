import sqlite3
from pathlib import Path

from app.config.settings import settings


def get_connection() -> sqlite3.Connection:
    db_path: Path = settings.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA synchronous = NORMAL;")

    return connection