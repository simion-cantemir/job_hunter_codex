"""Manual requirements stay exact and never bypass source or approval validation."""

import json
import unittest
from unittest.mock import patch

from jobhunter.analysis import analyze_draft
from jobhunter.manual_requirements import select_requirements, source_lines
from jobhunter.ollama import ChatResult, SourceQuoteError, _requirements_from_content
from jobhunter.ui_session import ReviewSession


SOURCE = "[SYNTHETIC] Job\r\n\r\nCerințe obligatorii:\r\n  - Experiență QA.  \r\nAvantaje:\r\n- Python.\r\n- Experiență QA."
PROFILE = {"version": "synthetic-manual-v1", "facts": [{"id": "F1", "kind": "experience", "text": "[SYNTHETIC] Experiență QA."}]}


class ManualRequirementsTests(unittest.TestCase):
    def test_unicode_crlf_and_repeated_lines_have_exact_offsets(self):
        lines = source_lines(SOURCE)
        for line in lines:
            self.assertEqual(SOURCE[line.start:line.end], line.text)
        self.assertEqual(lines[2].text, lines[-1].text)
        self.assertNotEqual(lines[2].start, lines[-1].start)
        result = select_requirements(SOURCE, [{"line_index": 2, "priority": "mandatory"}, {"line_index": 4, "priority": "optional"}])
        self.assertEqual([r["priority"] for r in result["requirements"]], ["mandatory", "optional"])

    def test_invalid_empty_duplicate_indices_or_priorities_are_rejected(self):
        variants = [[], [{"line_index": True, "priority": "mandatory"}],
                    [{"line_index": 999, "priority": "mandatory"}],
                    [{"line_index": 2, "priority": "mandatory"}] * 2,
                    [{"line_index": 2, "priority": "invented"}]]
        for selections in variants:
            with self.subTest(selections=selections), self.assertRaises(ValueError):
                select_requirements(SOURCE, selections)

    def test_paraphrased_model_quote_is_rejected_without_echoing_content(self):
        with self.assertRaises(SourceQuoteError) as caught:
            _requirements_from_content(json.dumps({"requirements": [{"quote": "PRIVATE incorrect paraphrase", "priority": "mandatory"}]}), SOURCE)
        self.assertNotIn("PRIVATE", str(caught.exception))

    @patch("jobhunter.analysis.extract_requirements")
    @patch("jobhunter.ai_matching.chat_local")
    def test_manual_path_calls_only_matching_and_stays_pending(self, chat, extract):
        selected = select_requirements(SOURCE, [{"line_index": 2, "priority": "mandatory"}])
        chat.return_value = ChatResult(json.dumps({"matches": [{"requirement_id": "R1", "status": "supported", "evidence_ids": ["F1"], "explanation": "Synthetic exact source."}]}), 0, 0, 0)
        draft = analyze_draft(SOURCE, PROFILE, selected_requirements=selected)
        extract.assert_not_called()
        chat.assert_called_once()
        self.assertEqual(draft.extraction.model, "manual")
        self.assertEqual(draft.extraction.prompt_version, "requirements-manual-1")
        self.assertEqual(draft.review_status, "pending_semantic_review")
        self.assertFalse(draft.decision_applied)
        sent = chat.call_args.args[1]["requirements"]
        self.assertEqual(sent, selected["requirements"])

    @patch("jobhunter.analysis.extract_requirements")
    @patch("jobhunter.ai_matching.chat_local")
    def test_modified_manual_quote_is_rejected_before_inference(self, chat, extract):
        selected = select_requirements(SOURCE, [{"line_index": 2, "priority": "mandatory"}])
        selected["requirements"][0]["quote"] = "Invented qualification"
        with self.assertRaises(ValueError):
            analyze_draft(SOURCE, PROFILE, selected_requirements=selected)
        chat.assert_not_called()
        extract.assert_not_called()

    def test_selection_edit_invalidates_existing_analysis_and_approval(self):
        workflow = ReviewSession()
        selection = {"mode": "manual", "selections": [{"line_index": 2, "priority": "mandatory"}]}
        workflow.sync_requirements(selection)
        workflow.report, workflow.approval = {"synthetic": True}, object()
        self.assertFalse(workflow.sync_requirements(selection))
        self.assertIsNotNone(workflow.report)
        workflow.sync_requirements({**selection, "selections": [{"line_index": 2, "priority": "optional"}]})
        self.assertIsNone(workflow.report)
        self.assertIsNone(workflow.approval)
