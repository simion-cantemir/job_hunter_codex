"""Local text extraction; files are read as data and are never executed."""

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import PurePosixPath
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile


MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 100_000
MAX_XML_BYTES = 8 * 1024 * 1024
MAX_PDF_PAGES = 50
IMPORTER_VERSION = "cv-import-1"


@dataclass(frozen=True)
class CVBlock:
    label: str
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class CVDocument:
    filename: str
    format: str
    file_sha256: str
    text_sha256: str
    text: str
    blocks: tuple[CVBlock, ...]
    warnings: tuple[str, ...]
    importer_version: str = IMPORTER_VERSION


def _assemble(filename, file_format, data, chunks, warnings=()):
    parts, blocks, position = [], [], 0
    for label, text in chunks:
        text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not text:
            continue
        if parts:
            parts.append("\n\n")
            position += 2
        start = position
        parts.append(text)
        position += len(text)
        if position > MAX_TEXT_CHARS:
            raise ValueError("CV-ul depășește limita de text a prototipului; nu a fost trunchiat.")
        blocks.append(CVBlock(label, start, position, text))
    text = "".join(parts)
    if not text.strip():
        raise ValueError("Nu s-a extras text. Pentru un PDF scanat este necesar OCR; poți importa textul manual.")
    return CVDocument(filename, file_format, sha256(data).hexdigest(), sha256(text.encode("utf-8")).hexdigest(),
                      text, tuple(blocks), tuple(warnings))


def _docx_chunks(data):
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    try:
        with ZipFile(BytesIO(data)) as archive:
            infos = archive.infolist()
            if len(infos) > 2048 or any("vbaproject" in item.filename.casefold() for item in infos):
                raise ValueError("Documentul DOCX conține prea multe componente sau macro-uri nesuportate.")
            names = [item.filename for item in infos]
            if names.count("word/document.xml") != 1:
                raise ValueError("Structură DOCX invalidă.")
            selected = ["word/document.xml"] + sorted(name for name in names if re.fullmatch(r"word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml", name))
            if len(set(selected)) != len(selected) or sum(archive.getinfo(name).file_size for name in selected) > MAX_XML_BYTES:
                raise ValueError("Conținutul XML al CV-ului depășește limitele sau are componente duplicate.")
            chunks = []
            for name in selected:
                xml = archive.read(name)
                declarations = xml.upper().replace(b"\x00", b"")
                if len(xml) > MAX_XML_BYTES or b"<!DOCTYPE" in declarations or b"<!ENTITY" in declarations:
                    raise ValueError("Declarațiile XML de entități nu sunt acceptate.")
                root = ET.fromstring(xml)
                if root.find(f".//{namespace}txbxContent") is not None:
                    raise ValueError("CV-ul folosește text boxes DOCX. Importă o versiune PDF cu text sau lipește textul pentru revizuire.")
                for index, paragraph in enumerate(root.iter(namespace + "p"), start=1):
                    text = "".join(element.text or "" if element.tag == namespace + "t" else
                                   "\t" if element.tag == namespace + "tab" else
                                   "\n" if element.tag in {namespace + "br", namespace + "cr"} else ""
                                   for element in paragraph.iter())
                    if text.strip():
                        chunks.append((f"{name}, paragraf {index}", text))
            return chunks
    except (BadZipFile, ET.ParseError, KeyError, RuntimeError, OSError):
        raise ValueError("Fișierul DOCX nu poate fi citit ca document valid.") from None


def import_cv(data: bytes, filename: str) -> CVDocument:
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_FILE_BYTES:
        raise ValueError("CV-ul trebuie să aibă între 1 byte și 10 MiB.")
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Lipsește numele documentului.")
    # This name is display metadata, never a destination path.
    safe_name = PurePosixPath(filename.replace("\\", "/")).name
    suffix = PurePosixPath(safe_name).suffix.casefold()
    if suffix == ".txt":
        try:
            text = data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeError:
            raise ValueError("Textul trebuie să fie UTF-8. Salvează-l în acest format sau folosește importul manual.") from None
        if "\x00" in text:
            raise ValueError("Fișierul nu este text UTF-8 valid pentru un CV.")
        chunks = [(f"Bloc {index}", match.group().strip()) for index, match in enumerate(
            re.finditer(r"\S.*?(?=\n[ \t]*\n|\Z)", text, re.S), start=1)]
        return _assemble(safe_name, "txt", data, chunks)
    if suffix == ".docx":
        return _assemble(safe_name, "docx", data, _docx_chunks(data),
                         ("Extragere text DOCX: paragrafe/tabele și antete/subsoluri, fără păstrarea layoutului sau OCR. Verifică ordinea și omisiunile.",))
    if suffix == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise ValueError("Fișierul nu are un antet PDF valid.")
        from pypdf import PdfReader
        try:
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted:
                raise ValueError("PDF-ul este criptat. Importă o copie necriptată autorizată.")
            if len(reader.pages) > MAX_PDF_PAGES:
                raise ValueError("PDF-ul depășește limita de 50 de pagini.")
            chunks, blank_pages = [], []
            for index, page in enumerate(reader.pages, start=1):
                content = page.get_contents()
                if content is not None and len(content.get_data()) > 5 * 1024 * 1024:
                    raise ValueError("O pagină PDF are conținut prea mare pentru importul local.")
                text = page.extract_text() or ""
                if not text.strip():
                    blank_pages.append(index)
                chunks.append((f"Pagina {index}", text))
            warnings = ["Extragere PDF fără OCR: verifică ordinea coloanelor, caracterele și secțiunile omise."]
            if blank_pages:
                warnings.append("Pagini fără text extras: " + ", ".join(map(str, blank_pages)))
        except ValueError:
            raise
        except Exception:
            raise ValueError("PDF-ul nu a putut fi citit. Poți importa textul manual, fără a modifica originalul.") from None
        return _assemble(safe_name, "pdf", data, chunks, warnings)
    raise ValueError("Format acceptat: TXT UTF-8, DOCX sau PDF cu text. Nu deschidem fișiere executabile sau DOCM.")
