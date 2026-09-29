"""Generate the source-grounded index used by AI learning workflows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote

from book_meta import load_catalog, resolve_book_dir, resolve_source_dir


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)\s]+)(?:\s+[^)]*)?\)")
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)")
DISPLAY_MATH_RE = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", re.DOTALL)


def heading_slug(text: str) -> str:
    """Use a predictable GitHub-style fragment for a source heading."""
    normalized = re.sub(r"[`*_~]", "", text).strip().lower()
    normalized = re.sub(r"[^\w\-\s\u3400-\u9fff]", "", normalized)
    return re.sub(r"[\s_]+", "-", normalized).strip("-")


def headings(markdown: str) -> list[dict[str, object]]:
    used: dict[str, int] = {}
    result = []
    for order, match in enumerate(HEADING_RE.finditer(markdown), start=1):
        title = match.group(2).strip()
        base = heading_slug(title) or f"heading-{order}"
        count = used.get(base, 0)
        used[base] = count + 1
        result.append(
            {
                "order": order,
                "level": len(match.group(1)),
                "title": title,
                "anchor": base if count == 0 else f"{base}-{count}",
            }
        )
    return result


def figures(markdown: str, source_path: Path, source_root: Path, book: Path) -> list[str]:
    result = []
    for raw_target in IMAGE_RE.findall(markdown):
        target = unquote(raw_target)
        if target.startswith(("http:", "https:", "data:")):
            continue
        resolved = (source_path.parent / target).resolve()
        if not resolved.is_file():
            raise ValueError(f"Missing learning-index figure: {source_path}: {raw_target}")
        try:
            result.append(resolved.relative_to(book).as_posix())
        except ValueError:
            result.append(resolved.relative_to(source_root).as_posix())
    return result


def formula_sections(markdown: str) -> list[str]:
    heading_matches = list(HEADING_RE.finditer(markdown))
    heading_data = headings(markdown)
    formula_positions = sorted(
        [match.start() for match in DISPLAY_MATH_RE.finditer(markdown)]
        + [match.start() for match in INLINE_MATH_RE.finditer(markdown)]
    )
    result = []
    for position in formula_positions:
        index = next(
            (offset for offset in range(len(heading_matches) - 1, -1, -1) if heading_matches[offset].start() <= position),
            None,
        )
        if index is not None:
            anchor = heading_data[index]["anchor"]
            if anchor not in result:
                result.append(anchor)
    return result


def learning_metadata(entry: dict, source_root: Path, book: Path) -> dict:
    source_path = source_root / entry["path"]
    markdown = source_path.read_text(encoding="utf-8")
    return {
        "path": source_path.relative_to(book).as_posix(),
        "headings": headings(markdown),
        "formula_count": len(DISPLAY_MATH_RE.findall(markdown)) + len(INLINE_MATH_RE.findall(markdown)),
        "formula_sections": formula_sections(markdown),
        "figures": figures(markdown, source_path, source_root, book),
    }


def build_index(book: Path) -> dict:
    book = book.resolve()
    zh_catalogue = load_catalog(book)
    en_root = resolve_source_dir(book, "en")
    en_catalogue = load_catalog(en_root)
    en_entries = {entry["id"]: entry for part in en_catalogue["parts"] for entry in part["chapters"]}
    chapters = []
    previous: str | None = None
    order = 0
    for part in zh_catalogue["parts"]:
        for entry in part["chapters"]:
            order += 1
            english = en_entries.get(entry["id"])
            if english is None:
                raise ValueError(f"Missing English learning-index entry: {entry['id']}")
            chapters.append(
                {
                    "id": entry["id"],
                    "part": part["id"],
                    "order": order,
                    "title": {"zh-Hans": entry["title"], "en": english["title"]},
                    "source": {
                        "zh-Hans": learning_metadata(entry, book, book),
                        "en": learning_metadata(english, en_root, book),
                    },
                    # The catalogue establishes a reading sequence, not a claim that
                    # adjacent chapters are conceptual prerequisites.
                    "navigation": {"previous": previous, "next": None},
                }
            )
            if previous:
                chapters[-2]["navigation"]["next"] = entry["id"]
            previous = entry["id"]
    return {"version": 1, "chapters": chapters}


def render_index(book: Path) -> str:
    return json.dumps(build_index(book), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book_dir", nargs="?")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    book = resolve_book_dir(args.book_dir)
    output = book.parent / "learning" / "index.json"
    rendered = render_index(book)
    if args.write:
        output.write_text(rendered, encoding="utf-8")
        print(output)
    elif not output.is_file() or output.read_text(encoding="utf-8") != rendered:
        raise SystemExit("learning/index.json is stale; run generate_learning_index.py --write")
    else:
        print("Learning index is current.")


if __name__ == "__main__":
    main()
