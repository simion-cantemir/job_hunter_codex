"""Source-cited master profiles, explicitly approved and stored only locally."""

from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

from jobhunter.cv_import import CVDocument, import_cv


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def _content(source_id, facts, citations):
    return {"source_id": source_id, "facts": facts, "citations": citations}


@dataclass(frozen=True)
class MasterDraft:
    document: CVDocument
    profile: dict
    citations: tuple[dict, ...]
    fingerprint: str


def prepare_master(document: CVDocument, selections: list[dict]) -> MasterDraft:
    if not isinstance(document, CVDocument) or not isinstance(selections, list) or not 0 < len(selections) <= 100:
        raise ValueError("Selectează între 1 și 100 de blocuri din CV.")
    if sha256(document.text.encode("utf-8")).hexdigest() != document.text_sha256:
        raise ValueError("Textul extras nu corespunde amprentei documentului.")
    facts, citations, seen = [], [], set()
    for selection in selections:
        if not isinstance(selection, dict) or set(selection) != {"block_index", "kind"}:
            raise ValueError("Selecție invalidă de fapt profesional.")
        index, kind = selection["block_index"], selection["kind"]
        if type(index) is not int or not 0 <= index < len(document.blocks) or index in seen or not isinstance(kind, str) or kind not in {"experience", "confirmed_gap"}:
            raise ValueError("Bloc duplicat, inexistent sau tip de fapt invalid.")
        seen.add(index)
        block = document.blocks[index]
        if document.text[block.start:block.end] != block.text:
            raise ValueError("Blocul nu corespunde sursei extrase.")
        identifier = f"F{len(facts) + 1}"
        facts.append({"id": identifier, "kind": kind, "text": block.text})
        citations.append({"fact_id": identifier, "start": block.start, "end": block.end, "quote": block.text, "label": block.label})
    source_id = document.file_sha256 + "-" + document.text_sha256
    profile_digest = _digest(_content(source_id, facts, citations))
    profile = {"version": "master-" + profile_digest, "facts": facts}
    fingerprint = _digest({"document": asdict(document), "profile": profile, "citations": citations})
    return MasterDraft(document, profile, tuple(citations), fingerprint)


def approve_master(draft: MasterDraft, *, expected_fingerprint: str, reviewer: str, note: str, confirmed: bool) -> dict:
    if confirmed is not True or not isinstance(reviewer, str) or not reviewer.strip() or not isinstance(note, str) or not note.strip():
        raise ValueError("Confirmarea explicită, numele reviewerului și nota sunt obligatorii.")
    selections = []
    for fact, citation in zip(draft.profile["facts"], draft.citations):
        index = next((i for i, b in enumerate(draft.document.blocks)
                      if (b.start, b.end, b.text, b.label) == (citation["start"], citation["end"], citation["quote"], citation["label"])), None)
        if index is None:
            raise ValueError("Citat fără bloc sursă corespunzător.")
        selections.append({"block_index": index, "kind": fact["kind"]})
    rebuilt = prepare_master(draft.document, selections)
    if rebuilt != draft or draft.fingerprint != expected_fingerprint:
        raise ValueError("Profilul a fost modificat. Revizuiește selecția curentă înainte de confirmare.")
    provenance = {"source_id": draft.document.file_sha256 + "-" + draft.document.text_sha256,
                  "file_sha256": draft.document.file_sha256, "text_sha256": draft.document.text_sha256,
                  "citations": list(draft.citations), "reviewer": reviewer.strip(), "review_note": note.strip(),
                  "approved_at": datetime.now(timezone.utc).isoformat(), "importer_version": draft.document.importer_version}
    result = {**draft.profile, "provenance": provenance}
    validate_provenance(result)
    return result


def validate_provenance(profile: dict) -> None:
    value = profile["provenance"]
    fields = {"source_id", "file_sha256", "text_sha256", "citations", "reviewer", "review_note", "approved_at", "importer_version"}
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("Invalid profile provenance.")
    for key in ("file_sha256", "text_sha256"):
        digest = value[key]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid CV source fingerprint.")
    if value["source_id"] != value["file_sha256"] + "-" + value["text_sha256"]:
        raise ValueError("Profile source identity mismatch.")
    if any(not isinstance(value[key], str) or not value[key].strip() for key in ("reviewer", "review_note", "importer_version")):
        raise ValueError("Profile review metadata must be nonblank.")
    try:
        if datetime.fromisoformat(value["approved_at"]).utcoffset() is None:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("Invalid profile review timestamp.") from None
    citations = value["citations"]
    if not isinstance(citations, list) or len(citations) != len(profile["facts"]):
        raise ValueError("Each master fact needs one source citation.")
    for fact, citation in zip(profile["facts"], citations):
        if not isinstance(citation, dict) or set(citation) != {"fact_id", "start", "end", "quote", "label"}:
            raise ValueError("Invalid fact citation fields.")
        start, end = citation["start"], citation["end"]
        if (citation["fact_id"] != fact["id"] or citation["quote"] != fact["text"]
                or type(start) is not int or type(end) is not int or start < 0 or end - start != len(fact["text"])
                or not isinstance(citation["label"], str) or not citation["label"].strip()):
            raise ValueError("Profile fact does not match its source citation.")
    if profile["version"] != "master-" + _digest(_content(value["source_id"], profile["facts"], citations)):
        raise ValueError("Master profile content changed; a new reviewed version is required.")


class MasterProfileStore:
    def __init__(self, path: Path):
        self.path = path
        with closing(sqlite3.connect(path)) as connection:
            with connection:
                connection.execute("CREATE TABLE IF NOT EXISTS master_documents (source_id TEXT PRIMARY KEY, raw BLOB NOT NULL, document TEXT NOT NULL)")
                connection.execute("CREATE TABLE IF NOT EXISTS master_profiles (version TEXT PRIMARY KEY, source_id TEXT NOT NULL, snapshot TEXT NOT NULL)")

    def save(self, document: CVDocument, raw: bytes, profile: dict) -> None:
        from jobhunter.matching import validate_profile
        validate_profile(profile)
        validate_provenance(profile)
        if import_cv(raw, document.filename) != document:
            raise ValueError("Documentul nu corespunde fișierului original.")
        provenance = profile["provenance"]
        if (provenance["source_id"] != document.file_sha256 + "-" + document.text_sha256
                or provenance["importer_version"] != document.importer_version):
            raise ValueError("Profilul nu aparține documentului importat.")
        for citation in provenance["citations"]:
            if document.text[citation["start"]:citation["end"]] != citation["quote"]:
                raise ValueError("Citatul profilului nu se află în document.")
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                existing = connection.execute("SELECT snapshot FROM master_profiles WHERE version = ?", (profile["version"],)).fetchone()
                if existing:
                    # Content-identical saves retain the first review, not a silent rewrite.
                    return
                connection.execute("INSERT OR IGNORE INTO master_documents VALUES (?, ?, ?)",
                                   (provenance["source_id"], raw, canonical(asdict(document))))
                connection.execute("INSERT INTO master_profiles VALUES (?, ?, ?)",
                                   (profile["version"], provenance["source_id"], canonical(profile)))

    def list_profiles(self) -> tuple[dict, ...]:
        with closing(sqlite3.connect(self.path)) as connection:
            rows = connection.execute("SELECT snapshot FROM master_profiles ORDER BY rowid DESC").fetchall()
        return tuple(json.loads(row[0]) for row in rows)

    def load(self, version: str) -> dict:
        from jobhunter.matching import validate_profile
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute("SELECT p.snapshot, d.document, d.raw FROM master_profiles p JOIN master_documents d ON d.source_id = p.source_id WHERE p.version = ?", (version,)).fetchone()
        if row is None:
            raise ValueError("Profilul master nu există.")
        profile, document = json.loads(row[0]), json.loads(row[1])
        validate_profile(profile)
        if (sha256(document["text"].encode()).hexdigest() != profile["provenance"]["text_sha256"]
                or sha256(row[2]).hexdigest() != profile["provenance"]["file_sha256"]):
            raise ValueError("Sursa stocată a fost modificată.")
        for citation in profile["provenance"]["citations"]:
            if document["text"][citation["start"]:citation["end"]] != citation["quote"]:
                raise ValueError("Citatul stocat nu corespunde sursei.")
        return profile

    def source(self, version: str) -> tuple[bytes, dict]:
        self.load(version)
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute("SELECT d.raw, d.document FROM master_documents d JOIN master_profiles p ON p.source_id = d.source_id WHERE p.version = ?", (version,)).fetchone()
        return row[0], json.loads(row[1])
