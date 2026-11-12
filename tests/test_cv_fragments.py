"""Exact user-selected excerpts, including partial parser blocks and ambiguity."""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from jobhunter.cv_import import import_cv
from jobhunter.master_profile import excerpt_ranges, prepare_master, approve_master, MasterProfileStore


ROOT = Path(__file__).resolve().parents[1]
TEXT = "[SYNTHETIC] Manager. Led a team. QA history.\n\n[SYNTHETIC] Earlier role. Led a team."


class FragmentTests(unittest.TestCase):
    def setUp(self):
        self.document = import_cv(TEXT.encode(), "synthetic.txt")

    def approve(self, draft):
        return approve_master(draft, expected_fingerprint=draft.fingerprint,
                              reviewer="[SYNTHETIC] Reviewer", note="Simulated excerpt review", confirmed=True)

    def test_partial_block_roundtrip_keeps_original_and_exact_citation(self):
        start, end = excerpt_ranges(self.document, "Manager. Led a team.")[0]
        draft = prepare_master(self.document, [{"start": start, "end": end, "kind": "experience"}])
        profile = self.approve(draft)
        self.assertEqual(profile["facts"][0]["text"], "Manager. Led a team.")
        with TemporaryDirectory(prefix="fragments-", dir=ROOT) as directory:
            store = MasterProfileStore(Path(directory) / "synthetic.sqlite3")
            store.save(self.document, TEXT.encode(), profile)
            self.assertEqual(store.load(profile["version"]), profile)
            raw, document = store.source(profile["version"])
            self.assertEqual(raw, TEXT.encode())
            self.assertIn("QA history", document["text"])

    def test_duplicate_text_occurrences_retain_distinct_context_and_versions(self):
        ranges = excerpt_ranges(self.document, "  Led a team.  ")
        self.assertEqual(len(ranges), 2)
        versions = []
        for start, end in ranges:
            draft = prepare_master(self.document, [{"start": start, "end": end, "kind": "experience"}])
            profile = self.approve(draft)
            self.assertEqual(profile["provenance"]["citations"][0]["start"], start)
            versions.append(profile["version"])
        self.assertNotEqual(*versions)
        self.assertEqual(excerpt_ranges(self.document, "Invented certification"), ())

    def test_invalid_ranges_duplicates_and_blank_selections_are_rejected(self):
        boundary = TEXT.index("\n\n")
        for start, end in [(-1, 5), (0, len(TEXT) + 1), (2, 1), (True, 5), (boundary, boundary + 2)]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                prepare_master(self.document, [{"start": start, "end": end, "kind": "experience"}])
        block = self.document.blocks[0]
        with self.assertRaises(ValueError):
            prepare_master(self.document, [{"block_index": 0, "kind": "experience"},
                                           {"start": block.start, "end": block.end, "kind": "experience"}])

    def test_spanning_blocks_and_existing_full_block_versions_are_supported(self):
        block = self.document.blocks[0]
        legacy = prepare_master(self.document, [{"block_index": 0, "kind": "experience"}])
        ranges = prepare_master(self.document, [{"start": block.start, "end": block.end, "kind": "experience"}])
        self.assertEqual(legacy, ranges)
        full = prepare_master(self.document, [{"start": 0, "end": len(TEXT), "kind": "experience"}])
        self.assertEqual(self.approve(full)["facts"][0]["text"], TEXT)

    def test_modified_excerpt_or_citation_requires_new_review(self):
        start, end = excerpt_ranges(self.document, "Manager.")[0]
        draft = prepare_master(self.document, [{"start": start, "end": end, "kind": "experience"}])
        modified = deepcopy(draft)
        modified.citations[0]["start"] += 1
        with self.assertRaises(ValueError):
            self.approve(modified)
        changed = prepare_master(self.document, [{"start": start, "end": end + 5, "kind": "experience"}])
        with self.assertRaises(ValueError):
            approve_master(changed, expected_fingerprint=draft.fingerprint, reviewer="[SYNTHETIC]",
                           note="Simulated stale approval", confirmed=True)
