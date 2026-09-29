#!/usr/bin/env python3
"""Audit editorial SVG diagrams and optionally rasterize them for visual review."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "{http://www.w3.org/2000/svg}"
NUMBER = re.compile(r"^-?(?:\d+(?:\.\d*)?|\.\d+)$")
PATH_TOKEN = re.compile(r"([MmLlHhVvCcZz])|(-?(?:\d+(?:\.\d*)?|\.\d+))")


def number(value: str | None) -> float | None:
    if value and NUMBER.match(value.strip()):
        return float(value)
    return None


def local_name(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def point_pairs(value: str | None) -> list[tuple[float, float]] | None:
    if not value:
        return None
    values = [float(match.group(0)) for match in re.finditer(r"-?(?:\d+(?:\.\d*)?|\.\d+)", value)]
    if len(values) < 4 or len(values) % 2:
        return None
    return list(zip(values[::2], values[1::2]))


def path_segments(value: str | None) -> list[tuple[tuple[float, float], tuple[float, float]]] | None:
    """Extract straight segments from a deliberately simple routing path."""
    if not value:
        return None
    tokens = [command or numeric for command, numeric in PATH_TOKEN.findall(value)]
    if not tokens:
        return None
    current: tuple[float, float] | None = None
    start: tuple[float, float] | None = None
    command: str | None = None
    index = 0
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    try:
        while index < len(tokens):
            if tokens[index].isalpha():
                command = tokens[index]
                index += 1
                if command in "Zz":
                    if current is not None and start is not None and current != start:
                        segments.append((current, start))
                    current = start
                    continue
            if command is None:
                return None
            relative = command.islower()
            if command in "MmLl":
                x, y = float(tokens[index]), float(tokens[index + 1])
                index += 2
                target = (x + current[0], y + current[1]) if relative and current else (x, y)
                if command in "Mm":
                    start = target
                elif current is not None:
                    segments.append((current, target))
                current = target
                if command in "Mm":
                    command = "l" if relative else "L"
            elif command in "Hh":
                x = float(tokens[index])
                index += 1
                if current is None:
                    return None
                target = (x + current[0], current[1]) if relative else (x, current[1])
                segments.append((current, target))
                current = target
            elif command in "Vv":
                y = float(tokens[index])
                index += 1
                if current is None:
                    return None
                target = (current[0], y + current[1]) if relative else (current[0], y)
                segments.append((current, target))
                current = target
            elif command in "Cc":
                if current is None:
                    return None
                values = [float(tokens[index + offset]) for offset in range(6)]
                index += 6
                base = current
                control_one = (values[0], values[1])
                control_two = (values[2], values[3])
                target = (values[4], values[5])
                if relative:
                    control_one = (base[0] + control_one[0], base[1] + control_one[1])
                    control_two = (base[0] + control_two[0], base[1] + control_two[1])
                    target = (base[0] + target[0], base[1] + target[1])
                previous = base
                for step in range(1, 13):
                    t = step / 12
                    inverse = 1 - t
                    point = (
                        inverse ** 3 * base[0] + 3 * inverse ** 2 * t * control_one[0]
                        + 3 * inverse * t ** 2 * control_two[0] + t ** 3 * target[0],
                        inverse ** 3 * base[1] + 3 * inverse ** 2 * t * control_one[1]
                        + 3 * inverse * t ** 2 * control_two[1] + t ** 3 * target[1],
                    )
                    segments.append((previous, point))
                    previous = point
                current = target
            else:
                return None
    except (IndexError, ValueError):
        return None
    return segments


def segment_intersects_rect(
    start: tuple[float, float], end: tuple[float, float], rect: tuple[float, float, float, float]
) -> bool:
    """Use Liang-Barsky clipping to test a line segment against a text safe zone."""
    x, y, width, height = rect
    x_min, x_max, y_min, y_max = x, x + width, y, y + height
    dx, dy = end[0] - start[0], end[1] - start[1]
    lower, upper = 0.0, 1.0
    for p, q in ((-dx, start[0] - x_min), (dx, x_max - start[0]), (-dy, start[1] - y_min), (dy, y_max - start[1])):
        if p == 0:
            if q < 0:
                return False
            continue
        ratio = q / p
        if p < 0:
            if ratio > upper:
                return False
            lower = max(lower, ratio)
        else:
            if ratio < lower:
                return False
            upper = min(upper, ratio)
    return lower <= upper


def connector_segments(node: ET.Element) -> list[tuple[tuple[float, float], tuple[float, float]]] | None:
    tag = local_name(node)
    if tag == "path":
        return path_segments(node.attrib.get("d"))
    if tag == "line":
        values = [number(node.attrib.get(key)) for key in ("x1", "y1", "x2", "y2")]
        if any(value is None for value in values):
            return None
        x1, y1, x2, y2 = values
        return [((x1, y1), (x2, y2))]
    if tag in {"polyline", "polygon"}:
        points = point_pairs(node.attrib.get("points"))
        if points is None:
            return None
        return list(zip(points, points[1:]))
    return None


def audit_svg(path: Path) -> list[str]:
    """Return deterministic, source-level quality errors for one SVG."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"invalid XML: {exc}"]
    errors: list[str] = []
    if root.attrib.get("role") != "img":
        errors.append('needs role="img"')
    children = {local_name(node) for node in root}
    for tag in ("title", "desc"):
        if tag not in children:
            errors.append(f"needs <{tag}>")
    view_box = (root.attrib.get("viewBox") or "").replace(",", " ").split()
    if len(view_box) != 4 or any(number(value) is None for value in view_box):
        return errors + ["needs numeric viewBox"]
    left, top, width, height = (float(value) for value in view_box)
    right, bottom = left + width, top + height
    for text in root.iter():
        if local_name(text) != "text":
            continue
        x, y = number(text.attrib.get("x")), number(text.attrib.get("y"))
        if x is not None and not left <= x <= right:
            errors.append("text x coordinate falls outside viewBox")
        if y is not None and not top <= y <= bottom:
            errors.append("text y coordinate falls outside viewBox")
    safe_zones: list[tuple[float, float, float, float]] = []
    connectors: list[list[tuple[tuple[float, float], tuple[float, float]]]] = []
    for node in root.iter():
        if node.attrib.get("data-figure-safe-zone") == "text":
            values = [number(node.attrib.get(key)) for key in ("x", "y", "width", "height")]
            if local_name(node) != "rect" or any(value is None for value in values) or values[2] < 0 or values[3] < 0:
                errors.append("text safe zone needs numeric non-negative dimensions")
            else:
                x, y, zone_width, zone_height = values
                safe_zones.append((x, y, zone_width, zone_height))
        if node.attrib.get("data-figure-connector") == "true":
            segments = connector_segments(node)
            if segments is None:
                errors.append("connector needs a supported straight routing path")
            else:
                connectors.append(segments)
    for segments in connectors:
        if any(segment_intersects_rect(start, end, zone) for start, end in segments for zone in safe_zones):
            errors.append("connector intersects text safe zone")
    return errors


def figures(root: Path) -> list[Path]:
    manifest = json.loads((root / "book" / "figures.json").read_text(encoding="utf-8"))
    return sorted(
        root / entry["path"]
        for entry in manifest["figures"]
        if entry.get("kind") == "diagram"
    )


def rasterize(path: Path, output: Path, width: int) -> str | None:
    if not shutil.which("rsvg-convert"):
        return "rsvg-convert is unavailable"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["rsvg-convert", "--width", str(width), str(path), "-o", str(output)],
        text=True,
        capture_output=True,
    )
    return result.stderr.strip() or f"rsvg-convert failed ({result.returncode})" if result.returncode else None


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    report = []
    for path in figures(root):
        relative = path.relative_to(root).as_posix()
        errors = audit_svg(path)
        if args.render_dir:
            output = args.render_dir / relative.replace(".svg", ".png")
            for width in (960, 390):
                render_error = rasterize(path, output.with_name(f"{output.stem}-{width}.png"), width)
                if render_error:
                    errors.append(render_error)
        report.append({"path": relative, "errors": errors})
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failures = [item for item in report if item["errors"]]
    print(f"Audited {len(report)} SVG diagrams; {len(failures)} issue(s).")
    for item in failures:
        print(item["path"], *[f"- {error}" for error in item["errors"]], sep="\n  ")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    sys.exit(main())
