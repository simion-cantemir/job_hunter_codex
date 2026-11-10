"""Run extraction and matching on fixed synthetic fixtures, without database writes."""

from dataclasses import asdict
import json
from pathlib import Path
import sys

from jobhunter.analysis import analyze_draft
from jobhunter.ollama import ExtractionError, OPTIONS


def main() -> int:
    fixtures = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
    source = (fixtures / "job_001.txt").read_text(encoding="utf-8")
    profile = json.loads((fixtures / "profile_001.json").read_text(encoding="utf-8"))
    expected_requirements = json.loads((fixtures / "job_001.expected.json").read_text(encoding="utf-8"))
    expected_matches = json.loads((fixtures / "matches_001.expected.json").read_text(encoding="utf-8"))
    try:
        draft = analyze_draft(source, profile)
    except (ExtractionError, ValueError) as error:
        print(f"Analiză nereușită: {error}", file=sys.stderr)
        return 1
    # Compare by quoted requirement, not model-assigned IDs or ordering.
    expected_by_id = {r["id"]: r["quote"] for r in expected_requirements["requirements"]}
    expected = {expected_by_id[m["requirement_id"]]: (m["status"], tuple(sorted(m["evidence_ids"])))
                for m in expected_matches["matches"]}
    actual_by_id = {r.id: r.quote for r in draft.extraction.requirements}
    actual = {actual_by_id[m.requirement_id]: (m.status, tuple(sorted(m.evidence_ids))) for m in draft.matching.matches}
    differences = [{"quote": quote, "expected": expected.get(quote), "actual": actual.get(quote)}
                   for quote in sorted(set(expected) | set(actual)) if expected.get(quote) != actual.get(quote)]
    report = {"synthetic": True, "options": OPTIONS, **asdict(draft),
              "comparison": {"expected_count": len(expected), "actual_count": len(actual),
                             "status_and_evidence_matches": sum(actual.get(q) == value for q, value in expected.items()),
                             "differences": differences,
                             "note": "Referință redactată de agent, nerevizuită de utilizator; nu este validare semantică umană."}}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
