"""Deterministic language matching over explicit, reviewable annotations.

This is not a natural-language parser or CEFR conversion table. Language mentions
only guard against unrelated evidence; a reviewer must validate the annotations.
"""

from copy import deepcopy
from dataclasses import asdict, replace
import re
import unicodedata

from jobhunter.matching import Match, validate_matches, validate_profile
from jobhunter.requirements import validate_requirements


LANGUAGES = {"en": "Engleză", "de": "Germană", "fr": "Franceză", "es": "Spaniolă", "ro": "Română", "it": "Italiană"}
LEVELS = {"unknown": "Necunoscut", "none": "Lipsă declarată explicit", "basic": "Cunoștințe de bază",
          "professional": "Nivel profesional confirmat", "fluent": "Fluent confirmat"}
MINIMUMS = {"unspecified": "De clarificat", "basic": "De bază", "professional": "Profesional", "fluent": "Fluent"}
RANK = {"none": 0, "basic": 1, "professional": 2, "fluent": 3}
ALIASES = {"en": {"english", "engleza", "engleze"}, "de": {"german", "germana", "germane"},
           "fr": {"french", "franceza", "franceze"}, "es": {"spanish", "spaniola", "spaniole"},
           "ro": {"romanian", "romana", "romane"}, "it": {"italian", "italiana", "italiene"}}


def _words(text: str) -> set[str]:
    normalized = "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))
    return set(re.findall(r"[a-z]+", normalized))


def mentioned_languages(text: str) -> tuple[str, ...]:
    words = _words(text)
    return tuple(code for code in LANGUAGES if words & ALIASES[code])


def validate_language_review(payload: object, requirements, profile):
    if (not isinstance(payload, dict) or set(payload) != {"schema_version", "abilities", "rules"}
            or payload["schema_version"] != "1" or not isinstance(payload["abilities"], list)
            or not isinstance(payload["rules"], list)):
        raise ValueError("Invalid structured language review.")
    facts = {f.id: f for f in profile.facts}
    abilities = {}
    for ability in payload["abilities"]:
        if not isinstance(ability, dict) or set(ability) != {"language", "level", "evidence_ids"}:
            raise ValueError("Invalid language ability fields.")
        code, level, refs = ability["language"], ability["level"], ability["evidence_ids"]
        if not isinstance(code, str) or code not in LANGUAGES or code in abilities:
            raise ValueError("Language abilities must use unique supported language codes.")
        if not isinstance(level, str) or level not in LEVELS:
            raise ValueError("Invalid language level.")
        if (not isinstance(refs, list) or any(not isinstance(ref, str) or ref not in facts for ref in refs)
                or len(set(refs)) != len(refs)):
            raise ValueError("Invalid language evidence IDs.")
        if level == "unknown":
            if refs:
                raise ValueError("Unknown language level must not claim conclusive evidence.")
        else:
            expected_kind = "confirmed_gap" if level == "none" else "experience"
            if not refs or any(facts[ref].kind != expected_kind for ref in refs):
                raise ValueError("Language level requires explicit evidence of the appropriate kind.")
            if any(code not in mentioned_languages(facts[ref].text) for ref in refs):
                raise ValueError("Dovada citată nu numește limba evaluată; nu folosim o altă limbă drept dovadă.")
        abilities[code] = ability
    requirements_by_id = {r.id: r for r in requirements}
    seen = set()
    for rule in payload["rules"]:
        if not isinstance(rule, dict) or set(rule) != {"requirement_id", "operator", "languages", "minimum"}:
            raise ValueError("Invalid language rule fields.")
        identifier, operator, codes, minimum = rule["requirement_id"], rule["operator"], rule["languages"], rule["minimum"]
        if not isinstance(identifier, str) or identifier not in requirements_by_id or identifier in seen:
            raise ValueError("Language rule needs a unique existing requirement ID.")
        if not isinstance(operator, str) or operator not in {"all", "any", "unclear"}:
            raise ValueError("Invalid language operator.")
        if not isinstance(minimum, str) or minimum not in MINIMUMS:
            raise ValueError("Invalid minimum language level.")
        if (not isinstance(codes, list) or any(not isinstance(code, str) or code not in LANGUAGES for code in codes)
                or len(set(codes)) != len(codes)):
            raise ValueError("Invalid languages in requirement.")
        mentioned = set(mentioned_languages(requirements_by_id[identifier].quote))
        if set(codes) != mentioned:
            raise ValueError("Lista limbilor trebuie să corespundă citatului; nu omite o limbă dintr-o condiție combinată.")
        if operator != "unclear" and not codes:
            raise ValueError("Cerința nu conține o limbă recunoscută; păstrează condiția de clarificat.")
        # Avoid flattening nested/mixed logical expressions into one simple operator.
        words = _words(requirements_by_id[identifier].quote)
        if operator != "unclear" and words & {"or", "sau"} and words & {"and", "și", "si"}:
            raise ValueError("Condiție mixtă OR/AND: necesită clarificare, fără simplificare automată.")
        if len(codes) > 1 and operator == "all" and words & {"or", "sau"}:
            raise ValueError("Citatul conține OR; nu îl transforma în AND.")
        if len(codes) > 1 and operator == "any" and words & {"and", "si"}:
            raise ValueError("Citatul conține AND; nu îl transforma în OR.")
        seen.add(identifier)
    return abilities


def evaluate_languages(payload: dict, requirements, profile) -> tuple[Match, ...]:
    abilities = validate_language_review(payload, requirements, profile)
    results = []
    for rule in payload["rules"]:
        identifier, minimum, operator = rule["requirement_id"], rule["minimum"], rule["operator"]
        branches = []
        for code in rule["languages"]:
            ability = abilities.get(code, {"language": code, "level": "unknown", "evidence_ids": []})
            level = ability["level"]
            status = ("unknown" if level == "unknown" else "confirmed_missing" if level == "none"
                      else "supported" if minimum != "unspecified" and RANK[level] >= RANK[minimum] else "partial")
            branches.append((code, status, ability))
        if operator == "unclear" or minimum == "unspecified" or not branches:
            status, selected = "unknown", []
        elif operator == "any":
            supported = [b for b in branches if b[1] == "supported"]
            if supported:
                status, selected = "supported", supported[:1]
            elif any(b[1] == "unknown" for b in branches):
                status, selected = "unknown", []
            elif any(b[1] == "partial" for b in branches):
                status, selected = "partial", [b for b in branches if b[1] == "partial"]
            else:
                status, selected = "confirmed_missing", branches
        else:
            missing = [b for b in branches if b[1] == "confirmed_missing"]
            if missing:
                status, selected = "confirmed_missing", missing
            elif any(b[1] == "unknown" for b in branches):
                status, selected = "unknown", []
            else:
                status = "partial" if any(b[1] == "partial" for b in branches) else "supported"
                selected = branches
        refs = tuple(dict.fromkeys(ref for branch in selected for ref in branch[2]["evidence_ids"]))
        descriptions = "; ".join(f"{LANGUAGES[code]}: {LEVELS[ability['level']]}" for code, _, ability in branches)
        conclusion = {"supported": "Cerința este susținută de dovezile indicate.",
                      "partial": "Există cunoștințe relevante, dar nivelul cerut nu este confirmat integral.",
                      "confirmed_missing": "Lipsa declarată explicit împiedică satisfacerea acestei condiții.",
                      "unknown": "Informațiile sau condiția sunt neclare; necesită clarificare, fără a presupune o lipsă."}[status]
        explanation = f"Evaluare deterministă pe date structurate. {descriptions or 'Limbă neidentificată'}. {conclusion}"
        results.append(Match(identifier, status, refs, explanation))
    return tuple(results)


def apply_language_review(material, payload: dict):
    """Return a pending material with computed corrections and the full rule snapshot."""
    requirements = validate_requirements(material.revised_requirements, material.source)
    profile = validate_profile(material.profile)
    overrides = {m.requirement_id: m for m in evaluate_languages(payload, requirements, profile)}
    revised_matches = deepcopy(material.revised_matches)
    for match in revised_matches["matches"]:
        if match["requirement_id"] in overrides:
            replacement = overrides[match["requirement_id"]]
            match.update(asdict(replacement) | {"evidence_ids": list(replacement.evidence_ids)})
    validate_matches(revised_matches, requirements, profile)
    original_req = {r["id"]: r for r in material.original_requirements["requirements"]}
    original_matches = {m["requirement_id"]: m for m in material.original_matches["matches"]}
    notes = {c["requirement_id"]: c["note"] for c in material.changes}
    new_matches = {m["requirement_id"]: m for m in revised_matches["matches"]}
    changes = []
    for requirement in material.revised_requirements["requirements"]:
        identifier = requirement["id"]
        before = {"priority": original_req[identifier]["priority"], **original_matches[identifier]}
        after = {"priority": requirement["priority"], **new_matches[identifier]}
        if before != after or identifier in overrides or identifier in notes:
            note = notes.get(identifier, "")
            if identifier in overrides:
                note = (note + " Evaluare deterministă a limbilor din adnotările explicite; necesită confirmarea reviewerului.").strip()
            changes.append({"requirement_id": identifier, "before": deepcopy(before), "after": deepcopy(after), "note": note})
    return replace(material, revised_matches=revised_matches, changes=tuple(changes), language_review=deepcopy(payload))


def verify_language_review(material) -> None:
    if material.language_review is None:
        return
    requirements = validate_requirements(material.revised_requirements, material.source)
    profile = validate_profile(material.profile)
    computed = evaluate_languages(material.language_review, requirements, profile)
    actual = {m["requirement_id"]: m for m in material.revised_matches["matches"]}
    for match in computed:
        expected = asdict(match) | {"evidence_ids": list(match.evidence_ids)}
        if actual[match.requirement_id] != expected:
            raise ValueError("Rezultatul revizuit nu corespunde regulilor de limbă atașate.")
