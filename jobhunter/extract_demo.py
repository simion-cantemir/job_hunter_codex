"""Run one local extraction on the fixed synthetic example, without writing data."""

from dataclasses import asdict
import json
from pathlib import Path
import sys

from jobhunter.ollama import ExtractionError, OPTIONS, extract_requirements


def main() -> int:
    fixtures = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
    source = (fixtures / "job_001.txt").read_text(encoding="utf-8")
    expected = json.loads((fixtures / "job_001.expected.json").read_text(encoding="utf-8"))
    try:
        result = extract_requirements(source)
    except ExtractionError as error:
        print(f"Extragere nereușită: {error}", file=sys.stderr)
        return 1
    actual_pairs = {(r.quote, r.priority) for r in result.requirements}
    expected_pairs = {(r["quote"], r["priority"]) for r in expected["requirements"]}
    report = {**asdict(result), "options": OPTIONS, "synthetic": True,
              "comparison": {
                  "expected_count": len(expected_pairs), "actual_count": len(result.requirements),
                  "exact_quote_and_priority_matches": len(actual_pairs & expected_pairs),
                  "missing": sorted(expected_pairs - actual_pairs),
                  "unexpected": sorted(actual_pairs - expected_pairs),
                  "note": "Un singur exemplu redactat de agent, nerevizuit încă de utilizator; nu este benchmark reprezentativ.",
              }}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
