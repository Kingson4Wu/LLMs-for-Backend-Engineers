"""Derive source publication signals and verify that exports preserve them."""
from __future__ import annotations

import hashlib
import base64
import json
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

from book_meta import APPENDIX_PREFIX_RE, catalog_entries, load_catalog, normalize_locale, resolve_source_dir, strip_markdown_formatting, top_heading


AI_GUIDE_MARKERS = {"zh-Hans": "用 AI 学习本书", "en": "Learn This Book with AI"}
PUBLIC_ASSET_ROOT = "https://kingson4wu.github.io/Understanding-LLMs/assets/"
DISPLAY_MATH_RE = re.compile(r"^\$\$\s*(.*?)\s*\$\$\s*$", re.MULTILINE | re.DOTALL)
IMAGE_RE = re.compile(r"!\[[^]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
HTML_HEADING_RE = re.compile(r"<h([1-6])\b([^>]*)>(.*?)</h\1\s*>", re.IGNORECASE | re.DOTALL)
ANCHOR_ID_RE = re.compile(r"<a\b[^>]*\bid=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
HEADING_ID_RE = re.compile(r"\bid=[\"']([^\"']+)[\"']", re.IGNORECASE)
ELEMENT_ID_RE = re.compile(r"<[A-Za-z][^>]*\bid=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
TEX_ANNOTATION_RE = re.compile(
    r'<annotation\b[^>]*encoding=["\']application/x-tex["\'][^>]*>(.*?)</annotation>', re.DOTALL
)


def normalize_math(value: str) -> str:
    return re.sub(r"\s+", "", unescape(value)).strip()


def math_fingerprint(value: str) -> str:
    return hashlib.sha256(normalize_math(value).encode("utf-8")).hexdigest()


def pdf_formula_evidence(value: str) -> dict:
    """Describe the deterministic PDF check available for one source formula."""
    normalized = normalize_math(value)
    fingerprint = math_fingerprint(value)
    if re.search(r"\\[A-Za-z]+|[_^]", normalized):
        return {
            "fingerprint": fingerprint,
            "status": "requires_allowlist",
            "detection_reason": "TeX control sequence or script syntax is not stable in PDF text extraction",
        }
    if not re.search(r"[A-Za-z0-9=≈≠≤≥+−×÷]", normalized):
        return {
            "fingerprint": fingerprint,
            "status": "requires_allowlist",
            "detection_reason": "formula has no stable plain-text token for PDF extraction",
        }
    return {"fingerprint": fingerprint, "status": "extractable", "text": normalized}


def validate_pdf_formula_allowlist(manifest: dict, allowlist: dict) -> list[str]:
    """Require review metadata for every formula PDF text cannot represent exactly."""
    defaults = allowlist.get("defaults", {})
    records = {
        (item.get("chapter"), item.get("fingerprint")): {**defaults, **item}
        for item in allowlist.get("formulas", [])
    }
    errors = [] if allowlist.get("version") == 1 else ["pdf allowlist: unsupported version"]
    for chapter in manifest["chapters"]:
        for evidence in chapter["pdf_display_math"]:
            if evidence["status"] != "requires_allowlist":
                continue
            record = records.get((chapter["id"], evidence["fingerprint"]))
            if record is None:
                errors.append(f"pdf allowlist:{chapter['id']}: missing formula {evidence['fingerprint'][:12]}")
            elif not all(isinstance(record.get(field), str) and record[field].strip() for field in ("reason", "reviewer", "reviewed_at")):
                errors.append(f"pdf allowlist:{chapter['id']}: incomplete review metadata {evidence['fingerprint'][:12]}")
    return errors


def pdf_formula_audit(manifest: dict, extracted_text: str, allowlist: dict) -> dict:
    """Return one durable audit record for every source display formula."""
    chapters = []
    for chapter in manifest["chapters"]:
        formulas = []
        defaults = allowlist.get("defaults", {})
        approved = {
            (item.get("chapter"), item.get("fingerprint")): {**defaults, **item}
            for item in allowlist.get("formulas", [])
        }
        for evidence in chapter["pdf_display_math"]:
            record = {"fingerprint": evidence["fingerprint"], "status": evidence["status"]}
            if evidence["status"] == "requires_allowlist":
                review = approved.get((chapter["id"], evidence["fingerprint"]))
                if review:
                    record.update({"status": "unavailable", **{key: review[key] for key in ("reason", "reviewer", "reviewed_at")}})
                else:
                    record["status"] = "unapproved"
                    record["reason"] = evidence["detection_reason"]
            else:
                record["present"] = _contains(extracted_text, evidence["text"])
                if not record["present"]:
                    review = approved.get((chapter["id"], evidence["fingerprint"]))
                    if review:
                        record.update({"status": "unavailable", **{key: review[key] for key in ("reason", "reviewer", "reviewed_at")}})
            formulas.append(record)
        chapters.append({"id": chapter["id"], "formulas": formulas})
    return {
        "version": 1,
        "heading_validation": {
            "status": "text-only",
            "reason": "PDF text extraction does not retain heading node structure",
        },
        "chapters": chapters,
    }


def validate_pdf_formula_audit(manifest: dict, audit: dict) -> list[str]:
    """Reject an audit that omits or weakens an individual formula record."""
    actual: dict[tuple[str | None, str | None], list[dict]] = defaultdict(list)
    for audited_chapter in audit.get("chapters", []):
        for formula in audited_chapter.get("formulas", []):
            actual[(audited_chapter.get("id"), formula.get("fingerprint"))].append(formula)
    errors = []
    if audit.get("heading_validation") != {"status": "text-only", "reason": "PDF text extraction does not retain heading node structure"}:
        errors.append("pdf audit: missing text-only heading policy")
    for chapter in manifest["chapters"]:
        occurrences: Counter[str] = Counter()
        for evidence in chapter["pdf_display_math"]:
            fingerprint = evidence["fingerprint"]
            occurrences[fingerprint] += 1
            records = actual[(chapter["id"], fingerprint)]
            record = records.pop(0) if records else None
            if record is None:
                suffix = f" occurrence {occurrences[fingerprint]}" if occurrences[fingerprint] > 1 else ""
                errors.append(f"pdf audit:{chapter['id']}: missing formula {fingerprint[:12]}{suffix}")
                continue
            if evidence["status"] == "requires_allowlist":
                if record.get("status") != "unavailable" or not all(record.get(key) for key in ("reason", "reviewer", "reviewed_at")):
                    errors.append(f"pdf audit:{chapter['id']}: unavailable formula is not allowlisted {fingerprint[:12]}")
            elif record.get("status") == "unavailable":
                if not all(record.get(key) for key in ("reason", "reviewer", "reviewed_at")):
                    errors.append(f"pdf audit:{chapter['id']}: unavailable formula is not allowlisted {fingerprint[:12]}")
            elif record.get("status") != "extractable" or not isinstance(record.get("present"), bool):
                errors.append(f"pdf audit:{chapter['id']}: invalid extractable formula record {fingerprint[:12]}")
    return errors


def write_pdf_formula_audit(manifest: dict, pdf: Path, output: Path, allowlist: dict) -> tuple[dict, list[str]]:
    text, _, _, _ = _pdf_content(pdf)
    audit = pdf_formula_audit(manifest, text, allowlist)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    errors = validate_pdf_formula_audit(manifest, audit)
    for chapter in audit["chapters"]:
        for formula in chapter["formulas"]:
            if formula["status"] == "extractable" and not formula["present"]:
                errors.append(f"pdf:{chapter['id']}: missing display math fingerprint {formula['fingerprint'][:12]}")
    return audit, errors


def display_math(text: str) -> list[str]:
    return [match.group(1) for match in DISPLAY_MATH_RE.finditer(text)]


def local_figures(text: str, source: Path, book: Path) -> list[str]:
    figures = []
    for target in IMAGE_RE.findall(text):
        if target.startswith(("http:", "https:", "data:")):
            continue
        candidate = (source.parent / target).resolve()
        if candidate.is_file() and candidate.is_relative_to(book.resolve()):
            figures.append(candidate.relative_to(book.resolve()).as_posix())
    return figures


def figure_records(text: str, source: Path, book: Path) -> list[dict]:
    return [
        {"path": figure, "sha256": hashlib.sha256((book / figure).read_bytes()).hexdigest()}
        for figure in local_figures(text, source, book)
    ]


def published_heading(entry: dict, number: int, *, appendix: bool, english: bool) -> str:
    """Mirror the normal publication renderer's chapter label exactly."""
    if appendix:
        title = entry["title"]
        if match := APPENDIX_PREFIX_RE.match(title):
            title = match.group(2)
        label = chr(ord("A") + number - 1)
        return f"Appendix {label}: {title}" if english else f"附录 {label}：{title}"
    return f"Chapter {number}: {entry['title']}" if english else f"第{number}章：{entry['title']}"


def markdown_heading(entry: dict, number: int, *, appendix: bool, english: bool) -> str:
    """Mirror the portable Markdown renderer, including its appendix label."""
    if appendix:
        prefix = "Appendix" if english else "附录"
        return f"{prefix}: {entry['title']}"
    return published_heading(entry, number, appendix=False, english=english)


def derive_source_manifest(book: Path, locale: str) -> dict:
    """Return ordered catalogue signals without duplicating source metadata."""
    code = normalize_locale(locale)
    source = resolve_source_dir(book, code)
    catalog = load_catalog(source)
    english = code == "en"
    published_h1 = {entry["id"]: entry["title"] for entry in catalog["frontmatter"]}
    markdown_h1 = dict(published_h1)
    chapter_number = appendix_number = 0
    for part in catalog["parts"]:
        for entry in part["chapters"]:
            appendix = part["id"] == "appendix"
            if appendix:
                appendix_number += 1
                number = appendix_number
            else:
                chapter_number += 1
                number = chapter_number
            published_h1[entry["id"]] = published_heading(entry, number, appendix=appendix, english=english)
            markdown_h1[entry["id"]] = markdown_heading(entry, number, appendix=appendix, english=english)
    chapters = []
    for entry in catalog_entries(catalog):
        path = source / entry["path"]
        raw = path.read_text(encoding="utf-8")
        chapters.append(
            {
                "id": entry["id"],
                "title": entry["title"],
                "h1": top_heading(raw) or "",
                "published_h1": published_h1[entry["id"]],
                "markdown_h1": markdown_h1[entry["id"]],
                "h2": [strip_markdown_formatting(item).strip() for item in H2_RE.findall(raw)],
                "display_math": [math_fingerprint(item) for item in display_math(raw)],
                "pdf_display_math": [pdf_formula_evidence(item) for item in display_math(raw)],
                "figures": figure_records(raw, path, book),
            }
        )
    marker = AI_GUIDE_MARKERS[code]
    return {
        "version": 1,
        "locale": code,
        "chapters": chapters,
        "ai_learning_guide_present": any(marker in chapter["h1"] or marker in chapter["h2"] for chapter in chapters),
        "ai_learning_guide_marker": marker,
    }


def text_from_html(raw: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(raw)))


def _markdown_headings(raw: str) -> list[tuple[int, str, str | None]]:
    events = [(match.start(), "anchor", match.group(1)) for match in ANCHOR_ID_RE.finditer(raw)]
    events.extend((match.start(), "heading", match) for match in MARKDOWN_HEADING_RE.finditer(raw))
    chapter_id: str | None = None
    headings = []
    for _position, kind, value in sorted(events, key=lambda event: event[0]):
        if kind == "anchor":
            chapter_id = value
            continue
        headings.append((len(value.group(1)), strip_markdown_formatting(value.group(2)).strip(), chapter_id))
    return headings


def _html_headings(raw: str) -> list[tuple[int, str, str | None]]:
    chapter_id: str | None = None
    headings = []
    for match in HTML_HEADING_RE.finditer(raw):
        explicit_id = HEADING_ID_RE.search(match.group(2))
        if explicit_id:
            chapter_id = explicit_id.group(1)
        headings.append((int(match.group(1)), text_from_html(match.group(3)).strip(), chapter_id))
    return headings


def _html_math(raw: str) -> list[str]:
    return [match.group(1) for match in TEX_ANNOTATION_RE.finditer(raw)]


def _html_figures(raw: str) -> list[str]:
    return re.findall(r"<img\b[^>]*\bsrc=[\"']([^\"']+)", raw, re.IGNORECASE)


def _data_uri_digest(uri: str) -> str | None:
    if not uri.startswith("data:") or ";base64," not in uri:
        return None
    try:
        return hashlib.sha256(base64.b64decode(uri.split(",", 1)[1])).hexdigest()
    except ValueError:
        return None


def _epub_content(path: Path) -> tuple[str, list[str], list[str], list[tuple[int, str, str | None]]]:
    texts: list[str] = []
    maths: list[str] = []
    figures: list[str] = []
    headings: list[tuple[int, str, str | None]] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xhtml"):
                continue
            raw = archive.read(name).decode("utf-8")
            texts.append(text_from_html(raw))
            headings.extend(_html_headings(raw))
            maths.extend(_html_math(raw))
            figures.extend(_html_figures(raw))
        figure_digests = [
            hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.startswith("EPUB/media/")
        ]
    return " ".join(texts), maths, figure_digests, headings


def _pdf_content(path: Path) -> tuple[str, list[str], list[str], list[str]]:
    raw = subprocess.check_output(["pdftotext", "-raw", str(path), "-"], text=True)
    # PDF extraction has no dependable heading-node tree across renderer and
    # platform versions. Heading policy is recorded in the formula audit;
    # this path retains only text evidence used by that audit and guide marker.
    return raw, [], [], []


def _artifact_content(kind: str, path: Path) -> tuple[str, list[str], list[str], list[tuple[int, str, str | None]]]:
    if kind == "markdown":
        raw = path.read_text(encoding="utf-8")
        return raw, display_math(raw), IMAGE_RE.findall(raw), _markdown_headings(raw)
    if kind == "html":
        raw = path.read_text(encoding="utf-8")
        return text_from_html(raw), _html_math(raw), _html_figures(raw), _html_headings(raw)
    if kind == "epub":
        return _epub_content(path)
    if kind == "pdf":
        return _pdf_content(path)
    raise ValueError(f"Unknown publication format: {kind}")


class ChapterSegments(dict[str, dict]):
    """Artifact segments plus any duplicate catalogue boundary IDs."""

    def __init__(self) -> None:
        super().__init__()
        self.duplicates: list[str] = []


def _segments_from_boundaries(raw: str, boundaries: list[tuple[int, str]], *, html: bool = False) -> ChapterSegments:
    """Return non-overlapping, catalogue-owned artifact slices."""
    segments = ChapterSegments()
    for index, (start, chapter_id) in enumerate(boundaries):
        end = boundaries[index + 1][0] if index + 1 < len(boundaries) else len(raw)
        slice_ = raw[start:end]
        if chapter_id in segments:
            segments.duplicates.append(chapter_id)
            continue
        segments[chapter_id] = {
            "text": text_from_html(slice_) if html else slice_,
            "formulas": _html_math(slice_) if html else display_math(slice_),
            "figures": _html_figures(slice_) if html else IMAGE_RE.findall(slice_),
            "headings": _html_headings(slice_) if html else _markdown_headings(slice_),
            "anchored": True,
        }
    return segments


def _markdown_segments(raw: str, chapter_ids: set[str]) -> ChapterSegments:
    boundaries = [
        (match.start(), match.group(1))
        for match in ANCHOR_ID_RE.finditer(raw)
        if match.group(1) in chapter_ids
    ]
    return _segments_from_boundaries(raw, boundaries)


def _html_segments(raw: str, chapter_ids: set[str]) -> ChapterSegments:
    # EPUB puts an ID on the enclosing <section>; print HTML puts it on the
    # chapter heading.  Both are authoritative chapter boundaries.
    boundaries = [
        (match.start(), match.group(1))
        for match in ELEMENT_ID_RE.finditer(raw)
        if match.group(1) in chapter_ids
    ]
    return _segments_from_boundaries(raw, boundaries, html=True)


def _epub_spine_resources(archive: zipfile.ZipFile) -> list[str]:
    """Return XHTML resources in the EPUB's declared reading order."""
    if "EPUB/content.opf" not in archive.namelist():
        # Minimal unit fixtures predate spine metadata. Production EPUBs are
        # separately required to carry a valid OPF package.
        return [name for name in archive.namelist() if name.endswith(".xhtml")]
    root = ET.fromstring(archive.read("EPUB/content.opf"))
    local_name = lambda element: element.tag.rsplit("}", 1)[-1]
    manifest = {
        item.attrib["id"]: item.attrib["href"]
        for item in root.iter()
        if local_name(item) == "item" and "id" in item.attrib and "href" in item.attrib
    }
    return [
        posixpath.normpath(posixpath.join("EPUB", manifest[itemref.attrib["idref"]]))
        for itemref in root.iter()
        if local_name(itemref) == "itemref" and itemref.attrib.get("idref") in manifest
        and manifest[itemref.attrib["idref"]].endswith(".xhtml")
    ]


def _epub_segments(path: Path, chapter_ids: set[str]) -> ChapterSegments:
    """Associate each chapter with its ordered EPUB XHTML spine resource."""
    with zipfile.ZipFile(path) as archive:
        resource_names = _epub_spine_resources(archive)
        segments = ChapterSegments()
        for name in resource_names:
            raw = archive.read(name).decode("utf-8")
            local_segments = _html_segments(raw, chapter_ids)
            segments.duplicates.extend(local_segments.duplicates)
            for chapter_id, segment in local_segments.items():
                if chapter_id in segments:
                    segments.duplicates.append(chapter_id)
                    continue
                segment["resource"] = name
                segment["figure_digests"] = [
                    hashlib.sha256(archive.read(posixpath.normpath(posixpath.join(posixpath.dirname(name), candidate)))).hexdigest()
                    for candidate in segment["figures"]
                    if not candidate.startswith(("http:", "https:", "data:"))
                    and posixpath.normpath(posixpath.join(posixpath.dirname(name), candidate)) in archive.namelist()
                ]
                segments[chapter_id] = segment
        return segments


def _artifact_segments(kind: str, path: Path, chapter_ids: set[str]) -> ChapterSegments:
    if kind == "markdown":
        return _markdown_segments(path.read_text(encoding="utf-8"), chapter_ids)
    if kind == "html":
        return _html_segments(path.read_text(encoding="utf-8"), chapter_ids)
    if kind == "epub":
        return _epub_segments(path, chapter_ids)
    return ChapterSegments()


def _contains(text: str, expected: str) -> bool:
    canonical = lambda value: re.sub(r"\s+", "", value).replace("’", "'").replace("‘", "'")
    return canonical(expected) in canonical(text)


def _heading_survives(text: str, expected: str) -> bool:
    """Compare a heading label exactly, allowing only publisher chapter prefixes."""
    def normalize(value: str) -> str:
        value = re.sub(r"\s+", " ", value).strip().replace("’", "'").replace("‘", "'")
        return re.sub(r"^(?:Chapter\s+\d+|第\s*\d+\s*章)\s*(?:[:：.\-—]\s*)?", "", value, flags=re.IGNORECASE)

    return normalize(text) == normalize(expected)


def _missing_structural_headings(headings: list[tuple[int, str, str | None]], labels: list[tuple[str, str]], *, allow_promoted_h2: bool) -> list[tuple[str, str]]:
    """Return source labels absent from one chapter-local export slice.

    A catalog chapter wrapper may promote source H2 headings by one level.
    That is permitted only when the slice was found by a chapter boundary,
    not in an unanchored single-chapter fixture or a document-wide fallback.
    """
    actual = [(level, text) for level, text, _chapter_id in headings if level in {1, 2, 3}]
    cursor = 0
    missing = []
    for expected_index, (label, label_kind) in enumerate(labels):
        while cursor < len(actual) and not _heading_survives(actual[cursor][1], label):
            cursor += 1
        if cursor == len(actual):
            missing.append((label, label_kind))
            continue
        level, _text = actual[cursor]
        if expected_index == 0 and level not in {1, 2}:
            missing.append((label, label_kind))
            continue
        if expected_index and level not in ({2, 3} if allow_promoted_h2 else {2}):
            missing.append((label, label_kind))
            continue
        cursor += 1
    return missing


def _chapter_heading_labels(chapter: dict, kind: str) -> list[tuple[str, str]]:
    """Check rendered headings; retain source H1 as provenance, not output identity."""
    labels = [(chapter["markdown_h1"] if kind == "markdown" else chapter["published_h1"], "heading")]
    labels.extend((label, "heading") for label in chapter["h2"])
    unique = []
    seen = set()
    for label, kind in labels:
        if label and label not in seen:
            unique.append((label, kind))
            seen.add(label)
    return unique


def _markdown_figure_matches(source_path: str, artifact_uri: str) -> bool:
    """Accept only the source-relative URI or its exact portable public URI."""
    if source_path == artifact_uri:
        return True
    if source_path.startswith("assets/"):
        return PUBLIC_ASSET_ROOT + source_path.removeprefix("assets/") == artifact_uri
    return False


def validate_artifact_manifest(manifest: dict, artifacts: dict[str, Path], *, formats: set[str]) -> list[str]:
    """Check requested exports against a source-derived manifest.

    A PDF is intentionally checked through extracted text rather than by
    assuming its internal layout representation.  TeX fingerprints can be
    compared exactly in Markdown/HTML/EPUB; the PDF path additionally guards
    against an empty math export by comparing its extracted equation count.
    """
    errors: list[str] = []
    marker = manifest["ai_learning_guide_marker"]
    for kind in sorted(formats):
        path = artifacts.get(kind)
        if path is None or not path.is_file():
            errors.append(f"missing {kind} artifact")
            continue
        text, formulas, figures, headings = _artifact_content(kind, path)
        segments = _artifact_segments(kind, path, {chapter["id"] for chapter in manifest["chapters"]})
        # Focused fixtures with one chapter predate explicit export anchors.
        # Real multi-chapter exports must expose their source-derived boundary.
        if kind != "pdf" and len(manifest["chapters"]) == 1 and not segments:
            only = manifest["chapters"][0]
            segments[only["id"]] = {
                "text": text,
                "formulas": formulas,
                "figures": figures,
                "headings": headings,
                "anchored": False,
                "figure_digests": set(),
            }
        if not _contains(text, marker):
            errors.append(f"{kind}: missing AI learning guide marker")
        if kind != "pdf":
            expected_order = [chapter["id"] for chapter in manifest["chapters"]]
            actual_order = list(segments)
            if actual_order != expected_order:
                errors.append(
                    f"{kind}: chapter segment order {actual_order!r} does not match catalog {expected_order!r}"
                )
            for chapter_id in segments.duplicates:
                errors.append(f"{kind}:{chapter_id}: duplicate chapter segment boundary")
        for chapter in manifest["chapters"]:
            labels = _chapter_heading_labels(chapter, kind)
            if kind == "pdf":
                segment = None
            else:
                segment = segments.get(chapter["id"])
                if segment is None:
                    errors.append(f"{kind}:{chapter['id']}: missing chapter segment")
                    continue
                missing = _missing_structural_headings(
                    segment["headings"], labels, allow_promoted_h2=segment.get("anchored", True)
                )
                for label, label_kind in missing:
                    errors.append(f"{kind}:{chapter['id']}: missing {label_kind} {label!r}")
            if kind != "pdf":
                actual_math = Counter(math_fingerprint(item) for item in segment["formulas"])
                expected_math = Counter(chapter["display_math"])
                for fingerprint, expected_count in expected_math.items():
                    for occurrence in range(actual_math[fingerprint] + 1, expected_count + 1):
                        suffix = f" occurrence {occurrence}" if expected_count > 1 else ""
                        errors.append(f"{kind}:{chapter['id']}: missing display math fingerprint {fingerprint[:12]}{suffix}")
            if kind == "markdown":
                candidates = list(segment["figures"])
                occurrences = Counter()
                expected = Counter(figure["path"] for figure in chapter["figures"])
                for figure in chapter["figures"]:
                    occurrences[figure["path"]] += 1
                    match = next((index for index, candidate in enumerate(candidates) if _markdown_figure_matches(figure["path"], candidate)), None)
                    if match is None:
                        suffix = f" occurrence {occurrences[figure['path']]}" if expected[figure["path"]] > 1 else ""
                        errors.append(f"{kind}:{chapter['id']}: missing figure {Path(figure['path']).name}{suffix}")
                    else:
                        candidates.pop(match)
            if kind == "html":
                digests = Counter(_data_uri_digest(candidate) for candidate in segment["figures"])
                for figure in chapter["figures"]:
                    if not digests[figure["sha256"]]:
                        errors.append(f"{kind}:{chapter['id']}: missing figure {Path(figure['path']).name}")
                    else:
                        digests[figure["sha256"]] -= 1
            if kind == "epub":
                digests = Counter(segment["figure_digests"])
                for figure in chapter["figures"]:
                    if not digests[figure["sha256"]]:
                        errors.append(f"{kind}:{chapter['id']}: missing figure {Path(figure['path']).name}")
                    else:
                        digests[figure["sha256"]] -= 1
    return errors
