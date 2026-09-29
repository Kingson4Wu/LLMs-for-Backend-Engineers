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


def svg_targets(source: Path) -> list[str]:
    """Return local SVG targets while allowing brackets in Markdown alt text."""
    return SVG_REFERENCE.findall(source.read_text(encoding="utf-8"))


def image_targets(source: Path) -> list[str]:
    """Return editorial image targets used by an explicit bilingual pair."""
    return IMAGE_REFERENCE.findall(source.read_text(encoding="utf-8"))


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
            errors.extend(validate_pairs(args.root.resolve(), json.loads(args.pairs.read_text(encoding="utf-8"))))
        except (OSError, ValueError) as exc:
            errors.append(f"Cannot read figure pair manifest: {exc}")
    if errors:
        print("Figure validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print("Figure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
