"""Apply the user's eligibility policy only after evidence validation."""

from dataclasses import dataclass
from hashlib import sha256

from jobhunter.matching import validate_matches, validate_profile
from jobhunter.requirements import validate_requirements


def source_digest(source: str) -> str:
    return sha256(source.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EligibilityReason:
    requirement_id: str | None
    code: str
    quote: str | None
    evidence_ids: tuple[str, ...]
    explanation: str


@dataclass(frozen=True)
class EligibilityDecision:
    policy_version: str
    profile_version: str
    source_sha256: str
    status: str
    reasons: tuple[EligibilityReason, ...]


def evaluate_eligibility(
    source: str, requirements_payload: object, profile_payload: object, matches_payload: object
) -> EligibilityDecision:
    """Return rejected, needs_review or eligible, independently of the score.

    Evidence structure is validated here. Semantic accuracy must still be reviewed;
    no model is called, and eligible is not a recommendation or an application.
    """
    requirements = validate_requirements(requirements_payload, source)
    profile = validate_profile(profile_payload)
    matches = validate_matches(matches_payload, requirements, profile)
    by_id = {match.requirement_id: match for match in matches}
    reasons = []
    rejected = False
    for requirement in requirements:
        match = by_id[requirement.id]
        if requirement.priority == "mandatory" and match.status == "confirmed_missing":
            rejected = True
            code = "mandatory_confirmed_missing"
        elif requirement.priority == "mandatory" and match.status in {"partial", "unknown"}:
            code = f"mandatory_{match.status}"
        elif requirement.priority == "unknown":
            code = "priority_unknown"
        else:
            continue
        reasons.append(EligibilityReason(requirement.id, code, requirement.quote,
                                         match.evidence_ids, match.explanation))
    if not requirements:
        reasons.append(EligibilityReason(None, "no_requirements", None, (),
                                         "Nu există cerințe extrase; eligibilitatea necesită revizuire."))
    status = "rejected" if rejected else "needs_review" if reasons else "eligible"
    return EligibilityDecision("1", profile.version, source_digest(source), status, tuple(reasons))
