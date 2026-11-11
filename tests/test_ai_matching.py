"""Validate local model matching proposals with mocked inference."""

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from jobhunter.ai_matching import propose_matches
from jobhunter.analysis import analyze_draft
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.ollama import ChatResult, ExtractionError, ExtractionResult, MODEL
from jobhunter.requirements import validate_requirements


FIXTURES = Path(__file__).parent / "fixtures"


def load_json(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AIMatchingTests(unittest.TestCase):
    def setUp(self):
        self.source = (FIXTURES / "job_001.txt").read_text(encoding="utf-8")
        self.requirements = load_json("job_001.expected.json")
        self.profile = load_json("profile_001.json")
        self.expected = load_json("matches_001.expected.json")

    def response(self, matches=None):
        content = {"matches": self.expected["matches"] if matches is None else matches}
        return ChatResult(json.dumps(content), 1.5, 300, 200)

    @patch("jobhunter.ai_matching.chat_local")
    def test_valid_proposal_uses_profile_evidence_and_romanian_instructions(self, chat):
        chat.return_value = self.response()
        result = propose_matches(self.source, self.requirements, self.profile)
        self.assertEqual([m.status for m in result.matches], ["supported", "partial", "confirmed_missing", "unknown"])
        self.assertEqual(result.profile_version, self.profile["version"])
        self.assertEqual(result.prompt_tokens, 300)
        prompt, data, schema = chat.call_args.args
        self.assertIn("Romanian", prompt)
        self.assertEqual(data["profile"]["version"], self.profile["version"])
        self.assertEqual(schema["properties"]["matches"]["items"]["properties"]["requirement_id"]["enum"], ["R1", "R2", "R3", "R4"])

    @patch("jobhunter.ai_matching.chat_local")
    def test_experimental_prompt_is_opt_in_and_recorded(self, chat):
        chat.return_value = self.response()
        default = propose_matches(self.source, self.requirements, self.profile)
        self.assertEqual(default.prompt_version, "matching-1")
        self.assertNotIn("description", chat.call_args.args[2]["properties"]["matches"]["items"]["properties"]["explanation"])
        experimental = propose_matches(self.source, self.requirements, self.profile, prompt_version="matching-2")
        self.assertEqual(experimental.prompt_version, "matching-2")
        self.assertIn("description", chat.call_args.args[2]["properties"]["matches"]["items"]["properties"]["explanation"])
        with self.assertRaises(ValueError):
            propose_matches(self.source, self.requirements, self.profile, prompt_version="unknown-version")

    @patch("jobhunter.ai_matching.chat_local")
    def test_invented_evidence_and_missing_conclusions_are_rejected(self, chat):
        invented = deepcopy(self.expected["matches"])
        invented[0]["evidence_ids"] = ["P999"]
        unsupported_gap = deepcopy(self.expected["matches"])
        unsupported_gap[3].update(status="confirmed_missing", evidence_ids=[])
        wrong_kind = deepcopy(self.expected["matches"])
        wrong_kind[2].update(status="supported", evidence_ids=["P3"])
        for matches in [invented, unsupported_gap, wrong_kind, self.expected["matches"][:-1]]:
            chat.return_value = self.response(matches)
            with self.subTest(matches=matches), self.assertRaises(ExtractionError):
                propose_matches(self.source, self.requirements, self.profile)

    @patch("jobhunter.ai_matching.chat_local")
    def test_invalid_json_or_extra_fields_are_rejected(self, chat):
        for content in ["not JSON", "[]", '{"matches": {}}', '{"matches": [], "score": 99}']:
            chat.return_value = ChatResult(content, 1, 1, 1)
            with self.subTest(content=content), self.assertRaises(ExtractionError):
                propose_matches(self.source, self.requirements, self.profile)

    @patch("jobhunter.ai_matching.chat_local")
    def test_invalid_inputs_fail_before_inference(self, chat):
        invalid = deepcopy(self.profile)
        invalid["facts"][0]["text"] = " "
        with self.assertRaises(ValueError):
            propose_matches(self.source, self.requirements, invalid)
        oversized = deepcopy(self.profile)
        oversized["facts"][0]["text"] = "x" * 12_001
        with self.assertRaises(ValueError):
            propose_matches(self.source, self.requirements, oversized)
        chat.assert_not_called()

    @patch("jobhunter.ai_matching.chat_local")
    def test_empty_requirements_skip_model(self, chat):
        result = propose_matches(self.source, {"schema_version": "1", "requirements": []}, self.profile)
        self.assertEqual(result.matches, ())
        chat.assert_not_called()

    @patch("jobhunter.ai_matching.chat_local", side_effect=ExtractionError("timeout"))
    def test_transport_error_has_no_fallback_match(self, chat):
        with self.assertRaises(ExtractionError):
            propose_matches(self.source, self.requirements, self.profile)
        chat.assert_called_once()

    @patch("jobhunter.analysis.propose_matches")
    @patch("jobhunter.analysis.extract_requirements")
    def test_combined_report_is_always_pending_even_when_suggesting_rejection(self, extract, match):
        # Turn AI adoption into a mandatory requirement in this synthetic variant.
        self.requirements["requirements"][2]["priority"] = "mandatory"
        validated = validate_requirements(self.requirements, self.source)
        extract.return_value = ExtractionResult(MODEL, "test", 1, 100, 50, validated)
        from jobhunter.ai_matching import MatchingResult
        match.return_value = MatchingResult(MODEL, "test", self.profile["version"], 1, 100, 50,
                                            validate_matches(self.expected, validated, validate_profile(self.profile)))
        draft = analyze_draft(self.source, self.profile)
        self.assertEqual(draft.suggested_eligibility.status, "rejected")
        self.assertEqual(draft.review_status, "pending_semantic_review")
        self.assertFalse(draft.decision_applied)
        self.assertEqual(draft.provisional_score.minimum_percent, 50)

    @patch("jobhunter.analysis.propose_matches")
    @patch("jobhunter.analysis.extract_requirements")
    def test_orchestrator_revalidates_model_references(self, extract, match):
        validated = validate_requirements(self.requirements, self.source)
        extract.return_value = ExtractionResult(MODEL, "test", 1, 1, 1, validated)
        from jobhunter.ai_matching import MatchingResult
        matches = validate_matches(self.expected, validated, validate_profile(self.profile))
        bad = (replace(matches[0], evidence_ids=("invented",)),) + matches[1:]
        match.return_value = MatchingResult(MODEL, "test", self.profile["version"], 1, 1, 1, bad)
        with self.assertRaises(ValueError):
            analyze_draft(self.source, self.profile)

    @patch("jobhunter.analysis.extract_requirements")
    def test_invalid_profile_prevents_even_extraction(self, extract):
        with self.assertRaises(ValueError):
            analyze_draft(self.source, {})
        extract.assert_not_called()
