"""Minimal SQLite persistence; no AI calls or external services."""

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class Job:
    id: int
    title: str
    description: str


class JobRepository:
    """Persist jobs in an explicitly chosen local database file."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL
                    )"""
                )

    def add(self, title: str, description: str) -> int:
        if not title.strip() or not description.strip():
            raise ValueError("Title and description must not be blank.")
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO jobs (title, description) VALUES (?, ?)",
                    (title, description),
                )
                return cursor.lastrowid

    def get(self, job_id: int) -> Job | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                "SELECT id, title, description FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
        return Job(*row) if row is not None else None
