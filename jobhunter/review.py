"""Build human-readable review material and traceable, still-pending corrections."""

from copy import deepcopy
from dataclasses import asdict, dataclass
from hashlib import sha256
from html import escape
import json
import re

from jobhunter.eligibility import evaluate_eligibility, source_digest
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.requirements import validate_requirements
from jobhunter.scoring import score_requirements


@dataclass(frozen=True)
class ReviewMaterial:
    analysis_fingerprint: str
    source: str
    profile: dict
    original_requirements: dict
    original_matches: dict
    revised_requirements: dict
    revised_matches: dict
    changes: tuple[dict, ...]
    review_status: str = "pending_semantic_review"
    decision_applied: bool = False
    language_review: dict | None = None


def material_snapshot(material: ReviewMaterial) -> dict:
    """Preserve canonical legacy snapshots when no structured language data exists."""
    snapshot = asdict(material)
    if material.language_review is None:
        snapshot.pop("language_review")
    return snapshot


def prepare_review(report: object, source: str, profile_payload: object,
                   corrections: object = None) -> ReviewMaterial:
    """Corrections are proposals, not approval; never persist eligibility here.

    Fingerprint binds corrections to the exact saved report, source and supplied
    profile snapshot. It is an identity checksum, not a signature or proof of review.
    """
    profile = validate_profile(profile_payload)
    if (not isinstance(report, dict) or report.get("source_sha256") != source_digest(source)
            or report.get("profile_version") != profile.version
            or report.get("review_status") != "pending_semantic_review"
            or report.get("decision_applied") is not False):
        raise ValueError("Expected a pending report for this source and profile version.")
    try:
        req_payload = {"schema_version": "1", "requirements": deepcopy(report["extraction"]["requirements"])}
        match_payload = {"schema_version": "1", "profile_version": report["matching"]["profile_version"],
                         "matches": deepcopy(report["matching"]["matches"])}
    except (KeyError, TypeError):
        raise ValueError("Invalid saved analysis structure.") from None
    requirements = validate_requirements(req_payload, source)
    validate_matches(match_payload, requirements, profile)
    try:
        canonical = json.dumps({"report": report, "source": source, "profile": profile_payload},
                               sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError):
        raise ValueError("Review inputs must be finite JSON data.") from None
    fingerprint = sha256(canonical.encode("utf-8")).hexdigest()
    revised_req, revised_matches = deepcopy(req_payload), deepcopy(match_payload)
    changes = []
    if corrections is not None:
        if (not isinstance(corrections, dict)
                or set(corrections) != {"analysis_fingerprint", "changes"}
                or corrections["analysis_fingerprint"] != fingerprint
                or not isinstance(corrections["changes"], list)):
            raise ValueError("Corrections must target this exact analysis fingerprint.")
        requirements_by_id = {r["id"]: r for r in revised_req["requirements"]}
        matches_by_id = {m["requirement_id"]: m for m in revised_matches["matches"]}
        seen = set()
        for change in corrections["changes"]:
            fields = {"requirement_id", "priority", "status", "evidence_ids", "explanation", "note"}
            if not isinstance(change, dict) or set(change) != fields:
                raise ValueError("Invalid correction fields.")
            identifier = change["requirement_id"]
            if (not isinstance(identifier, str) or identifier not in requirements_by_id or identifier in seen
                    or not isinstance(change["note"], str) or not change["note"].strip()):
                raise ValueError("Correction needs a unique existing requirement and a review note.")
            before = {"priority": requirements_by_id[identifier]["priority"], **deepcopy(matches_by_id[identifier])}
            requirements_by_id[identifier]["priority"] = change["priority"]
            matches_by_id[identifier].update({key: deepcopy(change[key]) for key in
                                             ("status", "evidence_ids", "explanation")})
            after = {"priority": change["priority"], **deepcopy(matches_by_id[identifier])}
            changes.append({"requirement_id": identifier, "before": before, "after": after, "note": change["note"]})
            seen.add(identifier)
        revised = validate_requirements(revised_req, source)
        validate_matches(revised_matches, revised, profile)
    return ReviewMaterial(fingerprint, source, deepcopy(profile_payload), req_payload, match_payload,
                          revised_req, revised_matches, tuple(changes))


def _quoted(text: str) -> str:
    # Escape external data so it remains inert text in a Markdown renderer.
    safe = re.sub(r"([\\`*_{}\[\]()#+.!|>~\-])", r"\\\1", escape(text, quote=False))
    return "\n".join("> " + line for line in safe.splitlines())


def render_review(material: ReviewMaterial) -> str:
    from jobhunter.languages import verify_language_review
    verify_language_review(material)
    profile = validate_profile(material.profile)
    requirements = validate_requirements(material.revised_requirements, material.source)
    matches = validate_matches(material.revised_matches, requirements, profile)
    score = score_requirements(requirements, matches)
    suggested = evaluate_eligibility(material.source, material.revised_requirements,
                                     material.profile, material.revised_matches)
    original_req = {r["id"]: r for r in material.original_requirements["requirements"]}
    original_matches = {m["requirement_id"]: m for m in material.original_matches["matches"]}
    facts = {f.id: f for f in profile.facts}
    labels = {"mandatory": "Obligatorie", "optional": "Opțională", "unknown": "Necunoscută",
              "supported": "Susținută", "partial": "Parțială", "confirmed_missing": "Lipsă confirmată"}
    eligibility = {"rejected": "Respingere propusă", "needs_review": "Necesită clarificare", "eligible": "Fără blocaj identificat"}
    interval = ("Indisponibil" if score.minimum_percent is None
                else f"{score.minimum_percent:.1f}–{score.maximum_percent:.1f}%")
    coverage = "Indisponibilă" if score.coverage_percent is None else f"{score.coverage_percent:.1f}%"
    lines = ["# Raport de revizuire — analiză provizorie", "",
             "**În așteptarea revizuirii semantice. Nicio decizie aplicată.**", "",
             "Modificările de mai jos sunt propuneri de revizuire, neaprobate în acest material.", "",
             f"Identitatea analizei: `{material.analysis_fingerprint}`", "",
             f"Scor provizoriu: **{interval}**, numai pentru cerințele cu prioritate cunoscută.", "",
             f"Acoperirea acelui subset: {coverage}. Excluderi din scor: {len(score.excluded_requirement_ids)}.", "",
             f"Eligibilitate propusă: **{eligibility[suggested.status]}**.", "",
             "Verifică și textul integral: citatele valide nu demonstrează că extragerea este completă.", ""]
    matches_by_id = {m.requirement_id: m for m in matches}
    for requirement in requirements:
        match = matches_by_id[requirement.id]
        old = original_matches[requirement.id]
        lines += ["## Cerință", "", _quoted(requirement.id), "", "Citat exact din job:", "", _quoted(requirement.quote), "",
                  f"Prioritate originală: {labels[original_req[requirement.id]['priority']]}. Prioritate propusă: {labels[requirement.priority]}.", "",
                  f"Matching original: {labels[old['status']]}. Matching propus: {labels[match.status]}.", "",
                  "Explicația originală a modelului, păstrată fără corectare:", "", _quoted(old["explanation"]), "",
                  "Dovezile citate de model, text exact din profil:", ""]
        for ref in old["evidence_ids"]:
            lines += [_quoted(f"{ref}: {facts[ref].text}"), ""]
        if not old["evidence_ids"]:
            lines += ["Fără dovezi concludente citate; informația rămâne necunoscută.", ""]
        if any(c["requirement_id"] == requirement.id for c in material.changes):
            change = next(c for c in material.changes if c["requirement_id"] == requirement.id)
            lines += ["**Corecție propusă — neaprobată:**", "", _quoted(match.explanation), "",
                      "Dovezi pentru propunere:", ""]
            for ref in match.evidence_ids:
                lines += [_quoted(f"{ref}: {facts[ref].text}"), ""]
            if not match.evidence_ids:
                lines += ["Fără dovezi concludente în propunere.", ""]
            lines += ["Motivul corecției:", "", _quoted(change["note"]), ""]
    lines += ["## Jobul integral — sursa revizuirii", "", _quoted(material.source), "",
              "## Profilul integral folosit la revizuire", "", _quoted(profile.version), ""]
    for fact in profile.facts:
        lines += [_quoted(f"{fact.id} ({fact.kind}): {fact.text}"), ""]
    if profile.provenance is not None:
        lines += ["## Trasabilitatea profilului master", "",
                  "Faptele provin din blocurile de text revizuite ale CV-ului local; documentul original este păstrat în stocarea privată.", ""]
        for citation in profile.provenance["citations"]:
            lines += [_quoted(f"{citation['fact_id']}: {citation['label']} · caractere {citation['start']}–{citation['end']}"), "",
                      _quoted(citation["quote"]), ""]
    if material.language_review is not None:
        lines += ["## Adnotări explicite pentru limbile evaluate în Python", "",
                  "Aceste asocieri și niveluri trebuie verificate de reviewer; nu sunt extrase automat sau aprobate implicit.", "",
                  _quoted(json.dumps(material.language_review, ensure_ascii=False, indent=2)), ""]
    lines += ["## Ce rămâne de verificat", "",
              "- Extragerea a omis cerințe sau a separat greșit alternativele?",
              "- Prioritățile și statusurile sunt justificate de sursele afișate?",
              "- Explicațiile păstrează exact sensul profilului?",
              "- Fiecare corecție trebuie revizuită înainte de aplicarea eligibilității.", "",
              "Acest raport nu aprobă analiza și nu modifică oportunitățile din SQLite.", ""]
    return "\n".join(lines)
