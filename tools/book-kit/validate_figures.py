#!/usr/bin/env python3
"""Check the source inventory and accessibility metadata for book SVG figures."""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


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
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.manifest.resolve())
    if errors:
        print("Figure validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print("Figure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
