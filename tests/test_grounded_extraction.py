"""Source-grounded quotes and bounded budgets in both analysis stages."""

from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from jobhunter.analysis import analyze_draft
from jobhunter.ollama import (OUTPUT_SCHEMA, ChatResult, OllamaResponseError, SourceQuoteError,
                             extract_requirements, extraction_output_budget, source_quote_candidates)
from jobhunter.ai_matching import propose_matches, matching_output_budget


SOURCE = "[SYNTHETIC] Job\r\nCerințe obligatorii:\r\n- English OR\r\n  German.\r\n\r\nAvantaje:\r\n- Python."


class GroundedExtractionTests(unittest.TestCase):
    def test_no_application_stage_uses_the_old_1024_minimum(self):
        self.assertEqual(extraction_output_budget(10), 2048)
        self.assertEqual(extraction_output_budget(2000), 3024)
        self.assertEqual(extraction_output_budget(8000), 4096)
        self.assertEqual(matching_output_budget(1), 2048)
        self.assertEqual(matching_output_budget(6), 2560)

    def test_candidates_preserve_wrapped_alternatives_and_exclude_section_titles(self):
        quotes = source_quote_candidates(SOURCE)
        self.assertIn("- English OR\r\n  German.", quotes)
        self.assertIn("- Python.", quotes)
        self.assertNotIn("Cerințe obligatorii:", quotes)
        self.assertNotIn("Avantaje:", quotes)
        for quote in quotes:
            self.assertIn(quote, SOURCE)

    @patch("jobhunter.ollama.chat_local")
    def test_grounded_schema_and_version_are_explicit_without_mutating_baseline(self, chat):
        original = deepcopy(OUTPUT_SCHEMA)
        quote = "- English OR\r\n  German."
        chat.return_value = ChatResult(json.dumps({"requirements": [{"quote": quote, "priority": "mandatory"}]}), 0, 0, 0, 2048)
        result = extract_requirements(SOURCE, grounded=True)
        self.assertEqual(result.prompt_version, "requirements-source-spans-1")
        self.assertEqual(result.output_limit, 2048)
        self.assertEqual(result.generation_policy, "requirements-output-budget-1")
        self.assertEqual(SOURCE[result.requirements[0].start:result.requirements[0].end], quote)
        schema = chat.call_args.args[2]
        self.assertEqual(schema["properties"]["requirements"]["items"]["properties"]["quote"]["enum"], list(source_quote_candidates(SOURCE)))
        self.assertEqual(chat.call_args.kwargs["max_output_tokens"], extraction_output_budget(len(SOURCE)))
        self.assertEqual(OUTPUT_SCHEMA, original)

    @patch("jobhunter.ollama.chat_local")
    def test_even_grounded_output_is_revalidated_and_keeps_error_type_and_stage(self, chat):
        chat.return_value = ChatResult('{"requirements": [{"quote": "Invented", "priority": "mandatory"}]}', 0, 0, 0)
        with self.assertRaises(SourceQuoteError) as caught:
            extract_requirements(SOURCE, grounded=True)
        self.assertEqual(caught.exception.stage, "extraction")
        self.assertIn("Extragerea cerințelor", str(caught.exception))
        self.assertNotIn("Invented", str(caught.exception))

    @patch("jobhunter.ollama.chat_local")
    @patch("jobhunter.analysis.propose_matches")
    def test_extraction_truncation_carries_stage_and_never_starts_matching(self, matching, chat):
        chat.side_effect = OllamaResponseError("output_limit", "Synthetic truncation", output_limit=2048, output_tokens=2048)
        with self.assertRaises(OllamaResponseError) as caught:
            analyze_draft(SOURCE, {"version": "synthetic", "facts": []}, grounded_extraction=True)
        self.assertEqual(caught.exception.stage, "extraction")
        self.assertEqual(caught.exception.output_limit, 2048)
        matching.assert_not_called()

    @patch("jobhunter.ai_matching.chat_local")
    def test_matching_truncation_has_matching_stage_and_is_not_recovered(self, chat):
        source = "English."
        requirements = {"schema_version": "1", "requirements": [{"id": "R1", "priority": "mandatory", "quote": source, "start": 0, "end": len(source)}]}
        chat.side_effect = OllamaResponseError("output_limit", "Synthetic truncation", output_limit=2048, output_tokens=2048)
        with self.assertRaises(OllamaResponseError) as caught:
            propose_matches(source, requirements, {"version": "synthetic", "facts": []}, recover_invalid=True)
        self.assertEqual(caught.exception.stage, "matching")
        self.assertEqual(caught.exception.code, "output_limit")
        chat.assert_called_once()
