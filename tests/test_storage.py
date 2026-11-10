"""Integration checks using synthetic jobs and temporary SQLite files."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from jobhunter.storage import JobRepository


class StorageTests(unittest.TestCase):
    def setUp(self):
        # Keep temporary files inside the project, and clean up only this folder.
        self.directory = TemporaryDirectory(prefix="jobhunter-test-", dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "synthetic.sqlite3"

    def test_job_survives_repository_reopening(self):
        repository = JobRepository(self.path)
        title = "[SYNTHETIC] Engineering Manager — Cluj"
        description = "Lead a QA team. Candidate's text: '); DROP TABLE jobs; --\nLocație: România."
        job_id = repository.add(title, description)

        # A fresh instance reads the committed record, including untrusted text.
        reopened = JobRepository(self.path)
        job = reopened.get(job_id)
        self.assertIsNotNone(job)
        self.assertEqual((job.id, job.title, job.description), (job_id, title, description))
        self.assertIsNone(reopened.get(job_id + 1))

    def test_blank_input_is_rejected_without_saving(self):
        repository = JobRepository(self.path)
        for title, description in [(" ", "Synthetic description"), ("Synthetic title", "\n")]:
            with self.subTest(title=title, description=description):
                with self.assertRaises(ValueError):
                    repository.add(title, description)
        self.assertIsNone(repository.get(1))
