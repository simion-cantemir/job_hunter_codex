"""Deterministic reference checks and evaluator tests; never call real inference."""

from copy import deepcopy
from dataclasses import asdict
import json
import unittest
from unittest.mock import Mock, patch

from jobhunter.ai_matching import MatchingResult
from jobhunter.analysis import AnalysisDraft
from jobhunter.eligibility import evaluate_eligibility, source_digest
from jobhunter.evaluate_languages import (CASES_PATH, compare_case, reference_payloads,
                                          main, render_evaluation, run_evaluation, validate_suite)
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.ollama import ExtractionError, ExtractionResult, MODEL
from jobhunter.requirements import validate_requirements
from jobhunter.scoring import score_requirements


class LanguageEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def reference_draft(self, source, profile_payload):
        case = next(c for c in self.suite["cases"] if c["source"] == source)
        req_payload, matches_payload = reference_payloads(case, profile_payload)
        requirements = validate_requirements(req_payload, source)
        matches = validate_matches(matches_payload, requirements, validate_profile(profile_payload))
        return AnalysisDraft(source_digest(source), profile_payload["version"],
                             ExtractionResult(MODEL, "synthetic-test", 0, 0, 0, requirements),
                             MatchingResult(MODEL, "synthetic-test", profile_payload["version"], 0, 0, 0, matches),
                             score_requirements(requirements, matches),
                             evaluate_eligibility(source, req_payload, profile_payload, matches_payload))

    def test_authored_language_references_match_policy_and_expected_arithmetic(self):
        validate_suite(self.suite)
        for case, expected_score, expected_status in zip(self.suite["cases"], [50, 200 / 3, 100], ["rejected", "eligible", "eligible"]):
            with self.subTest(case=case["id"]):
                draft = self.reference_draft(case["source"], self.suite["profile"])
                self.assertEqual(draft.suggested_eligibility.status, expected_status)
                self.assertAlmostEqual(draft.provisional_score.minimum_percent, expected_score)
        # OR remains one requirement, satisfied only by English evidence.
        alternative = self.suite["cases"][2]
        self.assertEqual(len(alternative["expected"]), 1)
        self.assertEqual(alternative["expected"][0]["evidence_ids"], ["P_EN"])

    def test_runner_passes_only_source_and_profile_to_analyzer(self):
        analyzer = Mock(side_effect=self.reference_draft)
        report = run_evaluation(self.suite, analyzer=analyzer)
        self.assertEqual(report["passed_measured_checks"], 3)
        self.assertEqual(analyzer.call_count, 3)
        for call, case in zip(analyzer.call_args_list, self.suite["cases"]):
            self.assertEqual(call.args, (case["source"], self.suite["profile"]))
            self.assertEqual(call.kwargs, {})
        self.assertTrue(all(not c["explanations_semantically_approved"] for c in report["cases"]))

    def test_wrong_priority_status_or_evidence_fails_measured_checks(self):
        case = self.suite["cases"][0]
        original = json.loads(json.dumps(asdict(self.reference_draft(case["source"], self.suite["profile"]))))
        for field in ["priority", "status", "evidence", "applied"]:
            actual = deepcopy(original)
            if field == "priority":
                actual["extraction"]["requirements"][1]["priority"] = "optional"
            elif field == "status":
                actual["matching"]["matches"][1]["status"] = "unknown"
            elif field == "evidence":
                actual["matching"]["matches"][1]["evidence_ids"] = ["P_EN"]
            else:
                actual["decision_applied"] = True
            with self.subTest(field=field):
                self.assertFalse(compare_case(case, actual)["passed_measured_checks"])

    def test_quote_alignment_ignores_id_and_order_variations(self):
        case = self.suite["cases"][0]
        actual = json.loads(json.dumps(asdict(self.reference_draft(case["source"], self.suite["profile"]))))
        for requirement, match in zip(actual["extraction"]["requirements"], actual["matching"]["matches"]):
            requirement["id"] += "_renamed"
            match["requirement_id"] += "_renamed"
        actual["extraction"]["requirements"].reverse()
        actual["matching"]["matches"].reverse()
        self.assertTrue(compare_case(case, actual)["passed_measured_checks"])

    def test_failure_is_recorded_and_other_cases_continue_without_retry(self):
        def analyzer(source, profile):
            if source == self.suite["cases"][0]["source"]:
                raise ExtractionError("Synthetic connection failure")
            return self.reference_draft(source, profile)
        mock = Mock(side_effect=analyzer)
        report = run_evaluation(self.suite, analyzer=mock)
        self.assertEqual(report["passed_measured_checks"], 2)
        self.assertIn("error", report["cases"][0])
        self.assertEqual(mock.call_count, 3)
        self.assertIn("Rulare nereușită", render_evaluation(report))

    def test_invalid_reference_is_rejected_before_inference(self):
        self.suite["cases"][1]["expected_eligibility"] = "rejected"
        analyzer = Mock()
        with self.assertRaises(ValueError):
            run_evaluation(self.suite, analyzer=analyzer)
        analyzer.assert_not_called()

    def test_label_agreement_does_not_approve_explanations(self):
        report = run_evaluation(self.suite, analyzer=self.reference_draft)
        case = report["cases"][0]
        case["actual"]["matching"]["matches"][0]["explanation"] = "<script>Invented explanation</script>"
        self.assertTrue(compare_case(self.suite["cases"][0], case["actual"])["passed_measured_checks"])
        self.assertFalse(case["explanations_semantically_approved"])
        rendered = render_evaluation(report)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_new_references_cover_absence_or_and_and(self):
        self.suite = json.loads((CASES_PATH.parent / "language_checks_new.json").read_text(encoding="utf-8"))
        validate_suite(self.suite)
        expected_statuses = ["eligible", "rejected", "needs_review", "eligible", "rejected"]
        expected_bounds = [(200 / 3, 200 / 3), (0, 0), (0, 100), (100, 100), (0, 0)]
        for case, status, bounds in zip(self.suite["cases"], expected_statuses, expected_bounds):
            with self.subTest(case=case["id"]):
                draft = self.reference_draft(case["source"], self.suite["profile"])
                self.assertEqual(draft.suggested_eligibility.status, status)
                self.assertAlmostEqual(draft.provisional_score.minimum_percent, bounds[0])
                self.assertAlmostEqual(draft.provisional_score.maximum_percent, bounds[1])
        self.assertEqual(run_evaluation(self.suite, analyzer=self.reference_draft)["passed_measured_checks"], 5)

    def test_cli_cannot_overwrite_original_baseline_or_escape_output_directory(self):
        for output_name in ["language_eval_001", "../outside", "", "folder/report"]:
            with self.subTest(output_name=output_name), patch("sys.argv", ["evaluate_languages", "--output-name", output_name]), \
                    patch("jobhunter.evaluate_languages.run_evaluation") as inference, \
                    patch("sys.stderr"), self.assertRaises(SystemExit) as caught:
                main()
            self.assertEqual(caught.exception.code, 2)
            inference.assert_not_called()
