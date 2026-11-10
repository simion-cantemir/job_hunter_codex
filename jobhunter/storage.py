"""Minimal SQLite persistence; no AI calls or external services."""

from contextlib import closing
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sqlite3

from jobhunter.eligibility import EligibilityDecision, source_digest


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
                connection.execute(
                    """CREATE TABLE IF NOT EXISTS job_decisions (
                        id INTEGER PRIMARY KEY,
                        job_id INTEGER NOT NULL REFERENCES jobs(id),
                        status TEXT NOT NULL CHECK (status IN ('rejected', 'needs_review', 'eligible')),
                        snapshot TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
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

    def save_decision(self, job_id: int, decision: EligibilityDecision) -> int:
        """Append a decision; retain prior decisions and the original job text."""
        if decision.status not in {"rejected", "needs_review", "eligible"}:
            raise ValueError("Invalid decision status.")
        if decision.status != "eligible" and not decision.reasons:
            raise ValueError("Rejection or review needs a reason.")
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                row = connection.execute("SELECT description FROM jobs WHERE id = ?", (job_id,)).fetchone()
                if row is None:
                    raise ValueError("Job does not exist.")
                if source_digest(row[0]) != decision.source_sha256:
                    raise ValueError("Decision source does not match the stored job.")
                cursor = connection.execute(
                    "INSERT INTO job_decisions (job_id, status, snapshot) VALUES (?, ?, ?)",
                    (job_id, decision.status, json.dumps(asdict(decision), ensure_ascii=False)),
                )
                return cursor.lastrowid

    def decision_history(self, job_id: int) -> tuple[dict, ...]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                "SELECT snapshot, created_at FROM job_decisions WHERE job_id = ? ORDER BY id", (job_id,)
            ).fetchall()
        return tuple({**json.loads(snapshot), "created_at": created_at} for snapshot, created_at in rows)

    def list_opportunities(self) -> tuple[Job, ...]:
        """List new/review/eligible jobs; exclude the latest rejected decisions."""
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                """SELECT j.id, j.title, j.description FROM jobs j
                   LEFT JOIN job_decisions d ON d.id = (
                       SELECT MAX(id) FROM job_decisions WHERE job_id = j.id
                   )
                   WHERE d.status IS NULL OR d.status != 'rejected'
                   ORDER BY j.id"""
            ).fetchall()
        return tuple(Job(*row) for row in rows)
