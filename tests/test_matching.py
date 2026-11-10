"""Synthetic matching contract checks, without model calls or personal data."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jobhunter.matching import validate_matches, validate_profile
from jobhunter.requirements import validate_requirements


FIXTURES = Path(__file__).parent / "fixtures"


def load_json(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class MatchingTests(unittest.TestCase):
    def setUp(self):
        source = (FIXTURES / "job_001.txt").read_text(encoding="utf-8")
        self.requirements = validate_requirements(load_json("job_001.expected.json"), source)
        self.profile_payload = load_json("profile_001.json")
        self.profile = validate_profile(self.profile_payload)
        self.payload = load_json("matches_001.expected.json")

    def validate(self, payload):
        return validate_matches(payload, self.requirements, self.profile)

    def test_reference_matches_cover_all_four_states(self):
        result = self.validate(self.payload)
        self.assertEqual([m.status for m in result], ["supported", "partial", "confirmed_missing", "unknown"])
        self.assertEqual(result[0].evidence_ids, ("P1",))
        self.assertEqual(result[3].evidence_ids, ())

    def test_absent_information_cannot_be_confirmed_missing(self):
        self.payload["matches"][3]["status"] = "confirmed_missing"
        with self.assertRaisesRegex(ValueError, "requires profile evidence"):
            self.validate(self.payload)

    def test_positive_fact_cannot_prove_a_confirmed_gap(self):
        self.payload["matches"][3].update(status="confirmed_missing", evidence_ids=["P1"])
        with self.assertRaisesRegex(ValueError, "Evidence kind"):
            self.validate(self.payload)

    def test_gap_cannot_support_a_positive_match(self):
        self.payload["matches"][2]["status"] = "supported"
        with self.assertRaisesRegex(ValueError, "Evidence kind"):
            self.validate(self.payload)

    def test_invented_duplicate_or_empty_evidence_is_rejected(self):
        for refs in [["invented"], ["P1", "P1"], [], [None], "P1"]:
            payload = deepcopy(self.payload)
            payload["matches"][0]["evidence_ids"] = refs
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                self.validate(payload)

    def test_omitted_duplicate_or_invented_requirements_are_rejected(self):
        variants = [self.payload["matches"][:-1], self.payload["matches"] + [self.payload["matches"][0]]]
        invented = deepcopy(self.payload["matches"])
        invented[0]["requirement_id"] = "R999"
        variants.append(invented)
        for matches in variants:
            payload = deepcopy(self.payload)
            payload["matches"] = matches
            with self.subTest(matches=matches), self.assertRaises(ValueError):
                self.validate(payload)

    def test_profile_version_must_match(self):
        self.payload["profile_version"] = "outdated-profile"
        with self.assertRaisesRegex(ValueError, "profile version"):
            self.validate(self.payload)

    def test_malformed_match_output_is_rejected(self):
        for change in [{"status": "perfect"}, {"status": []}, {"explanation": " "}, {"extra": 100}, {"status": "unknown", "evidence_ids": ["P1"]}]:
            payload = deepcopy(self.payload)
            payload["matches"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate(payload)
        for payload in [None, {}, {**self.payload, "schema_version": "2"}, {**self.payload, "matches": {}}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.validate(payload)

    def test_invalid_profiles_are_rejected(self):
        duplicate = deepcopy(self.profile_payload)
        duplicate["facts"].append(duplicate["facts"][0])
        for payload in [None, {}, {"version": " ", "facts": []}, {"version": "v1", "facts": {}}, duplicate]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_profile(payload)
        for change in [{"kind": "inferred_gap"}, {"kind": []}, {"text": " "}, {"extra": 1}]:
            payload = deepcopy(self.profile_payload)
            payload["facts"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_profile(payload)
