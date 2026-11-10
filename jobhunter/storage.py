"""Minimal SQLite persistence; no AI calls or external services."""

from contextlib import closing
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sqlite3

from jobhunter.eligibility import EligibilityDecision, source_digest
from jobhunter.approval import ReviewApproval, verify_approval
from jobhunter.review import ReviewMaterial


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
                connection.execute(
                    """CREATE TABLE IF NOT EXISTS review_approvals (
                        job_id INTEGER NOT NULL REFERENCES jobs(id),
                        review_fingerprint TEXT NOT NULL,
                        decision_id INTEGER NOT NULL UNIQUE REFERENCES job_decisions(id),
                        receipt TEXT NOT NULL,
                        PRIMARY KEY (job_id, review_fingerprint)
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

    def apply_approved_review(self, job_id: int, material: ReviewMaterial, approval: ReviewApproval) -> int:
        """Atomically append a reviewed decision and its full approval audit.

        Replaying the same receipt is idempotent. This is the application-facing
        path for AI reviews; save_decision remains a low-level curated-data API.
        """
        decision, score = verify_approval(material, approval)
        receipt = json.dumps(asdict(approval), ensure_ascii=False, sort_keys=True)
        snapshot = {**asdict(decision), "review": {
            "review_fingerprint": approval.review_fingerprint,
            "analysis_fingerprint": material.analysis_fingerprint,
            "reviewer": approval.reviewer, "note": approval.note,
            "approved_at": approval.approved_at,
        }, "reviewed_score": asdict(score)}
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute("SELECT description FROM jobs WHERE id = ?", (job_id,)).fetchone()
                if row is None or source_digest(row[0]) != decision.source_sha256:
                    raise ValueError("Reviewed source does not match the stored job.")
                existing = connection.execute(
                    "SELECT decision_id, receipt FROM review_approvals WHERE job_id = ? AND review_fingerprint = ?",
                    (job_id, approval.review_fingerprint),
                ).fetchone()
                if existing:
                    if existing[1] != receipt:
                        raise ValueError("This review was already applied with another approval receipt.")
                    return existing[0]
                cursor = connection.execute(
                    "INSERT INTO job_decisions (job_id, status, snapshot) VALUES (?, ?, ?)",
                    (job_id, decision.status, json.dumps(snapshot, ensure_ascii=False)),
                )
                decision_id = cursor.lastrowid
                connection.execute(
                    "INSERT INTO review_approvals (job_id, review_fingerprint, decision_id, receipt) VALUES (?, ?, ?, ?)",
                    (job_id, approval.review_fingerprint, decision_id, receipt),
                )
                return decision_id

    def approval_history(self, job_id: int) -> tuple[dict, ...]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                "SELECT receipt FROM review_approvals WHERE job_id = ? ORDER BY decision_id", (job_id,)
            ).fetchall()
        return tuple(json.loads(row[0]) for row in rows)
