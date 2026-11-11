"""Small synthetic evaluation, separate from unit tests and private job storage."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from jobhunter.analysis import analyze_draft
from jobhunter.eligibility import evaluate_eligibility
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.ollama import ExtractionError, MODEL, OPTIONS
from jobhunter.requirements import validate_requirements
from jobhunter.review import _quoted


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests/fixtures/language_cases.json"


def reference_payloads(case: dict, profile: dict) -> tuple[dict, dict]:
    """Convert authored expectations to the application contract, never to model input."""
    requirements, matches = [], []
    for index, expected in enumerate(case["expected"], start=1):
        identifier = f"R{index}"
        quote = expected["quote"]
        start = case["source"].find(quote)
        if start < 0 or case["source"].find(quote, start + 1) >= 0:
            raise ValueError("Reference quote must occur exactly once.")
        requirements.append({"id": identifier, "quote": quote, "priority": expected["priority"],
                             "start": start, "end": start + len(quote)})
        matches.append({"requirement_id": identifier, "status": expected["status"],
                        "evidence_ids": list(expected["evidence_ids"]), "explanation": "Authored synthetic reference; not model output."})
    return ({"schema_version": "1", "requirements": requirements},
            {"schema_version": "1", "profile_version": profile["version"], "matches": matches})


def validate_suite(suite: dict) -> None:
    if suite.get("schema_version") != "1" or suite.get("synthetic") is not True:
        raise ValueError("Expected the versioned synthetic language suite.")
    profile = validate_profile(suite["profile"])
    seen = set()
    if not suite["cases"]:
        raise ValueError("The evaluation suite must not be empty.")
    for case in suite["cases"]:
        if case["id"] in seen:
            raise ValueError("Evaluation case IDs must be unique.")
        seen.add(case["id"])
        req, matches = reference_payloads(case, suite["profile"])
        validated = validate_requirements(req, case["source"])
        validate_matches(matches, validated, profile)
        if evaluate_eligibility(case["source"], req, suite["profile"], matches).status != case["expected_eligibility"]:
            raise ValueError("Authored eligibility is inconsistent with the policy.")


def compare_case(case: dict, actual: dict) -> dict:
    """Measure exact extraction and status/evidence agreement, not explanation fidelity."""
    requirements = actual["extraction"]["requirements"]
    by_id = {r["id"]: r["quote"] for r in requirements}
    expected_pairs = {(r["quote"], r["priority"]) for r in case["expected"]}
    actual_pairs = {(r["quote"], r["priority"]) for r in requirements}
    expected_matches = {r["quote"]: (r["status"], tuple(sorted(r["evidence_ids"]))) for r in case["expected"]}
    actual_matches = {by_id[m["requirement_id"]]: (m["status"], tuple(sorted(m["evidence_ids"])))
                      for m in actual["matching"]["matches"]}
    checks = {"extraction_exact": actual_pairs == expected_pairs and len(requirements) == len(case["expected"]),
              "matching_status_and_evidence_exact": actual_matches == expected_matches,
              "eligibility_exact": actual["suggested_eligibility"]["status"] == case["expected_eligibility"],
              "draft_only": actual["review_status"] == "pending_semantic_review" and actual["decision_applied"] is False}
    return {"checks": checks, "passed_measured_checks": all(checks.values()),
            "missing_requirements": sorted(expected_pairs - actual_pairs),
            "unexpected_requirements": sorted(actual_pairs - expected_pairs),
            "matching_differences": [{"quote": quote, "expected": expected_matches.get(quote), "actual": actual_matches.get(quote)}
                                     for quote in sorted(set(expected_matches) | set(actual_matches))
                                     if expected_matches.get(quote) != actual_matches.get(quote)],
            "explanations_semantically_approved": False}


def run_evaluation(suite: dict, *, analyzer=analyze_draft) -> dict:
    validate_suite(suite)
    results = []
    for case in suite["cases"]:
        try:
            # Expected labels are deliberately not passed to inference.
            draft = analyzer(case["source"], suite["profile"])
            actual = json.loads(json.dumps(asdict(draft), ensure_ascii=False))
            result = {"case_id": case["id"], "title": case["title"], "source": case["source"],
                      "expected": case["expected"], "expected_eligibility": case["expected_eligibility"],
                      "actual": actual, **compare_case(case, actual)}
        except (ExtractionError, ValueError) as error:
            result = {"case_id": case["id"], "title": case["title"], "source": case["source"],
                      "expected": case["expected"], "expected_eligibility": case["expected_eligibility"],
                      "error": str(error), "passed_measured_checks": False,
                      "explanations_semantically_approved": False}
        results.append(result)
    return {"evaluated_at": datetime.now(timezone.utc).isoformat(), "synthetic": True,
            "model": MODEL, "options": dict(OPTIONS), "profile": suite["profile"],
            "case_count": len(results), "passed_measured_checks": sum(r["passed_measured_checks"] for r in results),
            "cases": results,
            "limitations": ["Only three synthetic cases, authored by the coding agent; not a representative benchmark.",
                            "Exact label/evidence agreement does not certify explanations or general model accuracy.",
                            "No user jobs, private database, approvals or applications are changed."]}


def render_evaluation(report: dict) -> str:
    lines = ["# Evaluarea limbilor — trei cazuri fictive", "",
             f"Cazuri care satisfac criteriile măsurate: **{report['passed_measured_checks']}/{report['case_count']}**.", "",
             "Verificăm citate/priorități, statusuri/dovezi, eligibilitate propusă și păstrarea draftului. Explicațiile nu sunt aprobate automat.", "",
             "Nu este un benchmark reprezentativ. Nicio decizie nu a fost aplicată în baza privată.", ""]
    for case in report["cases"]:
        lines += ["## Caz", "", _quoted(case["title"]), "", "Textul jobului:", "", _quoted(case["source"]), "",
                  f"Eligibilitate așteptată: {case['expected_eligibility']}.", ""]
        if "error" in case:
            lines += ["**Rulare nereușită, fără retry automat:**", "", _quoted(case["error"]), ""]
            continue
        actual = case["actual"]
        lines += [f"Criterii măsurate: {'trecute' if case['passed_measured_checks'] else 'diferențe identificate'}.", "",
                  f"Eligibilitate propusă de flux: {actual['suggested_eligibility']['status']}.", ""]
        by_id = {r["id"]: r for r in actual["extraction"]["requirements"]}
        for match in actual["matching"]["matches"]:
            requirement = by_id[match["requirement_id"]]
            lines += [_quoted(requirement["quote"]), "",
                      f"Prioritate: {requirement['priority']}; matching: {match['status']}.", "",
                      "Explicația brută a modelului:", "", _quoted(match["explanation"]), ""]
            for identifier in match["evidence_ids"]:
                fact = next(f for f in report["profile"]["facts"] if f["id"] == identifier)
                lines += [_quoted(f"{identifier}: {fact['text']}"), ""]
        if not case["passed_measured_checks"]:
            lines += ["Diferențe pentru revizuire:", "", _quoted(json.dumps({
                "missing": case["missing_requirements"], "unexpected": case["unexpected_requirements"],
                "matching": case["matching_differences"]}, ensure_ascii=False)), ""]
    return "\n".join(lines)


def main() -> int:
    suite = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    report = run_evaluation(suite)
    output = ROOT / "docs/evaluations"
    (output / "language_eval_001.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "language_eval_001.md").write_text(render_evaluation(report), encoding="utf-8")
    print(json.dumps({"case_count": report["case_count"], "passed_measured_checks": report["passed_measured_checks"],
                      "results": [{"id": c["case_id"], "passed": c["passed_measured_checks"], "error": c.get("error")}
                                  for c in report["cases"]]}, indent=2))
    return 0 if report["passed_measured_checks"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
