"""Review identity, evidence display and proposed corrections use saved synthetic data."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jobhunter.review import prepare_review, render_review


ROOT = Path(__file__).resolve().parents[1]


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((ROOT / "docs/evaluations/ollama_analysis_001_run_001.json").read_text(encoding="utf-8"))
        self.source = (ROOT / "tests/fixtures/job_001.txt").read_text(encoding="utf-8")
        self.profile = json.loads((ROOT / "tests/fixtures/profile_001.json").read_text(encoding="utf-8"))
        self.material = prepare_review(self.report, self.source, self.profile)
        self.change = {"requirement_id": "R2", "priority": "mandatory", "status": "partial",
                       "evidence_ids": ["P2"], "explanation": "Nivel B1; participă deja la cursuri. Nivelul profesional nu este confirmat.",
                       "note": "Propunere de corectare a explicației, fără schimbarea statusului."}

    def correct(self, changes):
        return prepare_review(self.report, self.source, self.profile,
                              {"analysis_fingerprint": self.material.analysis_fingerprint, "changes": changes})

    def test_report_displays_actual_evidence_original_error_and_pending_status(self):
        text = render_review(self.material)
        self.assertIn("profesionistul de calitate", text)
        self.assertIn("currently attending English classes", text)
        self.assertIn("Professional working proficiency in English", text)
        self.assertIn("60.0–60.0%", text)
        self.assertIn("Nicio decizie aplicată", text)
        self.assertIn("Profilul integral", text)

    def test_correction_preserves_original_and_is_not_approval(self):
        before = deepcopy(self.report)
        material = self.correct([self.change])
        self.assertEqual(self.report, before)
        self.assertEqual(material.review_status, "pending_semantic_review")
        self.assertFalse(material.decision_applied)
        self.assertIn("profesionistul de calitate", material.original_matches["matches"][1]["explanation"])
        self.assertEqual(material.revised_matches["matches"][1]["explanation"], self.change["explanation"])
        self.assertEqual(material.changes[0]["before"]["status"], "partial")
        self.assertIn("Corecție propusă", render_review(material))

    def test_corrections_cannot_target_another_analysis(self):
        with self.assertRaises(ValueError):
            prepare_review(self.report, self.source, self.profile,
                           {"analysis_fingerprint": "outdated", "changes": [self.change]})
        changed_report = deepcopy(self.report)
        changed_report["matching"]["matches"][0]["explanation"] = "Different interpretation."
        changed = prepare_review(changed_report, self.source, self.profile)
        self.assertNotEqual(changed.analysis_fingerprint, self.material.analysis_fingerprint)
        changed_profile = deepcopy(self.profile)
        changed_profile["facts"][0]["text"] += " Changed fact."
        self.assertNotEqual(prepare_review(self.report, self.source, changed_profile).analysis_fingerprint,
                            self.material.analysis_fingerprint)

    def test_wrong_source_version_or_already_applied_report_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare_review(self.report, self.source + "changed", self.profile)
        for change in [{"profile_version": "another-profile"}, {"decision_applied": True}, {"review_status": "approved"}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                prepare_review({**self.report, **change}, self.source, self.profile)

    def test_invalid_corrections_are_rejected(self):
        for change in [{"requirement_id": "invented"}, {"evidence_ids": ["invented"]},
                       {"status": "confirmed_missing", "evidence_ids": ["P2"]},
                       {"note": " "}, {"priority": "assumed"}, {"extra": True}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.correct([{**self.change, **change}])
        with self.assertRaises(ValueError):
            self.correct([self.change, self.change])

    def test_revised_values_recompute_score_instead_of_trusting_saved_score(self):
        self.report["provisional_score"]["minimum_percent"] = 99
        # A structurally valid proposal still needs semantic review.
        material = prepare_review(self.report, self.source, self.profile)
        self.assertIn("60.0–60.0%", render_review(material))
        corrected = prepare_review(self.report, self.source, self.profile,
                                  {"analysis_fingerprint": material.analysis_fingerprint,
                                   "changes": [{**self.change, "status": "unknown", "evidence_ids": []}]})
        self.assertIn("40.0–80.0%", render_review(corrected))

    def test_external_text_is_escaped_as_inert_markdown(self):
        self.report["matching"]["matches"][0]["explanation"] = '<script>alert(1)</script>\n[Click](https://example.com)'
        text = render_review(prepare_review(self.report, self.source, self.profile))
        self.assertNotIn("<script>", text)
        self.assertNotIn("[Click](https://example.com)", text)
        self.assertIn("&lt;script&gt;", text)

    def test_snapshots_do_not_change_when_callers_mutate_inputs(self):
        material = self.correct([self.change])
        self.change["evidence_ids"].append("later")
        self.profile["facts"][0]["text"] = "later change"
        self.assertEqual(material.revised_matches["matches"][1]["evidence_ids"], ["P2"])
        self.assertNotEqual(material.profile["facts"][0]["text"], "later change")

    def test_saved_evidence_is_revalidated_before_display(self):
        self.report["matching"]["matches"][0]["evidence_ids"] = ["invented"]
        with self.assertRaises(ValueError):
            prepare_review(self.report, self.source, self.profile)
