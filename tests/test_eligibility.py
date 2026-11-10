"""Synthetic working-language cases and durable rejection history."""

from contextlib import closing
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from jobhunter.eligibility import evaluate_eligibility
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.requirements import validate_requirements
from jobhunter.scoring import score_requirements
from jobhunter.storage import JobRepository


def language_case(status="confirmed_missing", priority="mandatory"):
    source = "[SYNTHETIC] German fluency is required for daily work."
    quote = "German fluency is required for daily work."
    start = source.index(quote)
    requirements = {"schema_version": "1", "requirements": [
        {"id": "language", "priority": priority, "quote": quote, "start": start, "end": len(source)}
    ]}
    text = {"confirmed_missing": "[SYNTHETIC] Candidate explicitly confirms not speaking German.",
            "supported": "[SYNTHETIC] Candidate is fluent in German.",
            "partial": "[SYNTHETIC] Candidate knows basic German; fluency is not confirmed."}
    profile = {"version": "synthetic-v1", "facts": [] if status == "unknown" else [
        {"id": "P1", "kind": "confirmed_gap" if status == "confirmed_missing" else "experience", "text": text[status]}
    ]}
    matches = {"schema_version": "1", "profile_version": profile["version"], "matches": [
        {"requirement_id": "language", "status": status,
         "evidence_ids": [] if status == "unknown" else ["P1"],
         "explanation": "Exemplu fictiv: " + (text.get(status) or "nu avem informații despre germană.")}
    ]}
    return source, requirements, profile, matches


class EligibilityTests(unittest.TestCase):
    def test_confirmed_missing_mandatory_language_rejects(self):
        decision = evaluate_eligibility(*language_case())
        self.assertEqual(decision.status, "rejected")
        self.assertEqual(decision.reasons[0].code, "mandatory_confirmed_missing")
        self.assertEqual(decision.reasons[0].evidence_ids, ("P1",))

    def test_unknown_or_partial_language_requires_review(self):
        for status in ["unknown", "partial"]:
            with self.subTest(status=status):
                self.assertEqual(evaluate_eligibility(*language_case(status)).status, "needs_review")

    def test_optional_gap_does_not_reject_and_supported_mandatory_is_eligible(self):
        self.assertEqual(evaluate_eligibility(*language_case(priority="optional")).status, "eligible")
        self.assertEqual(evaluate_eligibility(*language_case("supported")).status, "eligible")

    def test_unknown_priority_requires_review_not_rejection(self):
        self.assertEqual(evaluate_eligibility(*language_case(priority="unknown")).status, "needs_review")

    def test_empty_extraction_requires_review(self):
        source, requirements, profile, matches = language_case()
        requirements["requirements"] = []
        matches["matches"] = []
        self.assertEqual(evaluate_eligibility(source, requirements, profile, matches).status, "needs_review")

    def test_missing_evidence_is_rejected_before_policy(self):
        source, requirements, profile, matches = language_case()
        matches["matches"][0]["evidence_ids"] = []
        with self.assertRaises(ValueError):
            evaluate_eligibility(source, requirements, profile, matches)

    def test_rejection_overrides_high_score_and_other_review_reasons(self):
        source, requirements, profile, matches = language_case()
        # Extra optional criteria are supported; mandatory German remains missing.
        profile["facts"].append({"id": "P2", "kind": "experience", "text": "[SYNTHETIC] Vendor integrations."})
        for index in range(30):
            quote = f"Experience in synthetic area {index}."
            start = len(source) + 1
            source += "\n" + quote
            requirements["requirements"].append({"id": f"R{index}", "priority": "optional", "quote": quote, "start": start, "end": len(source)})
            matches["matches"].append({"requirement_id": f"R{index}", "status": "supported", "evidence_ids": ["P2"], "explanation": "Synthetic arithmetic input; not a semantic evaluation."})
        # Policy must not depend on the score or disregard a mandatory gap.
        validated = validate_requirements(requirements, source)
        validated_matches = validate_matches(matches, validated, validate_profile(profile))
        self.assertGreater(score_requirements(validated, validated_matches).minimum_percent, 90)
        self.assertEqual(evaluate_eligibility(source, requirements, profile, matches).status, "rejected")
        requirements["requirements"][1]["priority"] = "unknown"
        self.assertEqual(evaluate_eligibility(source, requirements, profile, matches).status, "rejected")


class EligibilityStorageTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory(prefix="eligibility-test-", dir=Path(__file__).resolve().parents[1])
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "synthetic.sqlite3"
        self.repository = JobRepository(self.path)

    def test_rejection_is_excluded_but_job_and_reason_survive_reopening(self):
        case = language_case()
        job_id = self.repository.add("[SYNTHETIC] German-language manager", case[0])
        self.repository.save_decision(job_id, evaluate_eligibility(*case))
        reopened = JobRepository(self.path)
        self.assertEqual(reopened.list_opportunities(), ())
        self.assertIsNotNone(reopened.get(job_id))
        history = reopened.decision_history(job_id)
        self.assertEqual(history[0]["status"], "rejected")
        self.assertEqual(history[0]["reasons"][0]["requirement_id"], "language")
        self.assertTrue(history[0]["created_at"].endswith("Z"))

    def test_new_review_and_eligible_jobs_remain_visible(self):
        new_id = self.repository.add("[SYNTHETIC] Unanalysed job", "Synthetic new job")
        ids = [new_id]
        for status in ["partial", "unknown", "supported"]:
            case = language_case(status)
            job_id = self.repository.add("[SYNTHETIC] Job " + status, case[0])
            self.repository.save_decision(job_id, evaluate_eligibility(*case))
            ids.append(job_id)
        self.assertEqual([j.id for j in self.repository.list_opportunities()], ids)

    def test_explicit_reevaluation_preserves_history_and_uses_latest_decision(self):
        case = language_case()
        job_id = self.repository.add("[SYNTHETIC] Job", case[0])
        self.repository.save_decision(job_id, evaluate_eligibility(*case))
        case = list(language_case("supported"))
        case[2]["version"] = "synthetic-v2"
        case[3]["profile_version"] = "synthetic-v2"
        self.repository.save_decision(job_id, evaluate_eligibility(*case))
        self.assertEqual([j.id for j in self.repository.list_opportunities()], [job_id])
        self.assertEqual([d["status"] for d in self.repository.decision_history(job_id)], ["rejected", "eligible"])

    def test_mismatched_source_or_missing_job_cannot_save_decision(self):
        decision = evaluate_eligibility(*language_case())
        job_id = self.repository.add("Other job", "Different source text")
        for identifier in [job_id, job_id + 1]:
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                self.repository.save_decision(identifier, decision)
        self.assertEqual(self.repository.decision_history(job_id), ())

    def test_existing_database_keeps_its_jobs(self):
        legacy = self.path.parent / "legacy.sqlite3"
        with closing(sqlite3.connect(legacy)) as connection:
            with connection:
                connection.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL)")
                connection.execute("INSERT INTO jobs VALUES (1, 'Synthetic legacy job', 'Synthetic description')")
        repository = JobRepository(legacy)
        self.assertEqual(repository.get(1).title, "Synthetic legacy job")
        self.assertEqual(len(repository.list_opportunities()), 1)
