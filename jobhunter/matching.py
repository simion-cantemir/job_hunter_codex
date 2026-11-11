"""Validate proposed matches against curated profile facts, without AI inference."""

from dataclasses import dataclass

from jobhunter.requirements import Requirement


@dataclass(frozen=True)
class ProfileFact:
    id: str
    kind: str
    text: str


@dataclass(frozen=True)
class Profile:
    version: str
    facts: tuple[ProfileFact, ...]
    provenance: dict | None = None


@dataclass(frozen=True)
class Match:
    requirement_id: str
    status: str
    evidence_ids: tuple[str, ...]
    explanation: str


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_profile(payload: object) -> Profile:
    """Check curated profile data; this cannot verify autobiographical truth.

    A real profile must be reviewed against the master CV by the user.
    confirmed_gap is an explicit statement, never inferred from missing facts.
    """
    if not isinstance(payload, dict) or set(payload) not in ({"version", "facts"}, {"version", "facts", "provenance"}):
        raise ValueError("Expected profile version and facts only.")
    if not _nonblank(payload["version"]) or not isinstance(payload["facts"], list):
        raise ValueError("Invalid profile version or facts.")
    facts = []
    seen = set()
    for fact in payload["facts"]:
        if not isinstance(fact, dict) or set(fact) != {"id", "kind", "text"}:
            raise ValueError("Expected fact id, kind and text only.")
        identifier, kind, text = fact["id"], fact["kind"], fact["text"]
        if not _nonblank(identifier) or identifier in seen or not _nonblank(text):
            raise ValueError("Fact IDs must be unique and fact text must be nonblank.")
        if not isinstance(kind, str) or kind not in {"experience", "confirmed_gap"}:
            raise ValueError("Invalid profile fact kind.")
        seen.add(identifier)
        facts.append(ProfileFact(identifier, kind, text))
    if "provenance" in payload:
        from jobhunter.master_profile import validate_provenance
        validate_provenance(payload)
    return Profile(payload["version"], tuple(facts), payload.get("provenance"))


def validate_matches(
    payload: object, requirements: tuple[Requirement, ...], profile: Profile
) -> tuple[Match, ...]:
    """Require complete coverage and valid evidence references.

    Use validated requirements and a validated, curated profile as inputs.
    This validates traceability, not whether an explanation is semantically true.
    """
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "profile_version", "matches"}:
        raise ValueError("Expected schema_version, profile_version and matches only.")
    if payload["schema_version"] != "1" or payload["profile_version"] != profile.version:
        raise ValueError("Unsupported match schema or mismatched profile version.")
    if not isinstance(payload["matches"], list):
        raise ValueError("Matches must be a list.")
    required_ids = {r.id for r in requirements}
    if len(required_ids) != len(requirements):
        raise ValueError("Requirement IDs must be unique.")
    facts = {fact.id: fact for fact in profile.facts}
    result = []
    seen = set()
    for item in payload["matches"]:
        if not isinstance(item, dict) or set(item) != {"requirement_id", "status", "evidence_ids", "explanation"}:
            raise ValueError("Invalid match fields.")
        identifier, status = item["requirement_id"], item["status"]
        evidence, explanation = item["evidence_ids"], item["explanation"]
        if not _nonblank(identifier) or identifier not in required_ids or identifier in seen:
            raise ValueError("Unknown or duplicate requirement ID.")
        if not isinstance(status, str) or status not in {"supported", "partial", "confirmed_missing", "unknown"}:
            raise ValueError("Invalid match status.")
        if not _nonblank(explanation):
            raise ValueError("Every match needs a nonblank explanation.")
        if not isinstance(evidence, list) or any(not _nonblank(ref) for ref in evidence):
            raise ValueError("Evidence IDs must be a list of nonblank strings.")
        if len(set(evidence)) != len(evidence) or any(ref not in facts for ref in evidence):
            raise ValueError("Unknown or duplicate profile evidence ID.")
        if status == "unknown":
            if evidence:
                raise ValueError("Unknown matches use no conclusive evidence in schema 1.")
        else:
            if not evidence:
                raise ValueError("A non-unknown status requires profile evidence.")
            expected_kind = "confirmed_gap" if status == "confirmed_missing" else "experience"
            if any(facts[ref].kind != expected_kind for ref in evidence):
                raise ValueError("Evidence kind does not support the proposed status.")
        seen.add(identifier)
        result.append(Match(identifier, status, tuple(evidence), explanation))
    if seen != required_ids:
        raise ValueError("Every requirement needs a match, including unknowns.")
    return tuple(result)
