"""Simulate approval with a fictional reviewer in a disposable local database."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from jobhunter.approval import approve_review, review_fingerprint
from jobhunter.review import ReviewMaterial
from jobhunter.storage import JobRepository


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "docs/evaluations/review_001.proposal.json").read_text(encoding="utf-8"))
    material = ReviewMaterial(**payload)
    fingerprint = review_fingerprint(material)
    approval = approve_review(material, expected_fingerprint=fingerprint,
                              reviewer="[SYNTHETIC] Demo reviewer",
                              note="Simulated review for technical demonstration; not a real user approval.",
                              confirmed=True)
    with TemporaryDirectory(prefix="approval-demo-", dir=root) as directory:
        repository = JobRepository(Path(directory) / "synthetic.sqlite3")
        job_id = repository.add("[SYNTHETIC] Engineering Manager", material.source)
        decision_id = repository.apply_approved_review(job_id, material, approval)
        replay_id = repository.apply_approved_review(job_id, material, approval)
        result = {"synthetic": True, "real_user_approval": False, "temporary_database": True,
                  "review_fingerprint": fingerprint, "reviewer": approval.reviewer,
                  "approved_at": approval.approved_at,
                  "status": repository.decision_history(job_id)[0]["status"],
                  "score": repository.decision_history(job_id)[0]["reviewed_score"]["minimum_percent"],
                  "decision_count": len(repository.decision_history(job_id)),
                  "approval_count": len(repository.approval_history(job_id)),
                  "replay_is_idempotent": replay_id == decision_id,
                  "opportunity_count": len(repository.list_opportunities())}
    (root / "docs/evaluations/approval_001.demo.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    print("Simulare fictiva; raportul utilizatorului ramane neaprobat. Baza temporara a fost eliminata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
