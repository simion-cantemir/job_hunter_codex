"""Evaluate explicit language rules over saved model outputs, with no inference or DB access."""

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from jobhunter.approval import review_fingerprint
from jobhunter.eligibility import evaluate_eligibility
from jobhunter.evaluate_languages import compare_case
from jobhunter.languages import apply_language_review
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.requirements import validate_requirements
from jobhunter.review import prepare_review, _quoted
from jobhunter.scoring import score_requirements


ROOT = Path(__file__).resolve().parents[1]


def annotation_payload(annotations, case_id, profile, requirements):
    by_quote = {r["quote"]: r["id"] for r in requirements}
    rules = []
    for rule in annotations["cases"][case_id]:
        if rule["quote"] not in by_quote:
            raise ValueError("Required quote was not extracted; annotation needs revision.")
        rules.append({"requirement_id": by_quote[rule["quote"]], **{k: deepcopy(rule[k]) for k in ("operator", "languages", "minimum")}})
    return {"schema_version": "1", "abilities": deepcopy(annotations["profiles"][profile["version"]]), "rules": rules}


def run_saved_evaluation():
    directory = ROOT / "docs/evaluations"
    annotations = json.loads((ROOT / "tests/fixtures/structured_language_reviews.json").read_text(encoding="utf-8"))
    results = []
    # Baseline outputs and failed matching-2 outputs are retained unchanged.
    for suite_file, raw_file in [("language_cases.json", "language_eval_001.json"),
                                 ("language_checks_new.json", "language_eval_v2_new.json")]:
        suite = json.loads((ROOT / "tests/fixtures" / suite_file).read_text(encoding="utf-8"))
        saved = json.loads((directory / raw_file).read_text(encoding="utf-8"))
        saved_by_id = {case["case_id"]: case for case in saved["cases"]}
        if saved["profile"] != suite["profile"]:
            raise ValueError("Saved profile and annotation profile differ.")
        for case in suite["cases"]:
            original = saved_by_id[case["id"]]["actual"]
            material = prepare_review(original, case["source"], suite["profile"])
            payload = annotation_payload(annotations, case["id"], suite["profile"], original["extraction"]["requirements"])
            revised = apply_language_review(material, payload)
            review_fingerprint(revised)  # Full audit and computed-rule consistency checks.
            requirements = validate_requirements(revised.revised_requirements, revised.source)
            matches = validate_matches(revised.revised_matches, requirements, validate_profile(revised.profile))
            decision = evaluate_eligibility(revised.source, revised.revised_requirements, revised.profile, revised.revised_matches)
            score = score_requirements(requirements, matches)
            actual = {"extraction": deepcopy(original["extraction"]),
                      "matching": {"engine": "language-rules-1", "matches": deepcopy(revised.revised_matches["matches"])},
                      "suggested_eligibility": asdict(decision), "provisional_score": asdict(score),
                      "review_status": revised.review_status, "decision_applied": False}
            results.append({"case_id": case["id"], "title": case["title"], "source_report": raw_file,
                            "before_eligibility": original["suggested_eligibility"]["status"],
                            "language_review": payload, "actual": actual, **compare_case(case, actual)})
    return {"evaluated_at": datetime.now(timezone.utc).isoformat(), "synthetic": True,
            "engine": "language-rules-1", "new_model_calls": 0, "user_approval": False,
            "annotations": "agent-authored, requiring user review; not automatically parsed or approved",
            "case_count": len(results), "passed_measured_checks": sum(c["passed_measured_checks"] for c in results),
            "cases": results}


def render(report):
    lines = ["# Reguli de limbă — verificare pe cele opt cazuri fictive", "",
             f"Criterii măsurate trecute: **{report['passed_measured_checks']}/{report['case_count']}**.", "",
             "Intrările structurate sunt adnotate de agent, nu extrase automat și nu aprobate de utilizator. Rezultatul măsoară regulile Python pe aceste intrări, nu precizia unui LLM.", "",
             "Nu au fost apelate modele și nu au fost aplicate decizii sau modificate baze private.", ""]
    for case in report["cases"]:
        actual = case["actual"]
        lines += ["## Caz", "", _quoted(case["title"]), "",
                  f"Propunere LLM salvată: {case['before_eligibility']}. Propunere după reguli: {actual['suggested_eligibility']['status']}.", ""]
        for match in actual["matching"]["matches"]:
            lines += [_quoted(f"{match['requirement_id']}: {match['status']} — {', '.join(match['evidence_ids']) or 'fără dovezi concludente'}"), "",
                      _quoted(match["explanation"]), ""]
    return "\n".join(lines)


def main():
    report = run_saved_evaluation()
    directory = ROOT / "docs/evaluations"
    (directory / "structured_languages_001.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (directory / "structured_languages_001.md").write_text(render(report), encoding="utf-8")
    print(json.dumps({"case_count": report["case_count"], "passed_measured_checks": report["passed_measured_checks"],
                      "model_calls": 0, "decisions_applied": 0}, indent=2))
    return 0 if report["passed_measured_checks"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
