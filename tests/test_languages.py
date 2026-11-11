"""Rules on reviewed annotations, isolated from inference and private databases."""

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from jobhunter.approval import approve_review, review_fingerprint, verify_approval
from jobhunter.evaluate_structured_languages import annotation_payload, run_saved_evaluation
from jobhunter.languages import apply_language_review, evaluate_languages, mentioned_languages
from jobhunter.matching import validate_profile
from jobhunter.requirements import Requirement
from jobhunter.review import ReviewMaterial, material_snapshot, prepare_review, render_review
from jobhunter.storage import JobRepository


ROOT = Path(__file__).resolve().parents[1]


class LanguageRuleTests(unittest.TestCase):
    def setUp(self):
        self.profile_payload = json.loads((ROOT / "tests/fixtures/language_checks_new.json").read_text(encoding="utf-8"))["profile"]
        self.profile_payload["facts"].append({"id": "P_ES", "kind": "experience", "text": "[SYNTHETIC] Spanish skills are basic."})
        self.profile = validate_profile(self.profile_payload)
        self.abilities = [{"language": "en", "level": "professional", "evidence_ids": ["P_EN"]},
                          {"language": "de", "level": "none", "evidence_ids": ["P_DE"]},
                          {"language": "fr", "level": "none", "evidence_ids": ["P_FR"]}]

    def payload(self, codes, operator="all", minimum="professional", abilities=None):
        return {"schema_version": "1", "abilities": deepcopy(self.abilities if abilities is None else abilities),
                "rules": [{"requirement_id": "R1", "operator": operator, "languages": codes, "minimum": minimum}]}

    def evaluate(self, quote, codes, operator="all", minimum="professional", abilities=None, priority="mandatory"):
        requirement = Requirement("R1", priority, quote, 0, len(quote))
        return evaluate_languages(self.payload(codes, operator, minimum, abilities), (requirement,), self.profile)[0]

    def test_wrong_language_gaps_do_not_prove_spanish_absence(self):
        match = self.evaluate("Spanish proficiency is mandatory.", ["es"])
        self.assertEqual((match.status, match.evidence_ids), ("unknown", ()))

    def test_optional_priority_does_not_hide_explicit_gap(self):
        mandatory = self.evaluate("German proficiency.", ["de"])
        optional = self.evaluate("German proficiency.", ["de"], priority="optional")
        self.assertEqual(mandatory, optional)
        self.assertEqual((optional.status, optional.evidence_ids), ("confirmed_missing", ("P_DE",)))

    def test_or_uses_one_satisfied_branch_and_never_an_unrelated_gap(self):
        match = self.evaluate("German OR English proficiency.", ["de", "en"], "any")
        self.assertEqual((match.status, match.evidence_ids), ("supported", ("P_EN",)))
        unknown = self.evaluate("German OR Italian proficiency.", ["de", "it"], "any")
        self.assertEqual((unknown.status, unknown.evidence_ids), ("unknown", ()))

    def test_and_requires_all_but_an_explicit_missing_branch_is_sufficient_for_gap(self):
        match = self.evaluate("English AND German proficiency.", ["en", "de"])
        self.assertEqual((match.status, match.evidence_ids), ("confirmed_missing", ("P_DE",)))
        unknown = self.evaluate("English AND Italian proficiency.", ["en", "it"])
        self.assertEqual((unknown.status, unknown.evidence_ids), ("unknown", ()))

    def test_or_all_missing_cites_both_relevant_gaps(self):
        match = self.evaluate("German OR French proficiency.", ["de", "fr"], "any")
        self.assertEqual((match.status, match.evidence_ids), ("confirmed_missing", ("P_DE", "P_FR")))

    def test_partial_is_not_an_explicit_gap_and_unknown_alternative_stays_unknown(self):
        abilities = self.abilities + [{"language": "es", "level": "basic", "evidence_ids": ["P_ES"]}]
        match = self.evaluate("Spanish proficiency.", ["es"], abilities=abilities)
        self.assertEqual((match.status, match.evidence_ids), ("partial", ("P_ES",)))
        alternative = self.evaluate("Spanish OR German proficiency.", ["es", "de"], "any", abilities=abilities)
        self.assertEqual((alternative.status, alternative.evidence_ids), ("partial", ("P_ES",)))
        unknown = self.evaluate("Spanish OR Italian proficiency.", ["es", "it"], "any", abilities=abilities)
        self.assertEqual(unknown.status, "unknown")

    def test_unreviewed_minimum_or_operator_cannot_produce_rejection(self):
        for operator, minimum in [("unclear", "professional"), ("all", "unspecified")]:
            with self.subTest(operator=operator, minimum=minimum):
                self.assertEqual(self.evaluate("German proficiency.", ["de"], operator, minimum).status, "unknown")

    def test_alias_guard_is_bounded_and_accepts_romanian_diacritics(self):
        self.assertEqual(mentioned_languages("Engleză și germană"), ("en", "de"))
        self.assertEqual(mentioned_languages("germination and romance"), ())
        match = self.evaluate("Engleză și germană.", ["en", "de"])
        self.assertEqual(match.status, "confirmed_missing")

    def test_language_cannot_be_dropped_or_operator_inverted(self):
        for codes, operator in [(["en"], "all"), (["en", "de"], "any")]:
            with self.subTest(codes=codes, operator=operator), self.assertRaises(ValueError):
                self.evaluate("English AND German proficiency.", codes, operator)
        with self.assertRaises(ValueError):
            self.evaluate("English OR German proficiency.", ["en", "de"], "all")

    def test_mixed_or_and_requires_clarification(self):
        quote = "English AND German OR French proficiency."
        with self.assertRaises(ValueError):
            self.evaluate(quote, ["en", "de", "fr"], "all")
        self.assertEqual(self.evaluate(quote, ["en", "de", "fr"], "unclear").status, "unknown")

    def test_unrelated_positive_or_gap_evidence_is_rejected(self):
        for level, refs in [("none", ["P_DE"]), ("professional", ["P_EN"]), ("none", ["P_EN"])]:
            abilities = [{"language": "fr", "level": level, "evidence_ids": refs}]
            with self.subTest(level=level, refs=refs), self.assertRaises(ValueError):
                self.evaluate("French proficiency.", ["fr"], abilities=abilities)

    def test_known_level_requires_evidence_and_unknown_must_not_claim_evidence(self):
        for level, refs in [("professional", []), ("unknown", ["P_EN"]), ("fluent", ["invented"])]:
            with self.subTest(level=level), self.assertRaises(ValueError):
                self.evaluate("English proficiency.", ["en"], abilities=[{"language": "en", "level": level, "evidence_ids": refs}])

    def test_unsupported_language_and_invalid_data_are_not_silently_inferred(self):
        self.assertEqual(self.evaluate("Dutch proficiency.", [], "unclear").status, "unknown")
        for abilities in [self.abilities * 2, [{"language": "xx", "level": "professional", "evidence_ids": ["P_EN"]}],
                          [{"language": "en", "level": "C2", "evidence_ids": ["P_EN"]}]]:
            with self.subTest(abilities=abilities), self.assertRaises(ValueError):
                self.evaluate("English proficiency.", ["en"], abilities=abilities)


class LanguageReviewIntegrationTests(unittest.TestCase):
    def setUp(self):
        raw = json.loads((ROOT / "docs/evaluations/language_eval_v2_new.json").read_text(encoding="utf-8"))
        self.case = next(c for c in raw["cases"] if c["case_id"] == "spanish_no_information")
        self.material = prepare_review(self.case["actual"], self.case["source"], raw["profile"])
        annotations = json.loads((ROOT / "tests/fixtures/structured_language_reviews.json").read_text(encoding="utf-8"))
        self.payload = annotation_payload(annotations, self.case["case_id"], raw["profile"],
                                          self.case["actual"]["extraction"]["requirements"])

    def test_saved_false_rejection_is_corrected_without_losing_original(self):
        revised = apply_language_review(self.material, self.payload)
        self.assertEqual(self.material.original_matches["matches"][0]["status"], "confirmed_missing")
        self.assertEqual(revised.revised_matches["matches"][0]["status"], "unknown")
        self.assertEqual(revised.revised_matches["matches"][0]["evidence_ids"], [])
        self.assertFalse(revised.decision_applied)
        self.assertIn("Adnotări explicite", render_review(revised))

    def test_approval_binds_rules_and_audit_persists_them(self):
        revised = apply_language_review(self.material, self.payload)
        approval = approve_review(revised, expected_fingerprint=review_fingerprint(revised), reviewer="[SYNTHETIC] Rules reviewer",
                                  note="Synthetic annotation review, not real user approval.", confirmed=True)
        with TemporaryDirectory(prefix="language-review-test-", dir=ROOT) as directory:
            repo = JobRepository(Path(directory) / "synthetic.sqlite3")
            job_id = repo.add("[SYNTHETIC] Spanish role", revised.source)
            repo.apply_approved_review(job_id, revised, approval)
            self.assertEqual(repo.decision_history(job_id)[0]["status"], "needs_review")
            snapshot = json.loads(repo.approval_history(job_id)[0]["snapshot_json"])
            self.assertEqual(snapshot["language_review"], self.payload)
            self.assertEqual(len(repo.list_opportunities()), 1)
        changed = deepcopy(revised)
        changed.language_review["abilities"][0]["level"] = "basic"
        with self.assertRaises(ValueError):
            verify_approval(changed, approval)

    def test_forged_result_cannot_override_attached_rule_even_with_consistent_change_history(self):
        revised = deepcopy(apply_language_review(self.material, self.payload))
        revised.revised_matches["matches"][0].update(status="confirmed_missing", evidence_ids=["P_DE"])
        revised.changes[0]["after"].update(status="confirmed_missing", evidence_ids=["P_DE"])
        with self.assertRaises(ValueError):
            review_fingerprint(revised)

    def test_legacy_material_keeps_old_approval_identity(self):
        payload = json.loads((ROOT / "docs/evaluations/review_001.proposal.json").read_text(encoding="utf-8"))
        legacy = ReviewMaterial(**payload)
        old_fingerprint = json.loads((ROOT / "docs/evaluations/approval_001.demo.json").read_text(encoding="utf-8"))["review_fingerprint"]
        self.assertNotIn("language_review", material_snapshot(legacy))
        self.assertEqual(review_fingerprint(legacy), old_fingerprint)

    def test_all_eight_saved_cases_are_checked_without_new_inference(self):
        report = run_saved_evaluation()
        self.assertEqual((report["case_count"], report["passed_measured_checks"]), (8, 8))
        self.assertEqual(report["new_model_calls"], 0)
        self.assertFalse(report["user_approval"])
