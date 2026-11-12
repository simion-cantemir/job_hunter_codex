"""Malformed model replies become visible unknowns only in the explicit UI mode."""

from copy import deepcopy
from dataclasses import asdict
import json
import unittest
from unittest.mock import patch

from jobhunter.ai_matching import propose_matches, matching_output_budget, GENERATION_POLICY
from jobhunter.analysis import analyze_draft
from jobhunter.matching import validate_profile, validate_matches
from jobhunter.ollama import ChatResult, ExtractionError, ExtractionResult, MODEL
from jobhunter.requirements import validate_requirements


SOURCE = "Lead an engineering team.\nGerman fluency is required."
QUOTES = ["Lead an engineering team.", "German fluency is required."]
REQUIREMENTS = {"schema_version": "1", "requirements": [
    {"id": f"R{i+1}", "priority": "mandatory", "quote": quote, "start": SOURCE.index(quote), "end": SOURCE.index(quote) + len(quote)}
    for i, quote in enumerate(QUOTES)
]}
PROFILE = {"version": "synthetic-F-ids-v1", "facts": [
    {"id": "F10", "kind": "experience", "text": "[SYNTHETIC] Led an engineering team."},
    {"id": "F20", "kind": "confirmed_gap", "text": "[SYNTHETIC] Explicitly does not speak German."},
]}
VALID = [
    {"requirement_id": "R1", "status": "supported", "evidence_ids": ["F10"], "explanation": "Synthetic leadership evidence."},
    {"requirement_id": "R2", "status": "confirmed_missing", "evidence_ids": ["F20"], "explanation": "Synthetic explicit gap."},
]


class MatchingRecoveryTests(unittest.TestCase):
    def test_matching_generation_capacity_scales_with_requirement_count_and_is_capped(self):
        self.assertEqual(matching_output_budget(1), 1024)
        self.assertEqual(matching_output_budget(6), 2560)
        self.assertEqual(matching_output_budget(100), 4096)

    @patch("jobhunter.ai_matching.chat_local")
    def test_schema_uses_real_fact_ids_and_exact_requirement_count(self, chat):
        chat.return_value = ChatResult(json.dumps({"matches": VALID}), 0, 0, 0)
        result = propose_matches(SOURCE, REQUIREMENTS, PROFILE)
        schema = chat.call_args.args[2]["properties"]["matches"]
        self.assertEqual((schema["minItems"], schema["maxItems"]), (2, 2))
        self.assertEqual(schema["items"]["properties"]["evidence_ids"]["items"]["enum"], ["F10", "F20"])
        self.assertEqual(result.issues, ())
        self.assertEqual(result.output_contract, "matching-schema-2")
        self.assertEqual(chat.call_args.kwargs["max_output_tokens"], matching_output_budget(2))
        self.assertEqual(result.generation_policy, GENERATION_POLICY)

    @patch("jobhunter.ai_matching.chat_local")
    def test_strict_error_identifies_reason_without_echoing_bad_external_ids(self, chat):
        bad = deepcopy(VALID)
        bad[0]["evidence_ids"] = ["private-person@example.com"]
        chat.return_value = ChatResult(json.dumps({"matches": bad}), 0, 0, 0)
        with self.assertRaises(ExtractionError) as caught:
            propose_matches(SOURCE, REQUIREMENTS, PROFILE)
        self.assertIn("Dovezile", str(caught.exception))
        self.assertIn("R1", str(caught.exception))
        self.assertNotIn("private-person", str(caught.exception))

    @patch("jobhunter.ai_matching.chat_local")
    def test_bad_evidence_is_unknown_and_valid_result_is_kept(self, chat):
        bad = deepcopy(VALID)
        bad[1]["evidence_ids"] = ["P999"]
        chat.return_value = ChatResult(json.dumps({"matches": bad}), 0, 0, 0)
        result = propose_matches(SOURCE, REQUIREMENTS, PROFILE, recover_invalid=True)
        self.assertEqual(result.matches[0].status, "supported")
        self.assertEqual((result.matches[1].status, result.matches[1].evidence_ids), ("unknown", ()))
        self.assertEqual(result.issues[0].code, "unknown_evidence")
        self.assertEqual(result.issues[0].requirement_id, "R2")

    @patch("jobhunter.ai_matching.chat_local")
    def test_missing_duplicate_or_malformed_rows_have_safe_complete_coverage(self, chat):
        variants = [VALID[:1], [VALID[0], VALID[0], VALID[1]], ["bad row", VALID[1]],
                    [{**VALID[0], "extra": 1}, VALID[1]], [{**VALID[0], "requirement_id": "invented"}, VALID[1]]]
        for rows in variants:
            chat.return_value = ChatResult(json.dumps({"matches": rows}), 0, 0, 0)
            with self.subTest(rows=rows):
                result = propose_matches(SOURCE, REQUIREMENTS, PROFILE, recover_invalid=True)
                self.assertEqual({m.requirement_id for m in result.matches}, {"R1", "R2"})
                self.assertTrue(result.issues)
                # Recovery output must still obey strict evidence validation.
                payload = {"schema_version": "1", "profile_version": PROFILE["version"],
                           "matches": [asdict(m) | {"evidence_ids": list(m.evidence_ids)} for m in result.matches]}
                validate_matches(payload, validate_requirements(REQUIREMENTS, SOURCE), validate_profile(PROFILE))

    @patch("jobhunter.ai_matching.chat_local")
    def test_wrong_kind_unknown_with_evidence_and_blank_explanation_are_not_repaired_as_truth(self, chat):
        for changes, code in [({"evidence_ids": ["F10"]}, "evidence_kind"),
                              ({"status": "unknown"}, "unknown_with_evidence"),
                              ({"explanation": " "}, "missing_explanation")]:
            rows = deepcopy(VALID)
            rows[1].update(changes)
            chat.return_value = ChatResult(json.dumps({"matches": rows}), 0, 0, 0)
            with self.subTest(changes=changes):
                result = propose_matches(SOURCE, REQUIREMENTS, PROFILE, recover_invalid=True)
                self.assertEqual(result.issues[0].code, code)
                self.assertEqual((result.matches[1].status, result.matches[1].evidence_ids), ("unknown", ()))

    @patch("jobhunter.ai_matching.chat_local")
    def test_invalid_json_or_envelope_retains_only_unknowns(self, chat):
        for content in ["not JSON", "[]", '{"matches": {}}', '{"matches": [], "unexpected": true}']:
            chat.return_value = ChatResult(content, 0, 0, 0)
            with self.subTest(content=content):
                result = propose_matches(SOURCE, REQUIREMENTS, PROFILE, recover_invalid=True)
                self.assertEqual([m.status for m in result.matches], ["unknown", "unknown"])
                self.assertEqual(len(result.issues), 1)

    @patch("jobhunter.ai_matching.chat_local", side_effect=ExtractionError("Synthetic timeout"))
    def test_transport_failures_do_not_masquerade_as_a_successful_analysis(self, chat):
        with self.assertRaises(ExtractionError):
            propose_matches(SOURCE, REQUIREMENTS, PROFILE, recover_invalid=True)
        chat.assert_called_once()

    @patch("jobhunter.ai_matching.chat_local")
    @patch("jobhunter.analysis.extract_requirements")
    def test_recovered_mandatory_gap_cannot_trigger_rejection_or_application(self, extract, chat):
        extract.return_value = ExtractionResult(MODEL, "synthetic", 0, 0, 0, validate_requirements(REQUIREMENTS, SOURCE))
        rows = deepcopy(VALID)
        rows[1]["evidence_ids"] = ["F10"]  # A positive fact cannot prove a gap.
        chat.return_value = ChatResult(json.dumps({"matches": rows}), 0, 0, 0)
        draft = analyze_draft(SOURCE, PROFILE, recover_matching=True)
        self.assertEqual(draft.suggested_eligibility.status, "needs_review")
        self.assertFalse(draft.decision_applied)
        self.assertEqual(draft.review_status, "pending_semantic_review")
        self.assertEqual((draft.provisional_score.minimum_percent, draft.provisional_score.maximum_percent), (50, 100))

    @patch("jobhunter.ai_matching.chat_local")
    def test_empty_profile_schema_forbids_nonempty_evidence(self, chat):
        chat.return_value = ChatResult('{"matches": []}', 0, 0, 0)
        result = propose_matches(SOURCE, REQUIREMENTS, {"version": "empty-synthetic", "facts": []}, recover_invalid=True)
        schema = chat.call_args.args[2]["properties"]["matches"]["items"]["properties"]["evidence_ids"]
        self.assertEqual(schema["maxItems"], 0)
        self.assertEqual([m.status for m in result.matches], ["unknown", "unknown"])
