"""Fictional approvals verify exact snapshots and atomic SQLite application."""

from contextlib import closing
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from jobhunter.approval import approve_review, review_fingerprint, verify_approval
from jobhunter.review import ReviewMaterial, prepare_review
from jobhunter.storage import JobRepository


ROOT = Path(__file__).resolve().parents[1]


class ApprovalFixtures:
    def setUp(self):
        payload = json.loads((ROOT / "docs/evaluations/review_001.proposal.json").read_text(encoding="utf-8"))
        self.material = ReviewMaterial(**payload)

    def approve(self, material=None):
        material = self.material if material is None else material
        return approve_review(material, expected_fingerprint=review_fingerprint(material),
                              reviewer="[SYNTHETIC] Test reviewer", note="Synthetic test confirmation.", confirmed=True)


class ApprovalTests(ApprovalFixtures, unittest.TestCase):

    def test_explicit_confirmation_and_reviewer_are_required(self):
        for confirmed in [False, None, 1, "yes"]:
            with self.subTest(confirmed=confirmed), self.assertRaises(ValueError):
                approve_review(self.material, expected_fingerprint=review_fingerprint(self.material),
                               reviewer="Fictional", note="Test", confirmed=confirmed)
        for reviewer, note in [(" ", "Test"), ("Fictional", " ")]:
            with self.subTest(reviewer=reviewer, note=note), self.assertRaises(ValueError):
                approve_review(self.material, expected_fingerprint=review_fingerprint(self.material),
                               reviewer=reviewer, note=note, confirmed=True)

    def test_receipt_contains_exact_snapshot_and_does_not_change_pending_material(self):
        approval = self.approve()
        decision, score = verify_approval(self.material, approval)
        self.assertEqual(decision.status, "needs_review")
        self.assertEqual(score.minimum_percent, 60)
        self.assertEqual(json.loads(approval.snapshot_json)["revised_matches"], self.material.revised_matches)
        self.assertEqual(self.material.review_status, "pending_semantic_review")
        self.assertFalse(self.material.decision_applied)

    def test_stale_fingerprint_cannot_be_approved(self):
        with self.assertRaises(ValueError):
            approve_review(self.material, expected_fingerprint=self.material.analysis_fingerprint,
                           reviewer="Fictional", note="Test", confirmed=True)

    def test_profile_source_or_correction_change_invalidates_receipt(self):
        approval = self.approve()
        variants = []
        modified = deepcopy(self.material)
        modified.profile["facts"][0]["text"] += " Changed fact."
        variants.append(modified)
        variants.append(replace(self.material, source=self.material.source + "\nChanged source."))
        modified = deepcopy(self.material)
        modified.changes[0]["note"] += " Updated review note."
        variants.append(modified)
        for material in variants:
            with self.subTest(material=material), self.assertRaises(ValueError):
                verify_approval(material, approval)

    def test_unrecorded_revision_is_rejected_even_before_approval(self):
        self.material.revised_matches["matches"][0]["explanation"] = "Unrecorded correction."
        with self.assertRaisesRegex(ValueError, "change history"):
            self.approve()

    def test_mismatched_original_audit_is_rejected(self):
        self.material.changes[0]["before"]["status"] = "supported"
        with self.assertRaises(ValueError):
            self.approve()

    def test_receipt_with_altered_snapshot_or_invalid_metadata_is_rejected(self):
        approval = self.approve()
        for changed in [replace(approval, snapshot_json="{}"), replace(approval, reviewer=" "),
                        replace(approval, approved_at="not-a-time"), replace(approval, approved_at="2026-11-10T12:00:00")]:
            with self.subTest(approval=changed), self.assertRaises(ValueError):
                verify_approval(self.material, changed)

    def test_changed_scoring_rules_invalidate_approval(self):
        approval = self.approve()
        _, score = verify_approval(self.material, approval)
        with patch("jobhunter.approval.score_requirements", return_value=replace(score, minimum_percent=99)):
            with self.assertRaises(ValueError):
                verify_approval(self.material, approval)


class ApprovalStorageTests(ApprovalFixtures, unittest.TestCase):
    def setUp(self):
        super().setUp()
        directory = TemporaryDirectory(prefix="approval-test-", dir=ROOT)
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "synthetic.sqlite3"
        self.repository = JobRepository(self.path)
        self.job_id = self.repository.add("[SYNTHETIC] Engineering Manager", self.material.source)

    def test_unapproved_proposal_cannot_apply(self):
        with self.assertRaises(ValueError):
            self.repository.apply_approved_review(self.job_id, self.material, self.material)
        self.assertEqual(self.repository.decision_history(self.job_id), ())

    def test_apply_and_reopen_preserve_full_audit_and_corrected_explanation(self):
        approval = self.approve()
        self.repository.apply_approved_review(self.job_id, self.material, approval)
        reopened = JobRepository(self.path)
        history = reopened.decision_history(self.job_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["review"]["reviewer"], approval.reviewer)
        self.assertEqual(history[0]["reviewed_score"]["minimum_percent"], 60)
        receipt = reopened.approval_history(self.job_id)[0]
        snapshot = json.loads(receipt["snapshot_json"])
        self.assertIn("profesionistul de calitate", snapshot["original_matches"]["matches"][1]["explanation"])
        self.assertIn("participarea actuală", snapshot["revised_matches"]["matches"][1]["explanation"])

    def test_replay_is_idempotent_but_another_receipt_is_not_silently_applied(self):
        approval = self.approve()
        first = self.repository.apply_approved_review(self.job_id, self.material, approval)
        self.assertEqual(self.repository.apply_approved_review(self.job_id, self.material, approval), first)
        with self.assertRaises(ValueError):
            self.repository.apply_approved_review(self.job_id, self.material, replace(approval, reviewer="Other fictional reviewer"))
        self.assertEqual(len(self.repository.decision_history(self.job_id)), 1)
        self.assertEqual(len(self.repository.approval_history(self.job_id)), 1)

    def test_wrong_or_changed_job_does_not_persist_any_approval(self):
        approval = self.approve()
        wrong_id = self.repository.add("Other fictional job", "Different synthetic source")
        for job_id in [wrong_id, wrong_id + 1]:
            with self.subTest(job_id=job_id), self.assertRaises(ValueError):
                self.repository.apply_approved_review(job_id, self.material, approval)
            self.assertEqual(self.repository.approval_history(job_id), ())
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute("UPDATE jobs SET description = ? WHERE id = ?", ("Changed source", self.job_id))
        with self.assertRaises(ValueError):
            self.repository.apply_approved_review(self.job_id, self.material, approval)
        self.assertEqual(self.repository.decision_history(self.job_id), ())

    def test_failed_audit_write_rolls_back_decision(self):
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute("""CREATE TRIGGER synthetic_audit_failure BEFORE INSERT ON review_approvals
                                      BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.apply_approved_review(self.job_id, self.material, self.approve())
        self.assertEqual(self.repository.decision_history(self.job_id), ())
        self.assertEqual(self.repository.approval_history(self.job_id), ())

    def test_simulated_approved_mandatory_gap_excludes_job(self):
        # Make the already explicit AI-adoption gap mandatory as a fictional edit.
        report = json.loads((ROOT / "docs/evaluations/ollama_analysis_001_run_001.json").read_text(encoding="utf-8"))
        original = prepare_review(report, self.material.source, self.material.profile)
        match = original.original_matches["matches"][2]
        material = prepare_review(report, original.source, original.profile, {
            "analysis_fingerprint": original.analysis_fingerprint,
            "changes": [{**match, "priority": "mandatory", "note": "Synthetic policy test, not a real job interpretation."}],
        })
        self.repository.apply_approved_review(self.job_id, material, self.approve(material))
        self.assertEqual(self.repository.list_opportunities(), ())
        self.assertEqual(self.repository.decision_history(self.job_id)[0]["status"], "rejected")
        self.assertIsNotNone(self.repository.get(self.job_id))
