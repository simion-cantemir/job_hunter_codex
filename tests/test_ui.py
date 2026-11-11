"""Simulate UI interactions with Streamlit AppTest, without a browser or real AI calls."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from jobhunter.ollama import ExtractionError
from jobhunter.storage import JobRepository


ROOT = Path(__file__).resolve().parents[1]


class UITests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory(prefix="ui-test-", dir=ROOT)
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "synthetic.sqlite3"
        environment = patch.dict(os.environ, {"JOBHUNTER_DB_PATH": str(self.path)})
        environment.start()
        self.addCleanup(environment.stop)
        self.at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
        self.assertEqual(len(self.at.exception), 0)

    def load(self):
        self.at.button(key="load_saved").click().run()
        self.assertEqual(len(self.at.exception), 0)

    def confirm(self):
        self.at.text_input(key="reviewer").set_value("[SYNTHETIC] UI test reviewer").run()
        self.at.text_area(key="review_note").set_value("Simulated UI confirmation, not user approval.").run()
        next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).check().run()
        self.at.button(key="apply_review").click().run()
        self.assertEqual(len(self.at.exception), 0)

    def test_initial_render_and_offline_load_never_call_model_or_apply(self):
        self.assertEqual(self.at.title[0].value, "Job Hunter AI")
        self.assertEqual(JobRepository(self.path).list_jobs(), ())
        with patch("jobhunter.analysis.analyze_draft") as inference:
            self.load()
        inference.assert_not_called()
        self.assertTrue(self.at.button(key="apply_review").disabled)
        self.assertEqual(len(self.at.metric), 2)
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_explicit_apply_is_audited_and_reruns_do_not_duplicate(self):
        self.load()
        self.confirm()
        repo = JobRepository(self.path)
        job_id = repo.list_jobs()[0].id
        self.assertEqual(len(repo.decision_history(job_id)), 1)
        self.assertEqual(repo.decision_history(job_id)[0]["review"]["reviewer"], "[SYNTHETIC] UI test reviewer")
        self.at.run()
        self.assertEqual(len(repo.decision_history(job_id)), 1)
        self.at.button(key="apply_review").click().run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(len(repo.list_jobs()), 1)
        self.assertEqual(len(repo.approval_history(job_id)), 1)

    def test_source_change_discards_analysis_and_confirmation(self):
        self.load()
        next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).check().run()
        self.at.text_area(key="job_source").set_value("[SYNTHETIC] Different job description.").run()
        self.assertIsNone(self.at.session_state["workflow"].report)
        self.assertIsNone(self.at.session_state["workflow"].approval)
        self.assertFalse(any(button.key == "apply_review" for button in self.at.button))
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_profile_change_invalidates_even_if_job_text_is_unchanged(self):
        self.load()
        next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).check().run()
        self.at.text_area(key="profile_P1").set_value("[SYNTHETIC] Leadership experience changed.").run()
        self.assertIsNone(self.at.session_state["workflow"].report)
        self.assertEqual(JobRepository(self.path).list_jobs(), ())
        self.at.button(key="load_saved").click().run()
        self.assertIsNone(self.at.session_state["workflow"].report)
        self.assertGreater(len(self.at.error), 0)

    def test_correction_requires_note_and_new_confirmation(self):
        self.load()
        next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).check().run()
        area = next(item for item in self.at.text_area if item.key.endswith("_R2_explanation"))
        area.set_value("Nivel B1; participă deja la cursuri. Nivelul profesional nu este confirmat.").run()
        self.assertGreater(len(self.at.error), 0)
        self.assertFalse(any(button.key == "apply_review" for button in self.at.button))
        note = next(item for item in self.at.text_input if item.key.endswith("_R2_note"))
        note.set_value("Corectăm explicația; păstrăm faptul original.").run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertFalse(next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).value)
        self.assertTrue(self.at.button(key="apply_review").disabled)
        self.assertEqual(JobRepository(self.path).list_jobs(), ())
        self.confirm()
        repo = JobRepository(self.path)
        snapshot = repo.approval_history(repo.list_jobs()[0].id)[0]["snapshot_json"]
        self.assertIn("Corectăm explicația", snapshot)

    def test_failed_inference_clears_old_report_and_shows_error(self):
        self.load()
        with patch("jobhunter.analysis.analyze_draft", side_effect=ExtractionError("Synthetic timeout")) as inference:
            self.at.button(key="analyze").click().run()
        inference.assert_called_once()
        self.assertEqual(len(self.at.exception), 0)
        self.assertIsNone(self.at.session_state["workflow"].report)
        self.assertGreater(len(self.at.error), 0)
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_reloading_analysis_requires_fresh_confirmation(self):
        self.load()
        next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).check().run()
        self.load()
        self.assertFalse(next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).value)
        self.assertTrue(self.at.button(key="apply_review").disabled)

    def test_invalid_evidence_blocks_application(self):
        self.load()
        status = next(item for item in self.at.selectbox if item.key.endswith("_R2_status"))
        status.select("confirmed_missing").run()
        note = next(item for item in self.at.text_input if item.key.endswith("_R2_note"))
        note.set_value("Synthetic invalid change: P2 is not an explicit gap.").run()
        self.assertGreater(len(self.at.error), 0)
        self.assertFalse(any(button.key == "apply_review" for button in self.at.button))
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_full_ai_workflow_uses_mocked_transport_and_does_not_apply(self):
        requirements = json.loads((ROOT / "tests/fixtures/job_001.expected.json").read_text(encoding="utf-8"))
        matches = json.loads((ROOT / "tests/fixtures/matches_001.expected.json").read_text(encoding="utf-8"))
        contents = [{"requirements": [{"priority": r["priority"], "quote": r["quote"]}
                                       for r in requirements["requirements"]]}, {"matches": matches["matches"]}]
        replies = [{"model": "llama3.2:3b", "done": True, "done_reason": "stop",
                    "message": {"role": "assistant", "content": json.dumps(content)}} for content in contents]
        with patch("jobhunter.ollama._post_local", side_effect=replies) as transport:
            self.at.button(key="analyze").click().run()
        self.assertEqual(transport.call_count, 2)
        self.assertEqual(len(self.at.exception), 0)
        self.assertIsNotNone(self.at.session_state["workflow"].report)
        self.assertTrue(self.at.button(key="apply_review").disabled)
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_confirmed_mandatory_gap_is_applied_only_after_confirmation(self):
        self.load()
        priority = next(item for item in self.at.selectbox if item.key.endswith("_R3_priority"))
        priority.select("mandatory").run()
        note = next(item for item in self.at.text_input if item.key.endswith("_R3_note"))
        note.set_value("Synthetic policy test: mandatory criterion with explicit gap.").run()
        self.assertEqual(JobRepository(self.path).list_jobs(), ())
        self.confirm()
        repo = JobRepository(self.path)
        self.assertEqual(repo.list_opportunities(), ())
        self.assertEqual(repo.decision_history(repo.list_jobs()[0].id)[0]["status"], "rejected")

    def test_edit_after_application_requires_new_review_without_erasing_audit(self):
        self.load()
        self.confirm()
        repo = JobRepository(self.path)
        job_id = repo.list_jobs()[0].id
        area = next(item for item in self.at.text_area if item.key.endswith("_R2_explanation"))
        area.set_value("Synthetic revised explanation for a second reviewed snapshot.").run()
        note = next(item for item in self.at.text_input if item.key.endswith("_R2_note"))
        note.set_value("Synthetic follow-up revision.").run()
        self.assertIsNone(self.at.session_state["workflow"].approval)
        self.assertFalse(next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).value)
        self.assertEqual(len(repo.decision_history(job_id)), 1)
        self.confirm()
        self.assertEqual(len(repo.list_jobs()), 1)
        self.assertEqual(len(repo.decision_history(job_id)), 2)

    def test_structured_language_controls_are_audited_and_edits_clear_confirmation(self):
        self.load()
        next(c for c in self.at.checkbox if c.key.endswith("_enabled")).check().run()
        minimum = next(s for s in self.at.selectbox if s.key.endswith("_R2_minimum"))
        minimum.select("professional").run()
        level = next(s for s in self.at.selectbox if s.key.endswith("_en_level"))
        level.select("basic").run()
        self.assertGreater(len(self.at.error), 0)  # A positive level requires evidence.
        evidence = next(m for m in self.at.multiselect if m.key.endswith("_en_evidence"))
        evidence.set_value(["P2"]).run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(len(self.at.error), 0)
        self.confirm()
        repo = JobRepository(self.path)
        job_id = repo.list_jobs()[0].id
        snapshot = json.loads(repo.approval_history(job_id)[0]["snapshot_json"])
        self.assertEqual(snapshot["language_review"]["abilities"][0]["level"], "basic")
        self.assertEqual(snapshot["revised_matches"]["matches"][1]["status"], "partial")
        minimum = next(s for s in self.at.selectbox if s.key.endswith("_R2_minimum"))
        minimum.select("fluent").run()
        self.assertIsNone(self.at.session_state["workflow"].approval)
        self.assertFalse(next(c for c in self.at.checkbox if c.key.startswith("confirmation_")).value)
        self.assertEqual(len(repo.decision_history(job_id)), 1)
