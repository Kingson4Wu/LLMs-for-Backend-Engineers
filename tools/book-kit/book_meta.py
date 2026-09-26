from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
from pathlib import Path


LINK_RE = re.compile(r"\(([^)#]+\.md)\)")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
TEXT_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
TOP_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
CHAPTER_PREFIX_RE = re.compile(
    r"^((?:第\s*[0-9A-Za-z一二三四五六七八九十百千]+\s*章)|(?:Chapter\s+[0-9A-Za-zIVXLC]+))[:：\s-]*(.+)$",
    re.IGNORECASE,
)
APPENDIX_PREFIX_RE = re.compile(
    r"^((?:附录\s*[A-Za-z一二三四五六七八九十]+)|(?:Appendix\s+[A-Za-z0-9]+))[:：\s-]*(.+)$",
    re.IGNORECASE,
)
DEFAULT_LOCALE = "zh-Hans"


def normalize_locale(locale: str | None) -> str:
    return "zh-Hans" if not locale or locale.lower() in ("zh-hans", "zh-cn", "zh") else locale


def resolve_book_dir(raw_path: str | None) -> Path:
    return Path(raw_path).resolve() if raw_path else Path(__file__).resolve().parents[2] / "book"


def resolve_source_dir(book_dir: Path, locale: str | None = None) -> Path:
    code = normalize_locale(locale)
    editions = json.loads((book_dir / "editions.json").read_text())["editions"]
    if code not in editions:
        raise ValueError(f"Unknown edition: {code}")
    source = (book_dir / editions[code]["source"]).resolve()
    if not source.is_dir() or not (source / "catalog.json").is_file():
        raise ValueError(f"Missing edition sources: {code}: {source}")
    return source


def resolve_build_dir(book_dir: Path, locale: str | None = None) -> Path:
    code = normalize_locale(locale)
    return book_dir / "_book" if code == DEFAULT_LOCALE else book_dir / "_book" / code


def load_meta(book_dir: Path, locale: str | None = None) -> dict:
    source = resolve_source_dir(book_dir, locale)
    meta = json.loads((source / "book.json").read_text(encoding="utf-8"))
    meta["language"] = normalize_locale(locale)
    meta["outputs"] = {"print_html": f"exported/{meta['language']}/book-print.html",
                       "pdf": f"exported/{meta['language']}/book.pdf",
                       "epub": f"exported/{meta['language']}/book.epub"}
    return meta


def catalog_entries(catalog: dict) -> list[dict]:
    return catalog["frontmatter"] + [chapter for part in catalog["parts"] for chapter in part["chapters"]]


def part_entries(catalog: dict) -> list[dict]:
    return [
        {"id": part["id"], "path": part["path"], "title": part["title"]}
        for part in catalog["parts"]
    ]


def load_catalog(source_dir: Path) -> dict:
    catalog = json.loads((source_dir / "catalog.json").read_text(encoding="utf-8"))
    if catalog.get("version") != 1:
        raise ValueError("Unsupported catalog version")
    entries = catalog_entries(catalog)
    ids = [entry["id"] for entry in entries] + [part["id"] for part in catalog["parts"]]
    paths = [entry["path"] for entry in entries]
    if len(set(ids)) != len(ids) or len(set(paths)) != len(paths):
        raise ValueError("Catalog IDs and paths must be unique")
    for entry in entries:
        path = (source_dir / entry["path"]).resolve()
        if not path.is_relative_to(source_dir.resolve()) or not path.is_file():
            raise ValueError(f"Missing or unsafe catalog source: {entry['path']}")
        if not entry["title"] or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]):
            raise ValueError(f"Invalid catalog entry: {entry}")
    for entry in part_entries(catalog):
        path = (source_dir / entry["path"]).resolve()
        if not path.is_relative_to(source_dir.resolve()) or not path.is_file():
            raise ValueError(f"Missing or unsafe part source: {entry['path']}")
    actual = {path.relative_to(source_dir).as_posix() for path in (source_dir / "chapters").rglob("*.md")}
    if actual != {path for path in paths if path.startswith("chapters/")}:
        raise ValueError("Catalog must include every chapter exactly once")
    return catalog


def render_summary(catalog: dict) -> str:
    lines = ["# Summary", ""]
    lines += [f"- [{entry['title']}]({entry['path']})" for entry in catalog["frontmatter"]]
    for part in catalog["parts"]:
        lines += ["", f"## {part['title']}", ""]
        lines += [f"- [{entry['title']}]({entry['path']})" for entry in part["chapters"]]
    return "\n".join(lines) + "\n"


def git_revision(book_dir: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=6", "HEAD"],
            cwd=book_dir,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    revision = result.stdout.strip()
    return revision or None


def release_display_items(book_dir: Path, meta: dict, *, draft: bool = False) -> list[str]:
    items: list[str] = []
    if draft:
        items.append(str(meta.get("draft_label", "Draft")).strip() or "Draft")
        items.append(dt.date.today().isoformat())
    else:
        release_date = str(meta.get("release_date", "")).strip()
        if release_date:
            items.append(release_date)

    revision = str(meta.get("revision", "")).strip() or git_revision(book_dir) or ""
    if revision:
        items.append(f"rev {revision}")

    return items


def chapter_paths(source_dir: Path) -> list[str]:
    return [entry["path"] for entry in catalog_entries(load_catalog(source_dir))]


def strip_markdown_links(text: str) -> str:
    return TEXT_LINK_RE.sub(r"\1", text)


def strip_local_file_links(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        label, target = match.groups()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        return label

    return TEXT_LINK_RE.sub(repl, text)


def strip_markdown_formatting(text: str) -> str:
    text = strip_markdown_links(text)
    text = text.replace("`", "")
    text = re.sub(r"[*_~]+", "", text)
    return text


def top_heading(text: str) -> str | None:
    match = TOP_HEADING_RE.search(text)
    if not match:
        return None
    return strip_markdown_formatting(match.group(1).strip())


def escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "^": r"\^{}",
        "~": r"\~{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def derive_short_title(title: str) -> str:
    title = strip_markdown_formatting(title).strip()

    for separator in ("：", ":"):
        if separator in title:
            return title.split(separator, 1)[0].strip()

    for pattern in (CHAPTER_PREFIX_RE, APPENDIX_PREFIX_RE):
        match = pattern.match(title)
        if match:
            prefix, rest = match.groups()
            for separator in ("：", ":", "，", ",", "、"):
                if separator in rest:
                    return f"{prefix} {rest.split(separator, 1)[0].strip()}".strip()
            return title

    for prefix in ("前言", "序言", "导读", "Preface", "Introduction"):
        if title.startswith(prefix):
            rest = title[len(prefix) :].strip()
            for separator in ("，", ",", "、", "：", ":", " "):
                if separator in rest:
                    return f"{prefix} {rest.split(separator, 1)[0].strip()}".strip()
            return title

    return title


def short_title_for_path(md_path: str, text: str) -> str | None:
    if md_path == "README.md":
        return None

    heading = top_heading(text)
    if not heading:
        return None
    return derive_short_title(heading)


def replace_top_heading_with_latex(text: str, *, short_title: str) -> str:
    match = TOP_HEADING_RE.search(text)
    if not match:
        return text

    long_title = escape_latex(strip_markdown_formatting(match.group(1).strip()))
    short_title = escape_latex(strip_markdown_formatting(short_title.strip()))
    replacement = f"\\chapter[{short_title}]{{{long_title}}}"
    return text[: match.start()] + replacement + text[match.end() :]


def normalize_readme(
    text: str,
    *,
    title: str,
    cover_alt: str | None,
    front_page_heading: str = "导读",
) -> str:
    lines = text.splitlines()
    filtered: list[str] = []
    normalized_front_heading = f"# {front_page_heading}".strip()
    for line in lines:
        stripped = line.strip()
        if stripped == f"# {title}":
            continue
        if stripped == normalized_front_heading:
            continue
        if cover_alt and stripped.startswith(f"![{cover_alt}]("):
            continue
        filtered.append(line)

    body = strip_markdown_links("\n".join(filtered).strip())
    return f"# {front_page_heading}\n\n" + body + "\n"
