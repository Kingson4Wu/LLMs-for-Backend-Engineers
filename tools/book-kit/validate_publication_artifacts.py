"""Validate generated HTML, EPUB, and PDF publication artifacts before release."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from book_meta import normalize_locale, resolve_book_dir


AI_LEARNING_GUIDE_MARKERS = {
    "zh-Hans": "用 AI 学习本书",
    "en": "Learn This Book with AI",
}

PROVENANCE_MARKERS = {
    "zh-Hans": "版权所有 © Kingson Wu",
    "en": "Copyright © Kingson Wu",
}

# Rotated PDF text can preserve its Latin words while normalizing or dropping
# the copyright glyph during extraction; use the distinctive name as the
# format-neutral assertion while the full visible mark remains in watermark.py.
VISUAL_WATERMARK_MARKER = "Kingson Wu"
# Poppler splits rotated watermark endpoints into these fragments and reports
# their unrotated boxes outside the page. They are intentionally excluded from
# the geometric body-text check below.
WATERMARK_BBOX_ARTIFACTS = {"©", "MS", "S"}


class HtmlInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.fragments: list[str] = []
        self.math_count = 0
        self.toc_depth = 0
        self.max_toc_depth = 0
        self.in_toc = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"])
        if tag == "a" and (href := attributes.get("href", "")).startswith("#") and href != "#":
            self.fragments.append(href[1:])
        if tag == "math":
            self.math_count += 1
        if attributes.get("id") == "TOC":
            self.in_toc = True
        if self.in_toc and tag in {"ul", "ol"}:
            self.toc_depth += 1
            self.max_toc_depth = max(self.max_toc_depth, self.toc_depth)

    def handle_endtag(self, tag: str) -> None:
        if self.in_toc and tag in {"ul", "ol"}:
            self.toc_depth -= 1
        if self.in_toc and tag == "nav":
            self.in_toc = False


def pdf_text_out_of_bounds(report: Path, *, ignored_words: set[str] | None = None) -> list[str]:
    root = ET.parse(report).getroot()
    errors: list[str] = []
    ignored_words = ignored_words or set()
    pages = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "page"]
    for page_number, page in enumerate(pages, start=1):
        width = float(page.attrib["width"])
        height = float(page.attrib["height"])
        for word in page.iter():
            if word.tag.rsplit("}", 1)[-1] != "word":
                continue
            if (word.text or "") in ignored_words:
                continue
            x_min, y_min, x_max, y_max = (float(word.attrib[name]) for name in ("xMin", "yMin", "xMax", "yMax"))
            if x_min < -0.01 or y_min < -0.01 or x_max > width + 0.01 or y_max > height + 0.01:
                errors.append(f"page {page_number}: {word.text or ''}")
    return errors


def pdf_toc_has_section_entries(text: str) -> bool:
    """Return whether an indented, dot-led section appears in the PDF contents."""
    leader = r"\.(?:\s*\.){2,}"
    return any(re.match(rf"^\s+\S.*{leader}\s*\d+\s*$", line) for line in text.splitlines())


def pdf_has_watermark_provenance(pdfinfo: str, marker: str) -> bool:
    return any(line.startswith("Subject:") and marker in line for line in pdfinfo.splitlines())


def validate_html(path: Path, guide_marker: str, watermark_marker: str) -> list[str]:
    inspector = HtmlInspector()
    inspector.feed(path.read_text(encoding="utf-8"))
    errors = []
    ids = set(inspector.ids)
    if len(ids) != len(inspector.ids):
        errors.append("duplicate HTML ids")
    if missing := sorted(set(inspector.fragments) - ids):
        errors.append(f"broken HTML fragments: {', '.join(missing[:3])}")
    if inspector.math_count == 0:
        errors.append("HTML has no MathML formulas")
    if inspector.max_toc_depth != 2:
        errors.append(f"HTML TOC must contain part and chapter levels only (depth {inspector.max_toc_depth})")
    if guide_marker not in path.read_text(encoding="utf-8"):
        errors.append("HTML is missing the embedded AI learning guide")
    if watermark_marker not in path.read_text(encoding="utf-8"):
        errors.append("HTML is missing the visual watermark")
    return errors


def epub_toc_depth(nav: ET.Element) -> int:
    toc = next((node for node in nav.iter() if node.attrib.get("{http://www.idpf.org/2007/ops}type") == "toc"), None)
    if toc is None:
        return 0

    def visit(node: ET.Element, list_depth: int = 0) -> int:
        if node.tag.rsplit("}", 1)[-1] in {"ul", "ol"}:
            list_depth += 1
        return max([list_depth, *(visit(child, list_depth) for child in node)])

    return visit(toc)


def validate_epub(path: Path, guide_marker: str, provenance_marker: str) -> list[str]:
    errors = []
    with zipfile.ZipFile(path) as archive:
        if archive.read("mimetype") != b"application/epub+zip":
            errors.append("invalid EPUB mimetype")
        if archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            errors.append("EPUB mimetype is compressed")
        names = set(archive.namelist())
        pages = {name: ET.fromstring(archive.read(name)) for name in names if name.endswith(".xhtml")}
        math_count = 0
        for name, page in pages.items():
            ids = {node.attrib["id"] for node in page.iter() if "id" in node.attrib}
            math_count += sum(node.tag.rsplit("}", 1)[-1] == "math" for node in page.iter())
            for node in page.iter():
                href = node.attrib.get("href", "")
                if not href or href.startswith(("http:", "https:", "mailto:")):
                    continue
                target, _, fragment = href.partition("#")
                destination = posixpath.normpath(posixpath.join(posixpath.dirname(name), target)) if target else name
                if destination not in names:
                    errors.append(f"missing EPUB resource: {name} -> {href}")
                elif fragment and destination in pages:
                    target_ids = {item.attrib["id"] for item in pages[destination].iter() if "id" in item.attrib}
                    if fragment not in target_ids:
                        errors.append(f"broken EPUB fragment: {name} -> {href}")
        if math_count == 0:
            errors.append("EPUB has no MathML formulas")
        if not any(guide_marker in "".join(page.itertext()) for page in pages.values()):
            errors.append("EPUB is missing the embedded AI learning guide")
        if not any(provenance_marker in "".join(page.itertext()) for page in pages.values()):
            errors.append("EPUB is missing the publication provenance")
        nav = pages.get("EPUB/nav.xhtml")
        if nav is None:
            errors.append("missing EPUB navigation")
        elif epub_toc_depth(nav) != 2:
            errors.append(f"EPUB TOC must contain part and chapter levels only (depth {epub_toc_depth(nav)})")
    return errors


def validate_pdf(path: Path, guide_marker: str, watermark_marker: str) -> list[str]:
    errors = []
    for command in (["qpdf", "--check", str(path)], ["pdffonts", str(path)]):
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode:
            errors.append(f"{' '.join(command[:2])} failed: {result.stderr.strip() or result.stdout.strip()}")
            return errors
        if command[0] == "pdffonts":
            for line in result.stdout.splitlines()[2:]:
                fields = line.split()
                if len(fields) >= 5 and fields[-5] != "yes":
                    errors.append(f"PDF font is not embedded: {fields[0]}")
    raw = subprocess.check_output(["pdftotext", "-raw", str(path), "-"], text=True)
    if re.search(r"[�□]", raw):
        errors.append("PDF text contains a missing-glyph replacement")
    if guide_marker not in raw:
        errors.append("PDF is missing the embedded AI learning guide")
    pdfinfo = subprocess.check_output(["pdfinfo", str(path)], text=True)
    if not pdf_has_watermark_provenance(pdfinfo, watermark_marker):
        errors.append("PDF is missing watermark provenance metadata")
    toc = subprocess.check_output(["pdftotext", "-layout", "-f", "1", "-l", "20", str(path), "-"], text=True)
    if pdf_toc_has_section_entries(toc):
        errors.append("PDF TOC contains section entries below the chapter level")
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "bbox.html"
        subprocess.run(["pdftotext", "-bbox", str(path), str(report)], check=True)
        # pdftotext's bounding boxes do not preserve rotation. The two edge
        # fragments of the centered visual watermark therefore appear outside
        # the page despite rendering within it. Keep all ordinary text bounds
        # checks intact.
        errors.extend(
            f"PDF text exceeds page bounds: {entry}"
            for entry in pdf_text_out_of_bounds(report, ignored_words=WATERMARK_BBOX_ARTIFACTS)
        )
    return errors


def validate_markdown(path: Path, guide_marker: str, provenance_marker: str) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    errors = []
    if guide_marker not in raw:
        errors.append("Markdown is missing the embedded AI learning guide")
    if provenance_marker not in raw:
        errors.append("Markdown is missing the publication provenance")
    if "# " not in raw or "## " not in raw:
        errors.append("Markdown is missing the book and chapter heading hierarchy")
    return errors


def validate(locale: str) -> list[str]:
    book = resolve_book_dir(None)
    code = normalize_locale(locale)
    guide_marker = AI_LEARNING_GUIDE_MARKERS[code]
    provenance_marker = PROVENANCE_MARKERS[code]
    output = book / "exported" / code
    artifacts = {
        "HTML": output / "Understanding-LLMs.print.html",
        "EPUB": output / "Understanding-LLMs.epub",
        "PDF": output / "Understanding-LLMs.pdf",
        "Markdown": output / "Understanding-LLMs.md",
    }
    errors = [f"missing {name}: {path}" for name, path in artifacts.items() if not path.is_file()]
    if errors:
        return errors
    return (
        validate_html(artifacts["HTML"], guide_marker, VISUAL_WATERMARK_MARKER)
        + validate_epub(artifacts["EPUB"], guide_marker, provenance_marker)
        + validate_pdf(artifacts["PDF"], guide_marker, VISUAL_WATERMARK_MARKER)
        + validate_markdown(artifacts["Markdown"], guide_marker, provenance_marker)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", required=True)
    args = parser.parse_args()
    errors = validate(args.locale)
    if errors:
        raise SystemExit("Publication artifact validation failed:\n- " + "\n- ".join(errors))
    print(f"Publication artifacts are valid for {normalize_locale(args.locale)}.")


if __name__ == "__main__":
    main()
