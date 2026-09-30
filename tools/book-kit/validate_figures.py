#!/usr/bin/env python3
"""Check the source inventory and accessibility metadata for book SVG figures."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_REFERENCE = re.compile(r"!\[.*?\]\(([^)\s]+\.svg)(?:\s+[^)]*)?\)")
IMAGE_REFERENCE = re.compile(r"!\[.*?\]\(([^)\s]+\.(?:svg|png))(?:\s+[^)]*)?\)")
SEMANTIC_IMAGE_REFERENCE = re.compile(r"!\[(.*?)\]\(([^)\s]+\.(?:svg|png))(?:\s+[^)]*)?\)")
HEADING_REFERENCE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


def svg_targets(source: Path) -> list[str]:
    """Return local SVG targets while allowing brackets in Markdown alt text."""
    return SVG_REFERENCE.findall(source.read_text(encoding="utf-8"))


def image_targets(source: Path) -> list[str]:
    """Return editorial image targets used by an explicit bilingual pair."""
    return IMAGE_REFERENCE.findall(source.read_text(encoding="utf-8"))


def source_image_context(root: Path, source: Path, figure: Path, ordinal: int | None = None) -> tuple[str, str] | None:
    """Return the nearest Markdown heading and authored alternative for one image."""
    heading = ""
    image_ordinal = 0
    for line in source.read_text(encoding="utf-8").splitlines():
        if match := HEADING_REFERENCE.match(line):
            heading = match.group(1).strip()
        for match in SEMANTIC_IMAGE_REFERENCE.finditer(line):
            image_ordinal += 1
            alternative, target = match.groups()
            if (source.parent / target).resolve() == figure.resolve() and (ordinal is None or ordinal == image_ordinal):
                return heading, alternative.strip()
    return None


def catalogued_source_ids(root: Path) -> dict[str, dict[str, str]]:
    """Map each bilingual catalogue source path to its canonical chapter ID."""
    from book_meta import catalog_entries, load_catalog

    result = {"zh": {}, "en": {}}
    for locale, source in (("zh", root / "book"), ("en", root / "book" / "translations" / "en")):
        if not (source / "catalog.json").is_file():
            continue
        for entry in catalog_entries(load_catalog(source)):
            result[locale][(source / entry["path"]).relative_to(root).as_posix()] = entry["id"]
    return result


def validate_semantics(root: Path, figures_data: dict, pairs_data: dict) -> list[str]:
    """Require explicit roles and bilingual instructional equivalents for diagrams."""
    root = root.resolve()
    figures = figures_data.get("figures")
    pairs = pairs_data.get("pairs")
    if not isinstance(figures, list):
        return ['Figure semantic inventory needs a "figures" list']
    if not isinstance(pairs, list):
        return ['Figure semantic inventory needs a "pairs" list']

    errors: list[str] = []
    source_ids = catalogued_source_ids(root)
    by_id: dict[str, dict] = {}
    by_path: dict[str, dict] = {}
    paired_ids = set()
    for figure in figures:
        if not isinstance(figure, dict) or not isinstance(figure.get("path"), str):
            continue
        path = figure["path"]
        identifier = figure.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"figure needs stable id: {path}")
        elif identifier in by_id:
            errors.append(f"figure id is duplicated: {identifier}")
        else:
            by_id[identifier] = figure
        if figure.get("role") not in {"informational", "decorative"}:
            errors.append(f"figure needs explicit role: {path}")
        by_path[path] = figure

    seen_pairs = set()
    for pair in pairs:
        if not isinstance(pair, dict):
            continue
        pair_id = pair.get("id")
        if not isinstance(pair_id, str) or not pair_id.strip():
            errors.append("figure pair needs stable id")
            continue
        if pair_id in seen_pairs:
            errors.append(f"figure pair id is duplicated: {pair_id}")
        seen_pairs.add(pair_id)
        locale_entries = (("zh", "Chinese"), ("en", "English"))
        referenced = []
        for locale, label in locale_entries:
            path, identifier = pair.get(locale), pair.get(f"{locale}_id")
            figure = by_path.get(path)
            if figure is None:
                errors.append(f"semantic pair references unlisted {locale} figure: {pair_id}")
                continue
            if identifier != figure.get("id"):
                errors.append(f"semantic pair needs matching {locale} figure id: {pair_id}")
            elif figure.get("role") == "informational":
                paired_ids.add(identifier)
            referenced.append((locale, label, figure))
        if not referenced or any(figure.get("role") != "informational" for _, _, figure in referenced):
            continue
        semantic = pair.get("semantics")
        if not isinstance(semantic, dict):
            errors.append(f"informational figure needs bilingual semantics: {pair_id}")
            continue
        for locale, label, figure in referenced:
            record = semantic.get(locale)
            if not isinstance(record, dict):
                errors.append(f"informational figure needs {locale} semantic record: {pair_id}")
                continue
            alternative = record.get("alternative")
            if not isinstance(alternative, str) or len(re.sub(r"\s+", "", alternative)) < 8:
                errors.append(f"informational figure needs {locale} alternative text: {pair_id}")
            source_key = f"{locale}_source"
            source_value = pair.get(source_key)
            if not isinstance(source_value, str) or not (root / source_value).is_file():
                errors.append(f"semantic pair needs {locale} source: {pair_id}")
                continue
            canonical_chapter = source_ids[locale].get(source_value)
            if canonical_chapter is None:
                errors.append(f"semantic {locale} source is absent from catalog: {pair_id}")
            elif canonical_chapter != pair.get("chapter"):
                errors.append(f"semantic {locale} source chapter does not match catalog: {pair_id}")
            elif record.get("chapter") != canonical_chapter:
                errors.append(f"semantic {locale} chapter does not match catalog: {pair_id}")
            if record.get("chapter") != pair.get("chapter"):
                errors.append(f"semantic chapter does not match pair: {pair_id}")
            context = source_image_context(root, root / source_value, root / figure["path"], pair.get("ordinal"))
            if context is None:
                errors.append(f"semantic {locale} source does not reference figure: {pair_id}")
                continue
            source_heading, source_alternative = context
            if record.get("heading") != source_heading:
                errors.append(f"semantic heading is absent from {locale} source: {pair_id}")
            if isinstance(alternative, str) and re.sub(r"\s+", " ", alternative).strip() != re.sub(r"\s+", " ", source_alternative).strip():
                errors.append(f"semantic alternative does not match {locale} source alt text: {pair_id}")
        canonical = [source_ids[locale].get(pair.get(f"{locale}_source")) for locale, _label in locale_entries]
        if all(chapter is not None for chapter in canonical) and canonical[0] != canonical[1]:
            errors.append(f"semantic zh and en source chapters disagree: {pair_id}")
    for identifier, figure in by_id.items():
        if figure.get("role") == "informational" and identifier not in paired_ids:
            errors.append(f"informational figure has no semantic pair: {identifier}")
    return errors


def validate_pairs(root: Path, data: dict) -> list[str]:
    """Validate explicit Chinese/English editorial-figure counterparts."""
    root = root.resolve()
    pairs = data.get("pairs")
    if not isinstance(pairs, list):
        return ['Figure pair manifest needs a "pairs" list']
    errors: list[str] = []
    seen = set()
    paired_chinese = Counter()
    for pair in pairs:
        if not isinstance(pair, dict):
            errors.append("Every figure pair needs an object")
            continue
        chapter, ordinal = pair.get("chapter"), pair.get("ordinal")
        zh, en = pair.get("zh"), pair.get("en")
        zh_source, en_source = pair.get("zh_source"), pair.get("en_source")
        if not isinstance(chapter, str) or not isinstance(ordinal, int):
            errors.append("Every figure pair needs a chapter and integer ordinal")
            continue
        key = (chapter, ordinal)
        if key in seen:
            errors.append(f"Figure pair is duplicated: {chapter} #{ordinal}")
        seen.add(key)
        if not isinstance(zh, str) or not isinstance(en, str):
            errors.append(f"Figure pair needs zh and en paths: {chapter} #{ordinal}")
            continue
        if isinstance(zh_source, str) and zh.endswith(".svg") and "/chapters/" in zh_source:
            paired_chinese[(zh_source, zh)] += 1
        if not (root / zh).is_file():
            errors.append(f"Figure pair has missing Chinese counterpart: {zh}")
        if not (root / en).is_file():
            errors.append(f"Figure pair has missing English counterpart: {en}")
        for locale, figure, source in (
            ("Chinese", zh, zh_source),
            ("English", en, en_source),
        ):
            if not isinstance(source, str):
                errors.append(f"Figure pair needs {locale} source: {chapter} #{ordinal}")
                continue
            source_path = root / source
            if not source_path.is_file():
                errors.append(f"Figure pair has missing {locale} source: {source}")
                continue
            references = {
                (source_path.parent / target).resolve()
                for target in image_targets(source_path)
            }
            if (root / figure).resolve() not in references:
                errors.append(
                    f"{source} does not reference {locale} counterpart: {figure}"
                )

    chinese_sources = root / "book" / "chapters"
    if chinese_sources.is_dir():
        discovered_chinese = Counter()
        for source_path in chinese_sources.rglob("*.md"):
            source = source_path.relative_to(root).as_posix()
            for target in svg_targets(source_path):
                figure = (source_path.parent / target).resolve().relative_to(root).as_posix()
                discovered_chinese[(source, figure)] += 1
        for (source, figure), count in sorted((discovered_chinese - paired_chinese).items()):
            errors.append(
                f"unpaired Chinese editorial figure: {source}: {figure} ({count} occurrence(s))"
            )
        for (source, figure), count in sorted((paired_chinese - discovered_chinese).items()):
            errors.append(
                f"Figure pair has no matching Chinese editorial figure: {source}: {figure} ({count} occurrence(s))"
            )
    return errors


def validate(root: Path, manifest: Path) -> list[str]:
    try:
        entries = json.loads(manifest.read_text(encoding="utf-8"))["figures"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"Cannot read figure manifest: {exc}"]

    listed = set()
    errors = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            errors.append("Every figure manifest entry needs a string path")
            continue
        relative = entry["path"]
        if relative in listed:
            errors.append(f"Figure is listed more than once: {relative}")
            continue
        listed.add(relative)
        path = root / relative
        if not path.is_file():
            errors.append(f"Listed figure is missing: {relative}")
            continue
        if entry.get("kind") != "diagram":
            continue
        try:
            svg = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"Invalid SVG {relative}: {exc}")
            continue
        tags = {node.tag.rsplit("}", 1)[-1] for node in svg}
        if svg.attrib.get("role") != "img":
            errors.append(f"Diagram needs role=\"img\": {relative}")
        for tag in ("title", "desc"):
            if tag not in tags:
                errors.append(f"Diagram needs <{tag}>: {relative}")

    actual = {
        path.relative_to(root).as_posix()
        for path in (root / "book" / "assets").rglob("*.svg")
    }
    for relative in sorted(actual - listed):
        errors.append(f"SVG asset is not listed in the figure manifest: {relative}")
    for relative in sorted(listed - actual):
        errors.append(f"Figure manifest path is not an SVG asset: {relative}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--manifest", type=Path, default=root / "book" / "figures.json")
    parser.add_argument("--pairs", type=Path, default=root / "book" / "figure-pairs.json")
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.manifest.resolve())
    if args.pairs.is_file():
        try:
            pairs = json.loads(args.pairs.read_text(encoding="utf-8"))
            figures = json.loads(args.manifest.read_text(encoding="utf-8"))
            errors.extend(validate_pairs(args.root.resolve(), pairs))
            errors.extend(validate_semantics(args.root.resolve(), figures, pairs))
        except (OSError, ValueError) as exc:
            errors.append(f"Cannot read figure pair manifest: {exc}")
    if errors:
        print("Figure validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print("Figure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
