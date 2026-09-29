#!/usr/bin/env python3
"""Migrate book SVGs from the legacy warm palette to the publication palette."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


COLOURS = {
    # Canvas and neutral scaffolding.
    "fffdf8": "FFFFFF", "fff8eb": "FFFFFF", "fff7f4": "FFFFFF", "f4f4f1": "F6F8FA",
    "e7f0ed": "EAF3FB", "e7f1ed": "EAF3FB", "edf6f0": "EAF3FB", "f0f4f1": "F4F8FC",
    "edf2ef": "F4F8FC", "f4f8f5": "F4F8FC", "f3f8f5": "F4F8FC", "d7e6de": "CFCECE",
    "d4e4dc": "CFCECE", "d3ddd7": "CFCECE", "a7beb4": "8EB6D8", "8db29f": "8EB6D8",
    "697a72": "5E7F9C", "6e8479": "5E7F9C", "516a61": "416985",
    # Deep ink and the former green information hierarchy.
    "183f37": "17324D", "173f36": "17324D", "183c36": "17324D", "244f46": "0F4D92",
    "315f55": "0F4D92", "246052": "3775BA", "426b61": "3775BA", "527a70": "5E7F9C",
    "55796f": "5E7F9C", "79a89d": "8EB6D8", "87b9a8": "8EB6D8", "9cc3b3": "AADCA9",
    "d8e9de": "DDF3DE", "dff3e9": "DDF3DE", "e5f1e9": "DDF3DE", "f3faf6": "F4FBF5",
    # Warm attention marks become the restrained publication emphasis colour.
    "bd7b36": "FFD700", "bd7a35": "FFD700", "d6a45d": "D8A919", "d7a563": "D8A919",
    "d9aa69": "D8A919", "f4d79f": "FFF1B8", "f3d59c": "FFF1B8", "fff5e7": "FFF8D6",
    "fff3e3": "FFF8D6", "fff2dc": "FFF8D6", "fff1df": "FFF8D6", "fff0eb": "FFF8D6",
    "714815": "765800", "754c19": "765800", "654413": "765800", "795b34": "765800",
    "8b5a1f": "765800", "8b7049": "765800", "8b5d42": "765800",
    # Existing danger/contrast semantics retain a clear red hierarchy.
    "bd6257": "B64342", "bd5f55": "B64342", "a34d43": "B64342", "873a32": "B64342",
    "873d35": "B64342", "9b4a43": "B64342", "6e302b": "8F3635", "79514b": "8F3635",
    "dc9e92": "E9A6A1", "e08d80": "E9A6A1", "c6887d": "E9A6A1", "f8e3dc": "F6CFCB",
    "f8e6df": "F6CFCB", "f9e4df": "F6CFCB", "f8deda": "F6CFCB", "f7e3dc": "F6CFCB",
    "ffe8e2": "F6CFCB", "fff1eb": "FDE9E7",
}
HEX = re.compile(r"#([0-9A-Fa-f]{6})")


def repaint_svg(path: Path) -> bool:
    """Apply only semantic colour substitutions and return whether a file changed."""
    source = path.read_text(encoding="utf-8")

    def replacement(match: re.Match[str]) -> str:
        return "#" + COLOURS.get(match.group(1).lower(), match.group(1).upper())

    repainted = HEX.sub(replacement, source)
    if repainted == source:
        return False
    path.write_text(repainted, encoding="utf-8")
    return True


def diagram_paths(root: Path) -> list[Path]:
    manifest = json.loads((root / "book" / "figures.json").read_text(encoding="utf-8"))
    return [root / item["path"] for item in manifest["figures"] if item.get("kind") == "diagram"]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--write", action="store_true", help="rewrite SVG source files")
    args = parser.parse_args()
    paths = diagram_paths(args.root.resolve())
    if not args.write:
        print(f"Would repaint {len(paths)} SVG diagrams; rerun with --write to apply.")
        return 0
    changed = sum(repaint_svg(path) for path in paths)
    print(f"Repainted {changed} of {len(paths)} SVG diagrams.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
