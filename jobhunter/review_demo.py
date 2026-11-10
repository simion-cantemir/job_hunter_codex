"""Create a readable synthetic review report without inference or database changes."""

from dataclasses import asdict
import json
from pathlib import Path

from jobhunter.review import prepare_review, render_review


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    fixtures = root / "tests" / "fixtures"
    evaluation_dir = root / "docs" / "evaluations"
    report = json.loads((evaluation_dir / "ollama_analysis_001_run_001.json").read_text(encoding="utf-8"))
    source = (fixtures / "job_001.txt").read_text(encoding="utf-8")
    profile = json.loads((fixtures / "profile_001.json").read_text(encoding="utf-8"))
    original = prepare_review(report, source, profile)
    corrections = {"analysis_fingerprint": original.analysis_fingerprint, "changes": [{
        "requirement_id": "R2", "priority": "mandatory", "status": "partial", "evidence_ids": ["P2"],
        "explanation": "Profilul fictiv indică nivelul B1 și participarea actuală la cursuri de engleză. Nivelul profesional cerut nu este confirmat și necesită clarificare.",
        "note": "Propunere a agentului: corectează formularea nefirească și păstrează faptul că persoana participă deja la cursuri; nu presupune înscriere viitoare.",
    }]}
    material = prepare_review(report, source, profile, corrections)
    report_path = evaluation_dir / "review_001.md"
    report_path.write_text(render_review(material), encoding="utf-8")
    (evaluation_dir / "review_001.proposal.json").write_text(
        json.dumps(asdict(material), ensure_ascii=False, indent=2), encoding="utf-8")
    print("Raport fictiv creat: docs/evaluations/review_001.md")
    print("Corectia este propusa de agent, neaprobata. Nicio decizie aplicata in SQLite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
