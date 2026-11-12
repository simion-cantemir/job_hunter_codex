"""Simulate UI interactions with Streamlit AppTest, without a browser or real AI calls."""

import json
import sqlite3
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from contextlib import closing

from streamlit.testing.v1 import AppTest

from jobhunter.ollama import ExtractionError, SourceQuoteError
from jobhunter.storage import JobRepository
from jobhunter.master_profile import MasterProfileStore


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
        self.assertEqual(self.at.radio(key="profile_mode").value, "Profil master din CV")
        self.at.radio(key="profile_mode").set_value("Profil fictiv").run()

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

    def import_master(self):
        self.at.radio(key="profile_mode").set_value("Profil master din CV").run()
        self.at.radio(key="master_import_method").set_value("Text lipit manual").run()
        text = (ROOT / "tests/fixtures/master_cv_synthetic.txt").read_text(encoding="utf-8")
        self.at.text_area(key="master_pasted").set_value(text).run()
        self.at.button(key="master_extract").click().run()
        next(r for r in self.at.radio if r.key.startswith("master_fragment_mode_")).set_value("Selectează blocuri întregi").run()
        blocks = next(m for m in self.at.multiselect if m.key.startswith("master_blocks_"))
        blocks.set_value([1, 2, 3, 4, 5]).run()
        kind = next(s for s in self.at.selectbox if s.key.startswith("master_kind_") and s.key.endswith("_5"))
        kind.select("confirmed_gap").run()
        self.assertEqual(len(self.at.exception), 0)

    def save_master(self):
        self.at.text_input(key="master_reviewer").set_value("[SYNTHETIC] Master UI reviewer").run()
        self.at.text_area(key="master_note").set_value("Simulated full-source review with QA history retained.").run()
        next(c for c in self.at.checkbox if c.key.startswith("master_confirmation_")).check().run()
        self.at.button(key="master_save").click().run()
        self.assertEqual(len(self.at.exception), 0)

    def test_unapproved_master_import_clears_old_analysis_and_cannot_be_used(self):
        self.load()
        self.import_master()
        self.assertIsNone(self.at.session_state["workflow"].report)
        self.assertFalse(any(button.key == "analyze" for button in self.at.button))
        self.assertTrue(self.at.button(key="master_save").disabled)
        self.assertEqual(MasterProfileStore(self.path).list_profiles(), ())

    def test_master_selection_change_requires_new_confirmation(self):
        self.import_master()
        next(c for c in self.at.checkbox if c.key.startswith("master_confirmation_")).check().run()
        blocks = next(m for m in self.at.multiselect if m.key.startswith("master_blocks_"))
        blocks.set_value([1, 2, 3, 4]).run()
        self.assertFalse(next(c for c in self.at.checkbox if c.key.startswith("master_confirmation_")).value)
        self.assertTrue(self.at.button(key="master_save").disabled)
        self.assertEqual(MasterProfileStore(self.path).list_profiles(), ())

    def test_master_profile_persists_and_is_used_by_job_analysis_without_metadata_in_prompt(self):
        self.import_master()
        self.save_master()
        store = MasterProfileStore(self.path)
        profile = store.list_profiles()[0]
        self.assertEqual(len(profile["facts"]), 5)
        self.assertIn("QA Lead", profile["facts"][1]["text"])
        self.assertTrue(self.at.button(key="load_saved").disabled)
        self.assertEqual(self.at.radio(key="master_action").value, "Folosește un profil salvat")
        self.at.text_input(key="job_title").set_value("[SYNTHETIC] Engineering Manager").run()
        self.at.text_area(key="job_source").set_value((ROOT / "tests/fixtures/job_001.txt").read_text(encoding="utf-8")).run()
        reference = json.loads((ROOT / "tests/fixtures/job_001.expected.json").read_text(encoding="utf-8"))
        matches = [{"requirement_id": f"R{i}", "status": status, "evidence_ids": refs, "explanation": "Synthetic source-grounded test result."}
                   for i, status, refs in [(1, "supported", ["F1"]), (2, "supported", ["F4"]), (3, "unknown", []), (4, "unknown", [])]]
        contents = [{"requirements": [{"priority": r["priority"], "quote": r["quote"]} for r in reference["requirements"]]}, {"matches": matches}]
        replies = [{"model": "llama3.2:3b", "done": True, "done_reason": "stop", "message": {"role": "assistant", "content": json.dumps(content)}} for content in contents]
        with patch("jobhunter.ollama._post_local", side_effect=replies) as transport:
            self.at.button(key="analyze").click().run()
        self.assertEqual(len(self.at.exception), 0)
        sent_profile = json.loads(transport.call_args_list[1].args[0]["messages"][1]["content"])["profile"]
        self.assertEqual(sent_profile["version"], profile["version"])
        self.assertNotIn("provenance", sent_profile)
        self.confirm()
        repo = JobRepository(self.path)
        job_id = repo.list_jobs()[0].id
        snapshot = json.loads(repo.approval_history(job_id)[0]["snapshot_json"])
        self.assertEqual(snapshot["profile"]["provenance"], profile["provenance"])
        # A fresh UI session can select the saved master; synthetic fields do not leak in.
        self.at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
        self.at.radio(key="profile_mode").set_value("Profil master din CV").run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(self.at.selectbox(key="master_saved_version").value, profile["version"])
        self.assertFalse(any(a.key == "profile_P1" for a in self.at.text_area))

    def test_corrupted_master_source_blocks_analysis_with_readable_error(self):
        self.import_master()
        self.save_master()
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute("UPDATE master_documents SET raw = ?", (b"Synthetic corruption",))
        self.at.run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertGreater(len(self.at.error), 0)
        self.assertFalse(any(button.key == "analyze" for button in self.at.button))

    def paste_fragment(self):
        self.at.radio(key="profile_mode").set_value("Profil master din CV").run()
        self.at.radio(key="master_import_method").set_value("Text lipit manual").run()
        self.at.text_area(key="master_pasted").set_value("[SYNTHETIC] Manager. Led a team. Earlier QA role.").run()
        # Reading the CV is automatic; no extraction button needed.
        area = next(a for a in self.at.text_area if a.key.startswith("master_excerpt_"))
        area.set_value("Manager. Led a team.").run()
        self.assertEqual(len(self.at.exception), 0)

    def test_copy_pasted_partial_fragment_is_saved_and_reusable_without_reupload(self):
        self.paste_fragment()
        self.assertFalse(any(a.key == "job_source" for a in self.at.text_area))
        self.save_master()
        store = MasterProfileStore(self.path)
        first = store.list_profiles()[0]
        self.assertEqual(first["facts"][0]["text"], "Manager. Led a team.")
        self.assertEqual(self.at.text_area(key="job_source").value, "")
        self.at.button(key="master_reselect").click().run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(self.at.radio(key="master_import_method").value, "CV deja salvat")
        self.assertIsNone(self.at.session_state["workflow"].report)
        area = next(a for a in self.at.text_area if a.key.startswith("master_excerpt_"))
        area.set_value("Earlier QA role.").run()
        self.save_master()
        self.assertEqual(len(store.list_profiles()), 2)
        self.assertEqual(store.load(first["version"]), first)
        self.assertEqual(store.list_profiles()[0]["facts"][0]["text"], "Earlier QA role.")
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_invalid_paste_blocks_save_and_restoring_text_does_not_restore_confirmation(self):
        self.paste_fragment()
        next(c for c in self.at.checkbox if c.key.startswith("master_confirmation_")).check().run()
        area = next(a for a in self.at.text_area if a.key.startswith("master_excerpt_"))
        area.set_value("Invented skill").run()
        self.assertGreater(len(self.at.error), 0)
        self.assertFalse(any(b.key == "master_save" for b in self.at.button))
        area = next(a for a in self.at.text_area if a.key.startswith("master_excerpt_"))
        area.set_value("Manager. Led a team.").run()
        self.assertFalse(next(c for c in self.at.checkbox if c.key.startswith("master_confirmation_")).value)
        self.assertEqual(MasterProfileStore(self.path).list_profiles(), ())

    def test_multiple_fragments_and_repeated_text_have_explicit_source_choices(self):
        self.paste_fragment()
        self.at.text_area(key="master_pasted").set_value("[SYNTHETIC] Manager. Led a team.\n\n[SYNTHETIC] QA Lead. Led a team.").run()
        area = next(a for a in self.at.text_area if a.key.startswith("master_excerpt_"))
        area.set_value("Led a team.").run()
        occurrence = next(s for s in self.at.selectbox if s.key.endswith("_occurrence"))
        occurrence.select(1).run()
        next(b for b in self.at.button if b.key.startswith("master_add_fragment_")).click().run()
        areas = [a for a in self.at.text_area if a.key.startswith("master_excerpt_")]
        areas[1].set_value("QA Lead.").run()
        self.save_master()
        profile = MasterProfileStore(self.path).list_profiles()[0]
        self.assertEqual(len(profile["facts"]), 2)
        self.assertEqual(profile["provenance"]["citations"][0]["start"],
                         "[SYNTHETIC] Manager. Led a team.\n\n[SYNTHETIC] QA Lead. Led a team.".rindex("Led a team."))

    def test_invalid_model_evidence_opens_review_with_unknowns_instead_of_generic_failure(self):
        reference = json.loads((ROOT / "tests/fixtures/job_001.expected.json").read_text(encoding="utf-8"))
        extraction = {"requirements": [{"priority": r["priority"], "quote": r["quote"]} for r in reference["requirements"]]}
        matching = {"matches": [{"requirement_id": "R1", "status": "supported", "evidence_ids": ["invented"],
                                 "explanation": "Synthetic invalid evidence, not real profile data."}]}
        replies = [{"model": "llama3.2:3b", "done": True, "done_reason": "stop", "message": {"role": "assistant", "content": json.dumps(content)}} for content in [extraction, matching]]
        with patch("jobhunter.ollama._post_local", side_effect=replies):
            self.at.button(key="analyze").click().run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(len(self.at.error), 0)
        self.assertGreater(len(self.at.warning), 0)
        workflow = self.at.session_state["workflow"]
        self.assertEqual([m["status"] for m in workflow.report["matching"]["matches"]], ["unknown"] * 4)
        self.assertTrue(workflow.report["matching"]["issues"])
        self.assertTrue(self.at.button(key="apply_review").disabled)
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_quote_failure_explains_manual_continuation_without_using_partial_report(self):
        self.load()
        with patch("jobhunter.analysis.extract_requirements", side_effect=SourceQuoteError("Citatul nu există exact în anunț.")):
            self.at.button(key="analyze").click().run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertIsNone(self.at.session_state["workflow"].report)
        self.assertTrue(any("Selectează manual" in message.value for message in self.at.info))
        self.assertEqual(JobRepository(self.path).list_jobs(), ())

    def test_manual_requirement_selection_compares_without_extraction_and_edits_clear_result(self):
        source = "[SYNTHETIC] Job\nCerințe obligatorii:\n- Coordonarea unei echipe.\nAvantaje:\n- Python."
        self.at.text_area(key="job_source").set_value(source).run()
        self.at.radio(key="requirements_mode").set_value("Selectează manual din anunț").run()
        self.assertTrue(self.at.button(key="analyze").disabled)
        next(m for m in self.at.multiselect if m.key.startswith("job_lines_")).set_value([2, 4]).run()
        priorities = [s for s in self.at.selectbox if s.key.startswith("job_line_priority_")]
        priorities[0].select("mandatory").run()
        [s for s in self.at.selectbox if s.key.startswith("job_line_priority_")][1].select("optional").run()
        reply = {"model": "llama3.2:3b", "done": True, "done_reason": "stop", "message": {"role": "assistant", "content": json.dumps({"matches": [
            {"requirement_id": "R1", "status": "supported", "evidence_ids": ["P1"], "explanation": "Synthetic leadership."},
            {"requirement_id": "R2", "status": "unknown", "evidence_ids": [], "explanation": "Synthetic unknown."}]})}}
        with patch("jobhunter.ollama._post_local", return_value=reply) as transport:
            self.at.button(key="analyze").click().run()
        self.assertEqual(len(self.at.exception), 0)
        transport.assert_called_once()
        workflow = self.at.session_state["workflow"]
        self.assertEqual(workflow.report["extraction"]["model"], "manual")
        self.assertTrue(self.at.button(key="apply_review").disabled)
        [s for s in self.at.selectbox if s.key.startswith("job_line_priority_")][0].select("unknown").run()
        self.assertIsNone(self.at.session_state["workflow"].report)
        self.assertEqual(JobRepository(self.path).list_jobs(), ())
