"""Deterministic scoring of validated matches; not a hiring probability."""

from dataclasses import dataclass
from math import isfinite

from jobhunter.matching import Match
from jobhunter.requirements import Requirement


@dataclass(frozen=True)
class ScoringRubric:
    version: str = "1"
    mandatory_weight: float = 2.0
    optional_weight: float = 1.0
    partial_credit: float = 0.5

    def __post_init__(self):
        if self.version != "1":
            raise ValueError("Unsupported scoring rubric version.")
        for weight in (self.mandatory_weight, self.optional_weight):
            if type(weight) not in (int, float) or not isfinite(weight) or weight <= 0:
                raise ValueError("Weights must be finite positive numbers.")
        if (type(self.partial_credit) not in (int, float)
                or not isfinite(self.partial_credit) or not 0 <= self.partial_credit <= 1):
            raise ValueError("Partial credit must be a finite number between zero and one.")


@dataclass(frozen=True)
class ScoreContribution:
    requirement_id: str
    priority: str
    status: str
    weight: float | None
    minimum_points: float | None
    maximum_points: float | None


@dataclass(frozen=True)
class ScoreWarning:
    requirement_id: str
    code: str


@dataclass(frozen=True)
class ScoreReport:
    rubric: ScoringRubric
    minimum_percent: float | None
    maximum_percent: float | None
    coverage_percent: float | None
    total_weight: float
    contributions: tuple[ScoreContribution, ...]
    warnings: tuple[ScoreWarning, ...]
    excluded_requirement_ids: tuple[str, ...]


def score_requirements(
    requirements: tuple[Requirement, ...],
    matches: tuple[Match, ...],
    rubric: ScoringRubric = ScoringRubric(),
) -> ScoreReport:
    """Calculate score bounds over requirements with known priority only.

    Inputs must first pass source/profile validation. This function checks
    correspondence and categories but cannot validate evidence without a profile.
    Unknown priorities are excluded explicitly, never assigned an assumed weight.
    Coverage measures resolved matching weight within the scored subset only.
    """
    requirement_ids = {r.id for r in requirements}
    by_id = {m.requirement_id: m for m in matches}
    if (len(requirement_ids) != len(requirements) or len(by_id) != len(matches)
            or requirement_ids != set(by_id)):
        raise ValueError("Expected exactly one match per unique requirement.")
    weights = {"mandatory": rubric.mandatory_weight, "optional": rubric.optional_weight}
    credits = {"supported": 1.0, "partial": rubric.partial_credit, "confirmed_missing": 0.0}
    contributions = []
    warnings = []
    excluded = []
    minimum = maximum = evaluated = total = 0.0
    for requirement in requirements:
        match = by_id[requirement.id]
        if requirement.priority not in {"mandatory", "optional", "unknown"}:
            raise ValueError("Invalid requirement priority.")
        if match.status not in {"supported", "partial", "confirmed_missing", "unknown"}:
            raise ValueError("Invalid match status.")
        if requirement.priority == "unknown":
            excluded.append(requirement.id)
            warnings.append(ScoreWarning(requirement.id, "priority_unknown_excluded"))
            contributions.append(ScoreContribution(requirement.id, requirement.priority, match.status, None, None, None))
            continue
        weight = weights[requirement.priority]
        if match.status == "unknown":
            low, high = 0.0, weight
        else:
            low = high = weight * credits[match.status]
            evaluated += weight
        if requirement.priority == "mandatory" and match.status != "supported":
            warnings.append(ScoreWarning(requirement.id, f"mandatory_{match.status}"))
        minimum += low
        maximum += high
        total += weight
        contributions.append(ScoreContribution(requirement.id, requirement.priority, match.status, weight, low, high))
    if not all(isfinite(value) for value in (minimum, maximum, evaluated, total)):
        raise ValueError("Scoring totals overflowed; use smaller weights.")
    return ScoreReport(
        rubric=rubric,
        minimum_percent=minimum / total * 100 if total else None,
        maximum_percent=maximum / total * 100 if total else None,
        coverage_percent=evaluated / total * 100 if total else None,
        total_weight=total,
        contributions=tuple(contributions),
        warnings=tuple(warnings),
        excluded_requirement_ids=tuple(excluded),
    )
