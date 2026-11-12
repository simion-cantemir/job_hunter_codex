"""Local before/after generation-budget check, using only synthetic fixtures."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

from jobhunter.analysis import analyze_draft
from jobhunter.manual_requirements import source_lines, select_requirements
from jobhunter.ollama import _post_local, ExtractionError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Use the previous fixed 1024-token budget")
    parser.add_argument("--automatic", action="store_true", help="Test extraction and matching, not just manual requirements")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = (root / "tests/fixtures/job_ro_quality_delivery_synthetic.txt").read_text(encoding="utf-8")
    profile = json.loads((root / "tests/fixtures/profile_001.json").read_text(encoding="utf-8"))
    bullet_indices = [i for i, line in enumerate(source_lines(source)) if line.text.startswith("- ")]
    requirements = select_requirements(source, [{"line_index": index, "priority": "mandatory" if i < 4 else "optional"}
                                               for i, index in enumerate(bullet_indices)])
    calls = []

    def capture(payload, timeout):
        if args.baseline:
            payload = {**payload, "options": {**payload["options"], "num_predict": 1024}}
        response = _post_local(payload, timeout)
        calls.append({"output_limit": payload["options"]["num_predict"], "done": response.get("done") is True,
                      "done_reason": response.get("done_reason") if response.get("done_reason") in ("stop", "length") else "other",
                      "expected_model": response.get("model") == payload["model"],
                      "output_tokens": response.get("eval_count")})
        return response

    summary = {"synthetic": True, "private_data_accessed": False, "baseline": args.baseline,
               "automatic_extraction": args.automatic,
               "requirement_count": len(bullet_indices), "calls": calls, "decision_applied": False}
    with patch("jobhunter.ollama._post_local", side_effect=capture):
        try:
            draft = analyze_draft(source, profile, selected_requirements=None if args.automatic else requirements,
                                  recover_matching=True, grounded_extraction=args.automatic, timeout=120)
            summary.update({"completed": True, "match_count": len(draft.matching.matches),
                            "extracted_requirements": [{"quote": r.quote, "priority": r.priority} for r in draft.extraction.requirements],
                            "expected_requirements_match": {(r.quote, r.priority) for r in draft.extraction.requirements} ==
                                {(r["quote"], r["priority"]) for r in requirements["requirements"]},
                            "matching_issues": [issue.code for issue in draft.matching.issues],
                            "review_status": draft.review_status})
        except (ExtractionError, ValueError) as error:
            summary.update({"completed": False, "error_code": getattr(error, "code", type(error).__name__),
                            "error_stage": getattr(error, "stage", None)})
    summary["note"] = "Transport and contract smoke only; not a semantic benchmark or reproduction of a private incident."
    suffix = "baseline" if args.baseline else "current"
    prefix = "completion_003.grounded" if args.automatic else "completion_001"
    (root / f"docs/evaluations/{prefix}.{suffix}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0 if summary["completed"] and summary.get("expected_requirements_match", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
