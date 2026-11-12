"""Mocked transport tests; this suite never calls a real model."""

from io import BytesIO
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from jobhunter.ollama import (ENDPOINT, MAX_RESPONSE_BYTES, MODEL, ExtractionError, OllamaResponseError, OPTIONS,
                             _NoRedirects, _post_local, extract_requirements, chat_local)


SOURCE = "[SYNTHETIC] Required: English proficiency."
QUOTE = "English proficiency."


def envelope(items=None):
    return {"model": MODEL, "done": True, "done_reason": "stop",
            "message": {"role": "assistant", "content": json.dumps({"requirements": items if items is not None else [
                {"priority": "mandatory", "quote": QUOTE}]})},
            "prompt_eval_count": 50, "eval_count": 20}


class OllamaExtractionTests(unittest.TestCase):
    @patch("jobhunter.ollama._post_local")
    def test_valid_extraction_calculates_offsets_and_separates_data(self, post):
        post.return_value = envelope()
        result = extract_requirements(SOURCE)
        self.assertEqual(result.requirements[0].start, SOURCE.index(QUOTE))
        self.assertEqual(result.requirements[0].end, len(SOURCE))
        self.assertEqual(result.prompt_tokens, 50)
        payload, timeout = post.call_args.args
        self.assertEqual(payload["model"], MODEL)
        self.assertFalse(payload["stream"])
        self.assertNotIn("tools", payload)
        self.assertEqual(json.loads(payload["messages"][1]["content"])["job_description"], SOURCE)
        self.assertEqual(timeout, 60)

    @patch("jobhunter.ollama._post_local")
    def test_empty_extraction_remains_empty(self, post):
        post.return_value = envelope([])
        self.assertEqual(extract_requirements(SOURCE).requirements, ())

    @patch("jobhunter.ollama._post_local")
    def test_bad_evidence_or_categories_are_rejected(self, post):
        for items in [[{"priority": "mandatory", "quote": "Invented German requirement."}],
                      [{"priority": "preferred", "quote": QUOTE}],
                      [{"priority": "mandatory", "quote": " "}],
                      [{"priority": "mandatory", "quote": QUOTE, "extra": 1}],
                      [{"priority": "mandatory", "quote": QUOTE}] * 2]:
            post.return_value = envelope(items)
            with self.subTest(items=items), self.assertRaises(ExtractionError):
                extract_requirements(SOURCE)

    @patch("jobhunter.ollama._post_local")
    def test_repeated_source_quote_is_ambiguous(self, post):
        post.return_value = envelope()
        with self.assertRaisesRegex(ExtractionError, "Ambiguous"):
            extract_requirements(SOURCE + "\n" + QUOTE)

    @patch("jobhunter.ollama._post_local")
    def test_invalid_incomplete_or_tool_responses_are_rejected(self, post):
        variants = [envelope() for _ in range(7)]
        variants[0]["done"] = False
        variants[1]["done_reason"] = "length"
        variants[2]["model"] = "unexpected"
        variants[3]["message"] = None
        variants[4]["message"]["content"] = "not JSON"
        variants[5]["message"]["content"] = '{"requirements": {}}'
        variants[6]["message"]["tool_calls"] = [{"function": "do_something"}]
        for response in variants:
            post.return_value = response
            with self.subTest(response=response), self.assertRaises(ExtractionError):
                extract_requirements(SOURCE)

    @patch("jobhunter.ollama._post_local")
    def test_invalid_input_never_calls_transport(self, post):
        for source in [None, " ", "x" * 8001]:
            with self.subTest(source_type=type(source)), self.assertRaises(ValueError):
                extract_requirements(source)
        for timeout in [0, -1, float("nan"), True, 121]:
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                extract_requirements(SOURCE, timeout=timeout)
        post.assert_not_called()


class OllamaTransportTests(unittest.TestCase):
    @patch("jobhunter.ollama._post_local")
    def test_generation_budget_is_bounded_per_request_without_mutating_defaults(self, post):
        post.return_value = envelope()
        original = dict(OPTIONS)
        result = chat_local("Synthetic", {}, {}, max_output_tokens=2560)
        self.assertEqual(post.call_args.args[0]["options"]["num_predict"], 2560)
        self.assertEqual(result.output_limit, 2560)
        self.assertEqual(OPTIONS, original)
        chat_local("Synthetic", {}, {})
        self.assertEqual(post.call_args.args[0]["options"]["num_predict"], 1024)

    @patch("jobhunter.ollama._post_local")
    def test_invalid_output_budgets_never_call_transport(self, post):
        for limit in [True, None, 0, -1, 127, 4097, 1024.0, "1024"]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                chat_local("Synthetic", {}, {}, max_output_tokens=limit)
        post.assert_not_called()

    @patch("jobhunter.ollama._post_local")
    def test_completion_failures_have_distinct_private_safe_diagnostics_without_retry(self, post):
        for changes, code in [({"done_reason": "length", "eval_count": 2560}, "output_limit"),
                              ({"done": False}, "incomplete"),
                              ({"model": "private-model-name"}, "unexpected_model"),
                              ({"done_reason": "private-stop-reason"}, "unexpected_stop")]:
            post.reset_mock()
            post.return_value = {**envelope(), **changes}
            with self.subTest(code=code), self.assertRaises(OllamaResponseError) as caught:
                chat_local("Synthetic", {}, {}, max_output_tokens=2560)
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(caught.exception.output_limit, 2560)
            self.assertNotIn("private-", str(caught.exception))
            post.assert_called_once()

    @patch("jobhunter.ollama._post_local")
    def test_complete_looking_json_is_rejected_when_server_reports_length(self, post):
        post.return_value = {**envelope(), "done_reason": "length", "eval_count": True}
        with self.assertRaises(OllamaResponseError) as caught:
            extract_requirements(SOURCE)
        self.assertEqual(caught.exception.code, "output_limit")
        self.assertIsNone(caught.exception.output_tokens)

    @patch("jobhunter.ollama.build_opener")
    def test_request_stays_local_with_timeout_and_bounded_read(self, build):
        response = build.return_value.open.return_value.__enter__.return_value
        response.read.return_value = json.dumps(envelope()).encode()
        self.assertTrue(_post_local({"model": MODEL}, 2)["done"])
        request = build.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, ENDPOINT)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(build.return_value.open.call_args.kwargs["timeout"], 2)
        self.assertEqual(build.call_args.args[0].proxies, {})
        self.assertIsInstance(build.call_args.args[1], _NoRedirects)
        response.read.assert_called_once_with(MAX_RESPONSE_BYTES + 1)

    @patch("jobhunter.ollama.build_opener")
    def test_unavailable_timeout_and_http_error_are_controlled(self, build):
        for error in [URLError("refused"), TimeoutError(), HTTPError(ENDPOINT, 404, "Missing", {}, BytesIO(b"private error body"))]:
            build.return_value.open.side_effect = error
            with self.subTest(error=type(error)), self.assertRaises(ExtractionError) as caught:
                _post_local({}, 1)
            self.assertNotIn("private error body", str(caught.exception))
        self.assertEqual(build.return_value.open.call_count, 3)

    @patch("jobhunter.ollama.build_opener")
    def test_invalid_or_oversized_http_bodies_are_rejected(self, build):
        response = build.return_value.open.return_value.__enter__.return_value
        for data in [b"not JSON", b"[]", b"x" * (MAX_RESPONSE_BYTES + 1)]:
            response.read.return_value = data
            with self.subTest(length=len(data)), self.assertRaises(ExtractionError):
                _post_local({}, 1)

    def test_redirect_is_refused(self):
        self.assertIsNone(_NoRedirects().redirect_request(None, None, 302, "", {}, "https://example.com"))
