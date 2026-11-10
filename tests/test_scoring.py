"""Verify score arithmetic, uncertainty and warnings independently of inference."""

from dataclasses import replace
import json
from pathlib import Path
import unittest

from jobhunter.matching import Match, validate_matches, validate_profile
from jobhunter.requirements import Requirement, validate_requirements
from jobhunter.scoring import ScoringRubric, score_requirements


FIXTURES = Path(__file__).parent / "fixtures"


def load_json(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ScoringTests(unittest.TestCase):
    def setUp(self):
        source = (FIXTURES / "job_001.txt").read_text(encoding="utf-8")
        self.requirements = validate_requirements(load_json("job_001.expected.json"), source)
        profile = validate_profile(load_json("profile_001.json"))
        self.matches = validate_matches(load_json("matches_001.expected.json"), self.requirements, profile)

    def test_reference_score_has_explained_exclusion_and_warning(self):
        # Leadership: 2; English: 1; AI adoption: 0. Total possible: 5.
        report = score_requirements(self.requirements, self.matches)
        self.assertEqual((report.minimum_percent, report.maximum_percent), (60, 60))
        self.assertEqual(report.coverage_percent, 100)
        self.assertEqual(report.total_weight, 5)
        self.assertEqual(report.excluded_requirement_ids, ("R4",))
        self.assertEqual([(w.requirement_id, w.code) for w in report.warnings],
                         [("R2", "mandatory_partial"), ("R4", "priority_unknown_excluded")])
        self.assertEqual([c.minimum_points for c in report.contributions], [2, 1, 0, None])
        self.assertEqual(report, score_requirements(self.requirements, self.matches))

    def test_unknown_matching_widens_interval_and_reduces_coverage(self):
        matches = tuple(replace(m, status="unknown", evidence_ids=()) if m.requirement_id == "R2" else m for m in self.matches)
        report = score_requirements(self.requirements, matches)
        self.assertEqual((report.minimum_percent, report.maximum_percent), (40, 80))
        self.assertEqual(report.coverage_percent, 60)
        self.assertIn("mandatory_unknown", [w.code for w in report.warnings])

    def test_all_matching_unknown_has_full_uncertainty(self):
        matches = tuple(replace(m, status="unknown", evidence_ids=()) for m in self.matches)
        report = score_requirements(self.requirements, matches)
        self.assertEqual((report.minimum_percent, report.maximum_percent, report.coverage_percent), (0, 100, 0))

    def test_all_supported_is_not_lowered_by_unknown_priority(self):
        matches = tuple(replace(m, status="supported", evidence_ids=("P1",)) for m in self.matches)
        report = score_requirements(self.requirements, matches)
        self.assertEqual((report.minimum_percent, report.maximum_percent), (100, 100))
        self.assertEqual(report.excluded_requirement_ids, ("R4",))

    def test_mandatory_gap_warns_even_with_high_overall_score(self):
        requirements = (Requirement("M", "mandatory", "synthetic", 0, 9),) + tuple(
            Requirement(f"O{i}", "optional", "synthetic", 0, 9) for i in range(20))
        matches = (Match("M", "confirmed_missing", ("gap",), "Synthetic explicit gap"),) + tuple(
            Match(f"O{i}", "supported", ("fact",), "Synthetic evidence") for i in range(20))
        report = score_requirements(requirements, matches)
        self.assertGreater(report.minimum_percent, 90)
        self.assertEqual(report.warnings[0].code, "mandatory_confirmed_missing")

    def test_empty_or_unknown_priority_only_is_unavailable(self):
        for requirements, matches in [((), ()), (self.requirements[-1:], self.matches[-1:])]:
            with self.subTest(requirements=requirements):
                report = score_requirements(requirements, matches)
                self.assertIsNone(report.minimum_percent)
                self.assertIsNone(report.maximum_percent)
                self.assertIsNone(report.coverage_percent)
                self.assertEqual(report.total_weight, 0)

    def test_missing_extra_and_duplicate_matches_are_rejected(self):
        for matches in [self.matches[:-1], self.matches + self.matches[:1],
                        self.matches + (replace(self.matches[0], requirement_id="extra"),)]:
            with self.subTest(matches=matches), self.assertRaises(ValueError):
                score_requirements(self.requirements, matches)
        with self.assertRaises(ValueError):
            score_requirements(self.requirements + self.requirements[:1], self.matches)

    def test_invalid_categories_are_rejected(self):
        with self.assertRaises(ValueError):
            score_requirements((replace(self.requirements[0], priority="assumed"),), self.matches[:1])
        with self.assertRaises(ValueError):
            score_requirements(self.requirements[:1], (replace(self.matches[0], status="perfect"),))

    def test_configurable_rubric_is_included_in_report(self):
        rubric = ScoringRubric(mandatory_weight=3, optional_weight=1, partial_credit=0.25)
        report = score_requirements(self.requirements, self.matches, rubric)
        self.assertEqual(report.rubric, rubric)
        self.assertAlmostEqual(report.minimum_percent, 3.75 / 7 * 100)
        self.assertEqual(report.total_weight, 7)

    def test_invalid_rubric_is_rejected(self):
        for change in [{"version": "2"}, {"mandatory_weight": 0}, {"optional_weight": -1},
                       {"mandatory_weight": True}, {"optional_weight": float("inf")},
                       {"partial_credit": float("nan")}, {"partial_credit": 1.1},
                       {"partial_credit": -0.1}, {"partial_credit": "0.5"}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                ScoringRubric(**change)

    def test_match_order_does_not_change_report(self):
        self.assertEqual(score_requirements(self.requirements, self.matches),
                         score_requirements(self.requirements, tuple(reversed(self.matches))))
