"""Prove local profile import/review/persistence on a fictional CV only."""

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from jobhunter.cv_import import import_cv
from jobhunter.master_profile import MasterProfileStore, prepare_master, approve_master


def main():
    root = Path(__file__).resolve().parents[1]
    raw = (root / "tests/fixtures/master_cv_synthetic.txt").read_bytes()
    document = import_cv(raw, "master_cv_synthetic.txt")
    selected = [{"block_index": i, "kind": "confirmed_gap" if i == 5 else "experience"} for i in range(1, 6)]
    draft = prepare_master(document, selected)
    profile = approve_master(draft, expected_fingerprint=draft.fingerprint, reviewer="[SYNTHETIC] Demo master reviewer",
                             note="Simulated review; not approval by the real user.", confirmed=True)
    with TemporaryDirectory(prefix="master-demo-", dir=root) as directory:
        path = Path(directory) / "synthetic.sqlite3"
        store = MasterProfileStore(path)
        store.save(document, raw, profile)
        reopened = MasterProfileStore(path)
        restored = reopened.load(profile["version"])
        original, source = reopened.source(profile["version"])
        report = {"synthetic": True, "real_user_approval": False, "temporary_database": True,
                  "profile_version": restored["version"], "fact_count": len(restored["facts"]),
                  "citations_exact": all(source["text"][c["start"]:c["end"]] == c["quote"] for c in restored["provenance"]["citations"]),
                  "original_bytes_preserved": original == raw,
                  "original_sha256": sha256(original).hexdigest(),
                  "qa_history_preserved": "QA Lead" in source["text"] and "QA Engineer" in source["text"],
                  "model_calls": 0, "job_decisions_applied": 0}
    (root / "docs/evaluations/master_profile_001.demo.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
