"""Explicit review receipts bound to exact original and corrected snapshots."""

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json

from jobhunter.eligibility import EligibilityDecision, evaluate_eligibility
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.requirements import validate_requirements
from jobhunter.review import ReviewMaterial, material_snapshot
from jobhunter.languages import verify_language_review
from jobhunter.scoring import ScoreReport, score_requirements


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _validate_material(material: ReviewMaterial) -> None:
    if not isinstance(material, ReviewMaterial):
        raise ValueError("Expected review material, not an analysis draft or decision.")
    if material.review_status != "pending_semantic_review" or material.decision_applied is not False:
        raise ValueError("Expected pending review material.")
    if (not isinstance(material.analysis_fingerprint, str) or len(material.analysis_fingerprint) != 64
            or any(c not in "0123456789abcdef" for c in material.analysis_fingerprint)):
        raise ValueError("Invalid original analysis fingerprint.")
    profile = validate_profile(material.profile)
    original = validate_requirements(material.original_requirements, material.source)
    validate_matches(material.original_matches, original, profile)
    revised = validate_requirements(material.revised_requirements, material.source)
    validate_matches(material.revised_matches, revised, profile)
    # Rebuild the revisions from the recorded changes to verify audit consistency.
    req = deepcopy(material.original_requirements)
    matches = deepcopy(material.original_matches)
    req_by_id = {r["id"]: r for r in req["requirements"]}
    match_by_id = {m["requirement_id"]: m for m in matches["matches"]}
    seen = set()
    for change in material.changes:
        if not isinstance(change, dict) or set(change) != {"requirement_id", "before", "after", "note"}:
            raise ValueError("Invalid change history.")
        identifier = change["requirement_id"]
        if (not isinstance(identifier, str) or identifier not in req_by_id or identifier in seen
                or not isinstance(change["note"], str) or not change["note"].strip()):
            raise ValueError("Invalid change identity or note.")
        before = {"priority": req_by_id[identifier]["priority"], **match_by_id[identifier]}
        if change["before"] != before:
            raise ValueError("Change history does not match the original values.")
        after = change["after"]
        if not isinstance(after, dict) or set(after) != set(before) or after["requirement_id"] != identifier:
            raise ValueError("Invalid corrected values.")
        req_by_id[identifier]["priority"] = after["priority"]
        match_by_id[identifier].update({key: deepcopy(after[key]) for key in
                                       ("status", "evidence_ids", "explanation")})
        seen.add(identifier)
    if req != material.revised_requirements or matches != material.revised_matches:
        raise ValueError("Revisions are not fully described by the change history.")
    verify_language_review(material)


def review_fingerprint(material: ReviewMaterial) -> str:
    """Identity of the reviewed data and calculated scoring/policy outcome."""
    _validate_material(material)
    decision, score = _outcome(material)
    snapshot = {"material": material_snapshot(material), "decision": asdict(decision), "score": asdict(score)}
    return sha256(_canonical(snapshot).encode("utf-8")).hexdigest()


def _outcome(material: ReviewMaterial) -> tuple[EligibilityDecision, ScoreReport]:
    profile = validate_profile(material.profile)
    requirements = validate_requirements(material.revised_requirements, material.source)
    matches = validate_matches(material.revised_matches, requirements, profile)
    return (evaluate_eligibility(material.source, material.revised_requirements,
                                 material.profile, material.revised_matches),
            score_requirements(requirements, matches))


@dataclass(frozen=True)
class ReviewApproval:
    review_fingerprint: str
    reviewer: str
    note: str
    approved_at: str
    snapshot_json: str
    outcome_json: str


def approve_review(material: ReviewMaterial, *, expected_fingerprint: str,
                   reviewer: str, note: str, confirmed: bool) -> ReviewApproval:
    """Call only after explicit review; a caller-supplied name is not authentication."""
    if confirmed is not True:
        raise ValueError("Explicit confirmation is required.")
    if not isinstance(reviewer, str) or not reviewer.strip() or not isinstance(note, str) or not note.strip():
        raise ValueError("Reviewer and review note must be nonblank.")
    fingerprint = review_fingerprint(material)
    if expected_fingerprint != fingerprint:
        raise ValueError("Review material changed; review the current version before approval.")
    decision, score = _outcome(material)
    return ReviewApproval(fingerprint, reviewer.strip(), note.strip(),
                          datetime.now(timezone.utc).isoformat(), _canonical(material_snapshot(material)),
                          _canonical({"decision": asdict(decision), "score": asdict(score)}))


def verify_approval(material: ReviewMaterial, approval: ReviewApproval
                    ) -> tuple[EligibilityDecision, ScoreReport]:
    if not isinstance(approval, ReviewApproval):
        raise ValueError("A draft or proposal is not a review approval.")
    if (not isinstance(approval.reviewer, str) or not approval.reviewer.strip()
            or not isinstance(approval.note, str) or not approval.note.strip()):
        raise ValueError("Invalid reviewer or review note.")
    try:
        timestamp = datetime.fromisoformat(approval.approved_at)
        if timestamp.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone.")
    except (ValueError, TypeError):
        raise ValueError("Invalid approval timestamp.") from None
    fingerprint = review_fingerprint(material)
    if approval.review_fingerprint != fingerprint or approval.snapshot_json != _canonical(material_snapshot(material)):
        raise ValueError("Approval does not match the current review snapshot.")
    decision, score = _outcome(material)
    if approval.outcome_json != _canonical({"decision": asdict(decision), "score": asdict(score)}):
        raise ValueError("Approved scoring or policy outcome changed; a new review is required.")
    return decision, score
