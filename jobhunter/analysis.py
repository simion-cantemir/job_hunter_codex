"""Draft-only analysis workflow: no persistence or automatic rejection."""

from dataclasses import asdict, dataclass

from jobhunter.ai_matching import MatchingResult, propose_matches
from jobhunter.eligibility import EligibilityDecision, evaluate_eligibility, source_digest
from jobhunter.ollama import ExtractionResult, extract_requirements
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.requirements import validate_requirements
from jobhunter.scoring import ScoreReport, score_requirements


@dataclass(frozen=True)
class AnalysisDraft:
    source_sha256: str
    profile_version: str
    extraction: ExtractionResult
    matching: MatchingResult
    provisional_score: ScoreReport
    suggested_eligibility: EligibilityDecision
    review_status: str = "pending_semantic_review"
    decision_applied: bool = False


def analyze_draft(source: str, profile_payload: object, *, timeout: float = 60) -> AnalysisDraft:
    # Validate curated input before spending resources on inference.
    profile = validate_profile(profile_payload)
    extraction = extract_requirements(source, timeout=timeout)
    requirements_payload = {"schema_version": "1", "requirements": [asdict(r) for r in extraction.requirements]}
    matching = propose_matches(source, requirements_payload, profile_payload, timeout=timeout)
    matches_payload = {"schema_version": "1", "profile_version": matching.profile_version,
                       "matches": [asdict(m) | {"evidence_ids": list(m.evidence_ids)} for m in matching.matches]}
    # Revalidate at the orchestration boundary; model-derived data is never trusted.
    requirements = validate_requirements(requirements_payload, source)
    matches = validate_matches(matches_payload, requirements, profile)
    score = score_requirements(requirements, matches)
    suggested = evaluate_eligibility(source, requirements_payload, profile_payload, matches_payload)
    return AnalysisDraft(source_digest(source), profile.version, extraction, matching, score, suggested)
