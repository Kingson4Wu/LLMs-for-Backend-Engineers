#!/usr/bin/env python3
"""Inventory structural Markdown units for Chinese-source bilingual review."""
from __future__ import annotations

import hashlib
import argparse
import json
import re
import sys
from pathlib import Path

from book_meta import catalog_entries, load_catalog


HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
LINK = re.compile(r"(?<!!)\[([^]]+)\]\(([^)]+)\)")
LIST = re.compile(r"^\s*(?:[-*+] |\d+[.)] )")
TABLE = re.compile(r"^\s*\|.+\|\s*$")
QUOTE = re.compile(r"^\s*>")
FENCE = re.compile(r"^\s*(```|~~~)")
DISPLAY_MATH = re.compile(r"^\$\$\s*(.*?)\s*\$\$$", re.MULTILINE | re.DOTALL)
LOCALIZED_TEX_TEXT = re.compile(r"\\text\{[^{}]*\}")


def normalized_fingerprint(text: str) -> str:
    """Return a stable fingerprint for a source unit without its presentation."""
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def formula_semantic_fingerprint(formula: str) -> str:
    """Fingerprint mathematical notation while excluding translated TeX labels.

    ``\\text{...}`` is explanatory prose in this book's display equations; its
    language may legitimately differ between editions. Operators, variables,
    delimiters, and every non-text TeX construct remain part of the fingerprint.
    """
    without_localized_text = LOCALIZED_TEX_TEXT.sub(r"\\text{}", formula)
    return normalized_fingerprint(without_localized_text)


def compare_formula_semantics(zh_formulas: list[str], en_formulas: list[str]) -> list[str]:
    """Require paired display equations to retain their mathematical structure."""
    errors: list[str] = []
    shared = min(len(zh_formulas), len(en_formulas))
    for ordinal in range(shared):
        if formula_semantic_fingerprint(zh_formulas[ordinal]) != formula_semantic_fingerprint(en_formulas[ordinal]):
            errors.append(f"Formula {ordinal + 1} mathematical structure differs")
    for ordinal in range(shared, len(zh_formulas)):
        errors.append(f"Chinese has an unmapped formula at ordinal {ordinal + 1}")
    for ordinal in range(shared, len(en_formulas)):
        errors.append(f"English has an unmapped formula at ordinal {ordinal + 1}")
    return errors


def inventory_markdown(source: str) -> list[dict[str, str | int]]:
    """Return ordered structural units without attempting to translate prose."""
    units: list[dict[str, str | int]] = []

    def add(kind: str, text: str, line: int) -> None:
        units.append(
            {
                "kind": kind,
                "ordinal": len(units),
                "line": line,
                "fingerprint": normalized_fingerprint(text),
            }
        )

    lines = source.splitlines()
    index = 0
    paragraph: list[str] = []
    paragraph_line = 0

    def flush_paragraph() -> None:
        nonlocal paragraph, paragraph_line
        if paragraph:
            add("paragraph", "\n".join(paragraph), paragraph_line)
        paragraph = []
        paragraph_line = 0

    while index < len(lines):
        line = lines[index]
        line_number = index + 1
        if not line.strip():
            flush_paragraph()
            index += 1
            continue

        fence = FENCE.match(line)
        if fence:
            flush_paragraph()
            marker = fence.group(1)
            block = [line]
            index += 1
            while index < len(lines):
                block.append(lines[index])
                if lines[index].lstrip().startswith(marker):
                    index += 1
                    break
                index += 1
            add("code", "\n".join(block), line_number)
            continue

        if line.strip().startswith("$$"):
            flush_paragraph()
            block = [line]
            if line.strip() != "$$":
                index += 1
            else:
                index += 1
                while index < len(lines):
                    block.append(lines[index])
                    if lines[index].strip() == "$$":
                        index += 1
                        break
                    index += 1
            add("formula", "\n".join(block), line_number)
            continue

        heading = HEADING.match(line)
        if heading:
            flush_paragraph()
            add(f"heading:{len(heading.group(1))}", heading.group(2), line_number)
            index += 1
            continue

        if IMAGE.search(line):
            flush_paragraph()
            for match in IMAGE.finditer(line):
                add("image", match.group(0), line_number)
            index += 1
            continue

        if LINK.search(line) and line.strip() == LINK.search(line).group(0):
            flush_paragraph()
            for match in LINK.finditer(line):
                add("link", match.group(0), line_number)
            index += 1
            continue

        if LIST.match(line):
            flush_paragraph()
            add("list", line, line_number)
            index += 1
            continue

        if TABLE.match(line):
            flush_paragraph()
            add("table-row", line, line_number)
            index += 1
            continue

        if QUOTE.match(line):
            flush_paragraph()
            add("blockquote", line, line_number)
            index += 1
            continue

        if not paragraph:
            paragraph_line = line_number
        paragraph.append(line)
        index += 1

    flush_paragraph()
    return units


def compare_ledgers(
    zh_units: list[dict[str, str | int]],
    en_units: list[dict[str, str | int]],
    ledger: dict,
) -> list[str]:
    """Require a monotonic one-to-one mapping for all structural units."""
    errors: list[str] = []
    mappings = ledger.get("units", [])
    mapped_zh: set[int] = set()
    mapped_en: set[int] = set()
    previous_zh = previous_en = -1

    for mapping in mappings:
        zh_ordinal = mapping.get("zh")
        en_ordinal = mapping.get("en")
        if not isinstance(zh_ordinal, int) or not isinstance(en_ordinal, int):
            errors.append("Ledger unit mapping needs integer zh and en ordinals")
            continue
        if zh_ordinal in mapped_zh or en_ordinal in mapped_en:
            errors.append(f"Duplicate ledger mapping: zh {zh_ordinal}, en {en_ordinal}")
            continue
        if zh_ordinal >= len(zh_units) or en_ordinal >= len(en_units):
            errors.append(f"Ledger mapping is outside article inventory: zh {zh_ordinal}, en {en_ordinal}")
            continue
        if zh_ordinal <= previous_zh or en_ordinal <= previous_en:
            errors.append(f"Ledger mapping is not in source order: zh {zh_ordinal}, en {en_ordinal}")
        if zh_units[zh_ordinal]["kind"] != en_units[en_ordinal]["kind"]:
            errors.append(
                f"Unit kind differs at zh {zh_ordinal} and en {en_ordinal}: "
                f"{zh_units[zh_ordinal]['kind']} != {en_units[en_ordinal]['kind']}"
            )
        mapped_zh.add(zh_ordinal)
        mapped_en.add(en_ordinal)
        previous_zh, previous_en = zh_ordinal, en_ordinal

    for ordinal, unit in enumerate(zh_units):
        if ordinal not in mapped_zh:
            errors.append(f"Chinese has an unmapped {unit['kind']} at ordinal {ordinal}")
    for ordinal, unit in enumerate(en_units):
        if ordinal not in mapped_en:
            errors.append(f"English has an unmapped {unit['kind']} at ordinal {ordinal}")
    return errors


def compare_inventories(
    zh_units: list[dict[str, str | int]], en_units: list[dict[str, str | int]]
) -> list[str]:
    """Report every positional structural difference between two inventories."""
    errors: list[str] = []
    shared = min(len(zh_units), len(en_units))
    for ordinal in range(shared):
        zh_kind = zh_units[ordinal]["kind"]
        en_kind = en_units[ordinal]["kind"]
        if zh_kind != en_kind:
            errors.append(f"Unit {ordinal} differs: Chinese {zh_kind}, English {en_kind}")
    for ordinal in range(shared, len(zh_units)):
        errors.append(f"Chinese has an unmapped {zh_units[ordinal]['kind']} at ordinal {ordinal}")
    for ordinal in range(shared, len(en_units)):
        errors.append(f"English has an unmapped {en_units[ordinal]['kind']} at ordinal {ordinal}")
    return errors


def normalized_asset_path(path: str) -> str:
    """Normalize a source link or manifest path to its assets-relative path."""
    marker = "assets/"
    if marker not in path:
        return path
    return marker + path.split(marker, 1)[1]


def image_paths(source: str) -> list[str]:
    """Return image targets in their source order."""
    paths: list[str] = []
    for line in source.splitlines():
        if "![" not in line or "](" not in line:
            continue
        target = line.rsplit("](", 1)[1].split(")", 1)[0]
        paths.append(target.split("#", 1)[0])
    return paths


def compare_figure_paths(
    zh_paths: list[str], en_paths: list[str], figure_pairs: list[dict]
) -> list[str]:
    """Require each source image to match the corresponding figure-pair entry."""
    errors: list[str] = []
    expected_zh = [normalized_asset_path(pair["zh"]) for pair in figure_pairs]
    expected_en = [normalized_asset_path(pair["en"]) for pair in figure_pairs]
    actual_zh = [normalized_asset_path(path) for path in zh_paths]
    actual_en = [normalized_asset_path(path) for path in en_paths]
    for ordinal, (actual, expected) in enumerate(zip(actual_zh, expected_zh), start=1):
        if actual != expected:
            errors.append(
                f"Figure {ordinal} Chinese asset differs: expected {expected}, found {actual}"
            )
    for ordinal, (actual, expected) in enumerate(zip(actual_en, expected_en), start=1):
        if actual != expected:
            errors.append(
                f"Figure {ordinal} English asset differs: expected {expected}, found {actual}"
            )
    if len(actual_zh) != len(expected_zh):
        errors.append(
            f"Chinese figure count differs: expected {len(expected_zh)}, found {len(actual_zh)}"
        )
    if len(actual_en) != len(expected_en):
        errors.append(
            f"English figure count differs: expected {len(expected_en)}, found {len(actual_en)}"
        )
    return errors


def audit_book(
    root: Path, *, part: str | None = None, article: str | None = None
) -> dict[str, list[str]]:
    """Compare all catalog-aligned Chinese and English article inventories."""
    book = root / "book"
    zh_catalog = load_catalog(book)
    en_root = book / "translations" / "en"
    en_catalog = load_catalog(en_root)
    zh_entries = catalog_entries(zh_catalog)
    en_entries = catalog_entries(en_catalog)
    figure_manifest = json.loads((book / "figure-pairs.json").read_text(encoding="utf-8"))
    errors: dict[str, list[str]] = {}
    for zh, en in zip(zh_entries, en_entries):
        if zh["id"] != en["id"]:
            errors[zh["id"]] = [f"Catalog ID differs: Chinese {zh['id']}, English {en['id']}"]
            continue
        if article and zh["id"] != article:
            continue
        if part and not any(
            candidate["id"] == zh["id"] and group["id"] == part
            for group in zh_catalog["parts"]
            for candidate in group["chapters"]
        ):
            continue
        zh_source = (book / zh["path"]).read_text(encoding="utf-8")
        en_source = (en_root / en["path"]).read_text(encoding="utf-8")
        zh_units = inventory_markdown(zh_source)
        en_units = inventory_markdown(en_source)
        article_errors = compare_inventories(zh_units, en_units)
        article_errors.extend(compare_formula_semantics(DISPLAY_MATH.findall(zh_source), DISPLAY_MATH.findall(en_source)))
        figure_pairs = [
            pair for pair in figure_manifest["pairs"] if pair["chapter"] == zh["id"]
        ]
        article_errors.extend(compare_figure_paths(image_paths(zh_source), image_paths(en_source), figure_pairs))
        if article_errors:
            errors[zh["id"]] = article_errors
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--part")
    parser.add_argument("--article")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors = audit_book(args.root.resolve(), part=args.part, article=args.article)
    if args.json:
        print(json.dumps(errors, ensure_ascii=False, indent=2))
    elif errors:
        for article, article_errors in errors.items():
            print(article)
            for error in article_errors:
                print(f"  - {error}")
    else:
        print("Chinese and English structural inventories match.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
