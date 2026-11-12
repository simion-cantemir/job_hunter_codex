"""Live local smoke check on a synthetic source-cited master profile only."""

import json
from pathlib import Path

from jobhunter.analysis import analyze_draft
from jobhunter.cv_import import import_cv
from jobhunter.master_profile import approve_master, prepare_master
from jobhunter.ollama import ExtractionError


def main():
    root = Path(__file__).resolve().parents[1]
    raw = (root / "tests/fixtures/master_cv_synthetic.txt").read_bytes()
    document = import_cv(raw, "master_cv_synthetic.txt")
    selected = [{"block_index": i, "kind": "confirmed_gap" if i == 5 else "experience"} for i in range(1, 6)]
    draft = prepare_master(document, selected)
    profile = approve_master(draft, expected_fingerprint=draft.fingerprint,
                             reviewer="[SYNTHETIC] Recovery smoke reviewer",
                             note="Simulated profile approval for a local technical test.", confirmed=True)
    source = (root / "tests/fixtures/job_001.txt").read_text(encoding="utf-8")
    try:
        result = analyze_draft(source, profile, recover_matching=True)
    except (ExtractionError, ValueError) as error:
        print(f"Synthetic live check failed: {error}")
        return 1
    summary = {"synthetic": True, "real_user_data": False, "private_database_accessed": False,
               "model": result.matching.model, "output_contract": result.matching.output_contract,
               "requirement_count": len(result.extraction.requirements), "match_count": len(result.matching.matches),
               "issues": [{"code": i.code, "requirement_id": i.requirement_id} for i in result.matching.issues],
               "matching_statuses": [{"id": m.requirement_id, "status": m.status} for m in result.matching.matches],
               "eligibility": result.suggested_eligibility.status,
               "review_status": result.review_status, "decision_applied": result.decision_applied,
               "note": "Transport/contract smoke check only, not a semantic benchmark or reproduction of the user's private input."}
    (root / "docs/evaluations/matching_recovery_001.smoke.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
