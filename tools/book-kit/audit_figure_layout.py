#!/usr/bin/env python3
"""Audit rendered SVG text against card and viewport boundaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from repaint_publication_figures import diagram_paths


Box = Mapping[str, float]


def containment_error(content: Box, container: Box, tolerance: float = 1.0) -> dict[str, float]:
    """Return sides by which a rendered content box escapes its container."""
    distances = {
        "left": container["x"] - content["x"],
        "right": content["x"] + content["width"] - container["x"] - container["width"],
        "top": container["y"] - content["y"],
        "bottom": content["y"] + content["height"] - container["y"] - container["height"],
    }
    return {side: round(distance, 1) for side, distance in distances.items() if distance > tolerance}


LAYOUT_SCRIPT = r"""() => {
  const box = element => {
    const rect = element.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  };
  const visible = element => {
    for (let node = element; node && node instanceof SVGElement; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0 || node.getAttribute('aria-hidden') === 'true') return false;
    }
    return true;
  };
  const overlap = (first, second) => Math.max(0, Math.min(first.x + first.width, second.x + second.width) - Math.max(first.x, second.x));
  const rects = [...document.querySelectorAll('rect')]
    .filter(element => visible(element) && !element.hasAttribute('data-figure-safe-zone'))
    .map(element => box(element))
    .filter(rect => rect.width >= 30 && rect.height >= 20);
  const viewport = box(document.documentElement);
  const labels = [];
  for (const text of document.querySelectorAll('text')) {
    if (!visible(text) || !text.textContent.trim()) continue;
    const label = box(text);
    const anchor = getComputedStyle(text).textAnchor || text.getAttribute('text-anchor') || 'start';
    const anchorX = anchor === 'middle' ? label.x + label.width / 2 : anchor === 'end' ? label.x + label.width : label.x;
    const anchorY = label.y + label.height / 2;
    const candidates = rects.filter(rect => {
      return anchorX >= rect.x - 1 && anchorX <= rect.x + rect.width + 1 && anchorY >= rect.y - 1 && anchorY <= rect.y + rect.height + 1;
    });
    const owner = candidates.sort((first, second) => first.width * first.height - second.width * second.height)[0];
    labels.push({ text: text.textContent.trim(), box: label, owner: owner || null, viewport });
  }
  return labels;
}"""


def layout_issues(labels: list[dict[str, object]], tolerance: float) -> list[dict[str, object]]:
    """Convert browser geometry into concise layout failures."""
    issues: list[dict[str, object]] = []
    for label in labels:
        viewport_error = containment_error(label["box"], label["viewport"], tolerance)
        owner_error = containment_error(label["box"], label["owner"], tolerance) if label["owner"] else {}
        if viewport_error or owner_error:
            issues.append({
                "text": label["text"],
                "card": owner_error,
                "viewport": viewport_error,
            })
    return issues


def inspect(paths: list[Path], tolerance: float = 15.0) -> dict[Path, list[dict[str, object]]]:
    """Use one Chromium session for actual SVG glyph boxes across all diagrams."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        results = {}
        for path in paths:
            page.goto(path.as_uri(), wait_until="load")
            results[path] = layout_issues(page.evaluate(LAYOUT_SCRIPT), tolerance)
        browser.close()
    return results


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--tolerance", type=float, default=15.0, help="maximum visible overflow in rendered CSS pixels")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    paths = diagram_paths(root)
    results = inspect(paths, args.tolerance)
    report = []
    for path in paths:
        issues = results[path]
        report.append({"path": path.relative_to(root).as_posix(), "issues": issues})
    failures = [item for item in report if item["issues"]]
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audited {len(report)} rendered SVG diagrams; {len(failures)} issue(s).")
    for item in failures:
        print(item["path"])
        for issue in item["issues"]:
            print(f"  - {issue['text']}: card={issue['card']} viewport={issue['viewport']}")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
