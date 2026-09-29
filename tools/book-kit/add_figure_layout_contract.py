#!/usr/bin/env python3
"""Add auditable text safety zones and connector markers to editorial SVGs."""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from repaint_publication_figures import diagram_paths


TEXT = re.compile(r"<text\b(?P<attrs>[^>]*)>(?P<body>.*?)</text>", re.DOTALL)
TAG = re.compile(r"<[^>]+>")
ATTRIBUTE = re.compile(r'''\b(?P<name>[\w:-]+)\s*=\s*(?P<quote>["'])(?P<value>.*?)(?P=quote)''')
MARKED_CONNECTOR = re.compile(r"<(?:path|line|polyline)\b(?=[^>]*\bmarker-(?:start|end)\s*=)(?![^>]*data-figure-connector)[^>]*>")
CONTRACT_GROUP = re.compile(r'<g aria-hidden="true" fill="none" opacity="0" pointer-events="none">.*?</g>(?=</svg>)', re.DOTALL)


def attributes(value: str) -> dict[str, str]:
    return {match.group("name"): match.group("value") for match in ATTRIBUTE.finditer(value)}


def font_size(attrs: dict[str, str]) -> float:
    value = attrs.get("font-size")
    if value:
        match = re.match(r"\d+(?:\.\d+)?", value)
        if match:
            return float(match.group(0))
    classes = set(attrs.get("class", "").split())
    if "h" in classes:
        return 22.0
    if "b" in classes:
        return 17.0
    return 17.0


def is_cjk(character: str) -> bool:
    codepoint = ord(character)
    return 0x3400 <= codepoint <= 0x4DBF or 0x4E00 <= codepoint <= 0x9FFF or 0xF900 <= codepoint <= 0xFAFF


def text_zone(match: re.Match[str]) -> str | None:
    attrs = attributes(match.group("attrs"))
    try:
        x, y = float(attrs["x"]), float(attrs["y"])
    except (KeyError, ValueError):
        return None
    label = html.unescape(TAG.sub("", match.group("body"))).strip()
    if not label:
        return None
    size = font_size(attrs)
    glyphs = sum(0.95 if is_cjk(character) else 0.52 for character in label)
    width = max(16.0, glyphs * size)
    anchor = attrs.get("text-anchor", "start")
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    return f'<rect data-figure-safe-zone="text" x="{x - 12:.1f}" y="{y - size - 12:.1f}" width="{width + 24:.1f}" height="{size * 1.35 + 24:.1f}"/>'


def mark_connector(match: re.Match[str]) -> str:
    tag = match.group(0)
    if tag.endswith("/>"):
        return tag[:-2] + ' data-figure-connector="true"/>'
    return tag[:-1] + ' data-figure-connector="true">'


def contract_svg(path: Path, refresh: bool = False) -> bool:
    """Mark visible text and arrowed routing paths once, preserving SVG drawing markup."""
    source = path.read_text(encoding="utf-8")
    if "data-figure-safe-zone" in source:
        if not refresh:
            return False
        source = CONTRACT_GROUP.sub("", source)
        source = source.replace(' data-figure-connector="true"', "")
    zones = [zone for match in TEXT.finditer(source) if (zone := text_zone(match))]
    if not zones:
        return False
    marked = MARKED_CONNECTOR.sub(mark_connector, source)
    contract = '<g aria-hidden="true" fill="none" opacity="0" pointer-events="none">' + "".join(zones) + "</g>"
    contracted = marked.replace("</svg>", contract + "</svg>")
    path.write_text(contracted, encoding="utf-8")
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--write", action="store_true", help="rewrite SVG source files")
    parser.add_argument("--refresh", action="store_true", help="recompute existing contract markers")
    args = parser.parse_args()
    paths = diagram_paths(args.root.resolve())
    if not args.write:
        print(f"Would add a layout contract to {len(paths)} SVG diagrams; rerun with --write to apply.")
        return 0
    changed = sum(contract_svg(path, refresh=args.refresh) for path in paths)
    print(f"Added a layout contract to {changed} of {len(paths)} SVG diagrams.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
