"""Validate extracted requirements against the original, unmodified job text."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Requirement:
    id: str
    priority: str
    quote: str
    start: int
    end: int


def validate_requirements(payload: object, source: str) -> tuple[Requirement, ...]:
    """Reject invalid output rather than guessing or repairing missing evidence.

    Offsets are Python string indexes (Unicode characters), end exclusive.
    This checks structure and provenance, not semantic correctness or completeness.
    """
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source must be a nonblank string.")
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "requirements"}:
        raise ValueError("Expected schema_version and requirements only.")
    if payload["schema_version"] != "1":
        raise ValueError("Unsupported schema version.")
    if not isinstance(payload["requirements"], list):
        raise ValueError("Requirements must be a list.")

    result = []
    seen = set()
    fields = {"id", "priority", "quote", "start", "end"}
    for item in payload["requirements"]:
        if not isinstance(item, dict) or set(item) != fields:
            raise ValueError("Each requirement must contain id, priority, quote, start, end only.")
        identifier, priority, quote = item["id"], item["priority"], item["quote"]
        start, end = item["start"], item["end"]
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen:
            raise ValueError("Requirement IDs must be nonblank, unique strings.")
        if not isinstance(priority, str) or priority not in {"mandatory", "optional", "unknown"}:
            raise ValueError("Invalid requirement priority.")
        if not isinstance(quote, str) or not quote.strip():
            raise ValueError("Evidence quote must be a nonblank string.")
        # bool is an int subclass, but is not a valid character offset.
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(source):
            raise ValueError("Invalid evidence offsets.")
        if source[start:end] != quote:
            raise ValueError("Evidence must exactly match the original source at its offsets.")
        seen.add(identifier)
        result.append(Requirement(identifier, priority, quote, start, end))
    return tuple(result)
