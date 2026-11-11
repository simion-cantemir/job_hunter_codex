"""UI workflow state independent of Streamlit widgets."""

from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha256
import json

from jobhunter.approval import ReviewApproval, approve_review, review_fingerprint
from jobhunter.review import ReviewMaterial, prepare_review
from jobhunter.languages import apply_language_review
from jobhunter.storage import JobRepository


def input_fingerprint(title: str, source: str, profile: dict) -> str:
    text = json.dumps({"title": title, "source": source, "profile": profile}, sort_keys=True,
                      ensure_ascii=False, allow_nan=False)
    return sha256(text.encode("utf-8")).hexdigest()


@dataclass
class ReviewSession:
    inputs: str | None = None
    report: dict | None = None
    changes: list = field(default_factory=list)
    approval: ReviewApproval | None = None
    job_id: int | None = None
    applied_decision_id: int | None = None
    epoch: int = 0
    revision: int = 0
    language_review: dict | None = None

    def sync_inputs(self, title: str, source: str, profile: dict) -> bool:
        current = input_fingerprint(title, source, profile)
        if current == self.inputs:
            return False
        self.inputs = current
        self.report = None
        self.changes = []
        self.language_review = None
        self.approval = None
        self.job_id = None
        self.applied_decision_id = None
        self.epoch += 1
        self.revision += 1
        return True

    def load_report(self, report: dict, title: str, source: str, profile: dict) -> None:
        prepare_review(report, source, profile)
        self.sync_inputs(title, source, profile)
        self.report = deepcopy(report)
        self.changes = []
        self.language_review = None
        self.approval = None
        self.applied_decision_id = None
        self.epoch += 1
        self.revision += 1

    def set_changes(self, changes: list) -> None:
        if changes != self.changes:
            self.changes = deepcopy(changes)
            self.approval = None
            self.applied_decision_id = None
            self.revision += 1

    def material(self, title: str, source: str, profile: dict) -> ReviewMaterial:
        if self.report is None or self.inputs != input_fingerprint(title, source, profile):
            raise ValueError("Datele s-au schimbat. Generează și revizuiește o analiză nouă.")
        original = prepare_review(self.report, source, profile)
        material = prepare_review(self.report, source, profile, {
            "analysis_fingerprint": original.analysis_fingerprint, "changes": self.changes,
        })
        return material if self.language_review is None else apply_language_review(material, self.language_review)

    def set_language_review(self, payload: dict | None) -> None:
        if payload != self.language_review:
            self.language_review = deepcopy(payload)
            self.approval = None
            self.applied_decision_id = None
            self.revision += 1

    def apply(self, repository: JobRepository, title: str, source: str, profile: dict, *,
              expected_fingerprint: str, reviewer: str, note: str, confirmed: bool) -> int:
        material = self.material(title, source, profile)
        if review_fingerprint(material) != expected_fingerprint:
            raise ValueError("Revizuirea s-a schimbat. Confirmă materialul actual.")
        if self.approval is None:
            self.approval = approve_review(material, expected_fingerprint=expected_fingerprint,
                                           reviewer=reviewer, note=note, confirmed=confirmed)
        else:
            # Confirmation is required even when replaying a failed application.
            if confirmed is not True or reviewer.strip() != self.approval.reviewer or note.strip() != self.approval.note:
                raise ValueError("Reaplicarea cere aceeași confirmare, identitate și notă.")
        if self.job_id is None:
            self.job_id = repository.add(title, source)
        self.applied_decision_id = repository.apply_approved_review(self.job_id, material, self.approval)
        return self.applied_decision_id
