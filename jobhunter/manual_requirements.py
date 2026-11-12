"""Explicit source-line selection; no guessed priority, rewriting or model call."""

from dataclasses import dataclass

from jobhunter.requirements import validate_requirements


@dataclass(frozen=True)
class SourceLine:
    start: int
    end: int
    text: str


def source_lines(source: str) -> tuple[SourceLine, ...]:
    result, offset = [], 0
    for line in source.splitlines(keepends=True):
        text = line.strip()
        if text:
            start = offset + len(line) - len(line.lstrip())
            result.append(SourceLine(start, start + len(text), text))
        offset += len(line)
    return tuple(result)


def select_requirements(source: str, selections: list[dict]) -> dict:
    lines = source_lines(source)
    if not isinstance(selections, list) or not 0 < len(selections) <= 100:
        raise ValueError("Selectează între 1 și 100 de cerințe din anunț.")
    rows, seen = [], set()
    for selection in selections:
        if not isinstance(selection, dict) or set(selection) != {"line_index", "priority"}:
            raise ValueError("Selecție de cerințe invalidă.")
        index = selection["line_index"]
        if type(index) is not int or not 0 <= index < len(lines) or index in seen:
            raise ValueError("Rând de cerință duplicat sau inexistent.")
        seen.add(index)
        line = lines[index]
        rows.append({"id": f"R{len(rows) + 1}", "priority": selection["priority"],
                     "quote": line.text, "start": line.start, "end": line.end})
    payload = {"schema_version": "1", "requirements": rows}
    validate_requirements(payload, source)
    return payload
